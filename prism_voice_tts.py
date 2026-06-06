"""
PRISM Voice TTS — natural-sounding speech for phone intake.

Priority:
  1. ElevenLabs (if ELEVENLABS_API_KEY) — most human
  2. Twilio Generative/Neural (PRISM_VOICE_TTS env) — no extra API key
  3. Twilio Neural fallback

Env:
  PRISM_VOICE_TTS              e.g. Polly.Ruth-Generative or Google.en-US-Chirp3-HD-Leda
  PRISM_VOICE_TTS_FALLBACK     e.g. Polly.Joanna-Neural
  ELEVENLABS_API_KEY           Optional premium voice
  ELEVENLABS_VOICE_ID          Default Rachel (warm, professional)
  ELEVENLABS_MODEL             Default eleven_turbo_v2_5
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
from typing import Optional, Union

logger = logging.getLogger("prism.voice.tts")

# Warm, natural defaults — override in .env
DEFAULT_GENERATIVE = "Polly.Ruth-Generative"
DEFAULT_NEURAL_FALLBACK = "Polly.Joanna-Neural"
DEFAULT_ELEVEN_VOICE = "21m00Tcm4TlvDq8ikWAM"  # Rachel — clear, warm

_AUDIO_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "uploads", "prism", "voice_audio"
)


def voice_id() -> str:
    return (os.environ.get("PRISM_VOICE_TTS") or DEFAULT_GENERATIVE).strip()


def voice_fallback() -> str:
    return (os.environ.get("PRISM_VOICE_TTS_FALLBACK") or DEFAULT_NEURAL_FALLBACK).strip()


def elevenlabs_enabled() -> bool:
    return bool((os.environ.get("ELEVENLABS_API_KEY") or "").strip())


def tts_provider_label() -> str:
    if elevenlabs_enabled():
        return "elevenlabs"
    v = voice_id()
    if "Generative" in v or "Chirp3" in v:
        return "twilio_generative"
    if "Neural" in v or "WaveNet" in v:
        return "twilio_neural"
    return "twilio_standard"


def _ensure_audio_dir() -> None:
    os.makedirs(_AUDIO_DIR, exist_ok=True)


def _audio_cache_path(text: str) -> str:
    key = hashlib.sha256(
        f"{text}|{os.environ.get('ELEVENLABS_VOICE_ID', DEFAULT_ELEVEN_VOICE)}".encode()
    ).hexdigest()[:20]
    return os.path.join(_AUDIO_DIR, f"{key}.mp3")


def synthesize_elevenlabs_mp3(text: str) -> Optional[str]:
    """Return local file path to mp3, or None on failure."""
    api_key = (os.environ.get("ELEVENLABS_API_KEY") or "").strip()
    if not api_key or not text.strip():
        return None

    _ensure_audio_dir()
    out_path = _audio_cache_path(text)
    if os.path.isfile(out_path) and os.path.getsize(out_path) > 500:
        return out_path

    voice_id_el = (os.environ.get("ELEVENLABS_VOICE_ID") or DEFAULT_ELEVEN_VOICE).strip()
    model = (os.environ.get("ELEVENLABS_MODEL") or "eleven_turbo_v2_5").strip()

    try:
        import urllib.error
        import urllib.request

        payload = {
            "text": text,
            "model_id": model,
            "voice_settings": {
                "stability": 0.45,
                "similarity_boost": 0.78,
                "style": 0.35,
                "use_speaker_boost": True,
            },
        }
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id_el}",
            data=__import__("json").dumps(payload).encode("utf-8"),
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            audio = resp.read()
        if len(audio) < 500:
            return None
        tmp = out_path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(audio)
        os.replace(tmp, out_path)
        return out_path
    except Exception as exc:
        logger.warning("ElevenLabs TTS failed, using Twilio voice: %s", exc)
        return None


def public_audio_url(local_path: str, base_url: str) -> str:
    """Map cached mp3 to public Play URL for Twilio."""
    name = os.path.basename(local_path)
    return f"{base_url.rstrip('/')}/prism/voice/audio/{name}"


def append_spoken(
    node,
    text: str,
    *,
    base_url: str = "",
) -> None:
    """
    Append Play (ElevenLabs) or Say (Twilio generative/neural) to a TwiML node.
    `node` is VoiceResponse, Gather, etc.
    """
    clean = re.sub(r"\s+", " ", (text or "").strip())
    if not clean:
        return

    if base_url and elevenlabs_enabled():
        mp3 = synthesize_elevenlabs_mp3(clean)
        if mp3:
            node.play(public_audio_url(mp3, base_url))
            return

    node.say(clean, voice=voice_id(), language="en-US")


def speak_for_phone(text: str) -> str:
    """Light copy edits so TTS sounds natural on a phone line."""
    t = text
    t = re.sub(r"\bDDI\b", "D D I", t)
    # Avoid robotic spelled-out URLs
    t = t.replace("deedavis.biz", "dee davis dot biz")
    t = t.replace("portal.deedavis.biz", "portal dot dee davis dot biz")
    # Confirmation IDs — add slight pauses via comma
    t = re.sub(
        r"(\d+)-DDI-(?:MOB-[ABCE]|TPA-[1-9]|NAV-[A-Z0-9])-(\d{8})-(\d{4})-(\d)",
        r"\1, D D I, \2 \3 \4, \5",
        t,
    )
    t = re.sub(r"(DDI-(?:MOB-[ABCE]|TPA-[1-9]|NAV-[A-Z0-9])-[A-Z]-\d{8}-\d{4})-(\d)", r"\1, \2", t)
    t = re.sub(r"\bMOB-([ABCE])\b", r"mobility \1", t)
    t = re.sub(r"\bTPA-(\d)\b", r"T P A \1", t)
    t = re.sub(r"(PRISM-V-\d{8}-\d{4})-(\w+)", r"\1, \2", t)
    return t
