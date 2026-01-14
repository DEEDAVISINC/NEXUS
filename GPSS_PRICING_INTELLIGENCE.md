# GPSS INTELLIGENT PRICING SYSTEM

## 📋 **PRICING INTELLIGENCE AIRTABLE SCHEMA**

### **TABLE: Pricing History**
Track all bids, wins, and pricing data for intelligent future pricing.

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Pricing ID** | Auto-number | PRIMARY FIELD - Auto-generated |
| **Opportunity** | Link to another record | Link to "Opportunities" table |
| **Proposal** | Link to another record | Link to "GPSS Proposals" table |
| **Contract Type** | Single select | Options: `Fixed Price`, `Time & Materials`, `Cost Plus`, `IDIQ`, `BPA` |
| **Service Category** | Single select | Options: `NEMT`, `Medical Transport`, `Healthcare IT`, `Consulting`, `Staffing`, `Facilities`, `Professional Services` |
| **Total Bid Amount** | Currency | Total amount we bid |
| **Estimated Costs** | Currency | Our internal cost estimate |
| **Labor Costs** | Currency | Staff/contractor costs |
| **Materials Costs** | Currency | Equipment, supplies, etc. |
| **Overhead Rate** | Percent | Company overhead % |
| **Profit Margin** | Percent | Desired profit margin |
| **Calculated Profit** | Formula | `{Total Bid Amount} - {Estimated Costs}` |
| **Actual Profit Margin %** | Formula | `({Calculated Profit} / {Total Bid Amount}) * 100` |
| **Competitor Count** | Number | How many competitors bid |
| **Winning Bid Amount** | Currency | What the winner bid (if we lost) |
| **Our Rank** | Number | Where we placed (1 = won) |
| **Win/Loss** | Single select | Options: `Won`, `Lost`, `Pending`, `No Bid` |
| **Win Probability Score** | Number | AI-calculated win probability (0-100) |
| **Price Competitiveness** | Formula | `({Total Bid Amount} / {Winning Bid Amount}) * 100` |
| **Market Rate ($/hr or $/unit)** | Currency | Industry standard rate |
| **Our Rate ($/hr or $/unit)** | Currency | Our proposed rate |
| **Rate Variance %** | Formula | `(({Our Rate} - {Market Rate}) / {Market Rate}) * 100` |
| **Contract Duration (months)** | Number | Length of contract |
| **Annual Value** | Formula | `{Total Bid Amount} / ({Contract Duration} / 12)` |
| **Agency** | Single line text | From linked Opportunity |
| **Set-Aside Type** | Single select | `EDWOSB`, `8(a)`, `HUBZone`, `SDVOSB`, `Unrestricted` |
| **Geographic Region** | Single select | `Federal`, `MI`, `OH`, `IL`, `IN`, `WI`, `Other` |
| **Bid Date** | Date | When we submitted |
| **Award Date** | Date | When contract was awarded |
| **Pricing Strategy Used** | Single select | `Aggressive`, `Competitive`, `Premium`, `Cost-Plus`, `Market Rate` |
| **Pricing Notes** | Long text | Why we priced this way |
| **Lessons Learned** | Long text | What worked, what didn't |
| **AI Pricing Recommendation** | Long text | What AI suggested |
| **Followed AI Recommendation** | Checkbox | Did we use AI pricing? |
| **Created Date** | Created time | Auto-generated |

---

### **TABLE: Cost Templates**
Reusable cost templates for different service types.

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Template ID** | Auto-number | PRIMARY FIELD |
| **Template Name** | Single line text | e.g., "NEMT - Full Service" |
| **Service Category** | Single select | Same as Pricing History |
| **Base Hourly Rate** | Currency | Starting rate per hour |
| **Labor Cost per Hour** | Currency | What we pay staff |
| **Materials Cost %** | Percent | % of total for materials |
| **Overhead Rate %** | Percent | Company overhead |
| **Target Profit Margin %** | Percent | Desired profit |
| **Minimum Margin %** | Percent | Lowest acceptable |
| **Vehicles Required** | Number | For NEMT |
| **Staff Required** | Number | FTE count |
| **Certifications Needed** | Long text | Required certs |
| **Typical Contract Duration** | Number | Months |
| **Pricing Formula** | Long text | How to calculate |
| **Last Updated** | Last modified time | Auto-generated |
| **Times Used** | Number | How many times applied |
| **Win Rate %** | Number | Success rate with this template |

---

### **TABLE: Market Intelligence**
Track competitor pricing and market rates.

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Intelligence ID** | Auto-number | PRIMARY FIELD |
| **Service Type** | Single select | Same categories |
| **Geographic Region** | Single select | Where this applies |
| **Market Rate (Low)** | Currency | Lowest seen in market |
| **Market Rate (Average)** | Currency | Typical market rate |
| **Market Rate (High)** | Currency | Premium pricing |
| **Data Source** | Single line text | Where we got this info |
| **Competitor Name** | Single line text | If known |
| **Date Observed** | Date | When we collected this |
| **Contract Size** | Single select | `Small (<$250K)`, `Medium ($250K-$1M)`, `Large ($1M-$10M)`, `Mega (>$10M)` |
| **Set-Aside Type** | Single select | Same as above |
| **Notes** | Long text | Additional context |
| **Confidence Level** | Single select | `High`, `Medium`, `Low` |
| **Last Verified** | Date | Last time we confirmed |

---

## 🎯 **VIEWS TO CREATE:**

### Pricing History:
1. **All Bids** - Default view
2. **Wins Only** - Filter: Win/Loss = Won
3. **Losses Only** - Filter: Win/Loss = Lost
4. **Pending Bids** - Filter: Win/Loss = Pending
5. **High Win Rate** - Filter: Win Probability > 70
6. **By Service Category** - Group by Service Category
7. **Profitability Analysis** - Sort by Actual Profit Margin % (descending)

### Cost Templates:
1. **All Templates** - Default
2. **High Win Rate** - Win Rate > 60%
3. **By Service** - Group by Service Category

### Market Intelligence:
1. **All Data** - Default
2. **Recent (Last 6 Months)** - Filter: Date Observed > 6 months ago
3. **By Region** - Group by Geographic Region
4. **By Service** - Group by Service Type
5. **High Confidence** - Filter: Confidence Level = High

---

## 🤖 **INTELLIGENT PRICING ENGINE - AI LOGIC:**

### **1. Data Inputs:**
- Historical bid/win data
- Cost templates
- Market intelligence
- Opportunity details (size, location, set-aside, urgency)
- Competitor analysis
- Company financial goals

### **2. Pricing Calculations:**

```python
Intelligent Price = Base Cost × (1 + Overhead Rate) × (1 + Target Margin) × Competition Factor × Win Probability Adjustment

Where:
- Base Cost = Labor + Materials + Subcontractors
- Competition Factor = 0.85 (many competitors) to 1.15 (few competitors)
- Win Probability Adjustment = Optimize for win rate vs. profit
```

### **3. Pricing Strategies:**

| Strategy | Use When | Multiplier |
|----------|----------|-----------|
| **Aggressive** | Must-win, high competition | 0.90-0.95 (lower price) |
| **Competitive** | Standard bid, medium competition | 0.95-1.05 (market rate) |
| **Premium** | Unique capability, low competition | 1.05-1.15 (higher price) |
| **Cost-Plus** | Government cost-plus contracts | Actual costs + fixed fee |
| **Market Rate** | Unknown market, play it safe | Exact market average |

### **4. Win Probability Model:**

```
Win Probability = f(
  Price Competitiveness,
  Past Win Rate in Category,
  Set-Aside Eligibility,
  Home State Advantage,
  Technical Score Estimate,
  Relationship with Agency
)
```

### **5. Pricing Recommendations:**

The AI will output:
- **Recommended Bid Range:** $X - $Y
- **Optimal Price:** $Z (highest probability × profit)
- **Win Probability:** % at recommended price
- **Expected Profit:** $ and %
- **Risk Assessment:** Low/Medium/High
- **Pricing Rationale:** Why this price was chosen
- **Competitive Position:** How we compare to market
- **Alternative Scenarios:** "If you bid $X, win probability is Y%"

---

## 📊 **PRICING DASHBOARD FEATURES:**

1. **Win Rate by Price Point** - Chart showing price vs. win rate
2. **Profit Margin Analysis** - Which bids were most profitable
3. **Market Position** - Are we typically high/low bidder?
4. **Category Performance** - Which service types are most profitable
5. **Pricing Accuracy** - How often AI recommendations win
6. **Cost Trending** - Are our costs increasing?
7. **Competitive Intelligence** - Who are we losing to and why

---

## ⚡ **QUICK START CHECKLIST:**

- [ ] Create **Pricing History** table in Airtable
- [ ] Create **Cost Templates** table in Airtable
- [ ] Create **Market Intelligence** table in Airtable
- [ ] Build **AI Pricing Agent** in backend
- [ ] Add **Pricing Calculator UI** to GPSS
- [ ] Integrate pricing intelligence into **Proposal Generation**
- [ ] Create **Pricing Analytics Dashboard**
- [ ] Import historical bid data (if available)
- [ ] Set up cost templates for common services
- [ ] Train AI on initial market intelligence

---

## 🎯 **ESTIMATED TIME:**
- Airtable Setup: 20-30 minutes
- AI Pricing Agent: 30-40 minutes
- Frontend UI: 40-50 minutes
- Integration & Testing: 20-30 minutes

**Total: ~2.5 hours for full intelligent pricing system**

---

## 💡 **FUTURE ENHANCEMENTS:**

1. **Real-time Market Data** - Web scraping of SAM.gov awards
2. **Competitor Database** - Track who wins what
3. **Cost Inflation Tracking** - Adjust for economic changes
4. **Seasonal Pricing** - Account for seasonal demand
5. **Multi-year Contract Modeling** - Price options
6. **Risk-Adjusted Pricing** - Factor in delivery risk
7. **Bundle Pricing** - Multiple services together
8. **Dynamic Pricing** - Adjust as deadline approaches

