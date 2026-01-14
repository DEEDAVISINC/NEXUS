# 🔒 SECURITY - API KEY ROTATION REQUIRED

## ⚠️ IMPORTANT: Your API keys were exposed in chat!

You MUST rotate (delete and recreate) these keys immediately:

---

## 1. ROTATE ANTHROPIC API KEY

### Steps:
1. Go to: https://console.anthropic.com
2. Click "API Keys" (left sidebar)
3. Find your current key (the one we used)
4. Click "Delete" on that key
5. Click "Create Key"
   - Name: `NEXUS Production`
6. **COPY THE NEW KEY** (starts with `sk-ant-api03-...`)
7. **SAVE IT SECURELY** (password manager, secure note)

✅ Old key is now invalid
✅ New key is secure

---

## 2. ROTATE AIRTABLE API KEY

### Steps:
1. Go to: https://airtable.com
2. Click your account icon (top right)
3. Click "Developer hub"
4. Click "Personal access tokens"
5. Find your current token
6. Click "Delete" or "Revoke"
7. Click "Create token"
   - Name: `NEXUS Backend`
   - Scopes: Check these 3:
     ✅ data.records:read
     ✅ data.records:write
     ✅ schema.bases:read
   - Access: Select "GPSS - Government Contracting" base
8. Click "Create token"
9. **COPY THE NEW TOKEN** (starts with `pat...`)
10. **SAVE IT SECURELY**

✅ Old token is now invalid
✅ New token is secure

---

## 3. SAVE YOUR NEW KEYS SECURELY

### Where to save them:

**OPTION A: Password Manager** (Best)
- 1Password, LastPass, Bitwarden, etc.
- Create secure note: "NEXUS API Keys"
- Store both keys there

**OPTION B: Encrypted Note**
- Apple Notes (with password)
- Microsoft OneNote (with password)
- Secure document on your computer

**NEVER:**
❌ Don't email them to yourself
❌ Don't save in plain text file
❌ Don't put in GitHub
❌ Don't share in chat/Slack

---

## 4. USE KEYS ONLY IN RENDER.COM

When you deploy to Render.com, you'll add them as **Environment Variables**

This keeps them:
- ✅ Encrypted
- ✅ Hidden from code
- ✅ Secure
- ✅ Never in GitHub

---

## WHAT TO DO NOW:

1. ✅ Rotate Anthropic key (delete old, create new)
2. ✅ Rotate Airtable token (delete old, create new)
3. ✅ Save new keys securely
4. ✅ Tell me when done
5. ✅ Then we'll continue deployment to Render.com

---

## After rotating keys:

The old keys will STOP WORKING immediately.
Anyone who saw them CAN'T use them anymore.
Your new keys are safe and secure! 🔒
