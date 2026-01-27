#!/usr/bin/env python3
"""
Generate HTML capability statement with highlights
"""

import json
import sys


def generate_highlights_html(highlights, accent_color):
    """Generate HTML for highlights section"""
    if not highlights:
        return ""
    
    html = '<div class="highlights-section">\n'
    
    for highlight in highlights:
        h_type = highlight.get('type', '')
        
        if h_type == 'naics':
            icon = '🏢'
            title = 'NAICS Code'
            content = highlight['content']
        elif h_type == 'partners':
            icon = '🤝'
            title = 'Key Partners'
            content = highlight['content'].replace('|', ' • ')
        elif h_type == 'performance':
            icon = '📊'
            title = 'Past Performance'
            content = highlight['content']
        elif h_type == 'certifications':
            icon = '✓'
            title = 'Additional Certifications'
            content = highlight['content'].replace('|', ' • ')
        elif h_type == 'service_area':
            icon = '📍'
            title = 'Service Area'
            content = highlight['content']
        elif h_type == 'custom':
            icon = '⭐'
            title = highlight.get('title', 'Highlight')
            content = highlight['content']
        else:
            continue
        
        html += f'''    <div class="highlight-card">
        <div class="highlight-icon">{icon}</div>
        <div class="highlight-content">
            <div class="highlight-title">{title}</div>
            <div class="highlight-text">{content}</div>
        </div>
    </div>\n'''
    
    html += '</div>\n'
    return html


def generate_html(config):
    """Generate full HTML capability statement"""
    
    c = config['company']
    rfq = config['rfq_details']
    colors = config['colors']
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Capability Statement - {c['name']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: {colors['text']};
            background: #f3f4f6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['accent']} 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header .tagline {{
            font-size: 1.2em;
            opacity: 0.95;
        }}
        
        /* Client Info Bar */
        .client-info {{
            background: {colors['primary']};
            color: white;
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}
        
        .client-info-item {{
            display: flex;
            flex-direction: column;
        }}
        
        .client-label {{
            font-size: 0.85em;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .client-value {{
            font-size: 1.2em;
            font-weight: 600;
            margin-top: 5px;
        }}
        
        /* Content */
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            color: {colors['primary']};
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid {colors['accent']};
        }}
        
        .section-text {{
            margin-bottom: 20px;
            line-height: 1.8;
        }}
        
        /* Company Details Grid */
        .company-details {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            background: linear-gradient(to right, {colors['primary']}10, {colors['accent']}10);
            padding: 30px;
            border-radius: 8px;
            margin: 30px 0;
        }}
        
        .detail-item {{
            display: flex;
            flex-direction: column;
        }}
        
        .detail-label {{
            font-weight: 600;
            color: {colors['primary']};
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .detail-value {{
            color: {colors['text']};
            font-size: 1.1em;
            margin-top: 5px;
        }}
        
        /* Core Competencies */
        .competencies-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin: 20px 0;
        }}
        
        .competency-item {{
            background: #f9fafb;
            padding: 15px 15px 15px 45px;
            border-left: 3px solid {colors['accent']};
            position: relative;
            border-radius: 4px;
        }}
        
        .competency-item:before {{
            content: "✓";
            position: absolute;
            left: 15px;
            color: {colors['accent']};
            font-weight: bold;
            font-size: 1.3em;
        }}
        
        /* Differentiators */
        .differentiators-list {{
            list-style: none;
            padding: 0;
        }}
        
        .differentiator-item {{
            background: linear-gradient(to right, {colors['accent']}15, transparent);
            padding: 15px 15px 15px 50px;
            margin: 12px 0;
            border-left: 4px solid {colors['accent']};
            position: relative;
            border-radius: 4px;
        }}
        
        .differentiator-item:before {{
            content: "⭐";
            position: absolute;
            left: 15px;
            font-size: 1.5em;
        }}
        
        /* Certifications */
        .certifications-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .cert-card {{
            background: {colors['primary']};
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .cert-name {{
            font-size: 1.5em;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        
        .cert-description {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        /* Highlights Section */
        .highlights-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .highlight-card {{
            background: #f9fafb;
            border: 2px solid {colors['accent']}30;
            border-radius: 8px;
            padding: 20px;
            display: flex;
            gap: 15px;
            transition: all 0.3s;
        }}
        
        .highlight-card:hover {{
            border-color: {colors['accent']};
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .highlight-icon {{
            font-size: 2em;
            flex-shrink: 0;
        }}
        
        .highlight-content {{
            flex-grow: 1;
        }}
        
        .highlight-title {{
            font-weight: 600;
            color: {colors['primary']};
            margin-bottom: 5px;
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .highlight-text {{
            color: {colors['text']};
            line-height: 1.6;
        }}
        
        /* Footer */
        .footer {{
            background: {colors['primary']};
            color: white;
            padding: 30px 40px;
            text-align: center;
        }}
        
        .footer-contact {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
            font-size: 0.9em;
        }}
        
        .footer-contact-item {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}
        
        /* Print Styles */
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>{c['name']}</h1>
            <div class="tagline">Capability Statement</div>
        </div>
        
        <!-- Client Info -->
        <div class="client-info">
            <div class="client-info-item">
                <span class="client-label">Client</span>
                <span class="client-value">{rfq['client_name']}</span>
            </div>
            <div class="client-info-item">
                <span class="client-label">RFQ Number</span>
                <span class="client-value">{rfq['rfq_number']}</span>
            </div>
            <div class="client-info-item">
                <span class="client-label">Date</span>
                <span class="client-value">{rfq['date']}</span>
            </div>
        </div>
        
        <!-- Company Details -->
        <div class="content">
            <div class="company-details">
                <div class="detail-item">
                    <span class="detail-label">CAGE Code</span>
                    <span class="detail-value">{c['cage_code']}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">UEI</span>
                    <span class="detail-value">{c['uei']}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">DUNS</span>
                    <span class="detail-value">{c['duns']}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Tax ID</span>
                    <span class="detail-value">{c['tax_id']}</span>
                </div>
            </div>
            
            <!-- Company Overview -->
            <div class="section">
                <h2 class="section-title">COMPANY OVERVIEW</h2>
                <div class="section-text">
                    {config['company_overview']}
                </div>
            </div>
"""
    
    # Add highlights if present
    if config.get('highlights'):
        html += generate_highlights_html(config['highlights'], colors['accent'])
    
    html += f"""
            <!-- Core Competencies -->
            <div class="section">
                <h2 class="section-title">CORE COMPETENCIES</h2>
                <div class="competencies-grid">
"""
    
    for comp in config['core_competencies']:
        html += f'                    <div class="competency-item">{comp}</div>\n'
    
    html += f"""                </div>
            </div>
            
            <!-- Differentiators -->
            <div class="section">
                <h2 class="section-title">WHAT SETS US APART</h2>
                <ul class="differentiators-list">
"""
    
    for diff in config['differentiators']:
        html += f'                    <li class="differentiator-item">{diff}</li>\n'
    
    html += f"""                </ul>
            </div>
            
            <!-- Certifications -->
            <div class="section">
                <h2 class="section-title">CERTIFICATIONS</h2>
                <div class="certifications-grid">
"""
    
    for cert in config['certifications']:
        html += f"""                    <div class="cert-card">
                        <div class="cert-name">{cert['name']}</div>
                        <div class="cert-description">{cert['description']}</div>
                    </div>
"""
    
    html += f"""                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <h3>Contact Information</h3>
            <div class="footer-contact">
                <div class="footer-contact-item">
                    <span>📍</span>
                    <span>{c['address']}</span>
                </div>
                <div class="footer-contact-item">
                    <span>📞</span>
                    <span>{c['phone']}</span>
                </div>
                <div class="footer-contact-item">
                    <span>✉️</span>
                    <span>{c['email']}</span>
                </div>
                <div class="footer-contact-item">
                    <span>🌐</span>
                    <span>{c['website']}</span>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_html_with_highlights.py <config.json>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    html = generate_html(config)
    
    output_file = config_file.replace('_config.json', '.html')
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"✓ Generated: {output_file}")


if __name__ == "__main__":
    main()
