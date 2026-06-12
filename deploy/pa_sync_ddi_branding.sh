#!/bin/bash
# Paste into PythonAnywhere Bash console (after this commit is on GitHub main).
# Fetches DDI branding + PRISM SMS webhook files, clears desk transfer, reminds reload.
set -euo pipefail

cd ~/nexus-backend || { echo "❌ ~/nexus-backend not found"; exit 1; }

RAW="https://raw.githubusercontent.com/DEEDAVISINC/NEXUS/main"
FILES=(
  company_info.py
  prism_orders_api.py
  nexus_confirmation_engine.py
  prism_nemt.py
  shield_notifications.py
  prism_voice_tts.py
  prism_voice_intake.py
  prism_pa_app.py
  member_satisfaction_survey.py
  member_trip_grade_audit_report.py
)

echo "=== DDI branding sync → PythonAnywhere ==="
for f in "${FILES[@]}"; do
  echo "  ↓ $f"
  curl -fsSL "$RAW/$f" -o "$f.tmp" && mv "$f.tmp" "$f"
done

mkdir -p uploads/confirmations uploads/prism uploads/member_satisfaction uploads/member_satisfaction/audit assets

if curl -fsSL "$RAW/assets/ddi_logo_base64.txt" -o assets/ddi_logo_base64.txt.tmp 2>/dev/null; then
  mv assets/ddi_logo_base64.txt.tmp assets/ddi_logo_base64.txt
  echo "  ✓ assets/ddi_logo_base64.txt"
else
  echo "  ⚠ assets/ddi_logo_base64.txt not on remote — logo falls back to cap statement extract if present"
fi

if [ -f .env ]; then
  if grep -q '^PRISM_VOICE_TRANSFER_NUMBER=' .env; then
    sed -i 's/^PRISM_VOICE_TRANSFER_NUMBER=.*/PRISM_VOICE_TRANSFER_NUMBER=/' .env
  else
    echo 'PRISM_VOICE_TRANSFER_NUMBER=' >> .env
  fi
  echo "  ✓ Cleared PRISM_VOICE_TRANSFER_NUMBER (no desk ring)"
else
  echo "  ⚠ No .env — set PRISM_VOICE_TRANSFER_NUMBER= empty manually"
fi

echo ""
echo "✅ Files updated."
echo "→ Web tab → Reload deedavis.pythonanywhere.com"
echo "→ Test: curl -s https://deedavis.pythonanywhere.com/prism/voice/status | python3 -m json.tool"
echo "→ Test SMS webhook: curl -s -o /dev/null -w '%{http_code}' -X POST https://deedavis.pythonanywhere.com/shield/webhook/twilio-inbound -d 'From=%2B15551234567&Body=HELP'"
