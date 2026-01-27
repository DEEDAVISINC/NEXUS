#!/usr/bin/env python3
"""
AUTO QUOTE GENERATOR - Drop files and go!
Monitors the 'DROP_QUOTES_HERE' folder and automatically generates PDFs
"""

import os
import time
import subprocess
import sys
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
END = '\033[0m'

WATCH_FOLDER = "DROP_QUOTES_HERE"
PROCESSED_FOLDER = "GENERATED_QUOTES"


def setup_folders():
    """Create folders if they don't exist"""
    Path(WATCH_FOLDER).mkdir(exist_ok=True)
    Path(PROCESSED_FOLDER).mkdir(exist_ok=True)


def print_banner():
    """Print startup banner"""
    print("\n" + "="*60)
    print(f"{BOLD}{BLUE}🚀 AUTO QUOTE GENERATOR - RUNNING{END}")
    print("="*60)
    print(f"\n{GREEN}✓{END} Watching folder: {BOLD}{WATCH_FOLDER}/{END}")
    print(f"{GREEN}✓{END} Output folder: {BOLD}{PROCESSED_FOLDER}/{END}")
    print(f"\n{YELLOW}💡 How to use:{END}")
    print(f"   1. Drop your quote template into {BOLD}{WATCH_FOLDER}/{END}")
    print(f"   2. PDF generates automatically!")
    print(f"   3. Find it in {BOLD}{PROCESSED_FOLDER}/{END}")
    print(f"\n{YELLOW}📝 Supported files:{END} .txt files with quote data")
    print(f"{YELLOW}⏹️  Stop watching:{END} Press Ctrl+C")
    print("\n" + "="*60 + "\n")


def process_file(filepath):
    """Process a quote request file"""
    filename = os.path.basename(filepath)
    print(f"\n{BLUE}📄 Found new file:{END} {BOLD}{filename}{END}")
    
    # Determine if it's RFQ or capability statement (default to RFQ)
    doc_type = 'rfq'
    
    try:
        # Generate the quote request
        print(f"{YELLOW}⚙️  Generating quote request...{END}")
        
        result = subprocess.run(
            ['python3', 'create_from_paste.py', doc_type, filepath],
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"{GREEN}✅ SUCCESS!{END} Quote request generated")
        
        # Find the generated files
        # Extract base name from the output
        output_lines = result.stdout.split('\n')
        generated_files = []
        
        for line in output_lines:
            if '.html' in line or '.pdf' in line or '.json' in line:
                # Extract filename
                for word in line.split():
                    if '.html' in word or '.pdf' in word or '.json' in word:
                        generated_files.append(word)
        
        # Move files to output folder
        for gen_file in generated_files:
            if os.path.exists(gen_file):
                dest = os.path.join(PROCESSED_FOLDER, os.path.basename(gen_file))
                os.rename(gen_file, dest)
                print(f"   {GREEN}✓{END} {os.path.basename(gen_file)} → {PROCESSED_FOLDER}/")
        
        # Move processed template to output folder
        processed_path = os.path.join(PROCESSED_FOLDER, f"PROCESSED_{filename}")
        os.rename(filepath, processed_path)
        print(f"   {GREEN}✓{END} Template saved as PROCESSED_{filename}")
        
        # Show summary
        print(f"\n{BOLD}{GREEN}🎉 READY TO SEND!{END}")
        print(f"   Open folder: {BOLD}{PROCESSED_FOLDER}/{END}")
        print(f"   Your PDF is ready to email to suppliers!")
        print("="*60 + "\n")
        
        # Open the output folder automatically
        subprocess.run(['open', PROCESSED_FOLDER])
        
    except subprocess.CalledProcessError as e:
        print(f"{RED}❌ Error generating quote:{END}")
        print(e.stderr)
        # Keep the file for retry
        print(f"   File kept in {WATCH_FOLDER} for manual check")
    except Exception as e:
        print(f"{RED}❌ Unexpected error:{END} {e}")


def watch_folder():
    """Watch folder for new files"""
    setup_folders()
    print_banner()
    
    processed_files = set()
    
    print(f"{YELLOW}👀 Watching for files...{END}\n")
    
    try:
        while True:
            # Check for new .txt files
            for filename in os.listdir(WATCH_FOLDER):
                if filename.endswith('.txt') and not filename.startswith('.'):
                    filepath = os.path.join(WATCH_FOLDER, filename)
                    
                    # Skip if already processed
                    if filepath in processed_files:
                        continue
                    
                    # Check if file is fully written (not being written)
                    try:
                        # Wait a moment to ensure file is complete
                        time.sleep(0.5)
                        
                        # Try to open it (will fail if still being written)
                        with open(filepath, 'r') as f:
                            f.read()
                        
                        # Process the file
                        processed_files.add(filepath)
                        process_file(filepath)
                        
                    except Exception as e:
                        # File not ready yet, skip
                        pass
            
            # Wait before checking again
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}⏹️  Stopped watching{END}")
        print(f"{GREEN}✓{END} Auto-generator shut down cleanly")
        print("="*60 + "\n")


if __name__ == "__main__":
    watch_folder()
