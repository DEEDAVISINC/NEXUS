#!/usr/bin/env python3
"""
Fill out RCOC 7802 RFQ cover sheet with proper coordinate calibration
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
import io

# Read the original PDF to get exact dimensions
existing_pdf = PdfReader(open("this is 7802.pdf", "rb"))
page_height = float(existing_pdf.pages[0].mediabox[3])
page_width = float(existing_pdf.pages[0].mediabox[2])

print(f"PDF dimensions: {page_width} x {page_height}")

# Create overlay
packet = io.BytesIO()
can = canvas.Canvas(packet, pagesize=(page_width, page_height))

# PAGE 1 - Company info at top (around line 10-13 in text)
# These fields appear to be at the top of the page after header
can.setFont("Helvetica", 9)

# Line 1: Company, Street Address, City
y_pos = page_height - 155  # Adjust based on actual position
can.drawString(45, y_pos, "DEE DAVIS INC")
can.drawString(210, y_pos, "755 W Big Beaver Rd, Suite 2020")
can.drawString(440, y_pos, "Troy")

# Line 2: State/Zip, Phone, Website
y_pos = page_height - 170
can.drawString(45, y_pos, "MI, 48084")
can.drawString(210, y_pos, "248-376-4550")
can.drawString(440, y_pos, "www.deedavis.biz")

can.showPage()

# PAGE 2 - Order desk and customer service contacts
can.setFont("Helvetica", 9)

# Order Desk section (left side)
y_pos = page_height - 400  # Approximate position, adjust as needed
can.drawString(45, y_pos, "Dee Davis")  # Order desk name
y_pos -= 15
can.drawString(45, y_pos, "248-376-4550")  # Order desk phone
y_pos -= 15
can.drawString(45, y_pos, "info@deedavis.biz")  # Order desk email

# Customer Service section (right side)
y_pos = page_height - 400
can.drawString(320, y_pos, "Dee Davis")  # CS name
y_pos -= 15
can.drawString(320, y_pos, "248-376-4550")  # CS phone
y_pos -= 15
can.drawString(320, y_pos, "info@deedavis.biz")  # CS email

# Additional questions section
y_pos = page_height - 480
can.drawString(380, y_pos, "30 days")  # Hold pricing

y_pos -= 15
can.drawString(420, y_pos, "14-21 days")  # Delivery days

y_pos -= 15
can.drawString(280, y_pos, "No minimum order requirement")  # Min order

y_pos -= 15
can.drawString(280, y_pos, "N/A")  # Penalty

y_pos -= 20
can.drawString(380, y_pos, "X")  # NO for payment discount
can.drawString(400, y_pos, "(NO)")

y_pos -= 15
can.drawString(280, y_pos, "N/A - no payment discounts offered")  # Discount details

y_pos -= 15
can.drawString(280, y_pos, "Standard manufacturer warranty applies to all products")  # Return policy

can.showPage()

# PAGE 3 - Signature section
can.setFont("Helvetica", 9)

# Top of signature area
y_pos = page_height - 220

# Email (right side of signature line)
can.drawString(320, y_pos, "info@deedavis.biz")

# Print Name (left side, below signature)
y_pos -= 20
can.drawString(45, y_pos, "Dee Davis")

# Date (right side)
can.drawString(320, y_pos, "February 5, 2026")

# Bottom company info repeat
y_pos -= 25
can.drawString(45, y_pos, "DEE DAVIS INC")
can.drawString(210, y_pos, "755 W Big Beaver Rd, Suite 2020")
can.drawString(440, y_pos, "Troy")

y_pos -= 15
can.drawString(45, y_pos, "MI, 48084")
can.drawString(210, y_pos, "248-376-4550")
can.drawString(440, y_pos, "www.deedavis.biz")

can.save()

# Merge PDFs
packet.seek(0)
overlay_pdf = PdfReader(packet)
output = PdfWriter()

for i in range(len(existing_pdf.pages)):
    page = existing_pdf.pages[i]
    if i < len(overlay_pdf.pages):
        page.merge_page(overlay_pdf.pages[i])
    output.add_page(page)

# Save
with open("RCOC_7802_COMPLETED_RFQ.pdf", "wb") as f:
    output.write(f)

print("✓ Generated: RCOC_7802_COMPLETED_RFQ.pdf")
print("  ✓ Company information filled")
print("  ✓ Contact information filled")
print("  ✓ Order desk details filled")
print("  ✓ Delivery terms filled")
print("  ⬜ SIGNATURE LINE LEFT BLANK for manual signing")
print("\nReady to print, sign, and upload to BidNet!")
