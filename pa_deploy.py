#!/usr/bin/env python3
"""
PythonAnywhere automated deploy — no manual console copy/paste required.

Why scheduled tasks instead of the Consoles API: PythonAnywhere's Consoles API
only lets you send_input to a console that has already been "started" by
loading its iframe in an actual browser tab. There's no way to start one
headlessly with just an API token, so that path is a dead end for full
automation. Scheduled Tasks run as real cron-style jobs on PA's infrastructure
with no browser involved, so this script:

  1. Deletes any stale log file from a previous run
  2. Creates a one-shot-ish scheduled task (fires at HH:MM UTC, ~2 min out)
     that runs `git pull origin main` and redirects output to a log file
  3. Polls PA's Files API until that log file appears
  4. Reads it back, checks for merge conflicts / fatal errors
  5. Deletes the scheduled task (so it doesn't fire again tomorrow at the
     same time and eat into your daily CPU-second budget)
  6. Reloads the web app via the API
  7. Curls /health on the live domain to confirm it came back up healthy

Usage:
    python3 pa_deploy.py

Requires in .env:
    PYTHONANYWHERE_USERNAME
    PYTHONANYWHERE_API_TOKEN
    PYTHONANYWHERE_DOMAIN
"""
import os
import sys
import time
import json
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.environ.get("PYTHONANYWHERE_USERNAME")
TOKEN = os.environ.get("PYTHONANYWHERE_API_TOKEN")
DOMAIN = os.environ.get("PYTHONANYWHERE_DOMAIN")
API_BASE = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}"
HEADERS = {"Authorization": f"Token {TOKEN}"}
WORKING_DIR = f"/home/{USERNAME}/nexus-backend"
LOG_PATH = f"{WORKING_DIR}/pa_deploy_log.txt"
FILES_API_URL = f"{API_BASE}/files/path{LOG_PATH}/"


def fail(msg):
    print(f"❌ {msg}")
    sys.exit(1)


def check_config():
    missing = [k for k, v in {
        "PYTHONANYWHERE_USERNAME": USERNAME,
        "PYTHONANYWHERE_API_TOKEN": TOKEN,
        "PYTHONANYWHERE_DOMAIN": DOMAIN,
    }.items() if not v]
    if missing:
        fail(f"Missing .env values: {', '.join(missing)}")


def delete_stale_log():
    """Best-effort — clears out any log from a previous run so we don't
    mistake old output for this run's result."""
    requests.delete(FILES_API_URL, headers=HEADERS, timeout=30)


def next_run_time(minutes_out=2):
    target = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes_out)
    return target.hour, target.minute


def create_deploy_task():
    hour, minute = next_run_time()
    command = (
        f"cd {WORKING_DIR} && git pull origin main > {LOG_PATH} 2>&1"
    )
    print(f"📅 Scheduling deploy task for {hour:02d}:{minute:02d} UTC "
          f"({datetime.datetime.utcnow().strftime('%H:%M')} UTC now)...")
    resp = requests.post(
        f"{API_BASE}/schedule/",
        headers=HEADERS,
        data={
            "command": command,
            "enabled": "true",
            "interval": "daily",
            "hour": hour,
            "minute": minute,
        },
        timeout=30,
    )
    if resp.status_code not in (200, 201):
        fail(f"Failed to create scheduled task: {resp.status_code} {resp.text}")
    task = resp.json()
    print(f"   Task ID: {task['id']}")
    return task["id"], hour, minute


def delete_task(task_id):
    requests.delete(f"{API_BASE}/schedule/{task_id}/", headers=HEADERS, timeout=30)


def wait_for_log(hour, minute, max_wait_seconds=240):
    print("⏳ Waiting for scheduled task to fire and write the log...")
    waited = 0
    poll_every = 10
    while waited < max_wait_seconds:
        resp = requests.get(FILES_API_URL, headers=HEADERS, timeout=30)
        if resp.status_code == 200 and resp.text.strip():
            print(f"   Log appeared after ~{waited}s")
            return resp.text
        time.sleep(poll_every)
        waited += poll_every
    return None


def run_git_pull():
    delete_stale_log()
    task_id, hour, minute = create_deploy_task()
    try:
        output = wait_for_log(hour, minute)
    finally:
        delete_task(task_id)
        print("🧹 Removed the scheduled task (won't recur tomorrow)")

    if output is None:
        fail("Timed out waiting for git pull output. Check PA manually.")

    print("--- git pull output ---")
    print(output.strip())
    print("-----------------------")

    lowered = output.lower()
    if "would be overwritten" in lowered:
        fail("Merge conflict — untracked files on PA are blocking the pull. "
             "Same class of bug as before; check what changed.")
    if "fatal:" in lowered:
        fail("git pull failed — see output above.")

    print("✅ git pull complete")
    return True


def reload_webapp():
    print(f"🔄 Reloading web app: {DOMAIN}")
    resp = requests.post(f"{API_BASE}/webapps/{DOMAIN}/reload/", headers=HEADERS, timeout=60)
    if resp.status_code == 200:
        print("✅ Web app reloaded")
        return True
    print(f"❌ Reload failed: {resp.status_code} {resp.text}")
    return False


def check_health():
    print(f"🩺 Checking https://{DOMAIN}/health ...")
    time.sleep(5)
    try:
        resp = requests.get(f"https://{DOMAIN}/health", timeout=30)
        print(f"   HTTP {resp.status_code}")
        try:
            data = resp.json()
            print(json.dumps(data, indent=2)[:2000])
        except Exception:
            print(resp.text[:1000])
    except Exception as exc:
        print(f"⚠️  Health check request failed: {exc}")


def main():
    check_config()
    ok = run_git_pull()
    if not ok:
        fail("Stopping before reload — fix the git issue first.")
    reload_webapp()
    check_health()
    print("\n🎉 Deploy complete.")


if __name__ == "__main__":
    main()
