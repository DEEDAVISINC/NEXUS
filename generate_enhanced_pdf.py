#!/usr/bin/env python3
"""
Capability Statement PDF Generator
Generates professional PDF capability statements from HTML
"""

import json
import sys
import os
from pathlib import Path
import subprocess


def generate_enhanced_pdf(config, output_file):
    """Generate PDF from config using HTML intermediate"""
    
    # First generate HTML
    config_path = Path('temp_config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    html_file = 'temp_capstat.html'
    
    # Import and use HTML generator
    from generate_html_with_highlights import generate_html
    generate_html(config, html_file)
    
    # Try to convert HTML to PDF using available tools
    pdf_generated = False
    
    # Method 1: Try wkhtmltopdf (if installed)
    try:
        result = subprocess.run(
            ['wkhtmltopdf', '--enable-local-file-access', html_file, output_file],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            pdf_generated = True
            print(f"✓ Generated PDF: {output_file}")
    except FileNotFoundError:
        pass
    
    # Method 2: Try weasyprint (if installed)
    if not pdf_generated:
        try:
            from weasyprint import HTML
            HTML(html_file).write_pdf(output_file)
            pdf_generated = True
            print(f"✓ Generated PDF: {output_file}")
        except ImportError:
            pass
    
    # Method 3: Try Chrome/Chromium headless
    if not pdf_generated:
        chrome_paths = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            'google-chrome',
            'chromium-browser',
            'chromium'
        ]
        
        for chrome_path in chrome_paths:
            try:
                result = subprocess.run(
                    [
                        chrome_path,
                        '--headless',
                        '--disable-gpu',
                        '--print-to-pdf=' + output_file,
                        html_file
                    ],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    pdf_generated = True
                    print(f"✓ Generated PDF: {output_file}")
                    break
            except FileNotFoundError:
                continue
    
    # Clean up temp files
    if config_path.exists():
        config_path.unlink()
    if Path(html_file).exists():
        Path(html_file).unlink()
    
    if not pdf_generated:
        print("⚠ Warning: Could not generate PDF automatically")
        print("Please install one of the following:")
        print("  - wkhtmltopdf: brew install wkhtmltopdf")
        print("  - weasyprint: pip install weasyprint")
        print("  - Or use Chrome browser to print the HTML file to PDF")
        
        # Generate HTML as fallback
        html_fallback = output_file.replace('.pdf', '.html')
        from generate_html_with_highlights import generate_html
        generate_html(config, html_fallback)
        print(f"✓ Generated HTML instead: {html_fallback}")
        print("  You can open this in a browser and print to PDF")
        
        return html_fallback
    
    return output_file


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python3 generate_enhanced_pdf.py <config.json>")
        print("Example: python3 generate_enhanced_pdf.py default_config.json")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    # Load config
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{config_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        sys.exit(1)
    
    # Generate output filename (remove _config suffix if present)
    config_path = Path(config_file)
    filename = config_path.stem
    if filename.endswith('_config'):
        filename = filename[:-7]  # Remove '_config'
    output_file = filename + '_enhanced.pdf'
    
    # Generate PDF
    generate_enhanced_pdf(config, output_file)


if __name__ == '__main__':
    main()
