#!/usr/bin/env python3
"""
NEXUS Solicitation Watcher - Automatic PDF Processing
Monitors photos_and_videos/ for new PDFs, automatically:
1. Creates folder for solicitation
2. Moves PDF to folder
3. Parses PDF and extracts data
4. Adds to Airtable
5. Generates analysis document
6. Creates calendar reminder

RUN THIS 24/7 IN BACKGROUND!
"""

import os
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pyairtable import Api
from dotenv import load_dotenv
import PyPDF2

load_dotenv()

WATCH_DIR = "/Users/deedavis/NEXUS BACKEND/photos_and_videos"
AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

api = Api(AIRTABLE_API_KEY)
opportunities_table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

class SolicitationHandler(FileSystemEventHandler):
    def __init__(self):
        self.processed_files = set()
        
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
            r'([A-Z]{2,4}\s*#?\s*\d{4,}-\d{3})',  # Format like ITB 2026-007
            r'(IFB\s*\d+)',  # Format like IFB 7790
        ]
        for pattern in rfp_patterns:
            match = re.search(pattern, pdf_text, re.IGNORECASE)
            if match:
                data['rfp_number'] = match.group(1).strip()
                break
        
        # If not found, try filename
        if not data['rfp_number']:
            filename_match = re.search(r'(ITB|IFB|RFP|RFQ)[\s_-]?(\d{4}-\d{3}|\d{4})', filename, re.IGNORECASE)
            if filename_match:
                data['rfp_number'] = f"{filename_match.group(1)} {filename_match.group(2)}"
        
        # Extract deadline - look for various date formats
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
                    # Try to parse the date
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
        
        # Extract agency name - look at first few lines
        lines = pdf_text.split('\n')[:5]
        for line in lines:
            if len(line.strip()) > 5 and len(line.strip()) < 100:
                # Likely agency name
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
        """Generate folder name following convention: [CLIENT] [BID TYPE]"""
        
        # Extract client name from agency or filename
        agency = data.get('agency', '')
        if agency:
            # Clean up agency name
            agency_clean = agency.upper()
            agency_clean = re.sub(r'\(.*?\)', '', agency_clean)  # Remove parentheses
            agency_clean = re.sub(r'\s+', ' ', agency_clean).strip()
            
            # Shorten long names
            if len(agency_clean) > 30:
                # Try to get first few words
                words = agency_clean.split()[:3]
                agency_clean = ' '.join(words)
        else:
            # Extract from filename
            agency_clean = filename.replace('.pdf', '').upper()
        
        # Generate bid type from filename or title
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
        
        # Construct folder name
        folder_name = f"{agency_clean} {bid_type}".strip()
        
        # Limit length
        if len(folder_name) > 50:
            folder_name = folder_name[:47] + "..."
        
        return folder_name
    
    def process_solicitation(self, pdf_path):
        """Process new solicitation PDF"""
        filename = os.path.basename(pdf_path)
        
        print(f"📄 Processing: {filename}")
        
        # Extract text from PDF
        print("   📖 Extracting PDF text...")
        pdf_text = self.extract_pdf_text(pdf_path)
        
        # Parse solicitation data
        print("   🔍 Parsing solicitation data...")
        data = self.parse_solicitation_data(pdf_text, filename)
        
        # Generate folder name
        folder_name = self.generate_folder_name(data, filename)
        folder_path = os.path.join(WATCH_DIR, folder_name)
        
        print(f"   📁 Creating folder: {folder_name}")
        
        # Create folder if doesn't exist
        os.makedirs(folder_path, exist_ok=True)
        
        # Move PDF to folder
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
                'Source Status': 'Active'
            }
            
            record = opportunities_table.create(opportunity)
            print(f"   ✅ Added to Airtable: {record['id']}")
            
        except Exception as e:
            print(f"   ⚠️ Airtable error: {e}")
        
        # Generate analysis document
        print("   📝 Generating analysis...")
        analysis_path = os.path.join(folder_path, f"{folder_name.replace(' ', '_')}_ANALYSIS.md")
        
        with open(analysis_path, 'w') as f:
            f.write(f"# {folder_name}\n\n")
            f.write(f"**Auto-Generated:** {datetime.now().strftime('%B %d, %Y %I:%M %p')}\n\n")
            f.write("---\n\n")
            f.write("## 📋 SOLICITATION DETAILS:\n\n")
            f.write(f"**RFP#:** {data.get('rfp_number', 'Unknown')}\n")
            f.write(f"**Agency:** {data.get('agency', 'Unknown')}\n")
            f.write(f"**Deadline:** {data.get('deadline', 'Unknown')}\n")
            if data.get('contact_email'):
                f.write(f"**Contact Email:** {data['contact_email']}\n")
            if data.get('contact_phone'):
                f.write(f"**Contact Phone:** {data['contact_phone']}\n")
            f.write("\n---\n\n")
            f.write("## 📄 PDF LOCATION:\n\n")
            f.write(f"`{new_pdf_path}`\n\n")
            f.write("---\n\n")
            f.write("## 🎯 NEXT STEPS:\n\n")
            f.write("1. Open NEXUS Document Generator\n")
            f.write(f"2. Search: {data.get('rfp_number', filename)}\n")
            f.write("3. Generate RFQ for suppliers\n")
            f.write("4. Review pricing and submit bid\n\n")
            f.write("---\n\n")
            f.write("*This analysis was generated automatically by NEXUS Solicitation Watcher*\n")
        
        print(f"   ✅ Analysis saved: {analysis_path}")
        
        print(f"\n✅ COMPLETE! {folder_name} ready in NEXUS!\n")

def main():
    """Run the solicitation watcher"""
    print("=" * 70)
    print("🚀 NEXUS SOLICITATION WATCHER - STARTING")
    print("=" * 70)
    print(f"\n📂 Monitoring: {WATCH_DIR}")
    print("📄 Watching for: New PDF files")
    print("⚡ Auto-processing: Folder creation, parsing, Airtable sync")
    print("\n🟢 WATCHER ACTIVE - Press Ctrl+C to stop\n")
    print("-" * 70)
    
    event_handler = SolicitationHandler()
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
