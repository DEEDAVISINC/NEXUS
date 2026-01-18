# ProposalBio™ Airtable Setup Guide

## Overview
This guide shows you how to add ProposalBio™ Quality Assurance fields to your existing `GPSS Proposals` table and create supporting tables.

---

## STEP 1: Add Fields to Existing "GPSS Proposals" Table

Open your **GPSS Proposals** table in Airtable and add these fields:

| Field Name | Field Type | Configuration |
|------------|------------|---------------|
| **ProposalBio Composite Score** | Number | Precision: 2 decimals, Format: Decimal (0.00) |
| **ProposalBio Status** | Single select | Options: `APPROVED`, `REVISE`, `REDRAFT`, `REJECT` |
| **ProposalBio Last Analyzed** | Date & time | Include time, Use GMT |
| **ProposalBio Gate** | Single select | Options: `LOCKED`, `UNLOCKED` |
| **ProposalBio Biohack Scores JSON** | Long text | Enable rich text: No |
| **ProposalBio Critical Issues JSON** | Long text | Enable rich text: No |
| **ProposalBio Priority Improvements JSON** | Long text | Enable rich text: No |
| **ProposalBio Revision Count** | Number | Integer, Default: 0 |
| **ProposalBio Approved By** | Single line text | |
| **ProposalBio Approved Date** | Date & time | Include time, Use GMT |
| **Agency Type** | Single select | Options: `Federal`, `State`, `Local`, `Cooperative` |
| **Region** | Single select | Options: `Northeast`, `Mid_Atlantic`, `Southeast`, `Midwest`, `Southwest`, `West_Coast` |
| **RFP Text** | Long text | (Optional) For familiarity analysis |

### Color Coding Recommendations:
- Set **ProposalBio Gate** `LOCKED` to red, `UNLOCKED` to green
- Set **ProposalBio Status** `APPROVED` to green, `REVISE` to yellow, `REDRAFT` to orange, `REJECT` to red

---

## STEP 2: Create "GPSS ProposalBio Scores" Table

Create a new table called **GPSS ProposalBio Scores** with these fields:

| Field Name | Field Type | Configuration |
|------------|------------|---------------|
| **Proposal** | Link to another record | Link to `GPSS Proposals` table |
| **Revision** | Number | Integer (tracks which revision this score is for) |
| **Biohack Number** | Number | Integer (1-10) |
| **Biohack Name** | Single line text | |
| **Score** | Number | Precision: 2 decimals |
| **PassFail** | Single select | Options: `Pass`, `Fail` |
| **Details JSON** | Long text | (Optional, for future expansion) |
| **Recommendations** | Long text | (Optional, for future expansion) |
| **Analyzed Date** | Date & time | Include time, Use GMT |

### Views to Create:
1. **All Scores** - Default view, sort by Analyzed Date (newest first)
2. **Failed Biohacks** - Filter: PassFail = `Fail`, Group by: Biohack Name
3. **By Proposal** - Group by: Proposal

---

## STEP 3: Create "GPSS ProposalBio Learning" Table (Adaptive Learning)

Create a new table called **GPSS ProposalBio Learning** with these fields:

| Field Name | Field Type | Configuration |
|------------|------------|---------------|
| **Proposal** | Link to another record | Link to `GPSS Proposals` table |
| **Outcome** | Single select | Options: `Won`, `Lost`, `No Decision` |
| **Win Value** | Currency | Format: USD |
| **Agency Type** | Single select | Options: `Federal`, `State`, `Local`, `Cooperative` |
| **Region** | Single select | Options: `Northeast`, `Mid_Atlantic`, `Southeast`, `Midwest`, `Southwest`, `West_Coast` |
| **Composite Score** | Number | Precision: 2 decimals |
| **Biohack 1** | Number | Precision: 2 decimals (Mirror Neuron score) |
| **Biohack 2** | Number | Precision: 2 decimals (Cognitive Ease score) |
| **Biohack 3** | Number | Precision: 2 decimals (Story Arc score) |
| **Biohack 4** | Number | Precision: 2 decimals (Reciprocity score) |
| **Biohack 5** | Number | Precision: 2 decimals (Yes Stacking score) |
| **Biohack 6** | Number | Precision: 2 decimals (Familiarity score) |
| **Biohack 7** | Number | Precision: 2 decimals (Name Recognition score) |
| **Biohack 8** | Number | Precision: 2 decimals (Sensory Language score) |
| **Biohack 9** | Number | Precision: 2 decimals (Rhythm score) |
| **Biohack 10** | Number | Precision: 2 decimals (Eye Tracking score) |
| **Recorded Date** | Date & time | Include time, Use GMT |

### Views to Create:
1. **Won Proposals** - Filter: Outcome = `Won`, Sort by: Win Value (descending)
2. **Lost Proposals** - Filter: Outcome = `Lost`
3. **By Agency Type** - Group by: Agency Type
4. **By Region** - Group by: Region
5. **High Scorers (Won)** - Filter: Outcome = `Won` AND Composite Score ≥ 90

### Purpose:
This table tracks win/loss outcomes with their corresponding ProposalBio scores. Over time, you can analyze which biohacks correlate most with wins and adjust strategies accordingly (adaptive learning).

---

## STEP 4: Optional Enhancement - Add to Existing Tables

### In "Opportunities" Table (if not already present):
| Field Name | Field Type | Configuration |
|------------|------------|---------------|
| **Agency Type** | Single select | Options: `Federal`, `State`, `Local`, `Cooperative` |
| **Region** | Single select | Options: `Northeast`, `Mid_Atlantic`, `Southeast`, `Midwest`, `Southwest`, `West_Coast` |

This allows metadata to flow automatically from Opportunity → Proposal → ProposalBio analysis.

---

## STEP 5: Verify Setup

### Quick Test Checklist:
1. ✅ **GPSS Proposals** table has all ProposalBio fields
2. ✅ **GPSS ProposalBio Scores** table exists with Proposal link
3. ✅ **GPSS ProposalBio Learning** table exists
4. ✅ All single select fields have correct options
5. ✅ Date fields are set to include time + GMT
6. ✅ Number fields have correct precision (2 decimals)

### Test the System:
1. Create a test proposal in **GPSS Proposals**
2. Fill in Executive Summary, Technical Approach, etc.
3. Set **Agency Type** and **Region**
4. From your frontend, click "Run ProposalBio™"
5. Verify scores appear in:
   - The proposal modal (frontend)
   - **GPSS Proposals** table (ProposalBio fields populated)
   - **GPSS ProposalBio Scores** table (10 records created, one per biohack)

---

## Regional Definitions

### Northeast
States: NY, NJ, CT, MA, RI, NH, VT, ME, PA  
**Style:** Direct, fast-paced, data-heavy

### Mid_Atlantic
States: DC, MD, VA, WV, DE  
**Style:** Policy-focused, formal (federal influence)

### Southeast
States: FL, GA, SC, NC, TN, AL, MS, LA, AR, KY  
**Style:** Relationship-oriented, warm

### Midwest
States: OH, MI, IN, IL, WI, MN, IA, MO, ND, SD, NE, KS  
**Style:** Practical, straightforward, humble

### Southwest
States: TX, OK, NM, AZ  
**Style:** Confident, independent, results-oriented

### West_Coast
States: CA, WA, OR, NV, HI, AK  
**Style:** Collaborative, innovation-focused

---

## Adaptive Learning Workflow

Once you have proposals with outcomes:

### 1. Record Outcomes
After a proposal is awarded or lost:
```
POST /gpss/proposalbio/outcome
{
  "proposal_id": "recXXXXX",
  "outcome": "Won",
  "win_value": 1500000
}
```

This automatically:
- Records the outcome in **GPSS ProposalBio Learning**
- Captures all 10 biohack scores with the outcome
- Associates with Agency Type and Region

### 2. Analyze Patterns (Future Enhancement)
After 20+ outcomes recorded:
- Run correlation analysis: which biohacks predict wins?
- Adjust scoring weights per agency type/region
- Identify your "winning formula"

Example insights you might discover:
- "For Federal agencies, Biohack #2 (Cognitive Ease) correlates 0.85 with wins"
- "For Southeast regions, Biohack #1 (Mirror Neuron) is crucial"
- "Proposals scoring 90+ have 67% win rate vs 23% for scores 60-75"

---

## Support & Troubleshooting

### Common Issues:

**1. "Analysis fails with 'Proposal not found'"**
- Solution: Make sure you're using the Airtable record ID (starts with "rec...")

**2. "Scores not appearing in Airtable"**
- Solution: Check your `.env` file has correct `AIRTABLE_BASE_ID`
- Solution: Verify field names match exactly (case-sensitive)

**3. "Can't create scores in GPSS ProposalBio Scores table"**
- Solution: Ensure the "Proposal" field is properly linked to GPSS Proposals table
- Solution: Check that linked record field allows linking to multiple records

**4. "Region/Agency Type not showing in analysis"**
- Solution: Make sure these fields are filled in the proposal or opportunity record
- Solution: You can pass them in metadata override when calling the API

---

## Next Steps

Once your Airtable is set up:

1. **Test with a sample proposal** - Generate a proposal and run ProposalBio analysis
2. **Review the 10 biohack scores** - Understand what each biohack measures
3. **Make improvements** - Use the priority improvements list to enhance proposals
4. **Record outcomes** - As proposals win/lose, record outcomes for learning
5. **Iterate** - Each analysis teaches the system what works for your division

---

## Quick Reference: The 10 Biohacks

1. **Mirror Neuron** - Regional and agency tone matching
2. **Cognitive Ease** - Reading level, simplicity, white space
3. **Story Arc** - Challenge-solution-result narratives
4. **Reciprocity** - Give-first value (insights, checklists)
5. **Yes Stacking** - Affirming statements before asks
6. **Familiarity** - RFP language mirroring
7. **Name Recognition** - Agency name frequency and placement
8. **Sensory Language** - Concrete vs vague terms
9. **Rhythm** - Sentence variety and cadence
10. **Eye Tracking** - Visual hierarchy, headings, white space

Target: **75/100 composite score to unlock submission**

---

**Estimated Setup Time:** 30-40 minutes

**Last Updated:** January 15, 2026

**Questions?** Check the main ProposalBio documentation or contact GPSS support.
