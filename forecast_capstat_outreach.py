"""
FORECAST CAPABILITY STATEMENT OUTREACH SYSTEM
Proactive relationship building for forecasted opportunities

This module connects:
- Federal Forecasts (upcoming contracts)
- Capability Statement Generator (tailored documents)
- Officer Outreach Tracking (relationship management)

Part of NEXUS Backend - Dee Davis Inc
"""

import os
from datetime import datetime
from typing import Dict, Optional
from pyairtable import Api

# Import ProposalBio™ for quality analysis
try:
    from proposalbio_module import ProposalBioAnalyzer
    PROPOSALBIO_AVAILABLE = True
except ImportError:
    PROPOSALBIO_AVAILABLE = False
    print("⚠️ ProposalBio module not available - forecast letters will generate without quality scoring")


class ForecastCapStatOutreach:
    """
    Generate capability statements and outreach letters for forecasted opportunities
    Proactive positioning BEFORE RFP drops (3-6 months advance)
    """
    
    def __init__(self, airtable_client):
        self.airtable = airtable_client
        self.company_info = self._load_company_info()
    
    def _load_company_info(self) -> Dict:
        """Load company information from environment"""
        return {
            'company_name': os.getenv('COMPANY_NAME', 'Dee Davis, Inc.'),
            'contact_name': os.getenv('CONTACT_NAME', 'Dee Davis'),
            'contact_title': os.getenv('CONTACT_TITLE', 'President'),
            'contact_email': os.getenv('CONTACT_EMAIL', 'info@deedavis.biz'),
            'contact_phone': os.getenv('CONTACT_PHONE', '248-376-4550'),
            'cage_code': os.getenv('CAGE_CODE', '8UMX3'),
            'uei_number': os.getenv('UEI_NUMBER', 'HJB4KNYJVGZ1'),
            'duns': os.getenv('DUNS_NUMBER', '002636755'),
            'sam_status': 'Active',
            'certifications': 'EDWOSB, WOSB, MBE, WBE',
        }
    
    def generate_forecast_capstat_and_outreach(self, forecast_record_id: str) -> Dict:
        """
        Complete workflow: Generate cap statement and outreach letter for forecast
        
        This is the MAIN function that orchestrates everything:
        1. Gets forecast details from Airtable
        2. Generates capability statement tailored to forecast
        3. Generates introduction/outreach email
        4. Creates Officer Outreach Tracking record
        5. Updates forecast record with all links
        
        Args:
            forecast_record_id: Airtable record ID from Federal Forecasts table
        
        Returns:
            Dict with cap statement paths, outreach letter, and tracking info
        """
        
        # 1. Get forecast details from Airtable
        forecast = self.airtable.get_record('Federal Forecasts', forecast_record_id)
        fields = forecast['fields']
        
        # Validate required fields
        if not fields.get('Contracting Officer') or not fields.get('Officer Email'):
            return {
                'success': False,
                'error': 'Forecast must have Contracting Officer name and email to generate outreach'
            }
        
        # 2. Generate capability statement TAILORED to this forecast
        capstat_result = self._generate_forecast_capstat(forecast)
        
        # 3. Generate introduction/outreach email
        outreach_letter = self._generate_forecast_outreach_letter(forecast, capstat_result)
        
        # 4. Create Officer Outreach Tracking record
        outreach_record_id = self._create_forecast_outreach_record(
            forecast, 
            capstat_result, 
            outreach_letter
        )
        
        # 5. Update forecast record with tracking info
        self.airtable.update_record('Federal Forecasts', forecast_record_id, {
            'Cap Statement Generated': True,
            'Outreach Status': 'Cap Statement Generated - Ready to Send',
            'Outreach Date': datetime.now().isoformat(),
            'Outreach Record': [outreach_record_id],
        })
        
        return {
            'success': True,
            'forecast_id': forecast_record_id,
            'forecast_title': fields.get('Title'),
            'capstat_pdf': capstat_result['pdf_file'],
            'capstat_html': capstat_result['html_file'],
            'outreach_record_id': outreach_record_id,
            'outreach_letter': outreach_letter,
            'officer_email': fields.get('Officer Email'),
            'officer_name': fields.get('Contracting Officer'),
        }
    
    def _generate_forecast_capstat(self, forecast: Dict) -> Dict:
        """
        Generate capability statement tailored to forecast
        
        NOTE: This uses the existing capability_statement_generator module
        We're adapting it to work with forecast data instead of opportunity data
        """
        from capability_statement_generator import handle_generate_capability_statement
        
        fields = forecast['fields']
        
        # Prepare config data
        agency = fields.get('Agency', 'Federal Agency')
        title = fields.get('Title', 'Upcoming Procurement')
        forecast_number = fields.get('Solicitation Number', f"FORECAST-{forecast['id'][:8]}")
        
        # Generate capability statement using existing generator
        result = handle_generate_capability_statement(
            client_name=agency,
            rfq_number=forecast_number,
            rfq_title=title,
            template=self._determine_template(fields)
        )
        
        return result
    
    def _determine_template(self, fields: Dict) -> str:
        """Determine which cap statement template to use based on forecast type"""
        title_lower = fields.get('Title', '').lower()
        desc_lower = fields.get('Description', '').lower()
        
        # Medical/Healthcare template
        if any(word in title_lower or word in desc_lower for word in [
            'medical', 'healthcare', 'hospital', 'clinic', 'va ', 'health', 'pharmaceutical'
        ]):
            return 'va_medical'
        
        # Construction template
        if any(word in title_lower or word in desc_lower for word in [
            'construction', 'building', 'renovation', 'repair', 'facility', 'hvac'
        ]):
            return 'construction'
        
        # Default (industrial supplies)
        return 'default'
    
    def _generate_forecast_outreach_letter(self, forecast: Dict, capstat: Dict) -> Dict:
        """
        Generate introduction letter for forecasted opportunity
        This is PROACTIVE outreach - reaching out BEFORE RFP drops
        """
        fields = forecast['fields']
        
        officer_name = fields.get('Contracting Officer', 'Contracting Officer')
        officer_email = fields.get('Officer Email', '')
        officer_title = fields.get('Officer Title', 'Contracting Officer')
        agency = fields.get('Agency', 'Your Agency')
        title = fields.get('Title', 'Upcoming Procurement')
        estimated_date = fields.get('Estimated Solicitation Date', 'upcoming')
        estimated_value = fields.get('Estimated Value', 0)
        set_aside = fields.get('Set-Aside Type', '')
        description = fields.get('Description', '')[:300]  # First 300 chars
        fit_analysis = fields.get('Fit Analysis', '')
        
        # Format estimated date nicely
        if estimated_date and estimated_date != 'upcoming':
            try:
                from dateutil import parser
                date_obj = parser.parse(estimated_date)
                estimated_date_formatted = date_obj.strftime('%B %Y')
            except:
                estimated_date_formatted = estimated_date
        else:
            estimated_date_formatted = 'the coming months'
        
        # Format estimated value nicely
        if estimated_value:
            value_formatted = f"${estimated_value:,.0f}"
        else:
            value_formatted = ''
        
        # Salutation
        if officer_name and officer_name != 'Contracting Officer':
            name_parts = officer_name.split()
            if len(name_parts) >= 2:
                salutation = f"Dear Ms./Mr. {name_parts[-1]},"
                first_name = name_parts[0]
            else:
                salutation = f"Dear {officer_name},"
                first_name = officer_name
        else:
            salutation = "Dear Contracting Officer,"
            first_name = "there"
        
        today = datetime.now().strftime("%B %d, %Y")
        
        # Build letter body based on what info we have
        intro_paragraph = f"""I am writing to introduce **{self.company_info['company_name']}** regarding {agency}'s upcoming procurement for {title}"""
        
        if estimated_date_formatted:
            intro_paragraph += f""", which we understand is planned for solicitation around {estimated_date_formatted}"""
        
        intro_paragraph += "."
        
        # Value proposition paragraph
        value_prop = ""
        if set_aside and 'WOSB' in set_aside:
            value_prop = f"""This procurement appears to be a **{set_aside} set-aside**, which aligns perfectly with our certifications. """
        
        value_prop += """We believe in proactive engagement with contracting officers to ensure you're aware of qualified, diverse suppliers like ours BEFORE the solicitation period begins. This allows you to:

- Understand available diverse supplier options
- Plan for successful socioeconomic goal achievement
- Reduce time spent sourcing qualified vendors when the RFP drops
- Access competitive pricing through our established supply partnerships"""
        
        # Why we're a good fit
        fit_paragraph = ""
        if fit_analysis:
            fit_paragraph = f"""**Why {self.company_info['company_name']} for This Project:**

{fit_analysis}"""
        else:
            fit_paragraph = f"""**Why {self.company_info['company_name']} for This Project:**

We have successfully delivered similar products and services to federal, state, and local government agencies. Our experience includes {title.lower()} and related procurement requirements."""
        
        # Full letter
        letter = f"""**Date:** {today}

**To:** {officer_name}
{f"**Title:** {officer_title}" if officer_title != 'Contracting Officer' else ""}
**Email:** {officer_email}
**Agency:** {agency}
**Re:** Upcoming Procurement - {title}

---

{salutation}

{intro_paragraph}

**Why We're Reaching Out Now:**

{value_prop}

**About {self.company_info['company_name']}:**

{self.company_info['company_name']} is a certified **Economically Disadvantaged Woman-Owned Small Business (EDWOSB)** with proven experience delivering high-quality products and services to government agencies nationwide.

**Our Certifications:**
- ✓ EDWOSB (Economically Disadvantaged Woman-Owned Small Business) - SBA Certified
- ✓ WOSB (Women-Owned Small Business) - SBA Certified  
- ✓ MBE (Minority Business Enterprise)
- ✓ WBE (Women Business Enterprise)
- ✓ SAM.gov Active Registration (CAGE: {self.company_info['cage_code']}, UEI: {self.company_info['uei_number']})

{fit_paragraph}

**What We Can Offer:**
- **Competitive Pricing:** Strategic partnerships with national distributors ensure cost-effective solutions
- **Proven Performance:** 98%+ on-time delivery rate across government contracts
- **Socioeconomic Credit:** Help your agency achieve WOSB/EDWOSB contracting goals
- **Professional Service:** Responsive, reliable partner throughout contract lifecycle
- **Quality Assurance:** All products meet or exceed specifications
- **Nationwide Capability:** Delivery to any location in the continental United States

**Our Request:**

We respectfully request the opportunity to:

1. **Be considered** when the solicitation is released
2. **Receive notification** when the RFP/RFQ is posted (if possible)
3. **Schedule a brief call** to discuss your specific requirements (optional, at your convenience)
4. **Provide additional information** about our capabilities or past performance

**Enclosed:**

I have attached our **Capability Statement** which provides detailed information about our company, certifications, past performance, and core competencies relevant to this procurement.

**When the Solicitation Is Released:**

We are prepared to respond with:
- Comprehensive, competitive proposal
- Detailed technical specifications
- Competitive pricing through established supply chain
- Past performance examples from similar contracts
- All required certifications and documentation

Thank you for considering {self.company_info['company_name']} for this upcoming procurement. We are genuinely excited about the opportunity to serve {agency} and contribute to your mission success.

Please feel free to contact me directly with any questions or to discuss this opportunity further.

Respectfully,

**{self.company_info['contact_name']}**
{self.company_info['contact_title']}
{self.company_info['company_name']}

---

**Contact Information:**

**Company:** {self.company_info['company_name']}  
**Contact:** {self.company_info['contact_name']}, {self.company_info['contact_title']}  
**Email:** {self.company_info['contact_email']}  
**Phone:** {self.company_info['contact_phone']}  
**CAGE Code:** {self.company_info['cage_code']}  
**UEI:** {self.company_info['uei_number']}  
**DUNS:** {self.company_info['duns']}  
**SAM.gov:** {self.company_info['sam_status']}

---

**Enclosure:** Company Capability Statement (PDF)
"""
        
        # Email subject line
        subject_line = f"Introduction - {self.company_info['company_name']} - Upcoming: {title}"
        
        result = {
            'letter': letter,
            'recipient_name': officer_name,
            'recipient_email': officer_email,
            'recipient_title': officer_title,
            'subject_line': subject_line,
            'forecast_title': title,
            'agency': agency,
            'estimated_date': estimated_date_formatted,
        }
        
        # ================================================================
        # AUTOMATICALLY RUN PROPOSALBIO™ QUALITY ANALYSIS ON LETTER
        # ================================================================
        if PROPOSALBIO_AVAILABLE:
            try:
                proposalbio_analysis = self._analyze_letter_quality(letter, agency, officer_name)
                result['proposalbio_score'] = proposalbio_analysis['composite_score']
                result['proposalbio_status'] = proposalbio_analysis['overall_status']
                result['proposalbio_analysis'] = proposalbio_analysis
                
                # Add quality badge
                if proposalbio_analysis['composite_score'] >= 75:
                    result['quality_badge'] = '🟢 HIGH QUALITY'
                elif proposalbio_analysis['composite_score'] >= 60:
                    result['quality_badge'] = '🟡 GOOD QUALITY'
                else:
                    result['quality_badge'] = '🔴 NEEDS IMPROVEMENT'
                    
            except Exception as e:
                print(f"⚠️ ProposalBio analysis failed: {e}")
                result['proposalbio_score'] = None
                result['quality_badge'] = '⚪ NOT ANALYZED'
        else:
            result['proposalbio_score'] = None
            result['quality_badge'] = '⚪ NOT ANALYZED'
        
        return result
    
    def _create_forecast_outreach_record(
        self, 
        forecast: Dict, 
        capstat: Dict, 
        outreach_letter: Dict
    ) -> str:
        """
        Create Officer Outreach Tracking record for forecast outreach
        This links everything together in Airtable
        """
        
        fields = forecast['fields']
        
        record_fields = {
            'Outreach Type': 'Forecast (Proactive)',
            'Related Forecast': [forecast['id']],
            'Officer Name': outreach_letter['recipient_name'],
            'Officer Email': outreach_letter['recipient_email'],
            'Officer Title': outreach_letter.get('recipient_title', ''),
            'Opportunity Title': f"FORECAST: {outreach_letter['forecast_title']}",
            'Agency': outreach_letter['agency'],
            'Letter Generated Date': datetime.now().isoformat(),
            'Status': 'Draft',
            'Letter Content': outreach_letter['letter'],
            'Subject Line': outreach_letter['subject_line'],
            'Tags': ['Forecast', 'Proactive', fields.get('Set-Aside Type', 'Unrestricted')],
            'Priority': fields.get('Priority', 'Medium'),
            'Next Action': 'Review letter, customize if needed, then send email with cap statement attached',
            'Next Action Date': datetime.now().isoformat(),
            'Created By': 'NEXUS AI - Forecast Outreach System with ProposalBio™ Quality Analysis',
        }
        
        # Add ProposalBio™ quality scores if available
        if outreach_letter.get('proposalbio_score') is not None:
            record_fields['ProposalBio Score'] = outreach_letter['proposalbio_score']
            record_fields['Quality Badge'] = outreach_letter.get('quality_badge', '')
            
            # Add quality status
            if outreach_letter['proposalbio_score'] >= 75:
                record_fields['Quality Status'] = 'Ready to Send'
            elif outreach_letter['proposalbio_score'] >= 60:
                record_fields['Quality Status'] = 'Good - Minor Edits'
            else:
                record_fields['Quality Status'] = 'Needs Improvement'
            
            # Add improvement notes if score is low
            analysis = outreach_letter.get('proposalbio_analysis', {})
            if analysis.get('letter_improvements'):
                improvements = "\n".join(f"• {imp}" for imp in analysis['letter_improvements'])
                record_fields['Improvement Notes'] = f"ProposalBio™ Recommendations:\n{improvements}"
        
        # Add optional fields if they exist in the table
        if outreach_letter.get('estimated_date'):
            record_fields['Notes'] = f"Estimated Solicitation Date: {outreach_letter['estimated_date']}"
        
        record = self.airtable.create_record('Officer Outreach Tracking', record_fields)
        
        return record['id']


# ========================================================================
# API HANDLER FOR FRONTEND/AIRTABLE BUTTON
# ========================================================================

def handle_forecast_capstat_outreach(forecast_id: str) -> Dict:
    """
    Main handler that can be called from:
    - API endpoint (POST /api/forecasts/{id}/generate-capstat-outreach)
    - Airtable automation (via webhook)
    - Make.com webhook
    - Direct Python call
    
    This is what the "📧 Reach Out to Officer" button calls!
    
    Args:
        forecast_id: Federal Forecasts record ID from Airtable
    
    Returns:
        Complete result with files, links, and next steps
    """
    from nexus_backend import AirtableClient
    
    try:
        airtable = AirtableClient()
        forecast_outreach = ForecastCapStatOutreach(airtable)
        
        result = forecast_outreach.generate_forecast_capstat_and_outreach(forecast_id)
        
        if not result.get('success'):
            return result
        
        return {
            'success': True,
            'message': f"✅ Capability statement and outreach letter generated for forecast!",
            'forecast_title': result['forecast_title'],
            'capstat_pdf': result['capstat_pdf'],
            'capstat_html': result['capstat_html'],
            'outreach_record_id': result['outreach_record_id'],
            'officer_email': result['officer_email'],
            'officer_name': result['officer_name'],
            'next_steps': [
                f"1. Download capability statement: {result['capstat_pdf']}",
                f"2. Review outreach letter in Airtable (Record ID: {result['outreach_record_id']})",
                "3. Customize letter if needed (add specific details)",
                f"4. Send email to {result['officer_email']} with cap statement attached",
                "5. Update 'Date Sent' field in Officer Outreach Tracking",
                "6. System will auto-schedule follow-up for 2 weeks later"
            ]
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to generate forecast outreach: {str(e)}"
        }


# ========================================================================
# BATCH PROCESSING
# ========================================================================

def process_high_priority_forecasts(limit: int = 5) -> Dict:
    """
    Batch process: Generate cap statements for multiple high-priority forecasts
    
    Useful for:
    - Weekly prep session (generate outreach for top 5 forecasts)
    - Monthly review (reach out to all high-priority forecasts)
    
    Args:
        limit: Maximum number of forecasts to process
    
    Returns:
        Summary of results
    """
    from nexus_backend import AirtableClient
    
    airtable = AirtableClient()
    forecast_outreach = ForecastCapStatOutreach(airtable)
    
    # Get high-priority forecasts that haven't been reached out to yet
    try:
        forecasts = airtable.get_all_records('Federal Forecasts', 
            formula="AND({Priority}='HIGH', {Fit Score}>=80, NOT({Cap Statement Generated}), {Contracting Officer}!='')"
        )
    except:
        # Fallback if formula doesn't work
        all_forecasts = airtable.get_all_records('Federal Forecasts')
        forecasts = [f for f in all_forecasts 
                    if f['fields'].get('Priority') == 'HIGH' 
                    and f['fields'].get('Fit Score', 0) >= 80
                    and not f['fields'].get('Cap Statement Generated')
                    and f['fields'].get('Contracting Officer')]
    
    if not forecasts:
        return {
            'success': True,
            'processed': 0,
            'message': 'No high-priority forecasts found that need outreach'
        }
    
    print(f"\n🎯 Found {len(forecasts)} high-priority forecasts ready for outreach")
    print(f"Processing up to {limit}...\n")
    
    results = []
    for i, forecast in enumerate(forecasts[:limit], 1):
        try:
            fields = forecast['fields']
            title = fields.get('Title', 'Unknown')[:50]
            
            print(f"[{i}/{min(limit, len(forecasts))}] Processing: {title}...")
            
            result = forecast_outreach.generate_forecast_capstat_and_outreach(forecast['id'])
            
            if result['success']:
                # Get the outreach letter with ProposalBio scores
                outreach_letter = result.get('outreach_letter', {})
                
                results.append({
                    'forecast_id': result['forecast_id'],
                    'forecast_title': result['forecast_title'],
                    'officer_name': result['officer_name'],
                    'officer_email': result['officer_email'],
                    'outreach_record_id': result['outreach_record_id'],
                    'capstat_pdf': result['capstat_pdf'],
                    'proposalbio_score': outreach_letter.get('proposalbio_score'),
                    'quality_badge': outreach_letter.get('quality_badge'),
                })
                
                # Show ProposalBio score if available
                if outreach_letter.get('proposalbio_score') is not None:
                    score = outreach_letter['proposalbio_score']
                    badge = outreach_letter.get('quality_badge', '')
                    print(f"    {badge} ProposalBio™ Score: {score:.1f}/100")
                    
                    # Show improvements if needed
                    analysis = outreach_letter.get('proposalbio_analysis', {})
                    if score < 75 and analysis.get('letter_improvements'):
                        print(f"    💡 Top Improvements:")
                        for imp in analysis['letter_improvements'][:2]:
                            print(f"       {imp}")
                else:
                    print(f"    ⚪ NOT ANALYZED (ProposalBio unavailable)")
                
                print(f"    ✅ Complete! Outreach record: {result['outreach_record_id'][:8]}...")
            else:
                print(f"    ❌ Failed: {result.get('error')}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    print(f"\n{'='*70}")
    print(f"✅ Processed {len(results)} forecasts")
    
    # Show ProposalBio summary if available
    if results and results[0].get('proposalbio_score') is not None:
        avg_score = sum(r['proposalbio_score'] for r in results if r.get('proposalbio_score')) / len(results)
        print(f"📊 Average ProposalBio™ Score: {avg_score:.1f}/100")
        
        high_quality = sum(1 for r in results if r.get('proposalbio_score', 0) >= 75)
        print(f"🟢 High Quality (≥75): {high_quality} letters")
        
        needs_work = sum(1 for r in results if r.get('proposalbio_score', 100) < 60)
        if needs_work > 0:
            print(f"🔴 Needs Improvement (<60): {needs_work} letters")
    
    print(f"📋 Review in Airtable → Officer Outreach Tracking → 'Ready to Send' view")
    print(f"{'='*70}\n")
    
    return {
        'success': True,
        'processed': len(results),
        'results': results,
        'timestamp': datetime.now().isoformat(),
    }


if __name__ == "__main__":
    """
    Test the system with a sample forecast
    """
    print("🔮 FORECAST CAPABILITY STATEMENT OUTREACH SYSTEM")
    print("=" * 60)
    print("\nThis system generates:")
    print("  1. Tailored capability statements for forecasts")
    print("  2. Proactive introduction letters to contracting officers")
    print("  3. Complete tracking in Officer Outreach Tracking")
    print("\nTo use:")
    print("  from forecast_capstat_outreach import handle_forecast_capstat_outreach")
    print("  result = handle_forecast_capstat_outreach('recXXXXXXXXXXXX')")
    print("\nOr batch process:")
    print("  from forecast_capstat_outreach import process_high_priority_forecasts")
    print("  results = process_high_priority_forecasts(limit=5)")
    print("\n" + "=" * 60)
