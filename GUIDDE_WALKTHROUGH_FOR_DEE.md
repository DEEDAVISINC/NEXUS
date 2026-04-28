# How to Use Guidde — Walkthrough for Dee

**Purpose:** Step-by-step instructions for using Guidde to record the SHIELD Navigator Training Video. Follow this before you start recording.

---

## Part 1: Setup (One-Time, ~5 minutes)

### 1. Sign Up
- Go to [guidde.com](https://www.guidde.com)
- Click **Get Started Free**
- Sign up with your Google account or email
- Free tier gives you 25 videos — more than enough

### 2. Install the Chrome Extension
- After signup, Guidde will prompt you to install the Chrome extension
- Or go directly to the Chrome Web Store and search "Guidde"
- Click **Add to Chrome**
- Pin it to your toolbar (click the puzzle piece icon in Chrome → pin Guidde)
- You'll see the Guidde icon in your browser toolbar

### 3. Start SHIELD Locally
Open two terminal windows:

**Terminal 1 — Backend:**
```
cd "/Users/deedavis/NEXUS BACKEND"
python3 api_server.py
```

**Terminal 2 — Frontend:**
```
cd "/Users/deedavis/NEXUS BACKEND/nexus-frontend"
npm start
```

Wait for both to load. Open Chrome and go to `http://localhost:3000/navigator`

---

## Part 2: How Guidde Works

Guidde is simple. Here's the whole concept:

1. You click the Guidde icon in your browser toolbar
2. You click **Start Recording**
3. You click through the app — whatever you do on screen, Guidde captures it
4. When you're done, click **Stop Recording**
5. Guidde automatically generates:
   - A step-by-step video with transitions
   - AI voiceover narration describing each step
   - Text annotations on each screen
   - A shareable link or downloadable video

**You don't talk. You don't narrate. You don't edit. You just click through the app.**

---

## Part 3: Recording the Training Video

Use the training video script (`SHIELD_NAVIGATOR_TRAINING_VIDEO_SCRIPT.md`) as your click-through checklist. Each chapter below is one Guidde recording. Doing them as separate recordings makes it easier to redo one if you mess up, and navigators can watch individual topics later.

### Before Each Recording
- Make sure the frontend and backend are running
- Clear any browser popups or notifications
- Make the browser window full-screen (Cmd+Shift+F in Chrome)
- Hide the bookmarks bar (Cmd+Shift+B)

### Recording Sequence

**Video 1: Login & Compliance (Chapters 1-2)**
1. Click the Guidde icon → Start Recording
2. Go to `localhost:3000/navigator`
3. Type "Angela Johnson" in the name field
4. Type "angela.johnson@cwcare.org" in the email field
5. Click Sign In
6. The HIPAA gate popup appears — pause for a second so Guidde captures it
7. Click "I Acknowledge — Proceed to SHIELD"
8. The workspace loads
9. Stop recording

**Video 2: Workspace Overview (Chapter 3)**
1. Start Recording
2. You're on the workspace — click each sidebar section slowly:
   - My Caseload (pause 2 seconds)
   - Calendar (pause 2 seconds)
   - Tasks (pause 2 seconds)
   - Phone (pause 2 seconds)
   - Messages (pause 2 seconds)
   - Time Log (pause 2 seconds)
3. Click the status dropdown at the top of the sidebar
4. Hover over each option (Online, In the Field, On Break, Off Duty)
5. Select "Online"
6. Stop recording

**Video 3: Caseload & Case Cards (Chapter 4)**
1. Start Recording
2. Click My Caseload in the sidebar
3. Slowly scroll through the case cards — let Guidde capture the urgency colors and SLA bars
4. Hover over an Emergency case (red) — pause
5. Hover over an Urgent case (amber) — pause
6. Hover over a Standard case (blue) — pause
7. Click the Refresh button
8. Stop recording

**Video 4: Working a Case (Chapter 5)**
This is the longest one. Take your time.
1. Start Recording
2. Click on the Johnson Family case card (Emergency, Wayne County)
3. Pause on the family header — let Guidde see the case number, county, urgency
4. Scroll down slowly to the children section — pause on the BLL levels
5. Scroll to Active Services — pause on each service card
6. Click the verification progress bar area — let it show the steps
7. Click "+ Add Service" — the service list appears
8. Click one service (e.g., "MIBridges Benefits Navigation") — it shows "Pending Approval"
9. Click "Log Note" — type a sample note like "Spoke with mom, confirmed Thursday appointment"
10. Save the note
11. Scroll to the milestones/timeline section — pause
12. Click the Back button to return to caseload
13. Stop recording

**Video 5: Calendar (Chapter 6)**
1. Start Recording
2. Click Calendar in the sidebar
3. Scroll through the appointments
4. Hover over the Directions button on one appointment — pause
5. Hover over the Add to Calendar button — pause
6. Stop recording

**Video 6: Tasks (Chapter 7)**
1. Start Recording
2. Click Tasks in the sidebar
3. Let the task list load — show overdue (red), today (amber), upcoming (blue)
4. Click one task card — it jumps to that case
5. Click Back, then click Tasks again
6. Stop recording

**Video 7: Phone — Logging Calls (Chapter 8)**
1. Start Recording
2. Click Phone in the sidebar
3. Select a family from the dropdown
4. Enter a phone number
5. Select "Outbound"
6. Enter duration: 5 minutes
7. Type in notes: "Spoke with Mrs. Johnson. Confirmed BLL test Thursday 10am. Needs NEMT ride."
8. Click Save Call
9. Scroll down to show the call history
10. Stop recording

**Video 8: Messages — SMS (Chapter 9)**
1. Start Recording
2. Click Messages in the sidebar
3. Select a family from the dropdown
4. Click one of the message templates — it loads into the text box
5. Click Send
6. Stop recording

**Video 9: Time Tracking (Chapter 10)**
1. Start Recording
2. Click Time Log in the sidebar
3. Point out the auto-recorded entries (scroll through them — the status badges)
4. Select an activity type from the Field Work Timer dropdown (e.g., "CHW Home Visit")
5. Click Start Timer — let it run for 5-10 seconds
6. Click Stop Timer
7. Type a note: "Home visit — Johnson family, environmental assessment"
8. Show the summary section (total hours, Medicaid hours)
9. Stop recording

**Video 10: Service Verification (Chapter 11)**
1. Start Recording
2. Click My Caseload → open a case with active services (Johnson Family)
3. Scroll to Active Services
4. Find a service with the verification progress bar
5. Click the "Complete" button on a navigator-owned step
6. Click "Send SMS" on a contractor/family step
7. Show the progress bar updating
8. Stop recording

---

## Part 4: After Recording

### Review & Edit
1. Go to [app.guidde.com](https://app.guidde.com) — your dashboard shows all recordings
2. Click on any video to preview it
3. Guidde auto-generates:
   - Step titles (you can rename them)
   - AI voiceover (you can change the voice style)
   - Annotations highlighting where you clicked
4. If a step description is wrong, click on it and edit the text
5. If you want to redo a video, just re-record that one chapter

### Customize (Optional)
- **Voice:** Change the AI voice in Settings if you don't like the default
- **Brand Kit (Pro only):** Add the CWC logo as a watermark
- **Blur sensitive data:** Guidde can auto-blur PII — turn this on since demo data still looks like real data

### Share
- Each video gets a shareable link — copy it and send to navigators
- Or download as MP4 if you want to host it yourself
- You can organize videos into a "collection" called "SHIELD Navigator Training"

---

## Part 5: Quick Reference — Recording Tips

| Tip | Why |
|-----|-----|
| Move the mouse slowly | Guidde tracks your cursor — fast movement looks chaotic |
| Pause 2-3 seconds on each important screen | Gives Guidde time to capture and annotate |
| Click deliberately, one thing at a time | Each click = one step in the video |
| Don't type too fast | Guidde captures keystrokes for text entry steps |
| Full-screen the browser | No desktop clutter in the recording |
| Close other tabs | Only SHIELD should be visible |
| If you make a mistake, stop and re-record that chapter | Each chapter is a separate video, so it's easy to redo one |
| Do 3-4 recordings per sitting | Your clicking hand and attention will fatigue after ~20 minutes |

---

## Checklist

- [ ] Guidde account created (guidde.com)
- [ ] Chrome extension installed and pinned
- [ ] Backend running (python3 api_server.py)
- [ ] Frontend running (npm start)
- [ ] Browser full-screen, bookmarks hidden, no other tabs
- [ ] Logged into SHIELD as Angela Johnson
- [ ] HIPAA gate accepted
- [ ] Training video script open on your phone or second monitor for reference
- [ ] Record Videos 1-10 following the sequence above
- [ ] Review and edit step titles in Guidde dashboard
- [ ] Share links or download MP4s
- [ ] Organize into "SHIELD Navigator Training" collection

---

*Total recording time: ~20 minutes of clicking.*
*Total output: 10 training videos, fully narrated and annotated, zero voiceover work.*
