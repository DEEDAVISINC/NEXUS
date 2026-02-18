#!/usr/bin/env python3
"""
SERVICE CONTRACT LABOR RATE CALCULATOR
Calculate billable hourly rates for service contracts
"""

def calculate_fully_burdened_labor_rate(
    base_wage: float,
    payroll_tax_rate: float = 0.0765,  # FICA (7.65%)
    workers_comp_rate: float = 0.05,   # 5% (varies by industry)
    health_insurance_per_hour: float = 3.50,  # ~$7K/year ÷ 2000 hours
    pto_percent: float = 0.08,  # 8% (4 weeks PTO)
    overhead_percent: float = 25.0,  # Company overhead
    profit_margin: float = 10.0  # Target profit %
) -> dict:
    """
    Calculate fully burdened hourly rate for service contracts.
    
    Args:
        base_wage: Base hourly wage for worker (e.g., $20/hour)
        payroll_tax_rate: FICA + unemployment taxes (default 7.65%)
        workers_comp_rate: Workers' comp insurance rate (varies by industry)
        health_insurance_per_hour: Health insurance cost per hour worked
        pto_percent: Paid time off as % of hours (default 8% = 4 weeks)
        overhead_percent: Company overhead allocation (facilities, admin, etc.)
        profit_margin: Target profit margin %
    
    Returns:
        Dict with breakdown of billable rate
    
    Example:
        >>> calculate_fully_burdened_labor_rate(base_wage=20, profit_margin=10)
        {
            'base_wage': 20.00,
            'payroll_taxes': 1.53,
            'workers_comp': 1.00,
            'health_insurance': 3.50,
            'pto_cost': 1.60,
            'direct_labor_cost': 27.63,
            'overhead': 6.91,
            'total_cost': 34.54,
            'profit': 3.45,
            'billable_rate': 37.99
        }
    """
    
    # Direct labor costs
    payroll_taxes = base_wage * payroll_tax_rate
    workers_comp = base_wage * workers_comp_rate
    pto_cost = base_wage * pto_percent
    
    direct_labor_cost = base_wage + payroll_taxes + workers_comp + health_insurance_per_hour + pto_cost
    
    # Overhead allocation
    overhead = direct_labor_cost * (overhead_percent / 100)
    
    # Total cost per hour
    total_cost = direct_labor_cost + overhead
    
    # Add profit margin
    profit = total_cost * (profit_margin / 100)
    billable_rate = total_cost + profit
    
    return {
        'base_wage': round(base_wage, 2),
        'payroll_taxes': round(payroll_taxes, 2),
        'workers_comp': round(workers_comp, 2),
        'health_insurance': round(health_insurance_per_hour, 2),
        'pto_cost': round(pto_cost, 2),
        'direct_labor_cost': round(direct_labor_cost, 2),
        'overhead': round(overhead, 2),
        'overhead_percent': overhead_percent,
        'total_cost': round(total_cost, 2),
        'profit': round(profit, 2),
        'profit_margin': profit_margin,
        'billable_rate': round(billable_rate, 2)
    }


def format_labor_rate_breakdown(rate_data: dict) -> str:
    """Format labor rate breakdown for display."""
    output = []
    output.append("FULLY BURDENED LABOR RATE BREAKDOWN")
    output.append("=" * 60)
    output.append("")
    output.append("DIRECT LABOR COSTS:")
    output.append(f"  Base Wage:              ${rate_data['base_wage']:>8.2f} /hour")
    output.append(f"  Payroll Taxes (7.65%):  ${rate_data['payroll_taxes']:>8.2f} /hour")
    output.append(f"  Workers' Comp:          ${rate_data['workers_comp']:>8.2f} /hour")
    output.append(f"  Health Insurance:       ${rate_data['health_insurance']:>8.2f} /hour")
    output.append(f"  PTO Cost:               ${rate_data['pto_cost']:>8.2f} /hour")
    output.append(f"  {'─' * 40}")
    output.append(f"  Direct Labor Cost:      ${rate_data['direct_labor_cost']:>8.2f} /hour")
    output.append("")
    output.append("OVERHEAD & PROFIT:")
    output.append(f"  Overhead ({rate_data['overhead_percent']}%):         ${rate_data['overhead']:>8.2f} /hour")
    output.append(f"  Total Cost:             ${rate_data['total_cost']:>8.2f} /hour")
    output.append(f"  Profit ({rate_data['profit_margin']}%):             ${rate_data['profit']:>8.2f} /hour")
    output.append(f"  {'═' * 40}")
    output.append(f"  BILLABLE RATE:          ${rate_data['billable_rate']:>8.2f} /hour")
    output.append("=" * 60)
    
    return "\n".join(output)


def calculate_service_contract_pricing(
    annual_hours: int,
    hourly_rate: float,
    num_years: int = 1,
    escalation_percent: float = 3.0
) -> dict:
    """
    Calculate total service contract pricing based on hourly rate.
    
    Args:
        annual_hours: Total hours per year
        hourly_rate: Billable hourly rate
        num_years: Contract duration in years
        escalation_percent: Annual rate increase %
    
    Returns:
        Dict with year-by-year breakdown
    """
    years = []
    total_value = 0
    
    for year_num in range(1, num_years + 1):
        # Apply escalation to hourly rate
        if year_num == 1:
            year_rate = hourly_rate
            year_label = "Base Year"
        else:
            year_rate = hourly_rate * ((1 + escalation_percent/100) ** (year_num - 1))
            year_label = f"Option Year {year_num - 1}"
        
        year_value = year_rate * annual_hours
        
        years.append({
            'year': year_num,
            'label': year_label,
            'hourly_rate': round(year_rate, 2),
            'annual_hours': annual_hours,
            'annual_value': round(year_value, 2)
        })
        
        total_value += year_value
    
    return {
        'years': years,
        'total_contract_value': round(total_value, 2),
        'avg_annual_value': round(total_value / num_years, 2)
    }


# ============================================================================
# INDUSTRY-SPECIFIC LABOR RATE PRESETS
# ============================================================================

LABOR_RATE_PRESETS = {
    'drug_testing_collector': {
        'base_wage': 22.00,  # $22/hour for certified collector
        'workers_comp_rate': 0.03,  # Lower risk (office/clinic work)
        'description': 'Drug Testing Specimen Collector'
    },
    'fingerprint_technician': {
        'base_wage': 25.00,  # $25/hour for Livescan certified
        'workers_comp_rate': 0.02,  # Very low risk
        'description': 'Fingerprinting / Livescan Technician'
    },
    'mobile_notary': {
        'base_wage': 30.00,  # $30/hour for notary + travel
        'workers_comp_rate': 0.03,  # Moderate risk (driving)
        'description': 'Mobile Notary Public'
    },
    'nemt_driver': {
        'base_wage': 18.00,  # $18/hour for medical transport driver
        'workers_comp_rate': 0.08,  # Higher risk (driving + patient handling)
        'description': 'NEMT Driver (Non-Emergency Medical Transport)'
    },
    'courier_driver': {
        'base_wage': 20.00,  # $20/hour for medical courier
        'workers_comp_rate': 0.06,  # Moderate-high risk (driving + specimens)
        'description': 'Medical Courier Driver'
    },
    'grounds_maintenance': {
        'base_wage': 18.00,  # $18/hour for grounds crew
        'workers_comp_rate': 0.12,  # High risk (equipment, outdoor work)
        'description': 'Grounds Maintenance Worker'
    },
    'janitorial': {
        'base_wage': 16.00,  # $16/hour for janitorial
        'workers_comp_rate': 0.05,  # Moderate risk
        'description': 'Janitorial / Custodial Worker'
    }
}


def calculate_service_rate_by_type(service_type: str, profit_margin: float = 10.0) -> dict:
    """
    Calculate billable rate for common DDI service types.
    
    Args:
        service_type: Key from LABOR_RATE_PRESETS
        profit_margin: Target profit margin %
    
    Returns:
        Labor rate breakdown
    """
    if service_type not in LABOR_RATE_PRESETS:
        raise ValueError(f"Unknown service type: {service_type}. Available: {list(LABOR_RATE_PRESETS.keys())}")
    
    preset = LABOR_RATE_PRESETS[service_type]
    
    rate_data = calculate_fully_burdened_labor_rate(
        base_wage=preset['base_wage'],
        workers_comp_rate=preset['workers_comp_rate'],
        profit_margin=profit_margin
    )
    
    rate_data['service_type'] = service_type
    rate_data['description'] = preset['description']
    
    return rate_data


if __name__ == "__main__":
    print("\n" + "="*80)
    print("SERVICE CONTRACT LABOR RATE CALCULATOR — DDI SERVICE LINES")
    print("="*80)
    
    # Calculate rates for all DDI service types
    for service_type, preset in LABOR_RATE_PRESETS.items():
        print(f"\n📊 {preset['description'].upper()}")
        print("-" * 60)
        
        rate_data = calculate_service_rate_by_type(service_type, profit_margin=10)
        
        print(f"  Base Wage:        ${rate_data['base_wage']:.2f}/hour")
        print(f"  Burdened Cost:    ${rate_data['direct_labor_cost']:.2f}/hour")
        print(f"  + Overhead (25%): ${rate_data['overhead']:.2f}/hour")
        print(f"  + Profit (10%):   ${rate_data['profit']:.2f}/hour")
        print(f"  ─────────────────────────────────")
        print(f"  BILLABLE RATE:    ${rate_data['billable_rate']:.2f}/hour")
        print("")
        print(f"  Annual Value (2000 hours): ${rate_data['billable_rate'] * 2000:,.2f}")
    
    print("\n" + "="*80)
    print("USAGE EXAMPLES")
    print("="*80)
    
    # Example 1: Drug testing contract
    print("\n📊 EXAMPLE 1: Drug Testing Contract (3 collectors, full-time)")
    print("-" * 60)
    drug_testing_rate = calculate_service_rate_by_type('drug_testing_collector', profit_margin=10)
    num_collectors = 3
    hours_per_year = 2000  # Full-time
    annual_value = drug_testing_rate['billable_rate'] * hours_per_year * num_collectors
    
    print(f"  Billable Rate: ${drug_testing_rate['billable_rate']:.2f}/hour")
    print(f"  Collectors: {num_collectors}")
    print(f"  Hours/Year: {hours_per_year:,}")
    print(f"  Annual Contract Value: ${annual_value:,.2f}")
    print(f"  Annual Profit: ${drug_testing_rate['profit'] * hours_per_year * num_collectors:,.2f}")
    
    # Example 2: Mobile notary contract
    print("\n\n📊 EXAMPLE 2: Mobile Notary Services (500 hours/year)")
    print("-" * 60)
    notary_rate = calculate_service_rate_by_type('mobile_notary', profit_margin=12)
    hours_per_year = 500
    annual_value = notary_rate['billable_rate'] * hours_per_year
    
    print(f"  Billable Rate: ${notary_rate['billable_rate']:.2f}/hour")
    print(f"  Hours/Year: {hours_per_year:,}")
    print(f"  Annual Contract Value: ${annual_value:,.2f}")
    print(f"  Annual Profit: ${notary_rate['profit'] * hours_per_year:,.2f}")
    
    print("\n" + "="*80)
    print("NOTE: These rates assume DDI self-performs the work.")
    print("For subcontractor services, use 10-15% markup on their quote instead.")
    print("="*80 + "\n")
