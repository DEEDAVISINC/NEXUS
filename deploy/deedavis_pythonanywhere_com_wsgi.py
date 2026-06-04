# ═══════════════════════════════════════════════════════════════════
# PythonAnywhere WSGI — deedavis.pythonanywhere.com
# ═══════════════════════════════════════════════════════════════════
#
# WHERE TO PASTE THIS:
#   Web tab → deedavis.pythonanywhere.com → WSGI configuration file
#   Path: /var/www/deedavis_pythonanywhere_com_wsgi.py
#
# Replace the ENTIRE file contents with this script (adjust paths if your
# clone lives somewhere other than ~/nexus-backend).
#
# After save: Web tab → green Reload button → wait 10s
#
# Smoke test:
#   curl https://deedavis.pythonanywhere.com/health
#   curl https://deedavis.pythonanywhere.com/prism/orders
# ═══════════════════════════════════════════════════════════════════

import os
import sys

# ── Project path (repo on PythonAnywhere) ──────────────────────────
PROJECT_HOME = "/home/deedavis/nexus-backend"

if PROJECT_HOME not in sys.path:
    sys.path.insert(0, PROJECT_HOME)

# ── Virtualenv (use the venv that has requirements.txt installed) ──
# Option A — venv inside repo (deploy_to_pythonanywhere.sh):
VENV_SITE = os.path.join(PROJECT_HOME, "venv", "lib", "python3.10", "site-packages")
# Option B — mkvirtualenv named "nexus" (PYTHONANYWHERE_DEPLOYMENT_GUIDE.md):
# VENV_SITE = "/home/deedavis/.virtualenvs/nexus/lib/python3.10/site-packages"

if os.path.isdir(VENV_SITE) and VENV_SITE not in sys.path:
    sys.path.insert(0, VENV_SITE)

# ── Environment variables (.env in project root) ───────────────────
from dotenv import load_dotenv

load_dotenv(os.path.join(PROJECT_HOME, ".env"))

# ── Flask application object (required name: application) ──────────
from api_server import app as application  # noqa: E402
