# Subcontractor Outreach — Medical Courier (Ohio)

**Opportunity:** Medical specimen courier services, Columbus/Reynoldsburg area  
**Scope:** Transport time/temperature-sensitive specimens to state public health lab  
**Your Role:** EDWOSB/MBE Prime Contractor  
**Their Role:** Subcontractor (field operations — driving, pickup, delivery)

---

## Email Template

**Subject:** Medical Courier Partner Needed — Ohio Government Contract

---

Hi [Contact Name],

My name is Dee Davis with Dee Davis Inc. We're a certified EDWOSB and MBE based in Michigan, and we provide medical courier services for government and healthcare clients. We're expanding operations in Ohio and need a qualified local courier partner for specimen transport in the Columbus/Reynoldsburg area.

The work involves transporting medical specimens and lab supplies to a state public health laboratory — time-sensitive and temperature-controlled transport. We handle the contract management, compliance, invoicing, and government reporting. You would handle the field operations — pickups, deliveries, chain of custody, and vehicle maintenance.

If your company has experience with medical/clinical specimen transport, temperature-controlled vehicles, and the necessary insurance and licensing, I'd love to have a quick conversation about working together.

Feel free to reply here or give me a call.

Dee Davis  
Dee Davis Inc.  
info@deedavis.biz  
248.376.4550

---

## Companies to Contact

Run `automated_sub_sourcing.py` to find qualified Ohio medical couriers:

```bash
python3 automated_sub_sourcing.py find --service "medical courier" --location "Columbus, Ohio" --radius 50
```

This will:
- Search Google Maps and Yelp for medical couriers in the Columbus area
- Filter by rating (4.0+) and reviews (10+)
- **Automatically check USASpending.gov** to exclude any courier that already wins their own government contracts
- Save results to Airtable SUBCONTRACTORS table
- Generate outreach emails for each qualified sub

---

## What NOT to Share (Until NDA is Signed)

- ❌ Ohio Department of Health
- ❌ Bureau of Public Health Laboratory
- ❌ Solicitation number (SRC0000036969 or DOH59579)
- ❌ Specific contract value
- ❌ Contracting officer name
- ❌ March 5 deadline

## What's OK to Share

- ✅ "State public health laboratory in Ohio"
- ✅ "Columbus/Reynoldsburg area"
- ✅ "Medical specimen transport"
- ✅ "Time and temperature sensitive"
- ✅ "Multi-year contract"
- ✅ That DDI is the prime contractor (EDWOSB/MBE)

---

## Follow-Up Questions (If They Reply)

1. "Do you have temperature-controlled vehicles (refrigerated or insulated)?"
2. "What's your coverage area — can you handle Columbus and surrounding counties?"
3. "Have you transported medical specimens or lab samples before?"
4. "What insurance coverage do you carry? (We need $1M general liability + $1M commercial auto)"
5. "Are your drivers trained in bloodborne pathogen safety and chain of custody?"
6. "Can you provide a quote for scheduled daily routes plus on-demand pickups?"

---

## Subcontractor Requirements (Verify Before Engaging)

- [ ] Ohio business license
- [ ] DOT/MC number (if applicable)
- [ ] Temperature-controlled vehicles
- [ ] OSHA bloodborne pathogen training for drivers
- [ ] Chain of custody documentation capability
- [ ] $1M+ general liability insurance
- [ ] $1M+ commercial auto insurance
- [ ] Workers' compensation
- [ ] DEE DAVIS INC listed as Additional Insured on COI
- [ ] No competing government contracts on USASpending (auto-checked by system)

---

*Created: February 17, 2026*  
*Opportunity: Ohio DOH Medical Courier (MBE Set-Aside)*
