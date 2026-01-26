#!/usr/bin/env python3
"""
Quick test to verify email automation can connect
"""

import os
import imaplib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EMAIL_ADDRESS = os.environ.get('NEXUS_EMAIL')
EMAIL_PASSWORD = os.environ.get('NEXUS_EMAIL_PASSWORD')
IMAP_SERVER = os.environ.get('IMAP_SERVER', 'imap.gmail.com')

print("=" * 60)
print("NEXUS Email Connection Test")
print("=" * 60)
print()

# Check environment variables
print("Checking configuration...")
print(f"Email: {EMAIL_ADDRESS}")
print(f"Password: {'*' * len(EMAIL_PASSWORD) if EMAIL_PASSWORD else 'NOT SET'}")
print(f"IMAP Server: {IMAP_SERVER}")
print()

if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    print("❌ ERROR: Email credentials not found in .env file")
    exit(1)

# Try to connect
print("Attempting to connect to Gmail...")
try:
    imap = imaplib.IMAP4_SSL(IMAP_SERVER)
    print("✓ SSL connection established")
    
    imap.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    print("✓ Login successful!")
    
    # Check inbox
    status, messages = imap.select('INBOX')
    if status == 'OK':
        print("✓ Inbox accessible")
        
        # Count messages
        status, data = imap.search(None, 'ALL')
        if status == 'OK':
            num_messages = len(data[0].split())
            print(f"✓ Found {num_messages} total messages in inbox")
        
        # Count unread
        status, data = imap.search(None, 'UNSEEN')
        if status == 'OK':
            num_unread = len(data[0].split()) if data[0] else 0
            print(f"✓ Found {num_unread} unread messages")
    
    imap.logout()
    print()
    print("=" * 60)
    print("SUCCESS! Email automation is ready to use!")
    print("=" * 60)
    
except imaplib.IMAP4.error as e:
    print(f"❌ IMAP Error: {e}")
    print()
    print("Common issues:")
    print("- Check that 2-Step Verification is enabled")
    print("- Verify you're using an App Password (not your regular password)")
    print("- Make sure the App Password has no spaces")
    exit(1)
    
except Exception as e:
    print(f"❌ Connection Error: {e}")
    exit(1)
