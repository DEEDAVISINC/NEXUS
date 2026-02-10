# 📆 IMPORT BID DEADLINES TO YOUR CALENDAR

**You have 17 calendar files ready to import!**

Location: `/Users/deedavis/NEXUS BACKEND/calendars/`

---

## 🍎 For Apple Calendar (macOS)

### Option 1: Quick Import All (Recommended)
```bash
# Import all calendar files at once
open calendars/*.ics
```

Or just run this from Terminal:
```bash
cd "/Users/deedavis/NEXUS BACKEND"
open calendars/*.ics
```

### Option 2: Manual Import
1. Open **Calendar** app
2. Go to **File** → **Import**
3. Navigate to: `/Users/deedavis/NEXUS BACKEND/calendars/`
4. Select all `.ics` files and click **Import**
5. Choose which calendar to add them to (or create new "NEXUS Bids" calendar)

---

## 📱 For iPhone/iPad

**Method 1: AirDrop**
1. Open Finder on Mac
2. Go to `calendars/` folder
3. Select all `.ics` files
4. Right-click → **Share** → **AirDrop** to your iPhone
5. Accept on iPhone - events automatically import

**Method 2: iCloud Sync**
If you imported on Mac and use iCloud Calendar, events will sync automatically!

---

## 📧 For Google Calendar

1. Open [Google Calendar](https://calendar.google.com)
2. Click **Settings** (gear icon) → **Settings**
3. Click **Import & Export** in left sidebar
4. Click **Select file from your computer**
5. Choose `.ics` files from `calendars/` folder
6. Select which calendar to add to
7. Click **Import**

**Note:** Import each file individually (Google doesn't support batch import)

---

## 🔔 What You'll Get

Each calendar event includes:

### Event Details:
- 🔥 **Title:** "BID DUE: [Bid Name]"
- 📅 **Date:** Deadline date at 2:00 PM
- 📍 **Location:** Submit via portal/email
- 📝 **Description:** Value, type, folder location

### Automatic Reminders:
1. **3 days before** - "Bid due in 3 days"
2. **1 day before** - "Bid due TOMORROW"
3. **2 hours before** - "Bid due in 2 hours"

---

## ✅ Quick Import Command

**Just run this:**
```bash
cd "/Users/deedavis/NEXUS BACKEND" && open calendars/*.ics
```

**That's it!** All 17 bid deadlines will appear in your calendar with reminders.

---

## 🔄 Calendar Updates Automatically

Every morning at 7:00 AM, the system:
1. ✅ Generates fresh calendar files
2. ✅ Updates TODAY_AGENDA.md
3. ✅ Asks status questions
4. ✅ Sends notification

**To import new calendars:** Just run `open calendars/*.ics` again!

---

## 🎯 Your Complete Workflow

**Every Morning (Automatic):**
- 🔔 Get notification: "5 urgent bids, 3 this week"
- 📅 Open `TODAY_AGENDA.md` - see what to work on
- 📆 Calendar shows today's approaching deadlines
- 🤔 Answer questions in `BID_STATUS_QUESTIONS.md`

**No hunting. No forgetting. All automated.**

---

## 💡 Pro Tips

1. **Create separate calendar** called "NEXUS Bids" to keep work organized
2. **Set calendar to show notifications** (Calendar preferences)
3. **Enable iCloud sync** so reminders appear on all devices
4. **Check TODAY_AGENDA.md first thing** - it's your daily command center

---

**Ready to import?** Run this now:

```bash
cd "/Users/deedavis/NEXUS BACKEND" && open calendars/*.ics
```
