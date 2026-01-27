# NEXUS PRICING AUTOMATION - SIMPLE & DIRECT

**One input → One output. No fluff.**

---

## 🎯 THE GOAL

User provides:
1. Supplier quote (cost)
2. Markup % (18%, 20%, etc.)

NEXUS returns:
- Your bid prices
- Extended totals
- Profit
- Done.

**No menus. No options. No "would you like to...?"**

---

## 📊 HOW IT WORKS

### **Input:**
```json
{
  "items": [
    {"name": "Item 010", "quantity": 750, "unit": "RL", "cost": 114.81},
    {"name": "Item 020", "quantity": 8850, "unit": "BX", "cost": 22.92},
    {"name": "Item 030", "quantity": 4200, "unit": "BX", "cost": 31.02}
  ],
  "markup_percent": 18
}
```

### **Output:**
```json
{
  "bid_prices": [
    {"item": "Item 010", "bid_price": 135.48, "unit": "RL", "extended": 101610.00},
    {"item": "Item 020", "bid_price": 27.05, "unit": "BX", "extended": 239392.50},
    {"item": "Item 030", "bid_price": 36.60, "unit": "BX", "extended": 153720.00}
  ],
  "total_cost": 419233.50,
  "total_bid": 494722.50,
  "total_profit": 75489.00
}
```

**That's it.** No explanations. User gets the numbers.

---

## 🔧 API ENDPOINT

### **POST /pricing/calculate**

**Request:**
```json
{
  "opportunity_id": "recXXXXXXX",
  "markup_percent": 18
}
```

**Response:**
```json
{
  "item_010": "$135.48 per RL",
  "item_020": "$27.05 per BX",
  "item_030": "$36.60 per BX",
  "total_bid": "$494,722.50",
  "profit": "$75,489.00"
}
```

**No status messages. No "calculating...". Just results.**

---

## 📝 AIRTABLE INTEGRATION

### **Opportunities Table - New Fields:**

| Field Name | Type | Formula/Purpose |
|------------|------|-----------------|
| `Supplier Cost` | Currency | Manual entry |
| `Markup Percent` | Number | Manual entry (18, 20, 25, etc.) |
| `Your Bid Price` | Currency | Auto-calculated |
| `Your Profit` | Currency | Auto-calculated |

### **Auto-Calculation Button:**

**Button Name:** "Calculate Pricing"

**Script:**
```javascript
// Gets supplier cost and markup %
// Calls NEXUS API
// Updates bid price fields
// Done in 1 click
```

**User sees:**
- Click button
- Numbers appear
- Done

---

## 💻 SIMPLE PYTHON FUNCTION

```python
def calculate_bid_pricing(items, markup_percent):
    """
    Calculate bid pricing with markup.
    
    Args:
        items: List of {"quantity": int, "cost": float}
        markup_percent: Integer (18 for 18%)
    
    Returns:
        Dict with bid prices and totals
    """
    results = []
    total_cost = 0
    total_bid = 0
    
    for item in items:
        cost = item["cost"]
        bid_price = round(cost * (1 + markup_percent/100), 2)
        extended = round(bid_price * item["quantity"], 2)
        
        results.append({
            "bid_price": bid_price,
            "extended": extended
        })
        
        total_cost += cost * item["quantity"]
        total_bid += extended
    
    return {
        "items": results,
        "total_cost": round(total_cost, 2),
        "total_bid": round(total_bid, 2),
        "profit": round(total_bid - total_cost, 2)
    }
```

**Usage:**
```python
items = [
    {"quantity": 750, "cost": 114.81},
    {"quantity": 8850, "cost": 22.92},
    {"quantity": 4200, "cost": 31.02}
]

result = calculate_bid_pricing(items, 18)
print(result)
```

**Output:**
```
{
  "total_bid": 494722.50,
  "profit": 75489.00
}
```

Done.

---

## 🎨 UI/UX - NEXUS FRONTEND

### **Pricing Calculator Screen:**

```
┌─────────────────────────────────────────┐
│ PRICING CALCULATOR                      │
├─────────────────────────────────────────┤
│                                         │
│ Opportunity: CPS Energy RFQ 7000205103  │
│                                         │
│ Supplier Cost:    $419,233.50          │
│ Markup Percent:   18%                   │
│                                         │
│         [CALCULATE]                     │
│                                         │
│ ─────────────────────────────────────  │
│                                         │
│ YOUR BID:         $494,722.50          │
│ YOUR PROFIT:      $75,489.00           │
│                                         │
│ Item 010:  $135.48 per RL              │
│ Item 020:  $27.05 per BX               │
│ Item 030:  $36.60 per BX               │
│                                         │
│    [COPY TO BID FORM]                  │
└─────────────────────────────────────────┘
```

**Interaction:**
1. User enters cost and markup
2. Clicks "Calculate"
3. Numbers appear
4. User clicks "Copy to Bid Form"
5. Done

**No:**
- "Are you sure?"
- "Would you like to see alternatives?"
- "Compare different markups?"
- Progress bars
- Loading animations for instant calculations

---

## 🚀 QUICK ACTIONS

### **From Opportunities Table:**

**Right-click menu:**
```
▸ Calculate Pricing (18% markup)
▸ Calculate Pricing (20% markup)
▸ Calculate Pricing (25% markup)
▸ Calculate Pricing (custom...)
```

**Click one → Numbers update → Done.**

---

## 📱 MAKE.COM AUTOMATION

### **Scenario: "New Supplier Quote Received"**

**Trigger:** Email with supplier quote arrives

**Actions:**
1. Extract pricing from email
2. Get markup % from Opportunities record
3. Calculate bid pricing
4. Update Airtable
5. Done

**No notifications. No confirmations. Just updates.**

---

## 💡 SMART DEFAULTS

### **Markup % by Opportunity Type:**

| Type | Default Markup |
|------|----------------|
| Industrial Supplies | 18% |
| Construction | 25% |
| Services | 30% |
| Products | 20% |

**NEXUS auto-suggests based on NAICS code.**

User can override. One click.

---

## 📋 BID FORM AUTO-FILL

### **After pricing calculation:**

**Button:** "Fill Bid Form"

**What happens:**
1. Opens RFQ PDF
2. Fills all pricing fields automatically
3. Fills company info automatically
4. User reviews
5. User clicks "Save"
6. Done

**Time saved:** 15 minutes → 30 seconds

---

## 🔄 PRICING VERSIONS

### **Track Multiple Pricing Scenarios:**

```
Opportunity: CPS Energy
├─ Version 1: 18% markup → $494,722
├─ Version 2: 20% markup → $503,080
└─ Version 3: 15% markup → $482,118
```

**User clicks version → Switches instantly → No recalculation needed**

---

## 📊 PROFIT CALCULATOR

### **Quick View:**

```
Supplier Cost:    $419,233.50
Your Bid:         $494,722.50
Margin:           18%
Profit:           $75,489.00

Over 3 years:     $25,163/year
Per month:        $2,097/month
```

**Automatic. No extra clicks.**

---

## ⚡ SPEED REQUIREMENTS

| Action | Max Time |
|--------|----------|
| Calculate pricing | < 100ms |
| Update Airtable | < 500ms |
| Fill PDF form | < 2 seconds |
| Load pricing screen | < 300ms |

**If it takes longer, something's wrong.**

---

## 🎯 USER FLOW - COMPLETE BID

### **From Start to Submit:**

1. **User opens opportunity** → Sees "Calculate Pricing" button
2. **User enters supplier cost** → Types $419,233.50
3. **User clicks "Calculate (18%)"** → Numbers appear instantly
4. **User clicks "Fill Bid Form"** → PDF opens with all fields filled
5. **User reviews** → Looks good
6. **User clicks "Generate Submission Email"** → Email draft appears
7. **User clicks "Send"** → Submitted

**Total time:** 3 minutes

**No:**
- Tutorial popups
- Confirmation dialogs (except for Send)
- "Are you sure?" messages
- Progress tracking
- Step counters

---

## 🔐 DATA VALIDATION

### **Simple Rules:**

- Markup % must be 5-50%
- Cost must be > $0
- Quantities must be positive integers

**If invalid:**
```
❌ Markup % must be between 5-50%
```

**Not:**
```
⚠️ Warning: The markup percentage you entered (2%) is below 
our recommended minimum of 5%. While you can proceed, this 
may result in insufficient profit margins to cover overhead 
and unexpected costs. Would you like to:
[ Adjust to 15% ] [ Adjust to 18% ] [ Continue anyway ]
```

---

## 📝 PRICING TEMPLATES

### **Save Common Markups:**

```
My Templates:
├─ Conservative (15%)
├─ Standard (18%)
├─ Aggressive (25%)
└─ Service (30%)
```

**Click template → Applied → Done.**

---

## 🎓 TEACHING OTHERS

### **Training Material:**

**What to teach:**
```
1. Enter supplier cost
2. Choose markup %
3. Click Calculate
4. Copy numbers to bid form
```

**4 steps. Anyone can learn in 2 minutes.**

---

## ✅ IMPLEMENTATION CHECKLIST

**Backend:**
- [ ] `/pricing/calculate` endpoint
- [ ] Markup calculation function
- [ ] Airtable integration
- [ ] Response time < 100ms

**Frontend:**
- [ ] Pricing calculator screen
- [ ] Copy to clipboard buttons
- [ ] Auto-fill bid form feature
- [ ] Markup templates

**Automation:**
- [ ] Make.com pricing scenario
- [ ] Email quote extraction
- [ ] Auto-update Airtable
- [ ] Generate submission emails

**Documentation:**
- [ ] 1-page quick start guide
- [ ] 4-step user flow diagram
- [ ] Video (< 2 minutes)

---

## 🚫 WHAT NOT TO BUILD

❌ Pricing "wizard" with multiple steps  
❌ "Compare different markup strategies" feature  
❌ Profit projections over 10 years  
❌ "AI-recommended pricing" that needs explanation  
❌ Settings panel with 20 options  
❌ Multiple confirmation dialogs  
❌ Tutorial mode that must be completed  

**If it slows the user down, don't build it.**

---

## 🎯 SUCCESS METRICS

**How to measure if NEXUS pricing is working:**

| Metric | Target |
|--------|--------|
| Time to calculate pricing | < 10 seconds |
| Time to complete bid form | < 5 minutes |
| User training time | < 3 minutes |
| Clicks to get bid price | ≤ 2 |
| User errors per bid | < 0.5 |

---

## 💬 USER FEEDBACK

**Good signs:**
- "That was fast"
- "Where did the numbers come from?" (they appeared so fast)
- "Can I use this for all bids?"

**Bad signs:**
- "How do I...?"
- "Where's the button for...?"
- "Why did it ask me...?"

**If users are confused, the UI is wrong.**

---

## 🔄 CONTINUOUS IMPROVEMENT

**After each bid:**
- Track time spent
- Count number of clicks
- Note any manual corrections
- Log any errors

**Monthly review:**
- Where do users spend time?
- Where do they get stuck?
- What can be automated?
- What can be removed?

**Goal: Fewer clicks, less time, less confusion.**

---

## 📞 SUPPORT

**If user asks: "How do I calculate pricing?"**

**Answer:**
```
1. Open opportunity
2. Enter supplier cost
3. Click "Calculate (18%)"
4. Copy numbers to bid form
```

**Not:**
```
Great question! NEXUS has a powerful pricing calculator 
that allows you to evaluate multiple markup scenarios...
[continues for 5 minutes]
```

---

## 🎯 REMEMBER

**Direct = Professional**  
**Fast = Valuable**  
**Simple = Teachable**

**If it takes more than 3 clicks, redesign it.**  
**If it takes more than 30 seconds, automate it.**  
**If it needs explanation, simplify it.**

---

*NEXUS Pricing: Calculate once. Use everywhere. No fluff.*
