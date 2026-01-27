# 🎯 SUPPLIER QUOTE REQUEST - QUICK GUIDE

**Get quotes from suppliers to price your government bids!**

---

## 🚨 CRITICAL: Protect Your Client!

**NEVER include in your supplier quote requests:**
- ❌ Government agency names (Canton Township, City of Detroit, etc.)
- ❌ Solicitation numbers (RFQ-123456, ITB-789, etc.)
- ❌ Procurement officer names
- ❌ Specific delivery addresses
- ❌ That it's a "government contract"

**Instead say:**
- ✅ "Michigan municipal client"
- ✅ "Metro Detroit area"
- ✅ "Southeast Michigan client"
- ✅ "Government client"

**Why?** If suppliers know the end buyer, they can bid directly and cut you out!

---

## ✅ How It Works

### Your Workflow:
1. **See government solicitation** (e.g., Canton needs water pipes)
2. **Request quotes from suppliers** ← THIS TOOL
3. **Get supplier pricing** (e.g., Ferguson quotes you $50K)
4. **Add your margin** (e.g., quote Canton $55K)
5. **Submit your bid** and win!

---

## 🚀 3 Simple Steps

### Step 1: Edit the Template
```bash
cd "/Users/deedavis/NEXUS BACKEND"
open -e supplier_quote_request_template.txt
```

**Fill in:**
- Your RFQ tracking number
- Brief generic title (no client names!)
- When you need quotes by
- The items from the solicitation

### Step 2: Generate the Quote Request
```bash
python3 create_from_paste.py rfq supplier_quote_request_template.txt
```

### Step 3: Send to Suppliers
You get a professional PDF to email to:
- Grainger
- Fastenal
- Ferguson
- HD Supply
- Your other suppliers

---

## 📝 Real Example

### You See This Solicitation:
> **Canton Township RFQ-2026-WTR-003**
> Water Infrastructure Supplies Needed
> - 2" Copper Tubing Type K - 500 feet
> - 2" Brass Fittings - 100 pieces
> - Gate Valves 2" - 50 pieces
> Due: February 15, 2026

### Your Supplier Quote Request Says:
```
RFQ_NUMBER: DDI-2026-WTR-001
TITLE: Plumbing Supplies for Municipal Project
ISSUE_DATE: January 26, 2026
DUE_DATE: February 2, 2026
DUE_TIME: 5:00 PM EST
CONTRACT_PERIOD: Immediate delivery

COLOR_SCHEME: 1

INTRODUCTION:
DEE DAVIS INC is preparing a bid for a Michigan municipal water infrastructure project. We need competitive quotes for the items below by February 2nd.

SCOPE:
We need firm pricing and availability for all items. Delivery would be to Southeast Michigan. Please provide your best pricing for this competitive opportunity.

KEY_REQUIREMENTS:
- Competitive pricing essential
- Confirm availability and lead times
- Delivery terms to Metro Detroit
- Payment terms

ITEMS:
1 | Copper Tubing Type K | 2" diameter, hard drawn | 500 feet | foot
2 | Brass Fittings | 2" compression fittings | 100 pieces | piece
3 | Gate Valves | 2" brass gate valves | 50 pieces | piece
```

**Notice:** No mention of Canton Township! ✅

---

## 💡 Smart Pricing Strategy

### What to Ask Suppliers:
1. **Unit pricing** - Per foot, per piece, per unit
2. **Volume discounts** - Can they do better for larger orders?
3. **Delivery terms** - FOB Destination preferred (they pay freight)
4. **Lead time** - How fast can they deliver?
5. **Payment terms** - Net 30? Net 60?
6. **Minimum orders** - Any minimum quantity requirements?

### Your Math:
```
Supplier quote: $50,000
Your margin: +10% = $5,000
Your bid: $55,000
```

**The solicitation is due Feb 15, so you need supplier quotes by Feb 2 to build your bid!**

---

## 🎯 Quick Commands

### Create Your Quote Request:
```bash
cd "/Users/deedavis/NEXUS BACKEND"
open -e supplier_quote_request_template.txt
# Edit with your items, save
python3 create_from_paste.py rfq supplier_quote_request_template.txt
# Email the PDF to suppliers!
```

### Send to Multiple Suppliers:
Email the generated PDF to:
- supplier1@grainger.com
- quotes@fastenal.com
- ferguson-quotes@ferguson.com
- etc.

**Get 3-5 quotes for competitive pricing!**

---

## 📋 Template Format

### ITEMS Section:
```
ITEMS:
1 | What it is | Exact specs from solicitation | Quantity | unit
2 | Another item | Specs | Qty | unit
```

**Copy items directly from the government solicitation!**

---

## ⚡ Speed Tips

### Tip 1: Template by Category
Save templates for common purchases:
```bash
cp supplier_quote_request_template.txt plumbing_template.txt
cp supplier_quote_request_template.txt electrical_template.txt
cp supplier_quote_request_template.txt cleaning_template.txt
```

### Tip 2: Know Your Suppliers
Keep a list of go-to suppliers for each category:
- **Plumbing:** Ferguson, HD Supply
- **Electrical:** Grainger, Graybar
- **Industrial:** Fastenal, MSC Industrial
- **Cleaning:** Unisource, Imperial Dade

### Tip 3: Faster Due Dates
Government bid due in 2 weeks? Ask suppliers for quotes in 1 week. Gives you time to build your bid!

---

## 🎨 Color Schemes

Pick what matches the solicitation:
- **1 = Navy/Gold** - General industrial, municipal
- **2 = Brown/Orange** - Construction, heavy equipment
- **3 = Purple/Violet** - Technology, IT equipment
- **4 = Blue/Teal** - Healthcare, medical supplies
- **5 = Dark Brown** - Building materials, aggregates

---

## ✅ What Suppliers Get

Your professional PDF includes:
- ✅ Clear RFQ number (your tracking number)
- ✅ Generic description (no client names)
- ✅ Exact specifications from solicitation
- ✅ When you need quotes
- ✅ Your company contact info
- ✅ Professional appearance

**Suppliers take you seriously = better pricing!**

---

## 🚨 Common Mistakes to Avoid

### ❌ DON'T:
```
Subject: Canton Township Water Bid - Need Quotes
We're bidding on Canton's RFQ-2026-WTR-003...
```
**Supplier looks up Canton's bid and submits directly!**

### ✅ DO:
```
Subject: Municipal Water Project - Quote Request
We have a Michigan municipal water infrastructure project...
```
**Supplier gives you pricing, you add margin, you win!**

---

## 📞 Sample Email to Suppliers

```
Subject: Quote Request - Municipal Water Infrastructure

Hi [Supplier Contact],

DEE DAVIS INC is preparing a bid for a Michigan municipal water 
infrastructure project. We need competitive pricing for the attached 
items by February 2nd.

Please see attached RFQ for full specifications and quantities.

Can you provide:
- Unit pricing for all items
- Lead times and availability
- Delivery terms to Metro Detroit area
- Payment terms

Looking forward to your competitive quote!

Best regards,
Dee Davis
DEE DAVIS INC
248-376-4550
info@deedavis.biz

Attachment: rfq_ddi_2026_wtr_001.pdf
```

---

## 💼 Real Business Example

### Government Solicitation:
- **Canton Township** needs $50K in water supplies
- Due: February 15, 2026

### Your Process:
1. **Jan 26:** See the solicitation
2. **Jan 26:** Request quotes from 4 suppliers (THIS TOOL)
3. **Feb 2:** Get supplier quotes back
4. **Feb 5:** Build your bid with markup
5. **Feb 12:** Submit to Canton
6. **Feb 20:** Win the contract! 🎉

**This tool does step 2 in 1 minute!**

---

## 🎯 Try It Now!

```bash
cd "/Users/deedavis/NEXUS BACKEND"
open -e supplier_quote_request_template.txt
```

1. Replace "Item description" with real items from your solicitation
2. Set due date (give yourself time before solicitation deadline!)
3. Save the file
4. Run: `python3 create_from_paste.py rfq supplier_quote_request_template.txt`
5. Email the PDF to your suppliers!

**Get competitive quotes = Win more bids = More revenue!** 🚀

---

**Remember: Protect your client identity = Protect your margins!**
