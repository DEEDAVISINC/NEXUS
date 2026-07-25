#!/usr/bin/env python3
"""
GATEWAY workforce letters — NEXUS-generated offer + welcome letters.

HTML is the controlled copy (downloadable from gateway.deedavis.biz).
Stored under uploads/hr_onboarding/letters/<record_id>/.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import company_info as ci

BASE_DIR = Path(__file__).resolve().parent
LETTERS_DIR = BASE_DIR / "uploads" / "hr_onboarding" / "letters"
GATEWAY_URL = "https://gateway.deedavis.biz"


def _esc(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def letter_dir(record_id: str) -> Path:
    d = LETTERS_DIR / record_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _shell(title: str, body_html: str, policy_id: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{_esc(title)}</title>
<style>
  body {{ font-family: Georgia, 'Times New Roman', serif; color: #1a1a1a; max-width: 720px; margin: 0 auto; padding: 2rem 1.25rem; line-height: 1.55; }}
  .co {{ font-family: Helvetica, Arial, sans-serif; font-size: 11px; letter-spacing: .06em; text-transform: uppercase; color: #5b21b6; font-weight: 700; }}
  h1 {{ font-size: 1.4rem; margin: .4rem 0 1rem; }}
  .meta {{ font-family: Helvetica, Arial, sans-serif; font-size: 12px; color: #4b5563; margin-bottom: 1.5rem; }}
  p {{ margin: 0 0 .75rem; }}
  ul {{ margin: 0 0 1rem; padding-left: 1.25rem; }}
  .sig {{ margin-top: 2rem; }}
  .footer {{ margin-top: 2.5rem; padding-top: 1rem; border-top: 1px solid #d1d5db; font-family: Helvetica, Arial, sans-serif; font-size: 11px; color: #6b7280; }}
  .cta {{ background: #f5f3ff; border: 1px solid #ddd6fe; padding: 12px 14px; border-radius: 6px; margin: 1.25rem 0; font-family: Helvetica, Arial, sans-serif; font-size: 13px; }}
  @media print {{ body {{ padding: .6in; }} }}
</style>
</head>
<body>
  <div class="co">Dee Davis Inc. · GATEWAY</div>
  <h1>{_esc(title)}</h1>
  {body_html}
  <div class="footer">
    {ci.COMPANY_NAME} | {ci.ADDRESS_FULL}<br/>
    Web/member: {ci.PHONE_WEBSITE_DISPLAY} | {ci.EMAIL} | Controlled copy: {_esc(policy_id)}
  </div>
</body>
</html>
"""


def build_offer_letter_html(rec: dict) -> str:
    name = rec.get("name") or "Team Member"
    role = rec.get("role") or "your assigned role"
    division = rec.get("division") or "your assigned division"
    start = rec.get("startdate") or "the confirmed start date"
    worker = "employee" if rec.get("workerType") == "employee" else "independent contractor"
    today = datetime.utcnow().strftime("%B %d, %Y")
    body = f"""
  <div class="meta">Date: {_esc(today)} · Personnel #: {_esc(rec.get('personnelNumber') or '—')}</div>
  <p>Dear {_esc(name)},</p>
  <p>We are pleased to confirm your engagement with {ci.COMPANY_NAME} as a {_esc(worker)}
  in the role of <strong>{_esc(role)}</strong>, assigned to <strong>{_esc(division)}</strong>,
  with a start date of <strong>{_esc(start)}</strong>.</p>
  <p>{ci.COMPANY_NAME} is a nationwide contract management Third-Party Administrator (TPA)
  headquartered in Troy, Michigan. Your onboarding and compliance acknowledgments are completed
  in the GATEWAY portal.</p>
  <div class="cta">
    <strong>Next step:</strong> Sign in at <a href="{GATEWAY_URL}">{GATEWAY_URL}</a> using {_esc(rec.get('email') or 'your email on file')}.
    Download this offer letter if needed, complete required uploads and policy acknowledgments,
    and follow your action items (status updates automatically).
  </div>
  <p>This letter confirms intent to engage you under DDI policies and applicable law.
  It is not a guarantee of continued employment or engagement duration beyond what your
  written agreement or applicable law provides. Independent contractors remain independent
  contractors; this letter does not create W-2 employment.</p>
  <p>Questions: email {ci.EMAIL} or call the NEXUS desk at {ci.PHONE_BUSINESS_GV}.</p>
  <div class="sig">
    <p>Sincerely,</p>
    <p><strong>{ci.OWNER_FULL_NAME}</strong><br/>{ci.OWNER_TITLE}<br/>{ci.COMPANY_NAME}</p>
  </div>
"""
    return _shell("Offer / Engagement Letter", body, "DDI-LTR-OFFER")


def build_welcome_letter_html(rec: dict) -> str:
    name = rec.get("name") or "Team Member"
    first = name.split()[0] if name else "there"
    today = datetime.utcnow().strftime("%B %d, %Y")
    body = f"""
  <div class="meta">Date: {_esc(today)}</div>
  <p>Welcome, {_esc(first)}.</p>
  <p>You are joining {ci.COMPANY_NAME} — a nationwide contract management TPA.
  GATEWAY is your onboarding home: documents, policy acknowledgments, and training status
  update automatically as we receive what we need from you.</p>
  <div class="cta">
    <strong>Sign in:</strong> <a href="{GATEWAY_URL}">{GATEWAY_URL}</a><br/>
    Use {_esc(rec.get('email') or 'your email on file')}. No password — magic link / code.
  </div>
  <p><strong>What you will do in GATEWAY</strong></p>
  <ul>
    <li>Upload required documents (status turns green when accepted)</li>
    <li>Open and e-sign required policies</li>
    <li>Complete assigned compliance training by the deadlines shown. If a platform lets you add a secondary email for certificates or completion notices, use <strong>hr@deedavis.biz</strong> (you must still log completion in GATEWAY).</li>
  </ul>
  <p><strong>What HR handles (not shown as your checklist)</strong></p>
  <ul>
    <li>Background / E-Verify / exclusion screening (as applicable)</li>
    <li>System provisioning, manager intros, and check-in meetings</li>
  </ul>
  <p>Legend in the portal: <strong style="color:#059669">Green</strong> = passed/accepted ·
  <strong style="color:#D97706">Yellow</strong> = more information needed from you ·
  <strong style="color:#DC2626">Red</strong> = needs attention / overdue.</p>
  <div class="sig">
    <p>Glad you are here,</p>
    <p><strong>{ci.OWNER_FULL_NAME}</strong><br/>{ci.OWNER_TITLE}<br/>{ci.COMPANY_NAME}</p>
  </div>
"""
    return _shell("Welcome to Dee Davis Inc.", body, "DDI-LTR-WELCOME")


def generate_letters_for_record(rec: dict) -> dict:
    """Write offer + welcome HTML for a record. Returns paths metadata."""
    rid = rec.get("id") or "unknown"
    d = letter_dir(rid)
    offer_path = d / "offer_letter.html"
    welcome_path = d / "welcome_letter.html"
    offer_path.write_text(build_offer_letter_html(rec), encoding="utf-8")
    welcome_path.write_text(build_welcome_letter_html(rec), encoding="utf-8")
    now = datetime.utcnow().isoformat() + "Z"
    meta = {
        "offerLetterPath": str(offer_path.relative_to(BASE_DIR)),
        "welcomeLetterPath": str(welcome_path.relative_to(BASE_DIR)),
        "offerLetterGeneratedAt": now,
        "welcomeLetterGeneratedAt": now,
    }
    letters = rec.get("letters") or {}
    letters.update(meta)
    rec["letters"] = letters
    return meta


def read_letter_html(rec: dict, which: str) -> str | None:
    letters = rec.get("letters") or {}
    key = "offerLetterPath" if which == "offer" else "welcomeLetterPath"
    rel = letters.get(key)
    if not rel:
        return None
    path = BASE_DIR / rel
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")
