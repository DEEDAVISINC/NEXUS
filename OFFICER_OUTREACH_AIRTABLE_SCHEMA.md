# 📬 OFFICER OUTREACH TRACKING - AIRTABLE SCHEMA

## Overview

This table tracks all introduction letters sent to contracting officers for closed opportunities. It's part of the relationship-building mining system that turns missed bids into future opportunities.

---

## TABLE: Officer Outreach Tracking

### Purpose
Track all outreach to contracting officers to build relationships and get on vendor lists for future opportunities.

### Fields

| Field Name | Field Type | Description | Options/Formula |
|-----------|-----------|-------------|-----------------|
| **Officer Name** | Single line text | Name of the contracting officer | Required |
| **Officer Email** | Email | Email address of the officer | Required |
| **Officer Phone** | Phone number | Phone number (if available) | Optional |
| **Opportunity Title** | Single line text | Title of the closed opportunity | |
| **Solicitation Number** | Single line text | Original solicitation number | |
| **Agency** | Single line text | Agency/organization | Auto-populated from opportunity |
| **Related Opportunity** | Link to another record | Link to Opportunities table | Links to: Opportunities |
| **Letter Generated Date** | Date | When letter was auto-generated | Auto-set by system |
| **Status** | Single select | Current status of outreach | Options: Draft, Sent, Follow-up Needed, Responded, Added to Vendor List, No Response |
| **Letter Content** | Long text | Full letter content | Markdown format |
| **Subject Line** | Single line text | Email subject line | |
| **Date Sent** | Date | When email was actually sent | Manual entry |
| **Follow-up Date** | Date | When to follow up (7-10 days after sent) | Formula: `DATEADD({Date Sent}, 10, 'days')` |
| **Response Received** | Checkbox | Did they respond? | |
| **Response Date** | Date | When they responded | |
| **Response Notes** | Long text | Notes about their response | |
| **Added to Vendor List** | Checkbox | Were we added to their vendor database? | |
| **Future Opportunities** | Link to another record | Future opps from this relationship | Links to: Opportunities |
| **Tags** | Multiple select | Categorize outreach | Options: VA, DoD, DOE, State, Local, Healthcare, IT, Construction, Supplies |
| **Priority** | Single select | How important is this relationship | Options: High, Medium, Low |
| **Next Action** | Single line text | What to do next | |
| **Next Action Date** | Date | When to take next action | |
| **Attachments Sent** | Attachment | Capability statements, certs sent | |
| **ProposalBio Score** | Number | Quality score from 10 biohacks (0-100) | Auto-generated |
| **Quality Badge** | Single line text | Quality indicator | 🟢 HIGH / 🟡 GOOD / 🔴 NEEDS WORK |
| **Quality Status** | Single select | Letter quality rating | Options: Ready to Send, Good - Minor Edits, Needs Improvement |
| **Improvement Notes** | Long text | ProposalBio™ recommendations | Auto-generated |
| **Created By** | Single line text | Who initiated this | Default: "NEXUS AI + ProposalBio™" |
| **Last Modified** | Last modified time | Track updates | Auto |

### Views

#### 1. **📋 All Outreach**
- **Type:** Grid view
- **Filter:** None
- **Sort:** Letter Generated Date (newest first)
- **Purpose:** See all outreach attempts

#### 2. **✉️ Ready to Send**
- **Type:** Grid view
- **Filter:** Status = "Draft"
- **Sort:** Letter Generated Date (oldest first)
- **Purpose:** Letters generated and ready to send

#### 3. **⏰ Follow-up Needed**
- **Type:** Grid view
- **Filter:** 
  - Status = "Sent"
  - Follow-up Date is before today
  - Response Received is not checked
- **Sort:** Follow-up Date (oldest first)
- **Purpose:** Officers who need follow-up

#### 4. **✅ Responded**
- **Type:** Grid view
- **Filter:** Response Received is checked
- **Sort:** Response Date (newest first)
- **Purpose:** Track successful outreach

#### 5. **🎯 High Priority**
- **Type:** Grid view
- **Filter:** Priority = "High"
- **Sort:** Next Action Date
- **Purpose:** Focus on most important relationships

#### 6. **📊 By Agency**
- **Type:** Grouped by Agency
- **Filter:** None
- **Sort:** Officer Name
- **Purpose:** Organize by contracting agency

---

## INTEGRATION WITH OPPORTUNITIES TABLE

### Add These Fields to Opportunities Table:

| Field Name | Field Type | Description |
|-----------|-----------|-------------|
| **Officer Outreach Sent** | Checkbox | Has an intro letter been generated? |
| **Officer Outreach Date** | Date | When letter was generated |
| **Officer Outreach Link** | Link to another record | Link to Officer Outreach Tracking |

This creates a two-way link so you can:
- See which opportunities have been reached out on
- Track outreach from the opportunity record
- Prevent duplicate letters

---

## WORKFLOW

### Automated Process:

1. **System identifies closed opportunities** with contracting officer contact info
2. **Generates personalized letter** based on opportunity details
3. **Creates record** in Officer Outreach Tracking (Status: Draft)
4. **Links to opportunity** record
5. **Marks opportunity** as "Officer Outreach Sent"

### Manual Process:

1. Review letters in "Ready to Send" view
2. Customize letter if needed
3. Send email with letter as PDF + attachments
4. Update "Date Sent" and Status to "Sent"
5. System auto-calculates follow-up date
6. Check "Follow-up Needed" view in 10 days
7. Send follow-up email if no response
8. Track responses and outcomes

---

## EXAMPLE RECORD

```
Officer Name: Jennifer Coleman
Officer Email: jennifer.coleman4@va.gov
Officer Phone: (803) 555-1234
Opportunity Title: FEMALE CONDOMS
Solicitation Number: 766-26-1-400-0182
Agency: VA Medical Center - 766 Ladson
Related Opportunity: [Link to Opportunities record]
Letter Generated Date: 01/21/2026
Status: Draft
Subject Line: Introduction - Dee Davis, Inc. - Female Condoms NSN 6515 (766-26-1-400-0182)
Letter Content: [Full letter text]
Tags: VA, Healthcare, Supplies
Priority: Medium
Created By: NEXUS AI
```

---

## SETUP INSTRUCTIONS

### Option 1: Create Table Manually

1. Go to your NEXUS Airtable base
2. Create new table: "Officer Outreach Tracking"
3. Add all fields listed above
4. Create the 6 views
5. Add fields to Opportunities table

### Option 2: Use Airtable Import (Recommended)

1. Create CSV with headers:
```csv
Officer Name,Officer Email,Officer Phone,Opportunity Title,Solicitation Number,Agency,Letter Generated Date,Status,Letter Content,Subject Line,Date Sent,Response Received,Response Date,Response Notes,Added to Vendor List,Tags,Priority,Next Action,Next Action Date,Created By
```

2. Import to new table
3. Configure field types
4. Create views
5. Link to Opportunities table

---

## BENEFITS

✅ **Never lose a lead** - Closed opportunities become relationship opportunities
✅ **Automated letters** - AI generates professional, personalized introductions
✅ **Systematic follow-up** - Never forget to follow up
✅ **Build vendor relationships** - Get added to agency vendor lists
✅ **Track success** - Measure response rates and outcomes
✅ **Future pipeline** - Relationships lead to future awards

---

## METRICS TO TRACK

- **Letters Generated per Week**
- **Response Rate** (Responses / Letters Sent)
- **Vendor List Adds** (Added to Vendor List / Responses)
- **Future Opportunities** (Opps won from relationships)
- **Average Time to Response**
- **Best Performing Agencies** (Highest response rates)

---

**Built by NEXUS AI | Contracting Officer Outreach System v1.0**
