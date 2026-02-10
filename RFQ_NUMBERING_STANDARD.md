# RFQ NUMBERING STANDARD
**Date Created:** February 4, 2026  
**Status:** MANDATORY - All RFQ generators MUST use this format

---

## STANDARD FORMAT

**All RFQs must follow this format:**

```
DDI-[YEAR]-[###]
```

### Components:
- **DDI** = Dee Davis Inc. (company prefix)
- **YEAR** = 4-digit year (e.g., 2026)
- **###** = Sequential 3-digit number (001, 002, 003, etc.)

**Simple sequential numbering - system just increments a counter. No product names, no buyer info, just a tracking number.**

---

## EXAMPLES

### ✅ CORRECT FORMAT:
- `DDI-2026-001` ✅ (First RFQ of 2026)
- `DDI-2026-002` ✅ (Second RFQ of 2026)
- `DDI-2026-003` ✅ (Third RFQ of 2026)
- `DDI-2026-004` ✅ (Fourth RFQ of 2026)

### ❌ INCORRECT FORMATS:
- `DDI-2026-TRUCKS-001` ❌ (Too complex - system needs to track product types)
- `DDI-2026-RCOC-001` ❌ (Reveals buyer!)
- `DDI-2026-GENESEE-001` ❌ (Reveals buyer!)
- `DDI-GENESEE-2026-001` ❌ (Wrong format + reveals buyer!)

---

## NUMBERING SEQUENCE

**Simple sequential numbering - one counter for everything:**

- `DDI-2026-001` (First RFQ generated)
- `DDI-2026-002` (Second RFQ generated)
- `DDI-2026-003` (Third RFQ generated)
- `DDI-2026-004` (Fourth RFQ generated)
- etc.

**System just tracks ONE number and auto-increments. Simple!**

**Track the current number in:** `RFQ_NUMBER_TRACKER.md`

---

## IMPLEMENTATION

**All RFQ generator scripts MUST:**
1. Follow this exact format
2. Include RFQ number prominently in PDF header
3. Reference RFQ number in filename
4. Track RFQ numbers in NEXUS system

---

## WHY THIS MATTERS

**Simplicity:**
- ✅ System just increments one counter
- ✅ No need to track product categories
- ✅ No complexity in RFQ generators
- ✅ Easy to implement and maintain

**Business Protection:**
- 🚨 **NEVER reveal client names** - No RCOC, Canton, Genesee, etc.
- 🚨 **NEVER reveal locations** - No city/county names
- 🚨 **NEVER reveal specific agencies** - Suppliers could contact them directly
- ✅ Generic numbers reveal nothing about the project or buyer

**Simple sequential = Easy to automate + Maximum security!**

---

## ENFORCEMENT

**Before generating any RFQ:**
1. Check this standard
2. Use the correct format
3. Verify in the generated PDF
4. Update tracking systems

**If you see an RFQ with wrong format → STOP and fix it before sending!**

---

*This is a mandatory standard. No exceptions.*

---

**Created:** February 4, 2026  
**Last Updated:** February 4, 2026  
**Status:** ACTIVE - ENFORCE IMMEDIATELY
