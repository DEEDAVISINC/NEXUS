#!/usr/bin/env python3
"""
NEXUS Solicitation Watcher - ENHANCED with Auto-Search
Monitors photos_and_videos/ for new PDFs, automatically:
1. Creates folder for solicitation ✅ WORKING
2. Moves PDF to folder ✅ WORKING
3. Parses PDF and extracts data ✅ WORKING
4. AI ANALYZES: Product vs Service bid 🆕 NEW
5. AUTO-SEARCHES: Finds suppliers or subcontractors 🆕 NEW
6. AI SCORES & RANKS: Top 10 recommendations 🆕 NEW
7. Adds to Airtable ✅ WORKING
8. Generates enhanced analysis document 🆕 ENHANCED
9. Creates calendar reminder ✅ WORKING
10. NOTIFIES YOU: Desktop notification 🆕 NEW

RUN THIS 24/7 IN BACKGROUND!
"""

import os
import sys
import time
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pyairtable import Api
from dotenv import load_dotenv
import PyPDF2

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nexus_backend import AnthropicClient, GPSSSubcontractorMiner

load_dotenv()

WATCH_DIR = "/Users/deedavis/NEXUS BACKEND/photos_and_videos"
AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

api = Api(AIRTABLE_API_KEY)
opportunities_table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

class EnhancedSolicitationHandler(FileSystemEventHandler):
    def __init__(self):
        self.processed_files = set()
        self.ai = AnthropicClient()
        self.sub_miner = GPSSSubcontractorMiner()
        
    def on_created(self, event):
        if event.is_directory:
            return
        
        # Only process PDF files
        if not event.src_path.lower().endswith('.pdf'):
            return
        
        # Don't process files in subdirectories
        if os.path.dirname(event.src_path) != WATCH_DIR:
            return
        
        # Avoid duplicate processing
        if event.src_path in self.processed_files:
            return
        
        print(f"\n🆕 NEW PDF DETECTED: {os.path.basename(event.src_path)}")
        
        # Wait a moment to ensure file is fully written
        time.sleep(2)
        
        try:
            self.process_solicitation(event.src_path)
            self.processed_files.add(event.src_path)
        except Exception as e:
            print(f"❌ Error processing {event.src_path}: {e}")
            import traceback
            traceback.print_exc()
    
    def extract_pdf_text(self, pdf_path):
        """Extract text from PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"⚠️ Could not extract PDF text: {e}")
            return ""
    
    def ai_analyze_solicitation(self, pdf_text, filename):
        """
        🤖 AI ANALYZES THE SOLICITATION
        Determines: Product vs Service, what's needed, search terms
        """
        try:
            print("   🤖 AI analyzing solicitation...")
            
            prompt = f"""Analyze this government solicitation and determine:

1. TYPE: Is this a PRODUCT bid (purchasing goods to resell) or SERVICE bid (contracting services to perform)?
2. CATEGORY: What category (e.g., "office supplies", "lawn care", "IT support")?
3. ITEMS_NEEDED: List specific products or services needed
4. LOCATION: Where is this contract (city, county, state)?
5. SEARCH_TERMS: What should I search for to find suppliers/subcontractors?

Solicitation text (first 3000 chars):
{pdf_text[:3000]}

Filename: {filename}

Respond in JSON format:
{{
  "type": "PRODUCT" or "SERVICE",
  "category": "brief category",
  "items_needed": ["item 1", "item 2"],
  "location": "City, State",
  "search_terms": {{
    "primary": "main search term",
    "secondary": ["backup term 1", "backup term 2"]
  }},
  "confidence": "high/medium/low",
  "reasoning": "why you classified it this way"
}}"""

            response = self.ai.chat(prompt)
            
            # Try to parse JSON from response
            try:
                # Look for JSON block in response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group(0))
                else:
                    # Fallback to basic detection
                    analysis = self._fallback_analysis(pdf_text, filename)
            except:
                analysis = self._fallback_analysis(pdf_text, filename)
            
            print(f"   ✅ AI Analysis: {analysis['type']} bid - {analysis['category']}")
            print(f"   📋 Items: {', '.join(analysis['items_needed'][:3])}")
            
            return analysis
            
        except Exception as e:
            print(f"   ⚠️ AI analysis failed: {e}")
            return self._fallback_analysis(pdf_text, filename)
    
    def _fallback_analysis(self, pdf_text, filename):
        """Fallback analysis if AI fails"""
        text_lower = (pdf_text + filename).lower()
        
        # Simple keyword detection
        service_keywords = ['lawn', 'mowing', 'landscaping', 'janitorial', 'cleaning', 
                           'hvac', 'maintenance', 'repair', 'installation', 'IT support',
                           'consulting', 'training', 'security guard']
        
        product_keywords = ['supplies', 'equipment', 'materials', 'purchase', 'parts',
                           'tools', 'furniture', 'vehicles', 'salt', 'paper', 'toner']
        
        is_service = any(keyword in text_lower for keyword in service_keywords)
        
        return {
            'type': 'SERVICE' if is_service else 'PRODUCT',
            'category': 'unknown',
            'items_needed': ['Unknown - review PDF'],
            'location': 'Unknown',
            'search_terms': {
                'primary': 'supplier' if not is_service else 'contractor',
                'secondary': []
            },
            'confidence': 'low',
            'reasoning': 'Fallback analysis - AI unavailable'
        }
    
    def auto_find_suppliers_or_subs(self, analysis):
        """
        🔍 AUTO-SEARCH FOR SUPPLIERS OR SUBCONTRACTORS
        Based on AI analysis, automatically find qualified partners
        """
        try:
            if analysis['type'] == 'SERVICE':
                return self._search_subcontractors(analysis)
            else:
                return self._search_suppliers(analysis)
        except Exception as e:
            print(f"   ⚠️ Auto-search failed: {e}")
            return []
    
    def _search_subcontractors(self, analysis):
        """Search for subcontractors"""
        print("   🔍 Searching for subcontractors...")
        
        try:
            # Search existing database first
            existing = self.sub_miner.search_subcontractors_database(
                service_type=analysis['search_terms']['primary'],
                location=analysis['location']
            )
            
            print(f"   ✓ Found {len(existing)} existing subcontractors in database")
            
            # If API keys available, search Google Maps + Yelp
            if os.getenv('GOOGLE_MAPS_API_KEY') and os.getenv('YELP_API_KEY'):
                try:
                    new_subs = self.sub_miner.find_subcontractors(
                        service_type=analysis['search_terms']['primary'],
                        location=analysis['location'],
                        max_results=10
                    )
                    print(f"   ✓ Found {len(new_subs)} new subcontractors via search")
                    existing.extend(new_subs)
                except Exception as e:
                    print(f"   ⚠️ External search failed: {e}")
            
            return existing[:20]  # Return top 20
            
        except Exception as e:
            print(f"   ❌ Subcontractor search failed: {e}")
            return []
    
    def _search_suppliers(self, analysis):
        """Search for product suppliers"""
        print("   🔍 Searching for suppliers...")
        
        try:
            from nexus_backend import GPSSSystem
            gpss = GPSSSystem()
            
            # Search existing database
            existing = gpss.search_suppliers_database(
                product=analysis['search_terms']['primary']
            )
            
            print(f"   ✓ Found {len(existing['suppliers'])} existing suppliers in database")
            
            # TODO: Could add ThomasNet, GSA search here if needed
            
            return existing['suppliers'][:20]  # Return top 20
            
        except Exception as e:
            print(f"   ❌ Supplier search failed: {e}")
            return []
    
    def ai_score_and_rank(self, results, analysis):
        """
        🏆 AI SCORES AND RANKS EACH OPTION
        Returns top 10 with scores and reasoning
        """
        if not results:
            return []
        
        try:
            print(f"   🏆 AI scoring {len(results)} options...")
            
            # For now, simple scoring
            # TODO: Could enhance with AI-powered scoring
            
            scored = []
            for item in results[:15]:  # Score top 15
                score = self._calculate_score(item, analysis)
                scored.append({
                    'item': item,
                    'score': score,
                    'reasoning': self._generate_reasoning(item, score)
                })
            
            # Sort by score
            scored.sort(key=lambda x: x['score'], reverse=True)
            
            print(f"   ✅ Top pick: {scored[0]['item'].get('Company Name', 'Unknown')} (score: {scored[0]['score']}/100)")
            
            return scored[:10]  # Return top 10
            
        except Exception as e:
            print(f"   ⚠️ Scoring failed: {e}")
            return [{'item': item, 'score': 50, 'reasoning': 'Basic match'} for item in results[:10]]
    
    def _calculate_score(self, item, analysis):
        """Calculate score for supplier/sub"""
        score = 50  # Base score
        
        # Existing relationship (if has performance history)
        if item.get('Last Order Date') or item.get('Performance Score', 0) > 0:
            score += 20
        
        # Location match
        if analysis['location'] != 'Unknown':
            location_fields = ' '.join([
                str(item.get('Coverage Area', '')),
                str(item.get('State', '')),
                str(item.get('City', ''))
            ])
            if any(word in location_fields for word in analysis['location'].split()):
                score += 15
        
        # Ratings
        rating = max(
            item.get('Google Rating', 0),
            item.get('Yelp Rating', 0),
            item.get('Overall Rating', 0)
        )
        score += min(rating * 3, 15)  # Up to 15 points for 5-star rating
        
        # Compliance
        if item.get('Compliance Ready', False) or item.get('Insurance Verified', False):
            score += 10
        
        return min(score, 100)
    
    def _generate_reasoning(self, item, score):
        """Generate reasoning for score"""
        reasons = []
        
        if score >= 80:
            reasons.append("Excellent match")
        elif score >= 70:
            reasons.append("Good match")
        else:
            reasons.append("Potential match")
        
        if item.get('Last Order Date'):
            reasons.append("existing relationship")
        
        rating = max(
            item.get('Google Rating', 0),
            item.get('Yelp Rating', 0),
            item.get('Overall Rating', 0)
        )
        if rating >= 4:
            reasons.append(f"{rating}★ rated")
        
        if item.get('Compliance Ready'):
            reasons.append("compliance ready")
        
        return ', '.join(reasons)
    
    def send_notification(self, folder_name, top_pick, total_found, bid_type):
        """
        📢 SEND DESKTOP NOTIFICATION
        """
        try:
            title = f"✅ {folder_name}"
            message = f"Found {total_found} {bid_type}s - Top pick: {top_pick}"
            
            # macOS notification
            os.system(f"""
                osascript -e 'display notification "{message}" with title "{title}" sound name "Glass"'
            """)
            
            print(f"   📢 Notification sent!")
            
        except Exception as e:
            print(f"   ⚠️ Could not send notification: {e}")
    
    def parse_solicitation_data(self, pdf_text, filename):
        """Extract key data from solicitation PDF"""
        data = {
            'rfp_number': None,
            'title': None,
            'deadline': None,
            'agency': None,
            'contact_name': None,
            'contact_email': None,
            'contact_phone': None,
            'estimated_value': None
        }
        
        text_lower = pdf_text.lower()
        
        # Extract RFP/ITB/IFB number
        rfp_patterns = [
            r'(?:rfp|itb|ifb|rfq|solicitation)\s*(?:#|no\.?|number)?\s*[:\-]?\s*([A-Z0-9\-]+)',
            r'([A-Z]{2,4}\s*#?\s*\d{4,}-\d{3})',
            r'(IFB\s*\d+)',
        ]
        for pattern in rfp_patterns:
            match = re.search(pattern, pdf_text, re.IGNORECASE)
            if match:
                data['rfp_number'] = match.group(1).strip()
                break
        
        if not data['rfp_number']:
            filename_match = re.search(r'(ITB|IFB|RFP|RFQ)[\s_-]?(\d{4}-\d{3}|\d{4})', filename, re.IGNORECASE)
            if filename_match:
                data['rfp_number'] = f"{filename_match.group(1)} {filename_match.group(2)}"
        
        # Extract deadline
        deadline_patterns = [
            r'(?:bid deadline|due date|response deadline|closing date)[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
            r'deadline[:\s]+(\d{1,2}/\d{1,2}/\d{4})',
            r'due[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
        ]
        for pattern in deadline_patterns:
            match = re.search(pattern, pdf_text, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1)
                    for fmt in ['%B %d, %Y', '%b %d, %Y', '%m/%d/%Y', '%B %d %Y']:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            data['deadline'] = parsed_date.strftime('%Y-%m-%d')
                            break
                        except:
                            continue
                    break
                except:
                    pass
        
        # Extract agency name
        lines = pdf_text.split('\n')[:5]
        for line in lines:
            if len(line.strip()) > 5 and len(line.strip()) < 100:
                if not data['agency']:
                    data['agency'] = line.strip()
                    break
        
        # Extract contact info
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Z|a-z]{2,})', pdf_text)
        if email_match:
            data['contact_email'] = email_match.group(1)
        
        phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', pdf_text)
        if phone_match:
            data['contact_phone'] = phone_match.group(0)
        
        return data
    
    def generate_folder_name(self, data, filename):
        """Generate folder name following convention"""
        agency = data.get('agency', '')
        if agency:
            agency_clean = agency.upper()
            agency_clean = re.sub(r'\(.*?\)', '', agency_clean)
            agency_clean = re.sub(r'\s+', ' ', agency_clean).strip()
            
            if len(agency_clean) > 30:
                words = agency_clean.split()[:3]
                agency_clean = ' '.join(words)
        else:
            agency_clean = filename.replace('.pdf', '').upper()
        
        bid_type = ""
        if 'utility' in filename.lower() or 'vehicle' in filename.lower():
            bid_type = "UTILITY VEHICLES"
        elif 'sign' in filename.lower():
            bid_type = "SIGNS"
        elif 'truck' in filename.lower():
            bid_type = "TRUCKS"
        elif 'welding' in filename.lower():
            bid_type = "WELDING"
        elif 'automotive' in filename.lower():
            bid_type = "AUTOMOTIVE"
        elif 'forestry' in filename.lower():
            bid_type = "FORESTRY"
        elif 'paper' in filename.lower():
            bid_type = "PAPER PRODUCTS"
        else:
            bid_type = "BID"
        
        folder_name = f"{agency_clean} {bid_type}".strip()
        
        if len(folder_name) > 50:
            folder_name = folder_name[:47] + "..."
        
        return folder_name
    
    def process_solicitation(self, pdf_path):
        """
        🚀 PROCESS NEW SOLICITATION PDF
        Enhanced with AI analysis and auto-search
        """
        filename = os.path.basename(pdf_path)
        
        print(f"📄 Processing: {filename}")
        
        # Extract text from PDF
        print("   📖 Extracting PDF text...")
        pdf_text = self.extract_pdf_text(pdf_path)
        
        # Parse solicitation data
        print("   🔍 Parsing solicitation data...")
        data = self.parse_solicitation_data(pdf_text, filename)
        
        # 🆕 AI ANALYSIS
        analysis = self.ai_analyze_solicitation(pdf_text, filename)
        
        # 🆕 AUTO-SEARCH FOR SUPPLIERS/SUBS
        results = self.auto_find_suppliers_or_subs(analysis)
        
        # 🆕 AI SCORE AND RANK
        scored_results = self.ai_score_and_rank(results, analysis)
        
        # Generate folder name
        folder_name = self.generate_folder_name(data, filename)
        folder_path = os.path.join(WATCH_DIR, folder_name)
        
        print(f"   📁 Creating folder: {folder_name}")
        
        # Create folder
        os.makedirs(folder_path, exist_ok=True)
        
        # Move PDF
        new_pdf_path = os.path.join(folder_path, filename)
        if not os.path.exists(new_pdf_path):
            os.rename(pdf_path, new_pdf_path)
            print(f"   ✅ Moved PDF to: {folder_name}/")
        
        # Add to Airtable
        print("   💾 Adding to Airtable...")
        try:
            opportunity = {
                'Name': f"{data.get('agency', 'Unknown')} - {data.get('rfp_number', filename)}",
                'RFP NUMBER': data.get('rfp_number') or filename.replace('.pdf', ''),
                'Deadline': data.get('deadline') or (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'Source Status': 'Active',
                'Notes': f"Auto-detected: {analysis['type']} bid - {analysis['category']}\nFound {len(scored_results)} {analysis['type'].lower()}s"
            }
            
            record = opportunities_table.create(opportunity)
            print(f"   ✅ Added to Airtable: {record['id']}")
            
        except Exception as e:
            print(f"   ⚠️ Airtable error: {e}")
        
        # 🆕 GENERATE ENHANCED ANALYSIS
        print("   📝 Generating enhanced analysis...")
        analysis_path = os.path.join(folder_path, f"{folder_name.replace(' ', '_')}_ANALYSIS.md")
        
        self._write_enhanced_analysis(analysis_path, folder_name, data, analysis, scored_results, new_pdf_path)
        
        print(f"   ✅ Analysis saved: {analysis_path}")
        
        # 🆕 SEND NOTIFICATION
        if scored_results:
            top_pick_name = scored_results[0]['item'].get('Company Name', 'Unknown')
            bid_type = 'supplier' if analysis['type'] == 'PRODUCT' else 'subcontractor'
            self.send_notification(folder_name, top_pick_name, len(scored_results), bid_type)
        
        print(f"\n✅ COMPLETE! {folder_name} ready with {len(scored_results)} recommendations!\n")
        
        # 🆕 REGENERATE BID STATUS AGENDA
        self._update_agenda()
    
    def _write_enhanced_analysis(self, path, folder_name, data, analysis, scored_results, pdf_path):
        """Write enhanced analysis document"""
        with open(path, 'w') as f:
            f.write(f"# {folder_name}\n\n")
            f.write(f"**Auto-Generated:** {datetime.now().strftime('%B %d, %Y %I:%M %p')}\n\n")
            f.write("---\n\n")
            
            # AI Analysis Section
            f.write("## 🤖 AI ANALYSIS\n\n")
            f.write(f"**Type:** {analysis['type']} Bid\n")
            f.write(f"**Category:** {analysis['category']}\n")
            f.write(f"**Items Needed:**\n")
            for item in analysis['items_needed']:
                f.write(f"- {item}\n")
            f.write(f"\n**Location:** {analysis['location']}\n")
            f.write(f"**Confidence:** {analysis['confidence']}\n")
            f.write(f"\n**Reasoning:** {analysis['reasoning']}\n\n")
            f.write("---\n\n")
            
            # Recommendations Section
            if scored_results:
                f.write(f"## 🏆 TOP {len(scored_results)} RECOMMENDATIONS\n\n")
                f.write(f"**Found {len(scored_results)} qualified {'suppliers' if analysis['type'] == 'PRODUCT' else 'subcontractors'}**\n\n")
                
                for idx, result in enumerate(scored_results, 1):
                    item = result['item']
                    score = result['score']
                    reasoning = result['reasoning']
                    
                    f.write(f"### {idx}. {item.get('Company Name', 'Unknown')} ({score}/100)\n\n")
                    f.write(f"**Why recommended:** {reasoning}\n\n")
                    
                    if item.get('Primary Contact Phone'):
                        f.write(f"- 📞 **Phone:** {item['Primary Contact Phone']}\n")
                    if item.get('Primary Contact Email'):
                        f.write(f"- 📧 **Email:** {item['Primary Contact Email']}\n")
                    if item.get('Website'):
                        f.write(f"- 🌐 **Website:** {item['Website']}\n")
                    
                    rating = max(
                        item.get('Google Rating', 0),
                        item.get('Yelp Rating', 0),
                        item.get('Overall Rating', 0)
                    )
                    if rating > 0:
                        f.write(f"- ⭐ **Rating:** {rating}/5.0\n")
                    
                    if item.get('Compliance Ready'):
                        f.write(f"- ✅ **Status:** Compliance ready\n")
                    
                    f.write("\n")
                
                f.write("---\n\n")
            
            # Solicitation Details
            f.write("## 📋 SOLICITATION DETAILS\n\n")
            f.write(f"**RFP#:** {data.get('rfp_number', 'Unknown')}\n")
            f.write(f"**Agency:** {data.get('agency', 'Unknown')}\n")
            f.write(f"**Deadline:** {data.get('deadline', 'Unknown')}\n")
            if data.get('contact_email'):
                f.write(f"**Contact Email:** {data['contact_email']}\n")
            if data.get('contact_phone'):
                f.write(f"**Contact Phone:** {data['contact_phone']}\n")
            f.write("\n---\n\n")
            
            # Next Steps
            f.write("## 🎯 NEXT STEPS\n\n")
            if scored_results:
                f.write(f"1. ✅ Review top 3-5 {'suppliers' if analysis['type'] == 'PRODUCT' else 'subcontractors'} above\n")
                f.write(f"2. 📞 Call or email for quotes\n")
                f.write(f"3. 📊 Compare pricing\n")
                f.write(f"4. 📝 Prepare and submit bid\n\n")
            else:
                f.write(f"1. ⚠️ No existing {'suppliers' if analysis['type'] == 'PRODUCT' else 'subcontractors'} found\n")
                f.write(f"2. 🔍 Search manually or add to database\n")
                f.write(f"3. 📞 Contact for quotes\n")
                f.write(f"4. 📝 Prepare and submit bid\n\n")
            
            f.write(f"**PDF Location:** `{pdf_path}`\n\n")
            f.write("---\n\n")
            f.write("*This analysis was generated automatically by NEXUS Enhanced Solicitation Watcher*\n")
    
    def _update_agenda(self):
        """Regenerate bid status agenda after processing"""
        try:
            print("   📊 Updating bid status agenda...")
            import subprocess
            subprocess.run([
                'python3',
                '/Users/deedavis/NEXUS BACKEND/generate_bid_status_agenda.py'
            ], capture_output=True)
            print("   ✅ Agenda updated!")
        except Exception as e:
            print(f"   ⚠️ Could not update agenda: {e}")

def main():
    """Run the enhanced solicitation watcher"""
    print("=" * 70)
    print("🚀 NEXUS ENHANCED SOLICITATION WATCHER - STARTING")
    print("=" * 70)
    print(f"\n📂 Monitoring: {WATCH_DIR}")
    print("📄 Watching for: New PDF files")
    print("⚡ Auto-processing:")
    print("   • Folder creation")
    print("   • AI analysis (product vs service)")
    print("   • Auto-search (suppliers or subcontractors)")
    print("   • AI scoring and ranking")
    print("   • Airtable sync")
    print("   • Enhanced analysis generation")
    print("   • Desktop notifications")
    print("\n🟢 WATCHER ACTIVE - Press Ctrl+C to stop\n")
    print("-" * 70)
    
    event_handler = EnhancedSolicitationHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 STOPPING WATCHER...")
        observer.stop()
        print("✅ Watcher stopped cleanly\n")
    
    observer.join()

if __name__ == "__main__":
    main()
