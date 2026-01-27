#!/usr/bin/env python3
"""
Create a watermark version of the logo (lightened for background use)
"""
from PIL import Image
import sys

def create_watermark_logo(input_path, output_path, opacity=0.3):
    """Create a watermark version of logo with reduced opacity"""
    try:
        # Open the logo
        img = Image.open(input_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Reduce opacity
        alpha = img.split()[3]  # Get alpha channel
        alpha = alpha.point(lambda p: int(p * opacity))  # Reduce opacity
        img.putalpha(alpha)
        
        # Save watermark version
        img.save(output_path, 'PNG')
        print(f"✓ Watermark logo created: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating watermark: {e}")
        return False

if __name__ == '__main__':
    input_logo = 'logo.png'
    output_logo = 'logo_watermark.png'
    
    if create_watermark_logo(input_logo, output_logo, opacity=0.25):
        print(f"✓ Use {output_logo} as watermark in PDFs")
