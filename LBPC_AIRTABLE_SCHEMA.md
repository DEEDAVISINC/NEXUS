# LBPC AIRTABLE SCHEMA - SURPLUS RECOVERY SYSTEM

## 📋 **COMPLETE AIRTABLE SETUP FOR LBPC**

### **OVERVIEW:**
LBPC (Lancaster Banques P.C.) manages surplus recovery from foreclosure auctions across all 50 states. This is a contingency-based service where you help property owners reclaim unclaimed funds and charge a 30% fee.

**Business Model:**
- Find property owners with unclaimed surplus funds (public records)
- Contact them via email, phone, and mail
- Offer free recovery services (30% contingency fee, no upfront cost)
- Handle all paperwork and legal requirements
- Client gets 70%, you get 30%

**You'll create 4 tables:**
1. **LBPC Leads** - Property owners with unclaimed funds
2. **LBPC Documents** - Generated notices, contracts, and checklists
3. **LBPC Tasks** - Automated workflow tasks
4. **LBPC Templates** - Document templates with variable placeholders

---

## 🏢 **TABLE 1: LBPC LEADS**

### **Purpose:** Track all surplus recovery leads from discovery to payment

### **STEP-BY-STEP FIELD CREATION:**

Go to your NEXUS Command Center Airtable base → Create new table → Name it "LBPC Leads"

---

### **SECTION A: IDENTIFICATION & PROPERTY INFO**

| Field Name | Field Type | Configuration |
|------------|-----------|--------------|
| **Lead ID** | Autonumber | Primary field - Format: LBPC-0001 |
| **Client Name** | Single line text | Full name of property owner |
| **Property Address** | Long text | Full property address (street, unit, etc.) |
| **City** | Single line text | City |
| **County** | Single line text | County name |
| **State** | Single select | Options: `MI`, `GA`, `MD`, `TX`, `CA`, `IL`, `AL`, `AK`, `AZ`, `AR`, `CO`, `CT`, `DE`, `FL`, `HI`, `ID`, `IN`, `IA`, `KS`, `KY`, `LA`, `ME`, `MA`, `MN`, `MS`, `MO`, `MT`, `NE`, `NV`, `NH`, `NJ`, `NM`, `NY`, `NC`, `ND`, `OH`, `OK`, `OR`, `PA`, `RI`, `SC`, `SD`, `TN`, `UT`, `VT`, `VA`, `WA`, `WV`, `WI`, `WY`, `DC` |
| **Zip Code** | Single line text | Postal code |
| **Case Number** | Single line text | Court or county case number |

---

### **SECTION B: FINANCIAL INFORMATION**

| Field Name | Field Type | Configuration |
|------------|-----------|--------------|
| **Surplus Amount** | Currency | Format: USD, 2 decimals |
| **Your Fee (30%)** | Formula | `{Surplus Amount} * 0.30` - Format as Currency |
| **Client Portion (70%)** | Formula | `{Surplus Amount} * 0.70` - Format as Currency |
| **Estimated Costs** | Currency | Optional - for tracking costs (legal fees, filing fees, etc.) |
| **Net Profit** | Formula | `{Your Fee (30%)} - {Estimated Costs}` - Format as Currency |

---

### **SECTION C: CONTACT INFORMATION**

| Field Name | Field Type | Configuration |
|------------|-----------|--------------|
| **Contact Phone** | Phone number | Property owner phone |
| **Contact Email** | Email | Property owner email |
| **Secondary Phone** | Phone number | Alternate contact |
| **Secondary Email** | Email | Alternate email |
| **Preferred Contact Method** | Single select | Options: `Email`, `Phone`, `Text`, `Mail`, `Unknown` |

---

### **SECTION D: LEAD STATUS & TRACKING**

| Field Name | Field Type | Configuration |
|------------|-----------|--------------|
| **Status** | Single select | Options: `New`, `Contacted`, `Document Sent`, `Contract Signed`, `Documents Submitted`, `Awaiting County Response`, `Funds Released`, `Client Paid`, `Complete`, `Lost`, `On Hold` |
| **Lead Stage** | Single select | Options: `Cold`, `Warm`, `Hot`, `Active`, `Won`, `Lost` |
| **Lead Source** | Single select | Options: `County Website Mining`, `State Website Mining`, `Manual Entry`, `Referral`, `Public Records Search`, `Court Records`, `Other` |
| **Source URL** | URL | Link to original public record |
| **Priority Score** | Number | 0-100 (AI-calculated) - Precision: 0 decimals |
| **Win Probability** | Number | 0-100 (AI-calculated) - Precision: 0 decimals |

---

### **SECTION E: AI QUALIFICATION DATA**

| Field Name | Field Type | Configuration |
|------------|-----------|--------------|
| **AI Qualification Result** | Long text | JSON output from AI analysis |
| **AI Recommendation** | Single select | Options: `GO - High Priority`, `GO - Standard`, `REVIEW - Needs Analysis`, `NO-GO - Skip` |
| **AI Strengths** | Long text | Competitive advantages for this lead |
| **AI Concerns** | Long text | Risks or challenges identified |
| **Qualification Date** | Date | When AI qualified this lead |

---

### **SECTION F: TIMELINE & DATES**

| Field Name | Field Type | Configuration |
|------------|-----------|--------------|
| **Date Discovered** | Date | When lead was found/added |
| **First Contact Date** | Date | When you first reached out |
| **Last Contact Date** | Date | Most recent contact attempt |
| **Next Follow-up Date** | Date | When to follow up next |
| **Contract Signed Date** | Date | When engagement agreement signed |
| **Documents Submitted Date** | Date | When claim submitted to county |
| **Funds Released Date** | Date | When county released funds |
| **Client Paid Date** | Date | When you sent client their 70% |
| **Case Closed Date** | Date | When everything completed |
| **Days Since Last Contact** | Formula | `DATETIME_DIFF(TODAY(), {Last Contact Date}, 'days')` - Format as Integer |

---

### **SECTION G: RELATIONSHIPS (Links to Other Tables)**

| Field Name | Field Type | Configuration |
|------------|-----------|--------------|
| **Documents** | Link to another record | Link to "LBPC Documents" table - Allow linking to multiple records |
| **Tasks** | Link to another record | Link to "LBPC Tasks" table - Allow linking to multiple records |
| **Invoice** | Link to another record | Link to "Invoices" table - Allow linking to multiple records |

---

### **SECTION H: COMMUNICATION LOG**

| Field Name | Field Type | Configuration |
|------------|-----------|--------------|
| **Communications Log** | Long text | History of all contacts (date, method, outcome) |
| **Email Sent Count** | Number | How many emails sent - Precision: 0 decimals |
| **Call Count** | Number | How many calls made - Precision: 0 decimals |
| **Mail Sent Count** | Number | How many physical mailings - Precision: 0 decimals |

---

### **SECTION I: NOTES & INTERNAL TRACKING**

| Field Name | Field Type | Configuration |
|------------|-----------|--------------|
| **Internal Notes** | Long text | Internal strategy, observations, next steps |
| **Lost Reason** | Long text | Why deal was lost (if applicable) |
| **On Hold Reason** | Long text | Why on hold (if applicable) |
| **Assigned To** | Single select | Options: `Charin Cross`, `Team Member 1`, `Team Member 2`, `Unassigned` |
| **Tags** | Multiple select | Options: `High Priority`, `Quick Win`, `Difficult Case`, `Legal Issue`, `Out of State`, `Recent Case`, `Old Case`, `High Value`, `Low Value`, `Add more as needed` |

---

### **SECTION J: SYSTEM FIELDS**

| Field Name | Field Type | Configuration |
|------------|-----------|--------------|
| **Created Date** | Created time | Auto-generated |
| **Last Modified** | Last modified time | Auto-generated |
| **Created By** | Created by | Auto-tracks who created record |

---

## 📄 **TABLE 2: LBPC DOCUMENTS**

### **Purpose:** Store all generated documents (notices, contracts, checklists)

### **STEP-BY-STEP FIELD CREATION:**

Create new table → Name it "LBPC Documents"

| Field Name | Field Type | Configuration |
|------------|-----------|--------------|
| **Document ID** | Autonumber | Primary field - Format: DOC-0001 |
| **Document Name** | Single line text | Auto-generated: "{Client Name} - {Document Type}" |
| **Lead** | Link to another record | Link to "LBPC Leads" table |
| **Document Type** | Single select | Options: `Initial Notice`, `Engagement Agreement`, `Document Checklist`, `Follow-up Letter`, `Limited Power of Attorney`, `Letter of Direction`, `Final Accounting Letter`, `Process Disclaimer`, `W-9 Form`, `Custom Document` |
| **Template Used** | Link to another record | Link to "LBPC Templates" table |
| **Generated Content** | Long text | Full document text with all variables filled |
| **Status** | Single select | Options: `Draft`, `Generated`, `Sent via Email`, `Sent via Mail`, `Sent via Both`, `Client Signed`, `Archived` |
| **Generated Date** | Date with time | When document was created |
| **Sent Date** | Date | When document was sent to client |
| **Sent Method** | Single select | Options: `Email`, `USPS Mail`, `Certified Mail`, `Both Email and Mail`, `In-Person`, `Not Yet Sent` |
| **Sent To Email** | Email | Email address where sent |
| **Tracking Number** | Single line text | USPS tracking number (if mailed) |
| **Client Response Date** | Date | When client responded/signed |
| **Document File (PDF)** | Attachment | PDF version of document |
| **AI Enhanced** | Checkbox | Was AI used to personalize this document? |
| **Version** | Number | Document version (1.0, 1.1, 2.0, etc.) |
| **Notes** | Long text | Internal notes about this document |
| **Created Date** | Created time | Auto-generated |

---

## ✅ **TABLE 3: LBPC TASKS**

### **Purpose:** Track automated workflow tasks and manual to-dos

### **STEP-BY-STEP FIELD CREATION:**

Create new table → Name it "LBPC Tasks"

| Field Name | Field Type | Configuration |
|------------|-----------|--------------|
| **Task ID** | Autonumber | Primary field - Format: TASK-0001 |
| **Task Title** | Single line text | Short description of task |
| **Lead** | Link to another record | Link to "LBPC Leads" table |
| **Task Type** | Single select | Options: `Send Initial Notice`, `Make Call`, `Send Follow-up Email`, `Send Contract`, `Follow Up on Contract`, `Submit Documents to County`, `Check Funds Status`, `Send Client Payment`, `Archive Case`, `Other` |
| **Task Description** | Long text | Detailed description and instructions |
| **Priority** | Single select | Options: `Critical`, `High`, `Medium`, `Low` |
| **Status** | Single select | Options: `Pending`, `In Progress`, `Completed`, `Cancelled`, `Blocked` |
| **Due Date** | Date | When task should be completed |
| **Due Time** | Single line text | Optional - specific time (e.g., "9:00 AM") |
| **Completed Date** | Date with time | When task was completed |
| **Assigned To** | Single select | Options: `Charin Cross`, `Team Member 1`, `Team Member 2`, `Unassigned` |
| **Auto-Generated** | Checkbox | Was this created by workflow automation? |
| **Triggered By Rule** | Single line text | Which workflow rule created this (e.g., "New Lead Day 0") |
| **Completion Notes** | Long text | Notes about how task was completed |
| **Blocked Reason** | Long text | Why task is blocked (if applicable) |
| **Created Date** | Created time | Auto-generated |
| **Last Modified** | Last modified time | Auto-generated |

---

## 📝 **TABLE 4: LBPC TEMPLATES**

### **Purpose:** Store document templates with variable placeholders

### **STEP-BY-STEP FIELD CREATION:**

Create new table → Name it "LBPC Templates"

| Field Name | Field Type | Configuration |
|------------|-----------|--------------|
| **Template Name** | Single line text | Primary field - e.g., "Initial Notice Letter v2.0" |
| **Template Type** | Single select | Options: `Initial Notice`, `Engagement Agreement`, `Document Checklist`, `Follow-up Letter`, `Limited Power of Attorney`, `Letter of Direction`, `Final Accounting Letter`, `Process Disclaimer`, `W-9 Form`, `Custom` |
| **Template Content** | Long text | Full template with {{placeholders}} |
| **Variable List** | Long text | List of all {{variables}} used in this template |
| **Active** | Checkbox | Is this template currently in use? |
| **Version** | Single line text | e.g., "2.0", "1.5" |
| **Effective Date** | Date | When this version became active |
| **Supersedes** | Link to another record | Link to previous version of this template |
| **Use AI Enhancement** | Checkbox | Should AI personalize this template? |
| **AI Enhancement Instructions** | Long text | Instructions for how AI should enhance (tone, focus, etc.) |
| **Usage Count** | Rollup | Count of documents using this template |
| **Notes** | Long text | Usage instructions, compliance notes, state-specific info |
| **Created Date** | Created time | Auto-generated |
| **Last Modified** | Last modified time | Auto-generated |

---

## 🎯 **VIEWS TO CREATE**

After creating all 4 tables, set up these views:

### **LBPC Leads Views:**

1. **All Leads** (Default)
   - Sort: Created Date (newest first)

2. **Active Leads**
   - Filter: Status is any of `Contacted`, `Document Sent`, `Contract Signed`, `Documents Submitted`, `Awaiting County Response`
   - Sort: Priority Score (high to low)

3. **High Priority**
   - Filter: Priority Score ≥ 80
   - Filter: Lead Stage is any of `Hot`, `Active`
   - Sort: Priority Score (high to low)

4. **Needs Follow-up**
   - Filter: Days Since Last Contact ≥ 3
   - Filter: Status is not `Complete`, `Lost`, `On Hold`
   - Sort: Days Since Last Contact (high to low)

5. **By State** (Group View)
   - Group by: State
   - Sort: Surplus Amount (high to low)

6. **Contract Signed**
   - Filter: Status = `Contract Signed` OR `Documents Submitted` OR `Awaiting County Response`
   - Sort: Contract Signed Date (oldest first)

7. **High Value Leads** (≥$25K)
   - Filter: Surplus Amount ≥ 25000
   - Sort: Surplus Amount (high to low)

8. **Lost Leads**
   - Filter: Status = `Lost`
   - Sort: Last Modified (newest first)

### **LBPC Documents Views:**

1. **All Documents** (Default)
2. **Pending Sending**
   - Filter: Status = `Generated` OR `Draft`
3. **Sent Documents**
   - Filter: Status contains `Sent`
4. **By Document Type** (Group View)
   - Group by: Document Type

### **LBPC Tasks Views:**

1. **All Tasks** (Default)
2. **My Open Tasks**
   - Filter: Status = `Pending` OR `In Progress`
   - Sort: Due Date (ascending)
3. **Overdue**
   - Filter: Due Date is before TODAY()
   - Filter: Status ≠ `Completed`, `Cancelled`
4. **By Priority** (Group View)
   - Group by: Priority
5. **Auto-Generated Tasks**
   - Filter: Auto-Generated = TRUE

### **LBPC Templates Views:**

1. **All Templates** (Default)
2. **Active Templates**
   - Filter: Active = TRUE

---

## 📊 **PRE-POPULATE TEMPLATES TABLE**

After creating the Templates table, add these 7 records:

---

### **Record 1: Initial Notice Letter**

**Template Name:** `Initial Notice Letter`  
**Template Type:** `Initial Notice`  
**Active:** ✓  
**Version:** `2.0`  
**Use AI Enhancement:** ✓

**Template Content:**
```
CHARIN CROSS
99 WALL ST. SUITE 1273
NEW YORK, NY 10005
347.434.4469
claims@lbpc.info | claims@deedavisinc.com

{{date}}

{{clientName}}
{{property}}
{{city}}, {{state}} {{zipCode}}

CLAIM# {{claimNumber}}

Re: Recovery of Unclaimed Funds

Hi {{clientName}},

Allow me to introduce myself, I am Charin Cross, A Claims Manager at LANCASTER BANQUES P.C. (an Associate of Dee Davis Inc.). We are a boutique auditing firm based in New York, NY. Upon completion of a recent audit, we may have uncovered unclaimed funds that potentially belong to you.

We would be pleased to extend our services to assist you with the recovery of these unclaimed funds.

• We will perform the necessary research to identify the source and amount of your Claim.
• We will cover "all" expenses and dedicate the labor required to recover your Claim on your behalf, including paying all legal expenses whether or not the claim is recovered.

THIS LETTER IS IN NO WAY OF A FORM OF SOLICITATION, NOR AN ATTEMPT TO COLLECT A DEBT. WE ARE NOT A DEBT COLLECTION AGENCY.

We make an effort to provide the highest level of service to all of our clients. If you have any questions, and/or would like our firm to recover these funds for you. Feel free to send us an email, or simply give us a call at 347.434.4469.

We look forward to speaking with you, and processing your claim.

Sincerely,

Charin Cross
Claims Management
LANCASTER BANQUES P.C. (an Associate of Dee Davis Inc.)
charin@lancasterbanquespc.com | claims@deedavisinc.com
```

**Variable List:**
```
{{date}}
{{clientName}}
{{property}}
{{city}}
{{state}}
{{zipCode}}
{{claimNumber}}
```

---

### **Record 2: Engagement Agreement**

**Template Name:** `Engagement Agreement`  
**Template Type:** `Engagement Agreement`  
**Active:** ✓  
**Version:** `2.0`  
**Use AI Enhancement:** ✓

**Template Content:**
```
LANCASTER BANQUES P.C. (an Associate of Dee Davis Inc.)
99 Wall Street, Suite 1273
New York, New York 10005
Phone: 347.434.4469
Email: claims@lbpc.info | claims@deedavisinc.com


ENGAGEMENT AGREEMENT

CLAIM # {{claimNumber}}

Re: Recovery of Unclaimed Funds

Dear {{clientName}}:

It was a pleasure speaking with you. LANCASTER BANQUES P.C. (the "Company") is pleased to accept the opportunity to assist you with the recovery of your unclaimed funds currently being held by a government agency (the "Claim"). This engagement letter (the "Agreement") outlines the scope and terms of our services and your responsibilities.

1. SERVICES

The Company agrees to provide the following services in connection with the Claim:

   a. Incur the expenses and dedicate the labor required to research and identify the exact source and amount of the Claim.
   
   b. Coordinating with the appropriate government agency for the preparation and submission of the appropriate paperwork for the recovery of the Claim.
   
   c. Coordinating with you to submit the appropriate paperwork and forms of identification for the recovery of the Claim.

2. YOUR RESPONSIBILITIES

In connection with the recovery of the Claim, you agree to the following:

   a. AUTHORIZATION
      You authorize the Company to act as your exclusive agent for the recovery of the Claim.
   
   b. PAPERWORK
      You agree to sign and return all documents required for recovery of the Claim to the Company within three (3) days of receipt of the documents from the Company.
   
   c. COOPERATION
      Both parties agree to cooperate fully with all reasonable requests from the other in performance of this Agreement.

3. COSTS AND FEES

   a. COSTS
      Company shall be responsible for ALL costs associated with the recovery of the Claim, including attorney's fees. UNDER NO CIRCUMSTANCES SHALL YOU BE RESPONSIBLE FOR ANY UPFRONT OR OUT-OF-POCKET COSTS associated with the recovery of your Claim.
   
   b. CONTINGENCY FEE
      Upon successful recovery of your claim, you agree to a contingent fee of thirty percent (30%) of the proceeds of the claim. The remaining seventy percent (70%) belongs to you. This shall apply whether we receive the check or if you receive the check. Regardless of which party receives the check, the other party shall immediately issue a check to the other party for their percentage by mail postmarked no later than three (3) business days of receiving the government-issued check.
      
      Should either party fail to pay the other party their portion of the Claim, the other party shall be legally entitled to three (3) times the amount due under this Agreement.

If the terms of this letter are acceptable to you, please acknowledge by signing below and returning to my attention at the address/email provided (Instructions available on the back of final page).

Very Truly Yours,

{{agentName}}
AGENT
LANCASTER BANQUES P.C. (an Associate of Dee Davis Inc.)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CLIENT ACCEPTANCE

I have read and agree to the terms of this Engagement Agreement.

Client Name: {{clientName}}
Date: {{date}}

Signature: _________________________________

Address: {{property}}, {{city}}, {{state}} {{zipCode}}

Phone: {{clientPhone}}
Email: {{clientEmail}}

Reference Number: {{claimNumber}}
```

**Variable List:**
```
{{claimNumber}}
{{clientName}}
{{agentName}}
{{date}}
{{property}}
{{city}}
{{state}}
{{zipCode}}
{{clientPhone}}
{{clientEmail}}
```

---

### **Record 3: Document Checklist**

**Template Name:** `Document Checklist`  
**Template Type:** `Document Checklist`  
**Active:** ✓  
**Version:** `2.0`  
**Use AI Enhancement:** ✗

**Template Content:**
```
LANCASTER BANQUES P.C. (an Associate of Dee Davis Inc.)
99 WALL STREET, SUITE 1273, NEW YORK, NY 10005
Phone: 347.434.4469
Email: claims@lbpc.info | claims@deedavisinc.com

RE: CLAIM NUMBER # {{claimNumber}}
DATE: {{date}}

Dear {{clientName}},

In order to process your claim, and to insure the claim is submitted correctly, proper identification for yourself as well as proof of ownership/residency is needed to expedite acceptance.

Below you will find a checklist of all required information.

☐ VALID PHOTO IDENTIFICATION
☐ COPY OF DEED
☐ UTILITY BILL FROM PROPERTY
☐ VISA, PASSPORT  
☐ CERTIFICATE OF DEATH (if applicable)
☐ LIMITED POWER OF ATTORNEY
☐ LETTER OF DIRECTION
☐ W-9 FORM
☐ ACH PAYMENT FORM (if applicable)

Please send documents to:

Email: claims@lbpc.info | claims@deedavisinc.com
Phone: 347.434.4469
Fax: 347.434.4469
Mail: LANCASTER BANQUES P.C.
      1221 BOWERS ST. SUITE 2141
      BIRMINGHAM, MICHIGAN 48012

THANK YOU,
STAFF
LANCASTER BANQUES P.C. (an Associate of Dee Davis Inc.)
```

**Variable List:**
```
{{claimNumber}}
{{date}}
{{clientName}}
```

---

### **Record 4: Limited Power of Attorney**

**Template Name:** `Limited Power of Attorney`  
**Template Type:** `Limited Power of Attorney`  
**Active:** ✓  
**Version:** `2.0`  
**Use AI Enhancement:** ✗

**Template Content:**
```
LIMITED POWER OF ATTORNEY


I, {{companyRepName}} on behalf of LANCASTER BANQUES P.C. (an Associate of Dee Davis Inc.), 
hereby appoint {{clientName}} on behalf of LANCASTER BANQUES P.C. as my 
true and lawful attorney for me and in my name and stead, and for my use and 
benefit to claim funds held for me by {{countyName}}, giving and 
granting unto my said attorney in fact full authority and power to do and 
perform any and all other acts necessary or incident to the performance and 
execution of the powers herein expressly granted with power to do and perform 
all acts authorized hereby; as fully to all intents and purposes as the 
Grantor might or could do if personally present.

I certify this is a true and correct copy of {{documentDescription}} in the 
possession of {{documentHolderName}}.

This Power of Attorney will cease twelve (12) months from date hereof.

Dated: {{date}}

By: _________________________________
Name: {{companyRepName}}
Title: {{companyRepTitle}}




STATE OF {{state}}) ss.
COUNTY OF {{county}})

The foregoing has been acknowledged before me this {{day}} day of {{month}}, 
{{year}}, by {{companyRepName}}. Witness my hand and official seal.

My commission expires: _______________

_________________________________
Notary Public


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For questions, contact:
LANCASTER BANQUES P.C. (an Associate of Dee Davis Inc.)
99 Wall Street, Suite 1273, New York, NY 10005
Email: claims@lbpc.info | claims@deedavisinc.com
Phone: 347.434.4469
```

**Variable List:**
```
{{companyRepName}}
{{clientName}}
{{countyName}}
{{documentDescription}}
{{documentHolderName}}
{{date}}
{{companyRepTitle}}
{{state}}
{{county}}
{{day}}
{{month}}
{{year}}
```

---

### **Record 5: Letter of Direction**

**Template Name:** `Letter of Direction`  
**Template Type:** `Letter of Direction`  
**Active:** ✓  
**Version:** `2.0`  
**Use AI Enhancement:** ✗

**Template Content:**
```
DIRECTION

Firm Direction Re: PROCEEDS OF OVERAGE


TO: {{countyTreasurerName}}
OF: {{countyName}}

RE: CLAIM FOR PROCEEDS OF OVERAGE FUNDS

CLAIMANT: {{clientName}}
FIRM: LANCASTER BANQUES P.C. (an Associate of Dee Davis Inc.)
PROPERTY ADDRESS: {{property}}
DESCRIPTION: PROCEEDS OF OVERAGE
MUNICIPALITY: {{municipalityName}}
DATE: {{date}}


The undersigned hereby irrevocably authorize {{countyName}} to send Proceeds 
of Overage Payment in respect of the above transaction payable as follows: in 
the trust of (firm) LANCASTER BANQUES P.C.


Address of Property: {{property}}, {{city}}, {{state}} {{zipCode}}

Pay Proceeds to: LANCASTER BANQUES P.C.
Phone Number: 347.434.4469
Mailing Address: 1221 BOWERS ST. SUITE 2141
                 BIRMINGHAM, MICHIGAN 48012
Email: claims@lbpc.info | claims@deedavisinc.com


Signature of Power of Direction Holder: _________________________________

Signature of Claimant: _________________________________

Date: {{date}}


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANY VIOLATION FROM EITHER PARTIES IN THE TERMS AS AGREED, VIOLATES THESE 
TERMS, AND WILL BE SUBJECT TO PENALTIES NEGOTIATED IN ENGAGEMENT AGREEMENT.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NOTARY SECTION

STATE OF {{state}})
COUNTY OF {{county}}) ss.

I, {{notaryName}}, the undersigned, a Notary Public in and for the County and 
State aforesaid, do hereby certify that {{clientName}} is/are personally known 
to me to be the same person(s) whose name is subscribed to this instrument 
appeared before me this day in person and acknowledged that he/she/they signed 
and delivered the said instrument as his/her/their own free and voluntary act.

Given under my hand and Notarial Seal this {{day}} day of {{month}}, {{year}}.


_________________________________
Notary Public

My Commission Expires: _______________


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LAW SOCIETY OF LANCASTER BANQUES P.C.:
NOT TO BE USED OR REPRODUCED WITHOUT PERMISSION
```

**Variable List:**
```
{{countyTreasurerName}}
{{countyName}}
{{clientName}}
{{property}}
{{municipalityName}}
{{date}}
{{city}}
{{state}}
{{zipCode}}
{{notaryName}}
{{county}}
{{day}}
{{month}}
{{year}}
```

---

### **Record 6: Final Accounting Letter**

**Template Name:** `Final Accounting Letter`  
**Template Type:** `Final Accounting Letter`  
**Active:** ✓  
**Version:** `2.0`  
**Use AI Enhancement:** ✗

**Template Content:**
```
LANCASTER BANQUES P.C. (an Associate of Dee Davis Inc.)
99 Wall Street, Suite 1273
New York, NY 10005
Phone: 347.434.4469
Email: claims@lbpc.info | claims@deedavisinc.com


DATE: {{date}}

RE: CLAIM #{{claimNumber}}


Dear {{clientName}},

Thank you for giving us the opportunity to serve you. We appreciate the confidence 
that you have placed in us and look forward to a continuing relationship which will 
prove to be beneficial to all concerned. Should you need any of our company services 
in the future, please do not hesitate to contact us.

The following is a description of fees, expenses, and client award computed in 
accordance to the Contingent Fee Contract. The following is based on the agreed 
contingent fee.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FINAL ACCOUNTING

OVERAGE PROCEEDS CLAIM TOTAL:                    ${{totalClaimAmount}}

FIRM/ATTORNEY FEES (30% OF TOTAL):               ${{firmFeeAmount}}

GROSS AMOUNT PAYABLE TO CLIENT (70%):            ${{clientPaymentAmount}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A check in the amount of ${{clientPaymentAmount}} has been issued and will 
arrive within 5-7 business days.

Thank you for your business!


Sincerely,

{{agentName}}
Claims Management
LANCASTER BANQUES P.C. (an Associate of Dee Davis Inc.)
charin@lancasterbanquespc.com | claims@deedavisinc.com
347.434.4469
```

**Variable List:**
```
{{date}}
{{claimNumber}}
{{clientName}}
{{totalClaimAmount}}
{{firmFeeAmount}}
{{clientPaymentAmount}}
{{agentName}}
```

---

### **Record 7: Process Disclaimer (Mailer Back / Email Footer)**

**Template Name:** `Process Disclaimer`  
**Template Type:** `Information / Disclaimer`  
**Active:** ✓  
**Version:** `2.0`  
**Use AI Enhancement:** ✗

**Template Content:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For your convenience, we included your engagement agreement. This agreement will 
allow LANCASTER BANQUES P.C. (an Associate of Dee Davis Inc.) to begin the claims 
process on your behalf. Upon receiving this agreement, your claims representative 
will contact you within 24 hours to complete the procedure.

PLEASE RETURN THIS AGREEMENT TO:

CLAIMS_L.B.P.C.
LANCASTER BANQUES P.C.
1221 BOWERS ST. STE 2141
BIRMINGHAM, MICHIGAN 48012

FAX: 347.434.4469
EMAIL: claims@lbpc.info | claims@deedavisinc.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ASSET RECOVERY PROCESS

1. LOCATING ASSETS
Lancaster Banques P.C.'s highly trained individuals and proprietary software locate 
dormant assets and unclaimed funds from a multitude of sources.

2. IDENTIFYING PARTIES DUE ASSETS OR FUNDS (PARTIES OF INTEREST)
A wholly separate work group within our company reviews volumes of private and 
public documents to determine which parties, businesses, individuals, and estates 
have rights to the assets or funds.

3. LOCATING CLIENTS
Our highly trained team of research professionals, skip tracers and private 
investigators use every tool available to locate our clients. We utilize several 
subscription databases, on-line public record databases and have even knocked on 
the doors of relatives and former neighbors to find our clients. This is the most 
time-consuming and costly part of the recovery process and can take from one month 
to several years.

4. CONTACT BY CLAIMS MANAGER
Each potential client is assigned to one of our claims managers. The assigned 
claims manager contacts the party of interest and determines the most effective way 
of claiming the funds. The claims manager then prepares a simple engagement 
agreement outlining the terms of the transaction.

5. PREPARING AND SUBMITTING CLAIMS

   DOCUMENT PREPARATION
   Once you agree to become a client of Lancaster Banques P.C., our team of claims 
   processors prepares all documents, pleadings, declarations and affidavits 
   required to document the rights to the assets or funds.

   DELIVERY OF DOCUMENTS TO CLIENT
   Our claims processors then arrange to have the documents delivered to our party 
   of interest to be executed and returned to Lancaster Banques P.C.

   CLAIM ASSEMBLY AND QUALITY CONTROL
   Once the documents are returned to our claims processing department, the claim 
   package is assembled. It then goes through two additional quality control levels 
   before it is filed with the holder of the assets or funds.

   NOTIFICATION THAT THE CLAIM HAS BEEN FILED
   A confirmation letter is sent informing our client when the claim was submitted 
   and approximately when to expect payment.

6. POST CLAIM FOLLOW UP AND TRACKING
Our claims processing team receives and answers all correspondences and questions 
from the asset holders and ensures that all timelines are met. In the rare event 
that outside legal assistance is required to receive payment, Lancaster Banques 
P.C. handles all aspects of the process and advances all expenses.

7. DETERMINATION AND PAYMENT OF CLAIM
We will notify you when the asset holder approves your claim. Once those funds are 
received, we will forward a check to you with a final accounting and customer 
survey.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LANCASTER BANQUES P.C. (an Associate of Dee Davis Inc.)
99 Wall Street, Suite 1273
New York, NY 10005
Phone: 347.434.4469
Email: claims@lbpc.info | claims@deedavisinc.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Variable List:**
```
(No variables - static text)
```

---

## ✅ **SETUP CHECKLIST**

Use this checklist as you build:

- [ ] Create "LBPC Leads" table with all 40+ fields
- [ ] Create "LBPC Documents" table with all fields
- [ ] Create "LBPC Tasks" table with all fields
- [ ] Create "LBPC Templates" table with all fields
- [ ] Set up all views for each table
- [ ] Pre-populate Templates table with 7 templates:
  - [ ] Initial Notice Letter
  - [ ] Engagement Agreement
  - [ ] Document Checklist
  - [ ] Limited Power of Attorney
  - [ ] Letter of Direction
  - [ ] Final Accounting Letter
  - [ ] Process Disclaimer
- [ ] Test linking between tables (create test lead → create test document)
- [ ] Add "LBPC" option to Invoices "Source System" field
- [ ] Create automations (after Pro upgrade)

---

## 🎯 **NEXT STEPS**

Once Airtable schema is complete:

1. Update `nexus_backend.py` with LBPC endpoints
2. Build `LBPCSystem.tsx` frontend
3. Implement lead mining system
4. Test document generation
5. Deploy and start finding surplus leads

**Estimated setup time:** 30-45 minutes for all 4 tables

---

Let me know when Airtable setup is complete and I'll proceed with backend integration! 🚀
