# AI CONVERSATIONS TABLE - AIRTABLE SCHEMA

## Purpose
Store all AI Copilot conversations for permanent record, analytics, and future reference.

---

## Table Name
**AI Conversations**

---

## Fields (12 fields)

### CONVERSATION BASICS
1. **Conversation ID** - Autonumber (rename "Name" field)
   - Primary field
   - Auto-increments

2. **Session ID** - Single line text
   - Unique identifier for each conversation session
   - Format: `session-TIMESTAMP-RANDOM`

3. **Started** - Created time
   - When conversation began

4. **Last Updated** - Last modified time
   - When last message was added

### MESSAGE CONTENT
5. **Messages** - Long text
   - JSON array of all messages in conversation
   - Format: `[{"role": "user", "content": "...", "timestamp": "..."}, ...]`

6. **Message Count** - Number
   - Total number of messages in conversation

7. **Summary** - Long text
   - AI-generated summary of the conversation (optional)

### CONTEXT & METADATA
8. **System Context** - Single select
   - Options: GPSS, ATLAS PM, DDCSS, Invoices, Command Center, General
   - Which system was user in when using copilot

9. **Topics** - Multiple select
   - Options: RFP Analysis, Proposal Generation, Project Planning, Invoice Help, Contract Questions, Business Strategy, Technical Support, Other
   - Main topics discussed

10. **Status** - Single select
    - Options: Active, Archived, Important
    - Default: Active

### ANALYTICS
11. **User Rating** - Single select (optional)
    - Options: ⭐, ⭐⭐, ⭐⭐⭐, ⭐⭐⭐⭐, ⭐⭐⭐⭐⭐
    - User feedback on conversation quality

12. **Notes** - Long text
    - User's personal notes about the conversation

---

## Views to Create

### 1. **All Conversations** (Default)
- Sort by: Last Updated (descending)
- Shows all conversations

### 2. **Recent Active**
- Filter: Status = Active
- Filter: Last Updated is within last 7 days
- Sort by: Last Updated (descending)

### 3. **By System**
- Group by: System Context
- Sort by: Last Updated (descending)

### 4. **Important**
- Filter: Status = Important
- Sort by: Last Updated (descending)

### 5. **Highly Rated**
- Filter: User Rating = ⭐⭐⭐⭐⭐ or ⭐⭐⭐⭐
- Sort by: Last Updated (descending)

---

## Setup Instructions

1. In your **NEXUS Command Center** Airtable base, create a new table called **"AI Conversations"**

2. Rename the default "Name" field to **"Conversation ID"** and set it to **Autonumber**

3. Add the remaining 11 fields as specified above

4. Create the 5 views listed above

5. Done! The AI Copilot will automatically save conversations here.

---

## Integration Notes

- Each new conversation creates a new record
- Messages are appended to the existing record as conversation continues
- Session ID allows frontend to track and update the same conversation
- Messages stored as JSON for easy parsing and display
- System Context auto-detected based on which NEXUS system user is in
- Topics can be manually added or AI-detected

---

## Privacy & Data

- All conversations are stored in your private Airtable base
- Only you have access to the data
- No conversations are sent to any third party beyond Claude AI processing
- You can delete any conversation record at any time
