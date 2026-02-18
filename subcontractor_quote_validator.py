#!/usr/bin/env python3
"""
SUBCONTRACTOR QUOTE VALIDATOR
Verify if subcontractor quotes are reasonable before marking up
"""

# Market rate benchmarks by service type (per year or per unit)
MARKET_RATE_BENCHMARKS = {
    'medical_courier_ohio': {
        'unit': 'per shipment',
        'low': 25,
        'typical': 40,
        'high': 75,
        'notes': 'Varies by distance, temperature control, urgency'
    },
    'nemt_per_mile': {
        'unit': 'per mile',
        'low': 2.00,
        'typical': 3.50,
        'high': 6.00,
        'notes': 'Wheelchair/stretcher higher than ambulatory'
    },
    'drug_testing_per_test': {
        'unit': 'per test',
        'low': 35,
        'typical': 50,
        'high': 85,
        'notes': 'Includes collection, chain of custody, lab coordination'
    },
    'fingerprinting_per_person': {
        'unit': 'per person',
        'low': 25,
        'typical': 40,
        'high': 65,
        'notes': 'Livescan equipment, FBI submission, SWFT certified'
    },
    'grounds_maintenance_per_acre': {
        'unit': 'per acre per month',
        'low': 150,
        'typical': 300,
        'high': 600,
        'notes': 'Varies by mowing frequency, trimming, cleanup scope'
    },
    'janitorial_per_sqft': {
        'unit': 'per sqft per month',
        'low': 0.10,
        'typical': 0.20,
        'high': 0.40,
        'notes': 'Daily cleaning higher than weekly'
    },
    'shuttle_per_hour': {
        'unit': 'per hour',
        'low': 45,
        'typical': 65,
        'high': 95,
        'notes': 'Includes driver, vehicle, fuel, insurance'
    }
}


def validate_subcontractor_quote(
    sub_quote: float,
    service_type: str,
    quantity: float = 1,
    region: str = None
) -> dict:
    """
    Validate if subcontractor quote is reasonable compared to market rates.
    
    Args:
        sub_quote: Total quote from subcontractor
        service_type: Key from MARKET_RATE_BENCHMARKS
        quantity: Number of units (shipments, miles, tests, etc.)
        region: Geographic area (for regional adjustments)
    
    Returns:
        Dict with validation results and recommendation
    
    Example:
        >>> validate_subcontractor_quote(50000, 'medical_courier_ohio', quantity=1000)
        {
            'is_reasonable': True,
            'per_unit_cost': 50.00,
            'market_low': 25,
            'market_typical': 40,
            'market_high': 75,
            'variance_from_typical': 25.0,
            'recommendation': 'REASONABLE — Within market range',
            'flags': []
        }
    """
    
    if service_type not in MARKET_RATE_BENCHMARKS:
        return {
            'is_reasonable': None,
            'error': f"Unknown service type: {service_type}",
            'available_types': list(MARKET_RATE_BENCHMARKS.keys())
        }
    
    benchmark = MARKET_RATE_BENCHMARKS[service_type]
    
    # Calculate per-unit cost
    per_unit_cost = sub_quote / quantity if quantity > 0 else sub_quote
    
    # Compare to market rates
    market_low = benchmark['low']
    market_typical = benchmark['typical']
    market_high = benchmark['high']
    
    # Calculate variance from typical
    variance_percent = ((per_unit_cost - market_typical) / market_typical) * 100
    
    # Determine if reasonable
    flags = []
    
    if per_unit_cost < market_low:
        is_reasonable = False
        recommendation = "⚠️  SUSPICIOUSLY LOW — Verify sub understands scope and has insurance"
        flags.append("Below market low")
        flags.append("May be missing costs (insurance, overhead, profit)")
        flags.append("Risk of sub backing out or poor performance")
    
    elif per_unit_cost <= market_typical * 1.15:  # Within 15% of typical
        is_reasonable = True
        recommendation = "✅ REASONABLE — Within market range"
    
    elif per_unit_cost <= market_high:
        is_reasonable = True
        recommendation = "⚠️  HIGHER THAN TYPICAL — Verify if justified (specialty, urgency, etc.)"
        flags.append("Above typical market rate")
        flags.append("May reduce DDI competitiveness")
        flags.append("Consider negotiating or finding alternative sub")
    
    else:
        is_reasonable = False
        recommendation = "❌ TOO HIGH — Above market high, likely overpriced"
        flags.append("Significantly above market rate")
        flags.append("Will make DDI bid non-competitive")
        flags.append("Find alternative subcontractor")
    
    return {
        'is_reasonable': is_reasonable,
        'per_unit_cost': round(per_unit_cost, 2),
        'unit': benchmark['unit'],
        'market_low': market_low,
        'market_typical': market_typical,
        'market_high': market_high,
        'variance_from_typical': round(variance_percent, 1),
        'recommendation': recommendation,
        'flags': flags,
        'notes': benchmark['notes']
    }


def format_validation_report(validation: dict) -> str:
    """Format validation results for display."""
    output = []
    output.append("SUBCONTRACTOR QUOTE VALIDATION")
    output.append("=" * 60)
    output.append("")
    output.append(f"Per-Unit Cost:     ${validation['per_unit_cost']:.2f} {validation['unit']}")
    output.append("")
    output.append("MARKET BENCHMARKS:")
    output.append(f"  Low:             ${validation['market_low']:.2f} {validation['unit']}")
    output.append(f"  Typical:         ${validation['market_typical']:.2f} {validation['unit']}")
    output.append(f"  High:            ${validation['market_high']:.2f} {validation['unit']}")
    output.append("")
    output.append(f"Variance from Typical: {validation['variance_from_typical']:+.1f}%")
    output.append("")
    output.append(validation['recommendation'])
    
    if validation['flags']:
        output.append("")
        output.append("FLAGS:")
        for flag in validation['flags']:
            output.append(f"  ⚠️  {flag}")
    
    output.append("")
    output.append(f"Notes: {validation['notes']}")
    output.append("=" * 60)
    
    return "\n".join(output)


def calculate_ddi_bid_from_sub_quote(
    sub_quote: float,
    markup_percent: float = 12.0,
    num_years: int = 1,
    escalation_percent: float = 3.0
) -> dict:
    """
    Calculate DDI's bid price from subcontractor quote.
    
    Args:
        sub_quote: Annual subcontractor quote
        markup_percent: DDI markup % (default 12% for service contracts)
        num_years: Contract duration
        escalation_percent: Annual escalation %
    
    Returns:
        Dict with DDI bid breakdown
    """
    from multi_year_pricing_calculator import calculate_multi_year_pricing
    
    return calculate_multi_year_pricing(
        base_year_cost=sub_quote,
        num_years=num_years,
        escalation_percent=escalation_percent,
        markup_percent=markup_percent,
        contract_type="service"
    )


if __name__ == "__main__":
    print("\n" + "="*80)
    print("SUBCONTRACTOR QUOTE VALIDATOR — EXAMPLES")
    print("="*80)
    
    # Example 1: Ohio DOH Medical Courier
    print("\n📊 EXAMPLE 1: Ohio DOH Medical Courier")
    print("-" * 80)
    print("Sub Quote: $50,000/year for 1,000 shipments")
    print("")
    
    validation = validate_subcontractor_quote(
        sub_quote=50000,
        service_type='medical_courier_ohio',
        quantity=1000
    )
    
    print(format_validation_report(validation))
    
    if validation['is_reasonable']:
        print("\n✅ PROCEED WITH THIS SUB")
        print("DDI Bid Calculation (12% markup):")
        print(f"  Sub Cost:   ${50000:,.2f}")
        print(f"  DDI Markup: ${50000 * 0.12:,.2f}")
        print(f"  DDI Bid:    ${50000 * 1.12:,.2f}")
        print(f"  DDI Profit: ${50000 * 0.12:,.2f}")
    
    # Example 2: Suspiciously low quote
    print("\n\n📊 EXAMPLE 2: Medical Courier — SUSPICIOUSLY LOW QUOTE")
    print("-" * 80)
    print("Sub Quote: $20,000/year for 1,000 shipments")
    print("")
    
    validation2 = validate_subcontractor_quote(
        sub_quote=20000,
        service_type='medical_courier_ohio',
        quantity=1000
    )
    
    print(format_validation_report(validation2))
    
    # Example 3: Too high quote
    print("\n\n📊 EXAMPLE 3: Medical Courier — TOO HIGH QUOTE")
    print("-" * 80)
    print("Sub Quote: $90,000/year for 1,000 shipments")
    print("")
    
    validation3 = validate_subcontractor_quote(
        sub_quote=90000,
        service_type='medical_courier_ohio',
        quantity=1000
    )
    
    print(format_validation_report(validation3))
    
    # Example 4: NEMT quote
    print("\n\n📊 EXAMPLE 4: NEMT Contract")
    print("-" * 80)
    print("Sub Quote: $350,000/year for 100,000 miles")
    print("")
    
    validation4 = validate_subcontractor_quote(
        sub_quote=350000,
        service_type='nemt_per_mile',
        quantity=100000
    )
    
    print(format_validation_report(validation4))
    
    if validation4['is_reasonable']:
        print("\n✅ PROCEED WITH THIS SUB")
        print("DDI Bid Calculation (15% markup):")
        print(f"  Sub Cost:   ${350000:,.2f}")
        print(f"  DDI Markup: ${350000 * 0.15:,.2f}")
        print(f"  DDI Bid:    ${350000 * 1.15:,.2f}")
        print(f"  DDI Profit: ${350000 * 0.15:,.2f}")
    
    print("\n" + "="*80)
    print("USE THIS TOOL BEFORE ACCEPTING ANY SUBCONTRACTOR QUOTE")
    print("="*80 + "\n")
