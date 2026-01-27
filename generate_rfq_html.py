#!/usr/bin/env python3
"""
Generate HTML from RFQ config
"""

import json
import sys


def generate_html(config):
    """Generate HTML from config"""
    
    c = config['company']
    rfq = config['rfq_details']
    colors = config['colors']
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{rfq['title']} - {c['name']}</title>
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
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.95;
        }}
        
        /* Company Info Bar */
        .company-info {{
            background: {colors['primary']};
            color: white;
            padding: 20px 40px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            font-size: 0.9em;
        }}
        
        .info-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .info-label {{
            font-weight: 600;
            opacity: 0.8;
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
        
        /* RFQ Details Box */
        .rfq-details {{
            background: linear-gradient(to right, {colors['primary']}10, {colors['accent']}10);
            border-left: 4px solid {colors['accent']};
            padding: 20px;
            margin: 30px 0;
            border-radius: 4px;
        }}
        
        .rfq-details-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 15px;
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
        
        /* Lists */
        .requirement-list, .submission-list {{
            list-style: none;
            padding-left: 0;
        }}
        
        .requirement-list li, .submission-list li {{
            padding: 12px 12px 12px 40px;
            margin: 8px 0;
            background: #f9fafb;
            border-left: 3px solid {colors['accent']};
            position: relative;
        }}
        
        .requirement-list li:before, .submission-list li:before {{
            content: "✓";
            position: absolute;
            left: 15px;
            color: {colors['accent']};
            font-weight: bold;
            font-size: 1.2em;
        }}
        
        /* Items Table */
        .items-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .items-table thead {{
            background: {colors['primary']};
            color: white;
        }}
        
        .items-table th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }}
        
        .items-table td {{
            padding: 15px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .items-table tbody tr:hover {{
            background: #f9fafb;
        }}
        
        .item-number {{
            background: {colors['accent']};
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: 600;
            display: inline-block;
        }}
        
        /* Terms Grid */
        .terms-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .term-card {{
            background: #f9fafb;
            padding: 20px;
            border-radius: 8px;
            border-left: 3px solid {colors['accent']};
        }}
        
        .term-title {{
            color: {colors['primary']};
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 1.1em;
        }}
        
        /* Evaluation Criteria */
        .criteria-list {{
            margin: 20px 0;
        }}
        
        .criterion-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            background: #f9fafb;
            border-radius: 8px;
        }}
        
        .criterion-name {{
            font-weight: 500;
        }}
        
        .criterion-weight {{
            background: {colors['accent']};
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 600;
        }}
        
        /* Footer */
        .footer {{
            background: {colors['primary']};
            color: white;
            padding: 30px 40px;
            text-align: center;
        }}
        
        .footer-contact {{
            margin-top: 20px;
            font-size: 0.9em;
            opacity: 0.9;
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
            <div class="subtitle">Request for Quote</div>
        </div>
        
        <!-- Company Info -->
        <div class="company-info">
            <div class="info-item">
                <span class="info-label">📍</span>
                <span>{c['address']}</span>
            </div>
            <div class="info-item">
                <span class="info-label">📞</span>
                <span>{c['phone']}</span>
            </div>
            <div class="info-item">
                <span class="info-label">✉️</span>
                <span>{c['email']}</span>
            </div>
            <div class="info-item">
                <span class="info-label">🌐</span>
                <span>{c['website']}</span>
            </div>
        </div>
        
        <!-- RFQ Details -->
        <div class="content">
            <div class="rfq-details">
                <h2 style="color: {colors['primary']}; margin-bottom: 15px;">{rfq['title']}</h2>
                <div class="rfq-details-grid">
                    <div class="detail-item">
                        <span class="detail-label">RFQ Number</span>
                        <span class="detail-value">{rfq['rfq_number']}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Issue Date</span>
                        <span class="detail-value">{rfq['issue_date']}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Due Date</span>
                        <span class="detail-value">{rfq['due_date']} at {rfq['due_time']}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Contract Period</span>
                        <span class="detail-value">{rfq['contract_period']}</span>
                    </div>
                </div>
            </div>
            
            <!-- Introduction -->
            <div class="section">
                <h2 class="section-title">INTRODUCTION</h2>
                <div class="section-text">
                    {config['introduction']}
                </div>
            </div>
            
            <!-- Scope of Work -->
            <div class="section">
                <h2 class="section-title">{config['scope_of_work']['title']}</h2>
                <div class="section-text">
                    {config['scope_of_work']['description']}
                </div>
                <h3 style="color: {colors['primary']}; margin: 20px 0 10px 0;">Key Requirements:</h3>
                <ul class="requirement-list">
"""
    
    for req in config['scope_of_work']['key_requirements']:
        html += f"                    <li>{req}</li>\n"
    
    html += f"""                </ul>
            </div>
            
            <!-- Items -->
            <div class="section">
                <h2 class="section-title">ITEMS REQUESTED</h2>
                <table class="items-table">
                    <thead>
                        <tr>
                            <th>Item #</th>
                            <th>Description</th>
                            <th>Specifications</th>
                            <th>Est. Quantity</th>
                            <th>Unit</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    for item in config['items']:
        html += f"""                        <tr>
                            <td><span class="item-number">{item['item_number']}</span></td>
                            <td><strong>{item['description']}</strong></td>
                            <td>{item['specifications']}</td>
                            <td>{item['estimated_quantity']}</td>
                            <td>{item['unit']}</td>
                        </tr>
"""
    
    html += f"""                    </tbody>
                </table>
            </div>
            
            <!-- Submission Requirements -->
            <div class="section">
                <h2 class="section-title">{config['submission_requirements']['title']}</h2>
                <ul class="submission-list">
"""
    
    for item in config['submission_requirements']['items']:
        html += f"                    <li>{item}</li>\n"
    
    html += f"""                </ul>
            </div>
            
            <!-- Terms & Conditions -->
            <div class="section">
                <h2 class="section-title">{config['terms_and_conditions']['title']}</h2>
                <div class="terms-grid">
"""
    
    for term in config['terms_and_conditions']['items']:
        html += f"""                    <div class="term-card">
                        <div class="term-title">{term['title']}</div>
                        <div>{term['description']}</div>
                    </div>
"""
    
    html += f"""                </div>
            </div>
            
            <!-- Evaluation Criteria -->
            <div class="section">
                <h2 class="section-title">{config['evaluation_criteria']['title']}</h2>
                <div class="section-text">
                    {config['evaluation_criteria']['description']}
                </div>
                <div class="criteria-list">
"""
    
    for criterion in config['evaluation_criteria']['criteria']:
        html += f"""                    <div class="criterion-item">
                        <span class="criterion-name">{criterion['criterion']}</span>
                        <span class="criterion-weight">{criterion['weight']}</span>
                    </div>
"""
    
    html += f"""                </div>
            </div>
            
            <!-- Additional Info -->
            <div class="section">
                <h2 class="section-title">{config['additional_info']['title']}</h2>
                <ul class="submission-list">
"""
    
    for item in config['additional_info']['items']:
        html += f"                    <li>{item}</li>\n"
    
    html += f"""                </ul>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <h3>Contact Information</h3>
            <div class="footer-contact">
                <strong>{c['contact_person']}</strong><br>
                {c['email']} | {c['phone']}<br>
                {c['website']}
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_rfq_html.py <config.json>")
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
