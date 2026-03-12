#!/usr/bin/env python3
"""
NEXUS VOICE ASSISTANT — Local Mac-Based AI Assistant
=====================================================
A simple voice assistant that runs on your Mac, reads NEXUS data,
and speaks responses. No AWS/Alexa setup required.

Usage:
    python3 nexus_voice_assistant.py

Voice Commands:
    "Hey NEXUS" - wake word (or just press Enter)
    "briefing" / "daily briefing" - get your morning briefing
    "emails" / "how many emails" - check email backlog
    "deadlines" - upcoming bid deadlines
    "stale" / "stale bids" - check dormant opportunities
    "quit" / "exit" - stop the assistant
"""

import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Paths
WORKSPACE = "/Users/deedavis/NEXUS BACKEND"
BRIEFING_PATH = os.path.join(WORKSPACE, "DAILY_BRIEFING.md")
BIDS_ROOT = os.path.join(WORKSPACE, "BIDS:RESOURCES")


def speak(text: str):
    """Use macOS 'say' command to speak text"""
    # Clean up text for speech
    text = text.replace("—", ", ")
    text = text.replace("•", "")
    text = text.replace("#", "")
    text = text.replace("*", "")
    text = text.replace("_", "")
    subprocess.run(["say", "-v", "Samantha", text], capture_output=True)


def read_briefing():
    """Read and parse the daily briefing file"""
    if not os.path.exists(BRIEFING_PATH):
        return None
    
    with open(BRIEFING_PATH, 'r') as f:
        content = f.read()
    
    # Parse key metrics
    ready_match = re.search(r'\*\*(\d+) emails ready to send', content)
    waiting_match = re.search(r'## 📨 SENT.*?\n\n\*\*(\d+)', content, re.DOTALL)
    stale_match = re.search(r'\*\*(\d+) bids with no activity', content)
    deadline_match = re.search(r'## 📅 UPCOMING DEADLINES.*?\n\n\*\*(\d+)', content, re.DOTALL)
    
    # Extract top actions
    top5_section = re.search(r"## ✅ TODAY'S TOP 5 ACTIONS\n\n(.*?)(?=\n---|\Z)", content, re.DOTALL)
    top_actions = []
    if top5_section:
        action_lines = re.findall(r'\d+\. [📅📧🔥⏰📋⚠️]+ \*\*([^*]+)\*\* — (.+)', top5_section.group(1))
        top_actions = [(name.strip(), desc.strip()) for name, desc in action_lines[:5]]
    
    # Extract deadlines
    deadline_section = re.search(r'## 📅 UPCOMING DEADLINES.*?\n\n(.*?)(?=\n---|\n##)', content, re.DOTALL)
    deadlines = []
    if deadline_section:
        deadline_rows = re.findall(r'\| ([^|]+) \| ([^|]+) \| ([^|]+) \|', deadline_section.group(1))
        deadlines = [(name.strip(), date.strip(), action.strip()) 
                     for name, date, action in deadline_rows if 'Opportunity' not in name]
    
    return {
        'ready_to_send': int(ready_match.group(1)) if ready_match else 0,
        'waiting_response': int(waiting_match.group(1)) if waiting_match else 0,
        'stale_bids': int(stale_match.group(1)) if stale_match else 0,
        'upcoming_deadlines': int(deadline_match.group(1)) if deadline_match else 0,
        'top_actions': top_actions,
        'deadlines': deadlines,
        'raw_content': content
    }


def handle_briefing():
    """Give the daily briefing"""
    briefing = read_briefing()
    if not briefing:
        speak("I can't find the daily briefing file. Please run the briefing generator first.")
        return
    
    ready = briefing['ready_to_send']
    stale = briefing['stale_bids']
    deadlines = briefing['upcoming_deadlines']
    top_actions = briefing['top_actions']
    
    # Build response
    response = f"Good morning Dee. Here's your NEXUS briefing for {datetime.now().strftime('%A, %B %d')}. "
    
    if ready > 0:
        response += f"You have {ready} emails ready to send. "
    else:
        response += "No emails are waiting to be sent. "
    
    if deadlines > 0:
        response += f"There are {deadlines} upcoming deadlines. "
    
    if stale > 10:
        response += f"Warning: {stale} bids have gone stale with no activity. "
    
    if top_actions:
        response += "Your top priorities are: "
        for i, (name, action) in enumerate(top_actions[:3], 1):
            response += f"{i}. {name}, {action}. "
    
    response += "Say 'emails' for details on your outreach backlog, or 'deadlines' for due dates."
    
    speak(response)
    print(f"\n📋 Briefing Summary:")
    print(f"   📧 Ready to Send: {ready}")
    print(f"   📅 Deadlines: {deadlines}")
    print(f"   ⚠️  Stale Bids: {stale}")


def handle_emails():
    """Report on email backlog"""
    briefing = read_briefing()
    if not briefing:
        speak("I can't read the briefing file.")
        return
    
    ready = briefing['ready_to_send']
    waiting = briefing['waiting_response']
    
    if ready == 0:
        response = "You're all caught up. No emails waiting to be sent."
    elif ready <= 5:
        response = f"You have {ready} emails ready to send. Open your daily briefing to see which ones."
    else:
        response = f"You have {ready} emails ready to send. That's a backlog. I recommend sending at least 10 today."
    
    if waiting > 0:
        response += f" Also, {waiting} emails are sent and waiting for a response."
    
    speak(response)
    print(f"\n📧 Email Status:")
    print(f"   Ready to Send: {ready}")
    print(f"   Awaiting Response: {waiting}")


def handle_deadlines():
    """Report on upcoming deadlines"""
    briefing = read_briefing()
    if not briefing:
        speak("I can't read the briefing file.")
        return
    
    deadlines = briefing['deadlines']
    
    if not deadlines:
        speak("No bid deadlines are currently tracked.")
        return
    
    response = f"You have {len(deadlines)} upcoming deadlines. "
    for name, date, action in deadlines[:3]:
        response += f"{name}, due {date}. "
    
    if len(deadlines) > 3:
        response += f"Plus {len(deadlines) - 3} more. Check your daily briefing for the full list."
    
    speak(response)
    print(f"\n📅 Upcoming Deadlines:")
    for name, date, action in deadlines[:5]:
        print(f"   • {name}: {date}")


def handle_stale():
    """Report on stale bids"""
    briefing = read_briefing()
    if not briefing:
        speak("I can't read the briefing file.")
        return
    
    stale = briefing['stale_bids']
    
    if stale == 0:
        response = "Great news. No stale bids. All your opportunities have recent activity."
    elif stale <= 5:
        response = f"You have {stale} stale bids. These haven't had activity in 14 or more days."
    else:
        response = f"Warning: {stale} bids have gone stale. That's a lot of dormant opportunities. Review your daily briefing and either send follow-ups or archive dead opportunities."
    
    speak(response)
    print(f"\n⚠️  Stale Bids: {stale}")


def handle_help():
    """List available commands"""
    response = """
    Available commands:
    'briefing' or 'daily briefing' - Get your morning briefing
    'emails' or 'how many emails' - Check email backlog
    'deadlines' - View upcoming bid deadlines
    'stale' or 'stale bids' - Check dormant opportunities
    'quit' or 'exit' - Stop the assistant
    """
    print(response)
    speak("You can say: briefing, emails, deadlines, stale, or quit.")


def process_command(command: str):
    """Process a voice/text command"""
    command = command.lower().strip()
    
    if not command:
        return True
    
    if command in ['quit', 'exit', 'bye', 'goodbye', 'stop']:
        speak("Goodbye Dee. NEXUS is standing by.")
        return False
    
    if 'briefing' in command or command in ['start', 'morning', 'update', 'status']:
        handle_briefing()
    elif 'email' in command or 'send' in command or 'outreach' in command:
        handle_emails()
    elif 'deadline' in command or 'due' in command:
        handle_deadlines()
    elif 'stale' in command or 'dormant' in command or 'inactive' in command:
        handle_stale()
    elif command in ['help', '?', 'commands']:
        handle_help()
    else:
        speak(f"I heard {command}, but I'm not sure what to do. Say 'help' for available commands.")
    
    return True


def main():
    """Main loop - text input mode (voice input requires additional setup)"""
    print("\n" + "="*60)
    print("  🎤 NEXUS VOICE ASSISTANT")
    print("="*60)
    print("\nCommands: briefing | emails | deadlines | stale | help | quit")
    print("Press Enter after typing your command.\n")
    
    speak("NEXUS voice assistant ready. Say 'briefing' to get started.")
    
    running = True
    while running:
        try:
            command = input("🎤 NEXUS > ").strip()
            running = process_command(command)
        except KeyboardInterrupt:
            speak("Goodbye.")
            break
        except EOFError:
            break
    
    print("\nNEXUS Voice Assistant stopped.")


if __name__ == "__main__":
    main()
