"""
CONTRACTING OFFICER OUTREACH SYSTEM
Automatically generate introduction letters for closed opportunities
Turn missed bids into relationship-building opportunities

Part of NEXUS Backend - Dee Davis Inc

INTEGRATES WITH: ProposalBio™ Quality Assurance
All letters are analyzed with 10 biohacks for maximum persuasiveness
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
from pyairtable import Api

# Import ProposalBio™ for quality analysis
try:
    from proposalbio_module import ProposalBioAnalyzer
    PROPOSALBIO_AVAILABLE = True
except ImportError:
    PROPOSALBIO_AVAILABLE = False
    print("⚠️ ProposalBio module not available - letters will generate without quality scoring")


class ContractingOfficerOutreachAgent:
    """
    Automatically generates introduction letters for closed opportunities
    Tracks outreach to contracting officers for relationship building
    """
    
    def __init__(self, airtable_client):
        self.airtable = airtable_client
        self.company_info = self._load_company_info()
    
    def _load_company_info(self) -> Dict:
        """Load company information from environment or Airtable"""
        return {
            'company_name': os.getenv('COMPANY_NAME', 'Dee Davis, Inc.'),
            'contact_name': os.getenv('CONTACT_NAME', 'Dee Davis'),
            'contact_title': os.getenv('CONTACT_TITLE', 'President'),
            'contact_email': os.getenv('CONTACT_EMAIL', 'info@deedavis.biz'),
            'contact_phone': os.getenv('CONTACT_PHONE', '248-376-4550'),
            'cage_code': os.getenv('CAGE_CODE', '8UMX3'),
            'uei_number': os.getenv('UEI_NUMBER', 'SAM.gov Active'),
            'gsa_schedule': os.getenv('GSA_SCHEDULE', ''),
            'certifications': os.getenv('CERTIFICATIONS', 'Economically Disadvantaged Woman-Owned Small Business (EDWOSB), Woman-Owned Small Business (WOSB), Minority Business Enterprise (MBE), Women\'s Business Enterprise (WBE)'),
            'business_description': os.getenv('BUSINESS_DESCRIPTION', 'certified diverse small business enterprise with extensive experience in medical supply procurement and distribution. We specialize in providing high-quality healthcare products to government agencies and healthcare facilities, with a particular focus on preventive health and family planning supplies.'),
        }
    
    def identify_closed_opportunities(self, days_old: int = 30) -> List[Dict]:
        """
        Find closed/inactive opportunities that we haven't reached out to yet
        
        Args:
            days_old: Look for opportunities closed in the last X days
        
        Returns:
            List of opportunities to reach out on
        """
        
        try:
            # Get all opportunities
            opportunities = self.airtable.get_all_records('Opportunities')
            
            closed_opps = []
            
            for opp in opportunities:
                fields = opp.get('fields', {})
                
                # Check if opportunity is closed/inactive
                status = fields.get('Status', '').lower()
                
                # Check if we already reached out
                already_reached_out = fields.get('Officer Outreach Sent', False)
                
                if status in ['closed', 'inactive', 'archived', 'cancelled'] and not already_reached_out:
                    # Check if it has contracting officer info
                    officer_name = fields.get('Point of Contact', '')
                    officer_email = fields.get('Contact Email', '')
                    
                    if officer_name or officer_email:
                        closed_opps.append({
                            'record_id': opp['id'],
                            'title': fields.get('Title', 'Opportunity'),
                            'solicitation_number': fields.get('Solicitation Number', ''),
                            'agency': fields.get('Agency', ''),
                            'officer_name': officer_name,
                            'officer_email': officer_email,
                            'naics_code': fields.get('NAICS Code', ''),
                            'description': fields.get('Description', ''),
                            'close_date': fields.get('Response Deadline', ''),
                        })
            
            return closed_opps
            
        except Exception as e:
            print(f"Error identifying closed opportunities: {e}")
            return []
    
    def generate_introduction_letter(self, opportunity: Dict) -> Dict:
        """
        Generate a personalized introduction letter for a closed opportunity
        
        Args:
            opportunity: Dictionary with opportunity details
        
        Returns:
            Dictionary with letter content, metadata, and ProposalBio™ quality score
        """
        
        # Extract opportunity details
        title = opportunity.get('title', 'Opportunity')
        solicitation = opportunity.get('solicitation_number', '')
        agency = opportunity.get('agency', '')
        officer_name = opportunity.get('officer_name', 'Contracting Officer')
        officer_email = opportunity.get('officer_email', '')
        naics = opportunity.get('naics_code', '')
        description = opportunity.get('description', '')[:200]  # First 200 chars
        
        # Determine salutation
        if officer_name and officer_name != 'Contracting Officer':
            # Try to parse last name
            name_parts = officer_name.split()
            if len(name_parts) >= 2:
                salutation = f"Dear Ms./Mr. {name_parts[-1]},"
            else:
                salutation = f"Dear {officer_name},"
        else:
            salutation = "Dear Contracting Officer,"
        
        # Generate letter based on opportunity type
        letter_body = self._generate_letter_body(opportunity)
        
        # Create full letter
        today = datetime.now().strftime("%B %d, %Y")
        
        letter = f"""**Date:** {today}

**To:** {officer_name}
**Email:** {officer_email}
**Re:** {title}
**Solicitation:** {solicitation}
**Agency:** {agency}

---

{salutation}

{letter_body}

**Contact Information:**

**Company:** {self.company_info['company_name']}
**Point of Contact:** {self.company_info['contact_name']}
**Email:** {self.company_info['contact_email']}
**Phone:** {self.company_info['contact_phone']}
**CAGE Code:** {self.company_info['cage_code']}
**UEI/SAM Registration:** {self.company_info['uei_number']}

We appreciate your consideration and look forward to the opportunity to serve your agency's needs. Please do not hesitate to contact us if you require any additional information about our company or capabilities.

Thank you for your time and consideration.

Respectfully,

{self.company_info['contact_name']}
{self.company_info['contact_title']}
{self.company_info['company_name']}

---

**Enclosures:**
- Company Capability Statement
- Relevant Certifications
- Past Performance References
"""
        
        result = {
            'letter': letter,
            'recipient_name': officer_name,
            'recipient_email': officer_email,
            'subject_line': f"Introduction - {self.company_info['company_name']} - {title} ({solicitation})",
            'opportunity_title': title,
            'solicitation_number': solicitation,
        }
        
        # Run ProposalBio™ quality analysis
        if PROPOSALBIO_AVAILABLE:
            try:
                proposalbio_analysis = self._analyze_letter_quality(letter, agency, officer_name)
                result['proposalbio_score'] = proposalbio_analysis['composite_score']
                result['proposalbio_status'] = proposalbio_analysis['overall_status']
                result['proposalbio_analysis'] = proposalbio_analysis
                
                # Add quality badge to result
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
    
    def _generate_letter_body(self, opportunity: Dict) -> str:
        """Generate the main body of the introduction letter"""
        
        title = opportunity.get('title', 'this opportunity')
        solicitation = opportunity.get('solicitation_number', '')
        
        body = f"""I am writing to introduce **{self.company_info['company_name']}** and express our strong interest in providing products and services related to {title}.

**Company Overview:**

{self.company_info['company_name']} is a {self.company_info['business_description']}

**Our Qualifications:**

- **Diverse Certification:** {self.company_info['certifications']}"""
        
        if self.company_info.get('gsa_schedule'):
            body += f"\n- **GSA Schedule:** {self.company_info['gsa_schedule']}"
        
        body += """
- **Quality Assurance:** We source products from reputable manufacturers and maintain rigorous quality standards
- **Reliable Supply Chain:** Established relationships with distributors ensure consistent availability
- **Competitive Pricing:** Volume purchasing power allows us to offer cost-effective solutions
- **Proven Track Record:** History of successful government contracts and on-time deliveries

**Our Interest:**

While we understand the solicitation period for this opportunity has closed, we wanted to formally introduce our company and express our strong interest in being considered for this and any future requirements your agency may have."""

        if solicitation:
            body += f" We are particularly interested in opportunities similar to {solicitation}."
        
        body += """

We are prepared to:
- Provide product specifications and samples upon request
- Submit pricing proposals for your review
- Demonstrate our supply chain capabilities
- Share references from other government contracts

**Request:**

We respectfully request the opportunity to:
1. Be added to your vendor database for future procurements
2. Receive notification of upcoming solicitations for similar items
3. Schedule a brief call or meeting to discuss your specific requirements
4. Provide additional company information or capability statements as needed"""
        
        return body
    
    def _analyze_letter_quality(self, letter_text: str, agency: str, officer_name: str) -> Dict:
        """
        Analyze letter quality using ProposalBio™ 10 Biohacks
        
        Args:
            letter_text: Full letter content
            agency: Agency name for name recognition scoring
            officer_name: Officer name for personalization
        
        Returns:
            ProposalBio™ analysis results with composite score and recommendations
        """
        
        if not PROPOSALBIO_AVAILABLE:
            return {
                'composite_score': 0,
                'overall_status': 'NOT_ANALYZED',
                'error': 'ProposalBio module not available'
            }
        
        try:
            # Prepare metadata for ProposalBio analysis
            metadata = {
                'client_name': agency,
                'agency': agency,
                'officer_name': officer_name,
                'document_type': 'introduction_letter',
                'rfp_keywords': [],  # No RFP for closed opportunities
            }
            
            # Run ProposalBio™ analysis
            analyzer = ProposalBioAnalyzer(letter_text, metadata)
            analysis = analyzer.analyze_all()
            
            # Add context-specific recommendations for introduction letters
            if analysis['composite_score'] < 75:
                analysis['letter_improvements'] = self._get_letter_improvements(analysis)
            
            return analysis
            
        except Exception as e:
            print(f"ProposalBio analysis error: {e}")
            return {
                'composite_score': 0,
                'overall_status': 'ERROR',
                'error': str(e)
            }
    
    def _get_letter_improvements(self, analysis: Dict) -> List[str]:
        """
        Get specific improvements for introduction letters based on ProposalBio™ scores
        
        Args:
            analysis: ProposalBio™ analysis results
        
        Returns:
            List of actionable improvements
        """
        improvements = []
        
        biohack_scores = {item['biohack_number']: item['score'] 
                         for item in analysis.get('biohack_scores', [])}
        
        # Biohack #7: Name Recognition (critical for introduction letters)
        if biohack_scores.get(7, 0) < 6:
            improvements.append("🎯 Use the agency name more frequently (target: 3-5 times in letter)")
        
        # Biohack #2: Cognitive Ease (keep it simple)
        if biohack_scores.get(2, 0) < 6:
            improvements.append("✂️ Shorten sentences (target: 12 words or less per sentence)")
        
        # Biohack #8: Sensory Language (paint a picture)
        if biohack_scores.get(8, 0) < 6:
            improvements.append("🎨 Replace vague terms like 'quality' and 'experience' with concrete examples")
        
        # Biohack #3: Story Arc (tell a story)
        if biohack_scores.get(3, 0) < 6:
            improvements.append("📖 Add a brief story about a past successful delivery or contract")
        
        # Biohack #10: Eye Tracking (visual hierarchy)
        if biohack_scores.get(10, 0) < 6:
            improvements.append("👁️ Add more white space and bold section headers for easy scanning")
        
        # Biohack #4: Reciprocity (give value first)
        if biohack_scores.get(4, 0) < 6:
            improvements.append("🎁 Offer something valuable upfront (free analysis, industry insights, samples)")
        
        return improvements[:3]  # Top 3 most important improvements
    
    def create_outreach_record(self, opportunity: Dict, letter: Dict) -> str:
        """
        Create a record in Airtable to track this outreach
        
        Args:
            opportunity: Original opportunity data
            letter: Generated letter data (includes ProposalBio™ score)
        
        Returns:
            Record ID of created outreach record
        """
        
        try:
            # Prepare record fields
            record_fields = {
                'Officer Name': letter['recipient_name'],
                'Officer Email': letter['recipient_email'],
                'Opportunity Title': letter['opportunity_title'],
                'Solicitation Number': letter['solicitation_number'],
                'Letter Generated Date': datetime.now().isoformat(),
                'Status': 'Draft',
                'Letter Content': letter['letter'],
                'Subject Line': letter['subject_line'],
                'Related Opportunity': [opportunity['record_id']],  # Link to opportunity
            }
            
            # Add ProposalBio™ quality scores if available
            if letter.get('proposalbio_score') is not None:
                record_fields['ProposalBio Score'] = letter['proposalbio_score']
                record_fields['Quality Badge'] = letter.get('quality_badge', '')
                
                # Add quality status
                if letter['proposalbio_score'] >= 75:
                    record_fields['Quality Status'] = 'Ready to Send'
                elif letter['proposalbio_score'] >= 60:
                    record_fields['Quality Status'] = 'Good - Minor Edits'
                else:
                    record_fields['Quality Status'] = 'Needs Improvement'
                
                # Add improvement notes if score is low
                analysis = letter.get('proposalbio_analysis', {})
                if analysis.get('letter_improvements'):
                    improvements = "\n".join(f"• {imp}" for imp in analysis['letter_improvements'])
                    record_fields['Improvement Notes'] = f"ProposalBio™ Recommendations:\n{improvements}"
            
            # Create record in Officer Outreach Tracking table
            record = self.airtable.create_record('Officer Outreach Tracking', record_fields)
            
            # Update opportunity to mark outreach initiated
            self.airtable.update_record('Opportunities', opportunity['record_id'], {
                'Officer Outreach Sent': True,
                'Officer Outreach Date': datetime.now().isoformat(),
            })
            
            return record['id']
            
        except Exception as e:
            print(f"Error creating outreach record: {e}")
            return None
    
    def process_closed_opportunities(self, limit: int = 10) -> List[Dict]:
        """
        Main workflow: Find closed opportunities and generate letters
        
        Args:
            limit: Maximum number of opportunities to process
        
        Returns:
            List of generated letters with metadata and ProposalBio™ scores
        """
        
        # Find closed opportunities
        closed_opps = self.identify_closed_opportunities()
        
        if not closed_opps:
            print("No closed opportunities found that need outreach")
            return []
        
        print(f"Found {len(closed_opps)} closed opportunities to reach out on")
        print(f"\n{'='*70}")
        print(f"GENERATING LETTERS WITH PROPOSALBIO™ QUALITY ANALYSIS")
        print(f"{'='*70}\n")
        
        # Process up to limit
        results = []
        for i, opp in enumerate(closed_opps[:limit], 1):
            try:
                print(f"\n[{i}/{min(limit, len(closed_opps))}] Processing: {opp['title'][:50]}...")
                
                # Generate letter with ProposalBio™ analysis
                letter = self.generate_introduction_letter(opp)
                
                # Show quality score
                if letter.get('proposalbio_score') is not None:
                    score = letter['proposalbio_score']
                    badge = letter.get('quality_badge', '')
                    print(f"    {badge} ProposalBio™ Score: {score:.1f}/100")
                    
                    # Show improvements if needed
                    analysis = letter.get('proposalbio_analysis', {})
                    if score < 75 and analysis.get('letter_improvements'):
                        print(f"    💡 Top Improvements:")
                        for imp in analysis['letter_improvements'][:2]:
                            print(f"       {imp}")
                else:
                    print(f"    ⚪ NOT ANALYZED (ProposalBio unavailable)")
                
                # Create tracking record
                record_id = self.create_outreach_record(opp, letter)
                
                if record_id:
                    results.append({
                        'opportunity': opp['title'],
                        'officer': letter['recipient_name'],
                        'email': letter['recipient_email'],
                        'record_id': record_id,
                        'letter': letter['letter'],
                        'proposalbio_score': letter.get('proposalbio_score'),
                        'quality_badge': letter.get('quality_badge'),
                        'quality_analysis': letter.get('proposalbio_analysis'),
                    })
                    
                    print(f"    ✅ Letter saved to Airtable (ID: {record_id[:8]}...)")
                else:
                    print(f"    ⚠️ Failed to create record")
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")
        
        # Summary
        print(f"\n{'='*70}")
        print(f"GENERATION COMPLETE")
        print(f"{'='*70}")
        print(f"✅ Generated: {len(results)} letters")
        
        if results and results[0].get('proposalbio_score') is not None:
            avg_score = sum(r['proposalbio_score'] for r in results if r.get('proposalbio_score')) / len(results)
            print(f"📊 Average ProposalBio™ Score: {avg_score:.1f}/100")
            
            high_quality = sum(1 for r in results if r.get('proposalbio_score', 0) >= 75)
            print(f"🟢 High Quality (≥75): {high_quality} letters")
            
            needs_work = sum(1 for r in results if r.get('proposalbio_score', 100) < 60)
            if needs_work > 0:
                print(f"🔴 Needs Improvement (<60): {needs_work} letters")
        
        print(f"\n📋 Review letters in Airtable > Officer Outreach Tracking")
        print(f"{'='*70}\n")
        
        return results
    
    def export_letter_to_file(self, letter_data: Dict, output_dir: str = "./outreach_letters/") -> str:
        """
        Export a letter to a markdown file
        
        Args:
            letter_data: Letter data from generate_introduction_letter
            output_dir: Directory to save letters
        
        Returns:
            Path to saved file
        """
        
        import os
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename
        solicitation = letter_data.get('solicitation_number', 'NO_SOL')
        solicitation = solicitation.replace('/', '_').replace(' ', '_')
        filename = f"{output_dir}{solicitation}_intro_letter.md"
        
        # Write file
        with open(filename, 'w') as f:
            f.write(f"# Introduction Letter - {letter_data['opportunity_title']}\n\n")
            f.write(letter_data['letter'])
            f.write(f"\n\n---\n\n## EMAIL TEMPLATE\n\n")
            f.write(f"**TO:** {letter_data['recipient_email']}\n\n")
            f.write(f"**SUBJECT:** {letter_data['subject_line']}\n\n")
            f.write("**BODY:**\n\n")
            f.write(f"Dear {letter_data['recipient_name'].split()[-1] if letter_data['recipient_name'] else 'Contracting Officer'},\n\n")
            f.write("Please find attached our introduction letter expressing interest in your agency's procurement needs.\n\n")
            f.write("We would appreciate the opportunity to be considered for future solicitations.\n\n")
            f.write("Thank you for your consideration.\n\n")
            f.write(f"Best regards,\n{self.company_info['contact_name']}\n")
        
        return filename


# =====================================================================
# INTEGRATION WITH EXISTING MINING SYSTEM
# =====================================================================

def run_officer_outreach_mining(airtable_client, limit: int = 10) -> Dict:
    """
    Run the contracting officer outreach mining process
    This can be called from the main mining workflow
    
    Args:
        airtable_client: AirtableClient instance
        limit: Maximum number of letters to generate
    
    Returns:
        Summary of results
    """
    
    outreach_agent = ContractingOfficerOutreachAgent(airtable_client)
    results = outreach_agent.process_closed_opportunities(limit=limit)
    
    return {
        'letters_generated': len(results),
        'results': results,
        'timestamp': datetime.now().isoformat(),
    }


if __name__ == "__main__":
    # Test the system
    from nexus_backend import AirtableClient
    
    print("🎯 CONTRACTING OFFICER OUTREACH SYSTEM")
    print("=" * 60)
    
    airtable = AirtableClient()
    result = run_officer_outreach_mining(airtable, limit=5)
    
    print(f"\n✅ Generated {result['letters_generated']} introduction letters")
    print("\nReview letters in Airtable > Officer Outreach Tracking table")
