#!/usr/bin/env python3
"""
MULTI-YEAR PRICING CALCULATOR
For government contracts with base year + option years
"""

def calculate_multi_year_pricing(
    base_year_cost: float,
    num_years: int,
    escalation_percent: float = 3.0,
    markup_percent: float = 18.0,
    contract_type: str = "product"  # "product" or "service"
) -> dict:
    """
    Calculate pricing for multi-year government contracts with annual escalation.
    
    Args:
        base_year_cost: Supplier/subcontractor cost for base year
        num_years: Total number of years (including base year)
        escalation_percent: Annual cost increase % (default 3%)
        markup_percent: DDI markup % (default 18% for products, 10-15% for services)
        contract_type: "product" or "service" (affects default markup)
    
    Returns:
        Dict with year-by-year breakdown and totals
    
    Example:
        >>> calculate_multi_year_pricing(50000, 5, escalation_percent=3, markup_percent=15)
        {
            'years': [
                {'year': 1, 'label': 'Base Year', 'cost': 50000, 'bid': 57500, 'profit': 7500},
                {'year': 2, 'label': 'Option Year 1', 'cost': 51500, 'bid': 59225, 'profit': 7725},
                {'year': 3, 'label': 'Option Year 2', 'cost': 53045, 'bid': 61002, 'profit': 7957},
                {'year': 4, 'label': 'Option Year 3', 'cost': 54636, 'bid': 62832, 'profit': 8196},
                {'year': 5, 'label': 'Option Year 4', 'cost': 56275, 'bid': 64716, 'profit': 8441}
            ],
            'total_cost': 265456,
            'total_bid': 305275,
            'total_profit': 39819,
            'avg_annual_profit': 7964
        }
    """
    
    # Adjust markup for service contracts if not explicitly set
    if contract_type == "service" and markup_percent == 18.0:
        markup_percent = 12.0  # Default for service contracts with subs
    
    years = []
    total_cost = 0
    total_bid = 0
    
    for year_num in range(1, num_years + 1):
        # Calculate cost for this year (with escalation)
        if year_num == 1:
            year_cost = base_year_cost
            year_label = "Base Year"
        else:
            # Apply escalation: cost × (1 + escalation%)^(year - 1)
            year_cost = base_year_cost * ((1 + escalation_percent/100) ** (year_num - 1))
            year_label = f"Option Year {year_num - 1}"
        
        # Calculate bid price (cost + markup)
        year_bid = year_cost * (1 + markup_percent/100)
        year_profit = year_bid - year_cost
        
        years.append({
            'year': year_num,
            'label': year_label,
            'cost': round(year_cost, 2),
            'bid': round(year_bid, 2),
            'profit': round(year_profit, 2)
        })
        
        total_cost += year_cost
        total_bid += year_bid
    
    total_profit = total_bid - total_cost
    avg_annual_profit = total_profit / num_years
    
    return {
        'years': years,
        'total_cost': round(total_cost, 2),
        'total_bid': round(total_bid, 2),
        'total_profit': round(total_profit, 2),
        'avg_annual_profit': round(avg_annual_profit, 2),
        'escalation_percent': escalation_percent,
        'markup_percent': markup_percent
    }


def format_multi_year_pricing(pricing_data: dict) -> str:
    """
    Format multi-year pricing data for display or proposal.
    
    Args:
        pricing_data: Output from calculate_multi_year_pricing()
    
    Returns:
        Formatted string for proposal/report
    """
    output = []
    output.append("MULTI-YEAR PRICING BREAKDOWN")
    output.append("=" * 80)
    output.append(f"Escalation Rate: {pricing_data['escalation_percent']}% annually")
    output.append(f"Markup: {pricing_data['markup_percent']}%")
    output.append("")
    output.append(f"{'Year':<20} {'Cost':<15} {'Bid Price':<15} {'Profit':<15}")
    output.append("-" * 80)
    
    for year in pricing_data['years']:
        output.append(
            f"{year['label']:<20} "
            f"${year['cost']:>12,.2f}  "
            f"${year['bid']:>12,.2f}  "
            f"${year['profit']:>12,.2f}"
        )
    
    output.append("-" * 80)
    output.append(
        f"{'TOTAL':<20} "
        f"${pricing_data['total_cost']:>12,.2f}  "
        f"${pricing_data['total_bid']:>12,.2f}  "
        f"${pricing_data['total_profit']:>12,.2f}"
    )
    output.append("")
    output.append(f"Average Annual Profit: ${pricing_data['avg_annual_profit']:,.2f}")
    output.append("=" * 80)
    
    return "\n".join(output)


def calculate_ohio_doh_pricing_example():
    """
    Example calculation for Ohio DOH Medical Courier bid.
    
    Contract: 4/1/2026 - 6/30/2027 (base) + up to 4 years renewal
    Budget: $70,000 per year
    """
    
    # Scenario 1: Sub quotes $50,000/year
    print("\n" + "="*80)
    print("OHIO DOH MEDICAL COURIER — PRICING SCENARIOS")
    print("="*80)
    print("\nContract Structure:")
    print("  Base Period: 4/1/2026 - 6/30/2027 (15 months)")
    print("  Option 1: 7/1/2027 - 6/30/2029 (24 months)")
    print("  Option 2: 7/1/2029 - 6/30/2031 (24 months)")
    print("  Total: 63 months (5.25 years)")
    print("\n" + "="*80)
    
    # Scenario 1: Conservative sub cost
    print("\n📊 SCENARIO 1: Sub quotes $50,000/year, 12% markup")
    print("-" * 80)
    
    # Base period (15 months = 1.25 years)
    base_period_cost = 50000 * 1.25
    
    # Option years (24 months each = 2 years each)
    pricing = calculate_multi_year_pricing(
        base_year_cost=50000,  # Annual cost
        num_years=5,  # 5 full years for calculation
        escalation_percent=3,
        markup_percent=12,
        contract_type="service"
    )
    
    print(format_multi_year_pricing(pricing))
    
    # Scenario 2: Higher sub cost
    print("\n\n📊 SCENARIO 2: Sub quotes $55,000/year, 12% markup")
    print("-" * 80)
    
    pricing2 = calculate_multi_year_pricing(
        base_year_cost=55000,
        num_years=5,
        escalation_percent=3,
        markup_percent=12,
        contract_type="service"
    )
    
    print(format_multi_year_pricing(pricing2))
    
    # Scenario 3: Aggressive pricing
    print("\n\n📊 SCENARIO 3: Sub quotes $60,000/year, 10% markup (competitive)")
    print("-" * 80)
    
    pricing3 = calculate_multi_year_pricing(
        base_year_cost=60000,
        num_years=5,
        escalation_percent=3,
        markup_percent=10,
        contract_type="service"
    )
    
    print(format_multi_year_pricing(pricing3))
    
    print("\n" + "="*80)
    print("RECOMMENDATION:")
    print("  - Get quotes from 3 couriers")
    print("  - Use 12% markup (standard for service contracts with subs)")
    print("  - Apply 3% annual escalation (industry standard)")
    print("  - Aim for $60K-70K total bid (within ODH budget)")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Run example
    calculate_ohio_doh_pricing_example()
    
    # Additional examples
    print("\n\n" + "="*80)
    print("ADDITIONAL EXAMPLES")
    print("="*80)
    
    # Example: 3-year NEMT contract
    print("\n📊 EXAMPLE: 3-Year NEMT Contract")
    print("-" * 80)
    nemt_pricing = calculate_multi_year_pricing(
        base_year_cost=200000,  # Sub quotes $200K/year
        num_years=3,
        escalation_percent=3,
        markup_percent=15,  # 15% for service contracts
        contract_type="service"
    )
    print(format_multi_year_pricing(nemt_pricing))
    
    # Example: 5-year grounds maintenance
    print("\n\n📊 EXAMPLE: 5-Year Grounds Maintenance Contract")
    print("-" * 80)
    grounds_pricing = calculate_multi_year_pricing(
        base_year_cost=150000,  # Sub quotes $150K/year
        num_years=5,
        escalation_percent=3,
        markup_percent=12,  # 12% for service contracts
        contract_type="service"
    )
    print(format_multi_year_pricing(grounds_pricing))
