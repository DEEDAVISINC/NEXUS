#!/usr/bin/env python3
"""
NEXUS Calendar Service
======================
System-wide calendar for all NEXUS modules.

Every scheduled event across every system — PRISM appointments, NEMT rides,
SHIELD service activations, GPSS CO meetings, COMPASS check-ins, ATLAS
milestones, bid deadlines, custom meetings — feeds into this single calendar.

When role-based auth is built, the GET endpoints filter by owner_id / role.
All events are stored with those fields from day one so the filter just works.

API:
  POST   /nexus/calendar/events          Create event (any system)
  GET    /nexus/calendar/events          List events (filterable)
  GET    /nexus/calendar/events/<id>     Single event
  PATCH  /nexus/calendar/events/<id>     Update / reschedule
  DELETE /nexus/calendar/events/<id>     Remove

  GET    /nexus/calendar/feed.ics        iCalendar feed (subscribe in Apple/Google)
  GET    /nexus/calendar/agenda          SCHEDULED_AGENDA.md content as JSON

Data: uploads/calendar/events.json
ICS files: calendars/ (same folder as existing hand-made files)
"""

from __future__ import annotations

import json
import os
import re
import uuid
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from flask import Blueprint, request, jsonify, Response

nexus_calendar = Blueprint("nexus_calendar", __name__)

EASTERN   = ZoneInfo("America/Detroit")
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(BASE_DIR, "uploads", "calendar")
DATA_FILE = os.path.join(DATA_DIR, "events.json")
ICS_DIR   = os.path.join(BASE_DIR, "calendars")
AGENDA_FILE = os.path.join(ICS_DIR, "SCHEDULED_AGENDA.md")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ICS_DIR,  exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# System color tags (used in UI + ICS categories)
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_COLORS: Dict[str, str] = {
    "PRISM":    "#1e40af",   # blue
    "NEMT":     "#7c3aed",   # purple
    "SHIELD":   "#f5c23e",   # gold
    "GPSS":     "#059669",   # green
    "COMPASS":  "#0891b2",   # cyan
    "ATLAS":    "#ea580c",   # orange
    "VERTEX":   "#dc2626",   # red
    "GBIS":     "#16a34a",   # emerald
    "DDCSS":    "#6b7280",   # gray
    "LBPC":     "#0284c7",   # sky
    "JETA":     "#9333ea",   # violet
    "NEXUS":    "#374151",   # slate (manually created)
    "DEADLINE": "#ef4444",   # red (bid deadlines)
}

SYSTEM_EMOJIS: Dict[str, str] = {
    "PRISM":    "🔬",
    "NEMT":     "🚗",
    "SHIELD":   "🛡️",
    "GPSS":     "🏛️",
    "COMPASS":  "🧭",
    "ATLAS":    "📐",
    "VERTEX":   "💰",
    "GBIS":     "🎯",
    "DDCSS":    "🏢",
    "LBPC":     "📋",
    "JETA":     "✈️",
    "NEXUS":    "📅",
    "DEADLINE": "🔥",
}

# ─────────────────────────────────────────────────────────────────────────────
# Storage
# ─────────────────────────────────────────────────────────────────────────────

_lock = threading.Lock()


def _load() -> List[Dict[str, Any]]:
    with _lock:
        if not os.path.exists(DATA_FILE):
            return []
        try:
            with open(DATA_FILE) as f:
                return json.load(f)
        except Exception:
            return []


def _save(events: List[Dict[str, Any]]) -> None:
    with _lock:
        tmp = DATA_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(events, f, indent=2)
        os.replace(tmp, DATA_FILE)


# ─────────────────────────────────────────────────────────────────────────────
# ICS helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ics_dt(iso: str) -> str:
    """Convert ISO datetime string to ICS TZID format."""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        dt_et = dt.astimezone(EASTERN)
        return dt_et.strftime("%Y%m%dT%H%M%S")
    except Exception:
        return ""


def _build_ics_content(event: Dict[str, Any]) -> str:
    uid      = f"{event['id']}@nexus.deedavis.biz"
    summary  = event.get("title", "NEXUS Event")
    location = event.get("location", "")
    desc     = event.get("description", "").replace("\n", "\\n")
    start    = _ics_dt(event.get("start_iso", ""))
    end      = _ics_dt(event.get("end_iso", event.get("start_iso", "")))
    now_str  = datetime.now(EASTERN).strftime("%Y%m%dT%H%M%SZ")
    system   = event.get("system", "NEXUS")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Dee Davis Inc//NEXUS Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:NEXUS",
        "X-WR-TIMEZONE:America/Detroit",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{now_str}",
        f"DTSTART;TZID=America/Detroit:{start}",
        f"DTEND;TZID=America/Detroit:{end}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:{desc}",
        f"LOCATION:{location}",
        f"CATEGORIES:{system}",
        "STATUS:CONFIRMED",
        "SEQUENCE:0",
        # 2-hour reminder
        "BEGIN:VALARM",
        "TRIGGER:-PT2H",
        f"DESCRIPTION:{summary} in 2 hours",
        "ACTION:DISPLAY",
        "END:VALARM",
        # 30-min reminder
        "BEGIN:VALARM",
        "TRIGGER:-PT30M",
        f"DESCRIPTION:{summary} in 30 minutes",
        "ACTION:DISPLAY",
        "END:VALARM",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return "\r\n".join(lines)


def _write_ics(event: Dict[str, Any]) -> str:
    """Write ICS file to calendars/ and return the filename."""
    safe = re.sub(r"[^A-Z0-9_]", "_", event.get("title", "EVENT").upper())[:40]
    date_part = event.get("start_iso", "")[:10].replace("-", "")
    filename  = f"{safe}_{date_part}_{event['id'][:6]}.ics"
    path      = os.path.join(ICS_DIR, filename)
    with open(path, "w") as f:
        f.write(_build_ics_content(event))
    return filename


# ─────────────────────────────────────────────────────────────────────────────
# SCHEDULED_AGENDA.md mirror
# ─────────────────────────────────────────────────────────────────────────────

def _update_agenda(event: Dict[str, Any], ics_filename: str) -> None:
    """Insert or update entry in SCHEDULED_AGENDA.md under the correct date."""
    try:
        dt       = datetime.fromisoformat(event["start_iso"].replace("Z", "+00:00")).astimezone(EASTERN)
        date_key = dt.strftime("%Y-%m-%d")
        weekday  = dt.strftime("%A")
        time_str = dt.strftime("%-I:%M %p ET")
        system   = event.get("system", "NEXUS")
        emoji    = SYSTEM_EMOJIS.get(system, "📅")
        title    = event.get("title", "Event")
        location = event.get("location", "")
        loc_str  = f" — {location}" if location else ""
        line     = f"- **{time_str}** — {emoji} [{system}] **{title}**{loc_str} · `.ics`: `calendars/{ics_filename}`\n"
        header   = f"\n## {date_key} — {weekday}\n"

        content = ""
        if os.path.exists(AGENDA_FILE):
            with open(AGENDA_FILE) as f:
                content = f.read()

        section = f"## {date_key}"
        if section in content:
            # Insert line at end of existing section
            idx = content.index(section)
            end = content.find("\n## ", idx + 1)
            if end == -1:
                content = content[:].rstrip() + "\n" + line
            else:
                content = content[:end].rstrip() + "\n" + line + content[end:]
        else:
            content = content.rstrip() + "\n" + header + line

        with open(AGENDA_FILE, "w") as f:
            f.write(content)
    except Exception as exc:
        import logging
        logging.getLogger("nexus.calendar").warning("Agenda update error: %s", exc)


# ─────────────────────────────────────────────────────────────────────────────
# Core create function — called by API and all system hooks
# ─────────────────────────────────────────────────────────────────────────────

def create_calendar_event(
    title: str,
    start_iso: str,
    end_iso: Optional[str] = None,
    location: str = "",
    description: str = "",
    system: str = "NEXUS",
    event_type: str = "meeting",
    internal_id: str = "",
    owner_id: str = "dee",
    visibility: str = "private",
    assigned_to: str = "",
    party_name: str = "",
    party_email: str = "",
    party_phone: str = "",
    send_confirmation: bool = False,
    confirmation_what: str = "",
    confirmation_why: str = "",
    confirmation_bring: str = "",
) -> Dict[str, Any]:
    """
    Create a calendar event. Called by any NEXUS system.

    Args:
        title:        Event title shown in calendar
        start_iso:    Start datetime in ISO 8601 (e.g. "2026-05-05T14:00:00")
        end_iso:      End datetime — defaults to start + 1 hour
        location:     Address or "Zoom / Video Call"
        description:  Notes / detail
        system:       Source system ("PRISM", "NEMT", "SHIELD", "GPSS", etc.)
        event_type:   "meeting" | "appointment" | "signing" | "deadline" | "ride" | "call"
        internal_id:  ID from the source system (PRISM order ID, etc.)
        owner_id:     Who owns this event (default "dee" until RBAC is live)
        visibility:   "private" | "role" | "assigned" — ready for RBAC
        assigned_to:  Agent/navigator ID if assigned
        party_name:   Other party's name (if external meeting)
        party_email:  Other party's email
        party_phone:  Other party's phone
        send_confirmation: If True, fire nexus_confirmation_engine automatically
        confirmation_what: WHAT field for confirmation message
        confirmation_why:  WHY field for confirmation message
        confirmation_bring: BRING field for confirmation message

    Returns:
        Created event dict including id, ics_filename
    """
    if not end_iso:
        try:
            start_dt = datetime.fromisoformat(start_iso)
            end_iso  = (start_dt + timedelta(hours=1)).isoformat()
        except Exception:
            end_iso = start_iso

    event_id = str(uuid.uuid4())[:8].upper()
    now_iso  = datetime.now(EASTERN).isoformat()

    # Human-readable datetime for display
    try:
        dt = datetime.fromisoformat(start_iso).astimezone(EASTERN)
        display_dt = dt.strftime("%a %b %-d, %Y at %-I:%M %p ET")
    except Exception:
        display_dt = start_iso

    event: Dict[str, Any] = {
        "id":           event_id,
        "title":        title,
        "start_iso":    start_iso,
        "end_iso":      end_iso,
        "display_dt":   display_dt,
        "location":     location,
        "description":  description,
        "system":       system.upper(),
        "event_type":   event_type,
        "internal_id":  internal_id,
        "owner_id":     owner_id,
        "visibility":   visibility,
        "assigned_to":  assigned_to,
        "party_name":   party_name,
        "party_email":  party_email,
        "party_phone":  party_phone,
        "status":       "scheduled",
        "created_at":   now_iso,
        "updated_at":   now_iso,
        "ics_filename": "",
    }

    # Write ICS + update agenda
    try:
        ics_filename         = _write_ics(event)
        event["ics_filename"] = ics_filename
        _update_agenda(event, ics_filename)
    except Exception as exc:
        import logging
        logging.getLogger("nexus.calendar").warning("ICS write error: %s", exc)

    # Persist
    events = _load()
    events.insert(0, event)
    _save(events)

    # Fire confirmation if requested and other party details are present
    if send_confirmation and (party_email or party_phone):
        def _confirm():
            try:
                from nexus_confirmation_engine import send_confirmation_request
                send_confirmation_request(
                    event_type=event_type,
                    party_name=party_name,
                    party_email=party_email,
                    party_phone=party_phone,
                    datetime_str=display_dt,
                    location=location,
                    internal_id=event_id,
                    notes=description,
                    who="Dieasha D. Davis, President & CEO — Dee Davis Inc.",
                    what=confirmation_what or title,
                    why=confirmation_why,
                    bring=confirmation_bring,
                )
            except Exception as exc:
                import logging
                logging.getLogger("nexus.calendar").warning("Confirmation error: %s", exc)
        threading.Thread(target=_confirm, daemon=True).start()

    return event


# ─────────────────────────────────────────────────────────────────────────────
# API Routes
# ─────────────────────────────────────────────────────────────────────────────

@nexus_calendar.route("/nexus/calendar/events", methods=["POST"])
def api_create_event():
    """
    Create a calendar event from anywhere — including the NEXUS web UI.

    Body (JSON):
      title*          Event title
      start_iso*      ISO 8601 start (e.g. "2026-05-05T14:00:00")
      end_iso         ISO 8601 end (defaults to start + 1h)
      location        Address or video link
      description     Notes
      system          Source system (default "NEXUS")
      event_type      meeting | appointment | signing | deadline | ride | call
      internal_id     Source system ID
      owner_id        User ID (default "dee")
      visibility      private | role | assigned
      assigned_to     Agent/nav ID
      party_name      Other party name
      party_email     Other party email
      party_phone     Other party phone
      send_confirmation  bool — send email+SMS confirmation to other party
      confirmation_what  WHAT for confirmation message
      confirmation_why   WHY for confirmation message
      confirmation_bring BRING for confirmation message
    """
    data = request.get_json(silent=True) or {}

    if not data.get("title") or not data.get("start_iso"):
        return jsonify({"error": "title and start_iso are required"}), 400

    event = create_calendar_event(
        title=data["title"],
        start_iso=data["start_iso"],
        end_iso=data.get("end_iso"),
        location=data.get("location", ""),
        description=data.get("description", ""),
        system=data.get("system", "NEXUS"),
        event_type=data.get("event_type", "meeting"),
        internal_id=data.get("internal_id", ""),
        owner_id=data.get("owner_id", "dee"),
        visibility=data.get("visibility", "private"),
        assigned_to=data.get("assigned_to", ""),
        party_name=data.get("party_name", ""),
        party_email=data.get("party_email", ""),
        party_phone=data.get("party_phone", ""),
        send_confirmation=bool(data.get("send_confirmation", False)),
        confirmation_what=data.get("confirmation_what", ""),
        confirmation_why=data.get("confirmation_why", ""),
        confirmation_bring=data.get("confirmation_bring", ""),
    )
    return jsonify({"success": True, "event": event}), 201


@nexus_calendar.route("/nexus/calendar/events", methods=["GET"])
def api_list_events():
    """
    List calendar events.

    Query params:
      system        Filter by source system
      event_type    Filter by type
      owner_id      Filter by owner (ready for RBAC)
      from_date     ISO date — events on/after this date
      to_date       ISO date — events on/before this date
      limit         Max results (default 200)
    """
    events = _load()

    system     = request.args.get("system", "").upper()
    event_type = request.args.get("event_type", "")
    owner_id   = request.args.get("owner_id", "")
    from_date  = request.args.get("from_date", "")
    to_date    = request.args.get("to_date", "")
    limit      = int(request.args.get("limit", 200))

    if system:
        events = [e for e in events if e.get("system", "").upper() == system]
    if event_type:
        events = [e for e in events if e.get("event_type") == event_type]
    if owner_id:
        events = [e for e in events if e.get("owner_id") == owner_id]
    if from_date:
        events = [e for e in events if e.get("start_iso", "") >= from_date]
    if to_date:
        events = [e for e in events if e.get("start_iso", "") <= to_date + "T23:59:59"]

    # Sort ascending by start time
    events = sorted(events, key=lambda e: e.get("start_iso", ""))[:limit]

    return jsonify({"events": events, "total": len(events)})


@nexus_calendar.route("/nexus/calendar/events/<event_id>", methods=["GET"])
def api_get_event(event_id: str):
    events = _load()
    event  = next((e for e in events if e["id"] == event_id), None)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    return jsonify({"event": event})


@nexus_calendar.route("/nexus/calendar/events/<event_id>", methods=["PATCH"])
def api_update_event(event_id: str):
    """Update an event. If start_iso changes, rewrites ICS and updates agenda."""
    events = _load()
    idx    = next((i for i, e in enumerate(events) if e["id"] == event_id), None)
    if idx is None:
        return jsonify({"error": "Event not found"}), 404

    data   = request.get_json(silent=True) or {}
    allowed = [
        "title", "start_iso", "end_iso", "location", "description",
        "status", "assigned_to", "party_name", "party_email", "party_phone",
        "visibility",
    ]
    rescheduled = "start_iso" in data and data["start_iso"] != events[idx]["start_iso"]

    for key in allowed:
        if key in data:
            events[idx][key] = data[key]

    events[idx]["updated_at"] = datetime.now(EASTERN).isoformat()

    # Refresh ICS + agenda on reschedule
    if rescheduled:
        try:
            ics_filename              = _write_ics(events[idx])
            events[idx]["ics_filename"] = ics_filename
            _update_agenda(events[idx], ics_filename)
        except Exception:
            pass

    _save(events)
    return jsonify({"success": True, "event": events[idx]})


@nexus_calendar.route("/nexus/calendar/events/<event_id>", methods=["DELETE"])
def api_delete_event(event_id: str):
    events = _load()
    before = len(events)
    events = [e for e in events if e["id"] != event_id]
    if len(events) == before:
        return jsonify({"error": "Event not found"}), 404
    _save(events)
    return jsonify({"success": True})


@nexus_calendar.route("/nexus/calendar/feed.ics", methods=["GET"])
def api_ics_feed():
    """
    Live iCalendar feed — subscribe this URL in Apple Calendar, Google Calendar,
    or Outlook to get all NEXUS events automatically.
    URL: https://nexus.deedavis.biz/nexus/calendar/feed.ics
    """
    events = _load()
    from_date = request.args.get("from_date", "")
    if from_date:
        events = [e for e in events if e.get("start_iso", "") >= from_date]

    uid_lines: List[str] = []
    for event in events:
        start = _ics_dt(event.get("start_iso", ""))
        end   = _ics_dt(event.get("end_iso",   event.get("start_iso", "")))
        if not start:
            continue
        desc = (event.get("description", "") or "").replace("\n", "\\n")
        uid_lines += [
            "BEGIN:VEVENT",
            f"UID:{event['id']}@nexus.deedavis.biz",
            f"DTSTAMP:{datetime.now(EASTERN).strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART;TZID=America/Detroit:{start}",
            f"DTEND;TZID=America/Detroit:{end}",
            f"SUMMARY:{SYSTEM_EMOJIS.get(event.get('system','NEXUS'),'📅')} {event.get('title','')}",
            f"DESCRIPTION:{desc}",
            f"LOCATION:{event.get('location','')}",
            f"CATEGORIES:{event.get('system','NEXUS')}",
            "STATUS:CONFIRMED",
            "BEGIN:VALARM",
            "TRIGGER:-PT2H",
            f"DESCRIPTION:{event.get('title','')} in 2 hours",
            "ACTION:DISPLAY",
            "END:VALARM",
            "END:VEVENT",
        ]

    feed = "\r\n".join([
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Dee Davis Inc//NEXUS Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:NEXUS Command Center",
        "X-WR-TIMEZONE:America/Detroit",
        "REFRESH-INTERVAL;VALUE=DURATION:PT1H",
        *uid_lines,
        "END:VCALENDAR",
    ])
    return Response(feed, mimetype="text/calendar",
                    headers={"Content-Disposition": "attachment; filename=nexus.ics"})


@nexus_calendar.route("/nexus/calendar/agenda", methods=["GET"])
def api_agenda():
    """Return SCHEDULED_AGENDA.md content as plain text."""
    if not os.path.exists(AGENDA_FILE):
        return jsonify({"content": "No agenda entries yet."})
    with open(AGENDA_FILE) as f:
        content = f.read()
    return jsonify({"content": content})


@nexus_calendar.route("/nexus/calendar/systems", methods=["GET"])
def api_systems():
    """Return the list of source systems with colors/emojis for the UI."""
    return jsonify({
        "systems": [
            {"id": k, "color": SYSTEM_COLORS[k], "emoji": SYSTEM_EMOJIS[k]}
            for k in SYSTEM_COLORS
        ]
    })
