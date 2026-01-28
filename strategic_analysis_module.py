"""
NEXUS Strategic Analysis Module
Implements RFP Success® Institute principles for strategic bid positioning

Complements ProposalBio™ (tactical quality) with strategic intelligence
Based on: "Compliance doesn't win, comfort does"

Author: NEXUS AI
Created: January 27, 2026
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from anthropic import Anthropic

# Airtable
from pyairtable import Api as AirtableApi

# Environment variables
AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# Initialize clients
airtable_api = AirtableApi(AIRTABLE_API_KEY)
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)


class StrategicAnalysisService:
    """
    Core service for strategic bid analysis
    Implements Go/No-Go scoring, evaluator profiling, and win theme management
    """
    
    def __init__(self):
        self.base = airtable_api.base(AIRTABLE_BASE_ID)
        
    # =====================================================
    # GO/NO-GO SCORECARD
    # =====================================================
    
    def calculate_go_no_go_score(
        self,
        opportunity_id: str,
        relationship_strength: int,
        price_competitiveness: int,
        technical_capability: int,
        resource_availability: int,
        past_performance: int
    ) -> Dict:
        """
        Calculate Go/No-Go score for bid decision
        
        Args:
            opportunity_id: Airtable record ID
            relationship_strength: 0-10 (pre-RFP contact with buyer)
            price_competitiveness: 0-10 (can you be competitive?)
            technical_capability: 0-10 (can you deliver?)
            resource_availability: 0-10 (do you have capacity?)
            past_performance: 0-10 (relevant experience?)
            
        Returns:
            {
                "total_score": 38,
                "recommendation": "Pursue",
                "win_probability": 65,
                "strengths": [...],
                "weaknesses": [...],
                "strategy": "..."
            }
        """
        
        # Calculate total score
        total_score = (
            relationship_strength +
            price_competitiveness +
            technical_capability +
            resource_availability +
            past_performance
        )
        
        # Determine recommendation
        if total_score < 25:
            recommendation = "Skip"
            win_probability = 15
        elif total_score < 35:
            recommendation = "Maybe"
            win_probability = 40
        else:
            recommendation = "Pursue"
            win_probability = 65
            
        # Identify strengths (scores >= 8)
        strengths = []
        if relationship_strength >= 8:
            strengths.append("Strong relationship with buyer")
        if price_competitiveness >= 8:
            strengths.append("Highly price competitive")
        if technical_capability >= 8:
            strengths.append("Excellent technical capability match")
        if resource_availability >= 8:
            strengths.append("Strong resource availability")
        if past_performance >= 8:
            strengths.append("Highly relevant past performance")
            
        # Identify weaknesses (scores <= 5)
        weaknesses = []
        if relationship_strength <= 5:
            weaknesses.append("Limited/no relationship with buyer - need outreach")
        if price_competitiveness <= 5:
            weaknesses.append("Price concern - may be 10-20% higher than competitors")
        if technical_capability <= 5:
            weaknesses.append("Technical capability gap - need partners/training")
        if resource_availability <= 5:
            weaknesses.append("Resource constraint - may need to hire/contract")
        if past_performance <= 5:
            weaknesses.append("Limited past performance in this category")
            
        # Generate strategy based on profile
        strategy = self._generate_win_strategy(
            total_score,
            relationship_strength,
            price_competitiveness,
            technical_capability,
            resource_availability,
            past_performance
        )
        
        # Save to Airtable
        try:
            opportunities_table = self.base.table('GPSS OPPORTUNITIES')
            opportunities_table.update(opportunity_id, {
                'Go/No-Go Score': total_score,
                'Relationship Strength': relationship_strength,
                'Price Competitiveness': price_competitiveness,
                'Technical Capability': technical_capability,
                'Resource Availability': resource_availability,
                'Past Performance Score': past_performance,
                'Strategic Recommendation': recommendation,
                'Win Probability': win_probability,
                'Strategic Notes': strategy,
                'Strategic Analysis Date': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Error saving Go/No-Go to Airtable: {e}")
            
        return {
            "total_score": total_score,
            "recommendation": recommendation,
            "win_probability": win_probability,
            "breakdown": {
                "relationship_strength": relationship_strength,
                "price_competitiveness": price_competitiveness,
                "technical_capability": technical_capability,
                "resource_availability": resource_availability,
                "past_performance": past_performance
            },
            "strengths": strengths,
            "weaknesses": weaknesses,
            "strategy": strategy
        }
        
    def _generate_win_strategy(
        self,
        total_score: int,
        relationship: int,
        price: int,
        technical: int,
        resources: int,
        past_perf: int
    ) -> str:
        """Generate strategic recommendations based on score profile"""
        
        strategies = []
        
        # Relationship strategy
        if relationship >= 8:
            strategies.append("✅ Leverage strong buyer relationship - mention past interactions")
        elif relationship <= 5:
            strategies.append("⚠️ CRITICAL: Initiate officer outreach NOW before submission")
            
        # Price strategy
        if price >= 8:
            strategies.append("✅ Lead with competitive pricing advantage")
        elif price <= 5:
            strategies.append("⚠️ Offset price concern by emphasizing value (local, responsive, quality)")
            
        # Technical strategy
        if technical >= 8:
            strategies.append("✅ Emphasize technical expertise and capability")
        elif technical <= 5:
            strategies.append("⚠️ Partner with subcontractor OR focus on proven process over technical specs")
            
        # Resource strategy
        if resources >= 8:
            strategies.append("✅ Highlight capacity and availability")
        elif resources <= 5:
            strategies.append("⚠️ Consider skip OR line up backup resources before bidding")
            
        # Past performance strategy
        if past_perf >= 8:
            strategies.append("✅ Lead with relevant past performance and references")
        elif past_perf <= 5:
            strategies.append("⚠️ Broaden past performance narrative - show transferable experience")
            
        # Overall strategy
        if total_score < 25:
            strategies.insert(0, "🔴 RECOMMENDATION: Skip this bid - too many weaknesses, low win probability")
        elif total_score < 35:
            strategies.insert(0, "🟡 RECOMMENDATION: Proceed with caution - address weaknesses or skip")
        else:
            strategies.insert(0, "🟢 RECOMMENDATION: Pursue - good win probability if executed well")
            
        return "\n".join(strategies)
    
    # =====================================================
    # EVALUATOR STYLE ANALYZER
    # =====================================================
    
    def analyze_evaluator_style(
        self,
        opportunity_id: str,
        rfp_text: str,
        agency_name: Optional[str] = None
    ) -> Dict:
        """
        Analyze RFP text to detect evaluator behavioral style
        Uses AI to identify: Analytical, Driver, Expressive, or Amiable
        
        Args:
            opportunity_id: Airtable record ID
            rfp_text: Full RFP text
            agency_name: Optional agency name for historical lookup
            
        Returns:
            {
                "primary_style": "Analytical",
                "secondary_style": "Amiable",
                "confidence": 85,
                "indicators": [...],
                "proposal_recommendations": [...]
            }
        """
        
        # Use Claude AI for style detection
        analysis_prompt = f"""Analyze this RFP to determine the evaluator's behavioral style.

RFP TEXT:
{rfp_text[:8000]}  # Limit to avoid token limits

TASK: Identify the PRIMARY and SECONDARY behavioral styles of the evaluators based on the RFP language, structure, and emphasis.

FOUR BEHAVIORAL STYLES:

1. ANALYTICAL (Data-Driven)
   - Characteristics: Detailed, precise, numbers-focused, thorough
   - RFP Indicators: Heavy technical specs, detailed requirements matrices, metrics emphasis, precise terminology
   - Scoring criteria: Heavily weighted on technical compliance
   
2. DRIVER (Results-Oriented)
   - Characteristics: Fast decisions, bottom-line focused, impatient, direct
   - RFP Indicators: Short deadlines, "executive summary required", clear deliverables, concise language
   - Scoring criteria: Price and delivery timeline heavily weighted
   
3. EXPRESSIVE (Relationship-Focused)
   - Characteristics: Values-driven, emotional connection, vision-oriented, enthusiastic
   - RFP Indicators: Mission statements, community impact, partnership language, qualitative criteria
   - Scoring criteria: Company values, cultural fit, passion for mission
   
4. AMIABLE (Consensus-Driven)
   - Characteristics: Risk-averse, team-focused, trust-building, collaborative
   - RFP Indicators: Multiple stakeholders mentioned, committee review, references required, team emphasis
   - Scoring criteria: References, team credentials, proven track record

RESPONSE FORMAT (JSON):
{{
  "primary_style": "Analytical" | "Driver" | "Expressive" | "Amiable",
  "primary_confidence": 0-100,
  "secondary_style": "Analytical" | "Driver" | "Expressive" | "Amiable",
  "secondary_confidence": 0-100,
  "indicators": ["Indicator 1", "Indicator 2", "Indicator 3"],
  "proposal_recommendations": [
    "Recommendation 1",
    "Recommendation 2",
    "Recommendation 3"
  ],
  "reasoning": "Brief explanation of style determination"
}}

Respond ONLY with valid JSON."""

        try:
            # Call Claude API
            response = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": analysis_prompt}
                ]
            )
            
            # Parse response
            response_text = response.content[0].text
            
            # Extract JSON (handle markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
            
            analysis = json.loads(response_text)
            
            # Calculate overall confidence
            overall_confidence = int(
                (analysis['primary_confidence'] * 0.7) +
                (analysis.get('secondary_confidence', 0) * 0.3)
            )
            
            # Save to Airtable
            try:
                opportunities_table = self.base.table('GPSS OPPORTUNITIES')
                opportunities_table.update(opportunity_id, {
                    'Evaluator Style Primary': analysis['primary_style'],
                    'Evaluator Style Secondary': analysis.get('secondary_style'),
                    'Evaluator Confidence': overall_confidence
                })
                
                # Also save to EVALUATOR PROFILES table (if exists)
                try:
                    profiles_table = self.base.table('EVALUATOR PROFILES')
                    profiles_table.create({
                        'Agency Name': agency_name or 'Unknown',
                        'Detected Style': analysis['primary_style'],
                        'Confidence Score': overall_confidence,
                        'RFP Text Analyzed': rfp_text[:5000],  # Truncate for storage
                        'Detection Date': datetime.now().isoformat(),
                        'Linked Opportunity': [opportunity_id]
                    })
                except Exception as e:
                    print(f"Could not save to EVALUATOR PROFILES (table may not exist): {e}")
                    
            except Exception as e:
                print(f"Error saving evaluator profile to Airtable: {e}")
            
            return {
                "primary_style": analysis['primary_style'],
                "secondary_style": analysis.get('secondary_style'),
                "confidence": overall_confidence,
                "indicators": analysis.get('indicators', []),
                "proposal_recommendations": analysis.get('proposal_recommendations', []),
                "reasoning": analysis.get('reasoning', '')
            }
            
        except Exception as e:
            print(f"Error in evaluator style analysis: {e}")
            return {
                "primary_style": "Unknown",
                "secondary_style": None,
                "confidence": 0,
                "indicators": [],
                "proposal_recommendations": ["Unable to analyze - use balanced approach"],
                "error": str(e)
            }
    
    # =====================================================
    # WIN THEMES LIBRARY
    # =====================================================
    
    def get_win_themes(self, industry: Optional[str] = None) -> List[Dict]:
        """
        Fetch available win themes from library
        
        Args:
            industry: Optional filter by industry
            
        Returns:
            List of win theme dictionaries
        """
        try:
            themes_table = self.base.table('WIN THEMES LIBRARY')
            
            # Build filter formula
            formula = "AND({Active} = 1"
            if industry:
                formula += f", FIND('{industry}', {{Applicable Industries}})"
            formula += ")"
            
            records = themes_table.all(formula=formula)
            
            themes = []
            for record in records:
                fields = record['fields']
                themes.append({
                    'id': record['id'],
                    'name': fields.get('Theme Name'),
                    'description': fields.get('Theme Description'),
                    'category': fields.get('Theme Category'),
                    'talking_points': fields.get('Talking Points', '').split('\n'),
                    'strength': fields.get('Strength Rating', 3),
                    'win_rate': fields.get('Win Rate When Used', 0),
                    'times_used': fields.get('Times Used', 0)
                })
                
            return themes
            
        except Exception as e:
            print(f"Error fetching win themes: {e}")
            # Return default Dee Davis Inc. themes
            return self._get_default_win_themes()
    
    def _get_default_win_themes(self) -> List[Dict]:
        """Default win themes for Dee Davis Inc."""
        return [
            {
                'id': 'default_1',
                'name': 'Michigan EDWOSB Certified',
                'description': 'Certified woman-owned small business based in Michigan',
                'category': 'Certification',
                'talking_points': [
                    'EDWOSB certified - eligible for set-asides and preferences',
                    'Supports small business and diversity goals',
                    'Michigan-based for local/regional preference'
                ],
                'strength': 5,
                'win_rate': 72
            },
            {
                'id': 'default_2',
                'name': 'Local Michigan Supplier',
                'description': 'Based in Michigan for fast delivery and lower costs',
                'category': 'Location',
                'talking_points': [
                    'Lower freight costs than out-of-state suppliers',
                    'Faster delivery times - 1-3 days vs 1-2 weeks',
                    'Support local Michigan economy'
                ],
                'strength': 4,
                'win_rate': 68
            },
            {
                'id': 'default_3',
                'name': 'Responsive Direct Communication',
                'description': 'Direct access to owner, no corporate bureaucracy',
                'category': 'Service',
                'talking_points': [
                    'Direct communication with ownership',
                    'No corporate red tape or layers',
                    'Quick decisions and problem resolution'
                ],
                'strength': 4,
                'win_rate': 61
            },
            {
                'id': 'default_4',
                'name': 'Government Compliance Expert',
                'description': 'Deep understanding of public sector requirements',
                'category': 'Experience',
                'talking_points': [
                    'Experienced with government contracting requirements',
                    'SAM.gov registered and compliant',
                    'Understand public procurement processes'
                ],
                'strength': 4,
                'win_rate': 65
            },
            {
                'id': 'default_5',
                'name': 'Small Business Flexibility',
                'description': 'Agile and adaptable to unique agency needs',
                'category': 'Service',
                'talking_points': [
                    'Flexible to accommodate special requirements',
                    'Not locked into rigid corporate policies',
                    'Can customize solutions to your needs'
                ],
                'strength': 3,
                'win_rate': 58
            }
        ]
    
    def select_optimal_win_themes(
        self,
        opportunity_id: str,
        all_themes: List[Dict],
        rfp_text: str
    ) -> List[Dict]:
        """
        Use AI to select 3-5 optimal win themes for this opportunity
        
        Args:
            opportunity_id: Airtable record ID
            all_themes: All available themes
            rfp_text: RFP text for context
            
        Returns:
            List of selected theme dictionaries
        """
        
        themes_description = "\n".join([
            f"{i+1}. {theme['name']} (Win Rate: {theme['win_rate']}%)\n   - {theme['description']}"
            for i, theme in enumerate(all_themes)
        ])
        
        selection_prompt = f"""Select the 3-5 most effective win themes for this RFP.

AVAILABLE WIN THEMES:
{themes_description}

RFP CONTEXT (first 3000 chars):
{rfp_text[:3000]}

TASK: Select 3-5 win themes that:
1. Are most relevant to this RFP's requirements
2. Have highest win rates
3. Address evaluator's likely concerns
4. Differentiate from competitors

RESPONSE FORMAT (JSON):
{{
  "selected_theme_numbers": [1, 2, 4],
  "reasoning": "Brief explanation of why these themes were selected"
}}

Respond ONLY with valid JSON."""

        try:
            response = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": selection_prompt}
                ]
            )
            
            response_text = response.content[0].text
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
                
            selection = json.loads(response_text)
            
            # Get selected themes
            selected = [
                all_themes[idx - 1]
                for idx in selection['selected_theme_numbers']
                if 0 < idx <= len(all_themes)
            ]
            
            # Save selection to Airtable
            try:
                opportunities_table = self.base.table('GPSS OPPORTUNITIES')
                theme_names = [t['name'] for t in selected]
                opportunities_table.update(opportunity_id, {
                    'Selected Win Themes': theme_names
                })
            except Exception as e:
                print(f"Error saving win themes to Airtable: {e}")
            
            return selected
            
        except Exception as e:
            print(f"Error selecting win themes: {e}")
            # Return top 3 by win rate
            sorted_themes = sorted(all_themes, key=lambda x: x['win_rate'], reverse=True)
            return sorted_themes[:3]
    
    # =====================================================
    # STRATEGIC REPORT
    # =====================================================
    
    def generate_strategic_report(self, opportunity_id: str) -> Dict:
        """
        Generate comprehensive strategic analysis report
        Combines Go/No-Go, evaluator profile, win themes, and recommendations
        
        Args:
            opportunity_id: Airtable record ID
            
        Returns:
            Complete strategic report dictionary
        """
        try:
            opportunities_table = self.base.table('GPSS OPPORTUNITIES')
            record = opportunities_table.get(opportunity_id)
            fields = record['fields']
            
            # Build report
            report = {
                'opportunity_id': opportunity_id,
                'opportunity_name': fields.get('Opportunity Name'),
                'agency': fields.get('Agency'),
                'deadline': fields.get('Deadline'),
                'estimated_value': fields.get('Estimated Value'),
                
                # Go/No-Go Analysis
                'go_no_go_score': fields.get('Go/No-Go Score', 0),
                'strategic_recommendation': fields.get('Strategic Recommendation', 'Unknown'),
                'win_probability': fields.get('Win Probability', 0),
                'strategic_notes': fields.get('Strategic Notes', ''),
                
                # Score Breakdown
                'breakdown': {
                    'relationship_strength': fields.get('Relationship Strength', 0),
                    'price_competitiveness': fields.get('Price Competitiveness', 0),
                    'technical_capability': fields.get('Technical Capability', 0),
                    'resource_availability': fields.get('Resource Availability', 0),
                    'past_performance': fields.get('Past Performance Score', 0)
                },
                
                # Evaluator Profile
                'evaluator_profile': {
                    'primary_style': fields.get('Evaluator Style Primary'),
                    'secondary_style': fields.get('Evaluator Style Secondary'),
                    'confidence': fields.get('Evaluator Confidence', 0)
                },
                
                # Win Themes
                'selected_win_themes': fields.get('Selected Win Themes', []),
                
                # Analysis Date
                'analysis_date': fields.get('Strategic Analysis Date')
            }
            
            return report
            
        except Exception as e:
            print(f"Error generating strategic report: {e}")
            return {
                'error': str(e),
                'opportunity_id': opportunity_id
            }


# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def initialize_win_themes_library():
    """
    One-time initialization of WIN THEMES LIBRARY table
    Creates default Dee Davis Inc. win themes
    """
    try:
        airtable_api = AirtableApi(AIRTABLE_API_KEY)
        base = airtable_api.base(AIRTABLE_BASE_ID)
        themes_table = base.table('WIN THEMES LIBRARY')
        
        default_themes = [
            {
                'Theme Name': 'Michigan EDWOSB Certified',
                'Theme Description': 'Certified woman-owned small business (EDWOSB) based in Michigan with federal certifications',
                'Theme Category': 'Certification',
                'Talking Points': """- EDWOSB certified - eligible for federal set-asides and preferences
- Supports small business and diversity goals
- Michigan-based for local/regional preference
- Registered in SAM.gov with active certifications""",
                'Strength Rating': 5,
                'Applicable Industries': ['Government', 'Federal', 'State', 'Municipal'],
                'Active': True
            },
            {
                'Theme Name': 'Local Michigan Supplier',
                'Theme Description': 'Michigan-based supplier providing faster delivery and lower freight costs',
                'Theme Category': 'Location',
                'Talking Points': """- Lower freight costs than out-of-state suppliers (15-30% savings)
- Faster delivery times - 1-3 days vs 1-2 weeks
- Support local Michigan economy and jobs
- Available for in-person meetings and site visits""",
                'Strength Rating': 4,
                'Applicable Industries': ['Government', 'Construction', 'Industrial'],
                'Active': True
            },
            {
                'Theme Name': 'Responsive Direct Communication',
                'Theme Description': 'Direct access to business owner with no corporate bureaucracy',
                'Theme Category': 'Service',
                'Talking Points': """- Direct communication with business ownership
- No corporate red tape or multiple approval layers
- Quick decisions and rapid problem resolution
- Personal accountability and relationship continuity""",
                'Strength Rating': 4,
                'Applicable Industries': ['Government', 'All'],
                'Active': True
            },
            {
                'Theme Name': 'Government Compliance Expert',
                'Theme Description': 'Deep understanding of public sector procurement requirements',
                'Theme Category': 'Experience',
                'Talking Points': """- Experienced with government contracting requirements
- SAM.gov registered and fully compliant
- Understand public procurement processes and timelines
- Familiar with federal, state, and municipal regulations""",
                'Strength Rating': 4,
                'Applicable Industries': ['Government', 'Federal', 'State', 'Municipal'],
                'Active': True
            },
            {
                'Theme Name': 'Small Business Flexibility',
                'Theme Description': 'Agile and adaptable to accommodate unique agency requirements',
                'Theme Category': 'Service',
                'Talking Points': """- Flexible to accommodate special requirements
- Not locked into rigid corporate policies
- Can customize solutions to specific needs
- Willing to work with agency processes and preferences""",
                'Strength Rating': 3,
                'Applicable Industries': ['Government', 'All'],
                'Active': True
            },
            {
                'Theme Name': 'Proven Past Performance',
                'Theme Description': 'Track record of successful contract delivery to similar agencies',
                'Theme Category': 'Experience',
                'Talking Points': """- Successfully delivered similar contracts
- Positive references from government clients
- On-time delivery and budget compliance
- Lessons learned from past projects applied to new work""",
                'Strength Rating': 5,
                'Applicable Industries': ['Government', 'All'],
                'Active': True
            }
        ]
        
        print("Initializing WIN THEMES LIBRARY...")
        for theme in default_themes:
            try:
                themes_table.create(theme)
                print(f"✅ Created theme: {theme['Theme Name']}")
            except Exception as e:
                print(f"❌ Error creating theme {theme['Theme Name']}: {e}")
                
        print("\n✅ WIN THEMES LIBRARY initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing WIN THEMES LIBRARY: {e}")


if __name__ == "__main__":
    print("Strategic Analysis Module - Test")
    print("=" * 50)
    
    # Test initialization
    print("\nInitializing WIN THEMES LIBRARY...")
    initialize_win_themes_library()
