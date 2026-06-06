"""
PRISM Voice Intake — AI-assisted phone call center for NEMT trip scheduling.

Inbound Twilio calls → structured slot collection → POST /prism/intake + NEMT order.

Env:
  TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER  (required for live calls)
  PRISM_VOICE_BASE_URL   Public HTTPS base (e.g. https://deedavis.pythonanywhere.com)
  PRISM_VOICE_TRANSFER_NUMBER  E.164 ops line for human handoff (+12483764550)
  OPENAI_API_KEY         Optional — improves speech parsing
  PRISM_VOICE_OPENAI_MODEL  Default gpt-4o-mini
  PRISM_VOICE_TTS        Twilio generative voice (default Polly.Ruth-Generative)
  ELEVENLABS_API_KEY     Optional — most natural human voice via ElevenLabs
  ELEVENLABS_VOICE_ID    ElevenLabs voice (default Rachel)
"""

from __future__ import annotations

import json
import logging
import os
import re
import threading
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from flask import Blueprint, Response, current_app, jsonify, request, send_from_directory
from twilio.twiml.voice_response import Gather, VoiceResponse

from prism_voice_tts import (
    append_spoken,
    speak_for_phone,
    tts_provider_label,
    voice_id,
    elevenlabs_enabled,
)

logger = logging.getLogger("prism.voice")

prism_voice = Blueprint("prism_voice", __name__)

EASTERN = ZoneInfo("America/Detroit")

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads", "prism")
_SESSIONS_FILE = os.path.join(_DATA_DIR, "voice_sessions.json")
_CALL_LOG_FILE = os.path.join(_DATA_DIR, "voice_call_log.json")

NEMT_SLOTS = [
    "member_name",
    "member_dob",
    "member_medicaid_id",
    "pickup_address",
    "dropoff_address",
    "pickup_when",
    "transport_type",
    "confirm",
]

SLOT_PROMPTS: Dict[str, str] = {}  # built dynamically — see _prompt_for_slot

RETRY_PROMPT = "Sorry, I didn't quite catch that — could you say that again?"
TIMEOUT_PROMPT = (
    "It sounds like you may have stepped away. "
    "Feel free to call us back whenever you're ready. Take care."
)

_GREETING = (
    "Thank you for trusting DDI. "
    "I'm here to help you plan your agenda. "
    "This call may be recorded for quality."
)


def _first_name(slots: Dict[str, str]) -> str:
    name = (slots.get("member_name") or "").strip()
    return name.split()[0] if name else ""


def _prompt_for_slot(slot: str, slots: Optional[Dict[str, str]] = None) -> str:
    """Conversational prompts — acknowledgments, not a script."""
    slots = slots or {}
    fn = _first_name(slots)

    prompts = {
        "member_name": "What is the member's full name?",
        "member_dob": (
            f"Got it, {fn}. What's their date of birth?"
            if fn
            else "What's the member's date of birth?"
        ),
        "member_medicaid_id": "And their Medicaid or member ID number?",
        "pickup_address": "Where should we pick them up? Street address and city is perfect.",
        "dropoff_address": "And where should we take them? Street address and city is perfect.",
        "pickup_when": "When do they need to be picked up? You can say something like tomorrow at nine A M.",
        "transport_type": (
            "Will a standard ride work, or do they need a wheelchair accessible vehicle?"
        ),
        "confirm": "Does all of that sound right?",
    }
    return prompts.get(slot, "")


def _confirmation_summary(slots: Dict[str, str]) -> str:
    tt = slots.get("transport_type", "ambulatory")
    tt_label = "a wheelchair accessible ride" if tt == "wheelchair" else "a standard ride"
    fn = _first_name(slots)
    who = f"for {fn}" if fn else "for the member"
    return speak_for_phone(
        f"Okay — let me make sure I have this right. "
        f"This is {tt_label} {who}, "
        f"picking up at {slots.get('pickup_address', '')}, "
        f"going to {slots.get('dropoff_address', '')}, "
        f"on {slots.get('pickup_when', '')}. "
        f"If that's correct, say yes. If not, say no and we can start over."
    )


def _ensure_data_dir() -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)


def _load_json(path: str, default: Any) -> Any:
    _ensure_data_dir()
    if not os.path.isfile(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path: str, data: Any) -> None:
    _ensure_data_dir()
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    os.replace(tmp, path)


def _twilio_configured() -> bool:
    return bool(
        os.environ.get("TWILIO_ACCOUNT_SID")
        and os.environ.get("TWILIO_AUTH_TOKEN")
        and os.environ.get("TWILIO_FROM_NUMBER")
    )


def _voice_base_url() -> str:
    explicit = (os.environ.get("PRISM_VOICE_BASE_URL") or "").strip().rstrip("/")
    if explicit:
        return explicit
    try:
        return request.url_root.rstrip("/")
    except RuntimeError:
        return ""


def _transfer_number() -> str:
    return _clean_phone(os.environ.get("PRISM_VOICE_TRANSFER_NUMBER", "2483764550"))


def _clean_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    return f"+{digits}" if digits else ""


def _mask_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) < 4:
        return ""
    return f"***-***-{digits[-4:]}"


def _get_session(call_sid: str) -> Dict[str, Any]:
    sessions = _load_json(_SESSIONS_FILE, {})
    if call_sid not in sessions:
        sessions[call_sid] = {
            "call_sid": call_sid,
            "flow": "nemt",
            "step_index": 0,
            "slots": {},
            "created_at": datetime.now(EASTERN).isoformat(),
            "updated_at": datetime.now(EASTERN).isoformat(),
        }
        _save_json(_SESSIONS_FILE, sessions)
    return sessions[call_sid]


def _update_session(call_sid: str, session: Dict[str, Any]) -> None:
    sessions = _load_json(_SESSIONS_FILE, {})
    session["updated_at"] = datetime.now(EASTERN).isoformat()
    sessions[call_sid] = session
    _save_json(_SESSIONS_FILE, sessions)


def _append_call_log(entry: Dict[str, Any]) -> None:
    log = _load_json(_CALL_LOG_FILE, [])
    log.insert(0, entry)
    _save_json(_CALL_LOG_FILE, log[:500])


def _current_slot(session: Dict[str, Any]) -> Optional[str]:
    idx = int(session.get("step_index", 0))
    if idx >= len(NEMT_SLOTS):
        return None
    return NEMT_SLOTS[idx]


def _advance_session(session: Dict[str, Any]) -> None:
    session["step_index"] = int(session.get("step_index", 0)) + 1


def _wants_transfer(speech: str) -> bool:
    s = (speech or "").lower()
    return any(
        k in s
        for k in (
            "representative",
            "operator",
            "agent",
            "human",
            "person",
            "transfer",
            "speak to someone",
            "talk to someone",
        )
    )


def _parse_yes_no(speech: str) -> Optional[bool]:
    s = (speech or "").lower().strip()
    if any(w in s for w in ("yes", "yeah", "yep", "correct", "confirm", "that's right", "sounds good")):
        return True
    if any(w in s for w in ("no", "nope", "wrong", "start over", "again", "cancel")):
        return False
    return None


def _parse_transport_type(speech: str) -> str:
    s = (speech or "").lower()
    if any(w in s for w in ("wheelchair", "wav", "wheel chair", "accessible", "lift")):
        return "wheelchair"
    return "ambulatory"


def _openai_parse_slot(slot: str, speech: str, session: Dict[str, Any]) -> Optional[str]:
    api_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key or not speech.strip():
        return None
    model = os.environ.get("PRISM_VOICE_OPENAI_MODEL", "gpt-4o-mini")
    system = (
        "You extract one field from a DDI ride-scheduling phone call. "
        "Return ONLY the extracted value as plain text, no JSON, no explanation. "
        "For confirm slot return exactly YES or NO."
    )
    user = f"Field: {slot}\nCaller said: {speech}\nKnown so far: {json.dumps(session.get('slots', {}))}"
    try:
        import urllib.error
        import urllib.request

        payload = json.dumps(
            {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "max_tokens": 120,
                "temperature": 0,
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
        if slot == "confirm":
            if text.upper().startswith("Y"):
                return "yes"
            if text.upper().startswith("N"):
                return "no"
        return text or None
    except Exception as exc:
        logger.warning("OpenAI slot parse skipped: %s", exc)
        return None


def _normalize_slot_value(slot: str, speech: str, session: Dict[str, Any]) -> Optional[str]:
    raw = (speech or "").strip()
    if not raw:
        return None

    ai = _openai_parse_slot(slot, raw, session)
    if ai:
        raw = ai

    if slot == "transport_type":
        return _parse_transport_type(raw)
    if slot == "confirm":
        yn = _parse_yes_no(raw)
        if yn is True:
            return "yes"
        if yn is False:
            return "no"
        return None
    if slot == "member_medicaid_id":
        return re.sub(r"\s+", "", raw.upper())
    return raw


def _split_pickup_when(when: str) -> Tuple[str, str]:
    """Best-effort split into date + time strings for PRISM intake."""
    when = (when or "").strip()
    if not when:
        return datetime.now(EASTERN).strftime("%m/%d/%Y"), ""
    m = re.match(r"(.+?)\s+(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm).*)", when)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return when, ""


def _submit_nemt_order(session: Dict[str, Any], caller_phone: str) -> Dict[str, Any]:
    slots = session.get("slots") or {}
    sched_date, sched_time = _split_pickup_when(slots.get("pickup_when", ""))
    transport = slots.get("transport_type", "ambulatory")
    from prism_confirmation_ids import generate_confirmation_id

    conf = generate_confirmation_id(
        "nemt",
        "voice",
        details={
            "mobility_lane": "MOB-A",
            "program_type": "Medicaid / MCO / Plan NEMT",
            "payer": "HAP CareSource",
            "contract_payer_id": 1,
        },
        client_company="HAP CareSource Member",
        payer_name="HAP CareSource",
        contract_payer_id=1,
    )
    member_phone = _clean_phone(caller_phone)

    intake_payload = {
        "service_key": "nemt",
        "service_label": "NEMT & Medical Mobility",
        "channel": "voice",
        "urgency": "scheduled",
        "tier": 2,
        "confirmation": conf,
        "client_company": "HAP CareSource Member",
        "client_name": slots.get("member_name", ""),
        "client_contact": slots.get("member_name", ""),
        "client_phone": member_phone,
        "subject_first": (slots.get("member_name", "").split() or [""])[0],
        "subject_last": " ".join((slots.get("member_name", "").split() or [""])[1:]),
        "subject_dob": slots.get("member_dob", ""),
        "subject_phone": member_phone,
        "donor-location": slots.get("pickup_address", ""),
        "collection-site": slots.get("dropoff_address", ""),
        "subject_location": slots.get("pickup_address", ""),
        "sched_date": sched_date,
        "sched_time": sched_time,
        "sched_tz": "EST",
        "notes": f"Voice intake call {session.get('call_sid', '')}",
        "details": {
            "program_type": "Medicaid / MCO / Plan NEMT",
            "mobility_lane": "MOB-A",
            "trip_type": "Wheelchair (WAV)" if transport == "wheelchair" else "Ambulatory",
            "leg_type": "One-way",
            "appointment_purpose": "Medical appointment",
            "member_id": slots.get("member_medicaid_id", ""),
            "pickup_address": slots.get("pickup_address", ""),
            "dropoff_address": slots.get("dropoff_address", ""),
            "intake_channel": "voice_ai",
            "voice_call_sid": session.get("call_sid"),
            "confirmation_phone_last4": re.sub(r"\D", "", member_phone)[-4:] if member_phone else "",
        },
        "billing_tier": "contract",
        "payment_method": "mco_billing",
        "order_total": 0,
        "pricing_model": "scoped_per_event",
    }

    prism_result: Dict[str, Any] = {}
    try:
        from prism_orders_api import _create_intake_order_impl

        with current_app.test_request_context(
            "/prism/intake", method="POST", json=intake_payload
        ):
            resp = _create_intake_order_impl()
            if isinstance(resp, tuple):
                body, status = resp[0], resp[1]
                prism_result = body.get_json() if hasattr(body, "get_json") else {}
                if status >= 400:
                    raise RuntimeError(prism_result.get("error", f"Intake failed ({status})"))
            else:
                prism_result = resp.get_json() if hasattr(resp, "get_json") else {}
    except Exception as exc:
        logger.exception("PRISM intake from voice failed")
        raise RuntimeError(f"Could not create PRISM order: {exc}") from exc

    nemt_result: Dict[str, Any] = {}
    try:
        from nemt_billing import PAYER_DEFAULT
        from prism_nemt import create_nemt_order

        pickup_iso = f"{sched_date} {sched_time}".strip()
        nemt_order = create_nemt_order(
            member_medicaid_id=slots.get("member_medicaid_id", ""),
            member_name=slots.get("member_name", ""),
            member_dob=slots.get("member_dob", "Pending verification"),
            payer=PAYER_DEFAULT,
            transport_type=transport,
            pickup_address=slots.get("pickup_address", ""),
            dropoff_address=slots.get("dropoff_address", ""),
            pickup_time=pickup_iso or sched_date,
            trip_purpose="Medical appointment",
            notes=f"Voice intake {conf} · call {session.get('call_sid', '')}",
        )
        nemt_result = nemt_order
    except Exception as exc:
        logger.warning("NEMT order mirror skipped: %s", exc)

    order_id = (prism_result.get("order") or {}).get("id") or conf
    return {
        "confirmation": order_id,
        "prism": prism_result,
        "nemt_order_id": nemt_result.get("order_id"),
    }


def _gather_twiml(session: Dict[str, Any], prompt: str, call_sid: str) -> str:
    base = _voice_base_url()
    action = f"{base}/prism/voice/gather"
    vr = VoiceResponse()
    gather = Gather(
        input="speech",
        action=action,
        method="POST",
        speech_timeout="auto",
        language="en-US",
        hints="yes,no,wheelchair,standard,Medicaid,appointment,tomorrow,today",
        timeout=8,
    )
    append_spoken(gather, speak_for_phone(prompt), base_url=base)
    vr.append(gather)
    append_spoken(vr, TIMEOUT_PROMPT, base_url=base)
    vr.hangup()
    return str(vr)


def _transfer_twiml() -> str:
    base = _voice_base_url()
    vr = VoiceResponse()
    transfer = _transfer_number()
    if transfer:
        append_spoken(vr, "No problem — let me connect you with someone on our team.", base_url=base)
        vr.dial(transfer)
    else:
        append_spoken(
            vr,
            "Our team is available after noon Eastern. "
            "You can also schedule online at portal dot dee davis dot biz. "
            "Thanks for calling.",
            base_url=base,
        )
        vr.hangup()
    return str(vr)


def _complete_twiml(confirmation: str) -> str:
    base = _voice_base_url()
    vr = VoiceResponse()
    conf_spoken = confirmation.replace("-", ", ")
    append_spoken(
        vr,
        speak_for_phone(
            f"You're all set. Your confirmation number is {conf_spoken}. "
            "We'll text you your trip details shortly. "
            "Take care."
        ),
        base_url=base,
    )
    vr.hangup()
    return str(vr)


def _handle_slot_input(
    session: Dict[str, Any], speech: str, caller_phone: str
) -> Tuple[str, Optional[str]]:
    """Process speech for current slot. Returns (next_twiml, confirmation_id_if_done)."""
    slot = _current_slot(session)
    if not slot:
        return _transfer_twiml(), None

    if _wants_transfer(speech):
        return _transfer_twiml(), None

    if slot == "confirm":
        if not session.get("slots", {}).get("_summary_spoken"):
            session.setdefault("slots", {})["_summary_spoken"] = "1"
            _update_session(session["call_sid"], session)
            return _gather_twiml(session, _confirmation_summary(session.get("slots") or {}), session["call_sid"]), None

        value = _normalize_slot_value(slot, speech, session)
        if value is None:
            return _gather_twiml(session, RETRY_PROMPT + " Just say yes to confirm, or no to start over.", session["call_sid"]), None
        if value == "no":
            session["step_index"] = 0
            session["slots"] = {}
            _update_session(session["call_sid"], session)
            return _gather_twiml(session, "No problem, let's start fresh. " + _prompt_for_slot("member_name"), session["call_sid"]), None
        if value != "yes":
            return _gather_twiml(session, RETRY_PROMPT, session["call_sid"]), None

        try:
            result = _submit_nemt_order(session, caller_phone)
            conf = result["confirmation"]
            session["status"] = "completed"
            session["confirmation"] = conf
            _update_session(session["call_sid"], session)
            _append_call_log(
                {
                    "call_sid": session["call_sid"],
                    "caller": _mask_phone(caller_phone),
                    "flow": "nemt",
                    "status": "completed",
                    "confirmation": conf,
                    "slots": {k: v for k, v in (session.get("slots") or {}).items() if not k.startswith("_")},
                    "completed_at": datetime.now(EASTERN).isoformat(),
                }
            )
            return _complete_twiml(conf), conf
        except Exception as exc:
            logger.exception("Voice order submit failed")
            session["status"] = "error"
            _update_session(session["call_sid"], session)
            _append_call_log(
                {
                    "call_sid": session["call_sid"],
                    "caller": _mask_phone(caller_phone),
                    "flow": "nemt",
                    "status": "error",
                    "error": str(exc),
                    "completed_at": datetime.now(EASTERN).isoformat(),
                }
            )
            vr = VoiceResponse()
            base = _voice_base_url()
            append_spoken(
                vr,
                "I'm sorry — something went wrong saving your request. "
                "Let me get you to a team member who can help.",
                base_url=base,
            )
            dial = _transfer_number()
            if dial:
                vr.dial(dial)
            else:
                vr.hangup()
            return str(vr), None

    value = _normalize_slot_value(slot, speech, session)
    if not value:
        return _gather_twiml(
            session,
            RETRY_PROMPT + " " + _prompt_for_slot(slot, session.get("slots") or {}),
            session["call_sid"],
        ), None

    session.setdefault("slots", {})[slot] = value
    _advance_session(session)
    _update_session(session["call_sid"], session)

    next_slot = _current_slot(session)
    if not next_slot:
        return _transfer_twiml(), None
    if next_slot == "confirm":
        session.setdefault("slots", {})["_summary_spoken"] = "1"
        _update_session(session["call_sid"], session)
        return _gather_twiml(session, _confirmation_summary(session.get("slots") or {}), session["call_sid"]), None
    prompt = _prompt_for_slot(next_slot, session.get("slots") or {})
    return _gather_twiml(session, prompt, session["call_sid"]), None


# ─── Routes ───────────────────────────────────────────────────────────────────


@prism_voice.route("/prism/voice/status", methods=["GET"])
def voice_status():
    base = _voice_base_url()
    return jsonify(
        {
            "enabled": True,
            "twilio_configured": _twilio_configured(),
            "openai_configured": bool(os.environ.get("OPENAI_API_KEY")),
            "elevenlabs_configured": elevenlabs_enabled(),
            "tts_provider": tts_provider_label(),
            "tts_voice": voice_id(),
            "transfer_number_masked": _mask_phone(_transfer_number()),
            "webhook_base_url": base or None,
            "inbound_webhook": f"{base}/prism/voice/inbound" if base else None,
            "gather_webhook": f"{base}/prism/voice/gather" if base else None,
            "default_flow": "nemt_hap_caresource",
            "slots": NEMT_SLOTS,
        }
    )


@prism_voice.route("/prism/voice/audio/<filename>", methods=["GET"])
def voice_audio(filename: str):
    """Serve cached ElevenLabs mp3 for Twilio <Play>."""
    if not re.match(r"^[a-f0-9]{20}\.mp3$", filename):
        return jsonify({"error": "Not found"}), 404
    audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads", "prism", "voice_audio")
    path = os.path.join(audio_dir, filename)
    if not os.path.isfile(path):
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(audio_dir, filename, mimetype="audio/mpeg")


@prism_voice.route("/prism/voice/calls", methods=["GET"])
def voice_calls():
    limit = min(int(request.args.get("limit", 50)), 200)
    log = _load_json(_CALL_LOG_FILE, [])[:limit]
    active = _load_json(_SESSIONS_FILE, {})
    in_progress = [
        s
        for s in active.values()
        if s.get("status") not in ("completed", "error")
        and int(s.get("step_index", 0)) > 0
    ]
    return jsonify(
        {
            "calls": log,
            "active_sessions": len(in_progress),
            "count": len(log),
        }
    )


@prism_voice.route("/prism/voice/inbound", methods=["POST", "GET"])
def voice_inbound():
    """Twilio voice webhook — start NEMT intake flow."""
    call_sid = request.values.get("CallSid", f"local-{uuid.uuid4().hex[:8]}")
    caller = request.values.get("From", "")

    session = _get_session(call_sid)
    session["caller_phone"] = caller
    session["step_index"] = 0
    session["slots"] = {}
    session["status"] = "in_progress"
    _update_session(call_sid, session)

    _append_call_log(
        {
            "call_sid": call_sid,
            "caller": _mask_phone(caller),
            "flow": "nemt",
            "status": "started",
            "started_at": datetime.now(EASTERN).isoformat(),
        }
    )

    greeting = _GREETING + " " + _prompt_for_slot("member_name")
    twiml = _gather_twiml(session, greeting, call_sid)
    return Response(twiml, mimetype="text/xml")


@prism_voice.route("/prism/voice/gather", methods=["POST"])
def voice_gather():
    call_sid = request.values.get("CallSid", "")
    speech = (request.values.get("SpeechResult") or "").strip()
    caller = request.values.get("From", "")

    session = _get_session(call_sid)
    if not speech:
        slot = _current_slot(session) or "member_name"
        twiml = _gather_twiml(
            session,
            RETRY_PROMPT + " " + _prompt_for_slot(slot, session.get("slots") or {}),
            call_sid,
        )
        return Response(twiml, mimetype="text/xml")

    twiml, _conf = _handle_slot_input(session, speech, caller or session.get("caller_phone", ""))
    return Response(twiml, mimetype="text/xml")


@prism_voice.route("/prism/voice/call-status", methods=["POST"])
def voice_call_status():
    """Optional Twilio status callback."""
    call_sid = request.values.get("CallSid", "")
    status = request.values.get("CallStatus", "")
    if call_sid and status in ("completed", "busy", "failed", "no-answer", "canceled"):
        sessions = _load_json(_SESSIONS_FILE, {})
        if call_sid in sessions and sessions[call_sid].get("status") != "completed":
            sessions[call_sid]["status"] = status
            _save_json(_SESSIONS_FILE, sessions)
    return "", 204


@prism_voice.route("/prism/voice/simulate", methods=["POST"])
def voice_simulate():
    """
    Dev/test: POST JSON { "call_sid": "...", "speech": "...", "caller": "+1..." }
    Returns next prompt text (no Twilio required).
    """
    data = request.get_json(silent=True) or {}
    call_sid = data.get("call_sid") or f"sim-{uuid.uuid4().hex[:8]}"
    speech = data.get("speech", "")
    caller = data.get("caller", "+12483764550")

    session = _get_session(call_sid)
    session.setdefault("caller_phone", caller)
    if not speech and int(session.get("step_index", 0)) == 0:
        return jsonify({
            "prompt": _prompt_for_slot("member_name"),
            "step": "member_name",
            "call_sid": call_sid,
        })

    twiml, conf = _handle_slot_input(session, speech, caller)
    says = re.findall(r"<Say[^>]*>([^<]+)</Say>", twiml)
    prompt = says[0] if says else twiml[:200]
    return jsonify(
        {
            "call_sid": call_sid,
            "step_index": session.get("step_index"),
            "slots": {k: v for k, v in (session.get("slots") or {}).items() if not str(k).startswith("_")},
            "prompt": prompt,
            "confirmation": conf,
            "status": session.get("status"),
        }
    )
