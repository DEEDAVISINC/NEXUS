#!/usr/bin/env python3
"""
Fill out RCOC 7802 RFQ cover sheet with DEE DAVIS INC information
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
import io

# Create overlay with company information
packet = io.BytesIO()
can = canvas.Canvas(packet, pagesize=letter)

# Page 1 - Top company info
can.setFont("Helvetica", 10)
can.drawString(72, 735, "DEE DAVIS INC")  # Company
can.drawString(200, 735, "755 W Big Beaver Rd, Suite 2020")  # Street address
can.drawString(450, 735, "Troy")  # City

can.drawString(72, 720, "MI, 48084")  # State, Zip
can.drawString(200, 720, "248-376-4550")  # Phone
can.drawString(450, 720, "www.deedavis.biz")  # Website

# Order Desk contact (around line 60-63)
can.drawString(72, 340, "Dee Davis")  # Order desk name
can.drawString(200, 340, "Dee Davis")  # Customer service name

can.drawString(72, 325, "248-376-4550")  # Order desk phone
can.drawString(200, 325, "248-376-4550")  # Customer service phone

can.drawString(72, 310, "info@deedavis.biz")  # Order desk email
can.drawString(200, 310, "info@deedavis.biz")  # Customer service email

# Page 2 - Additional information
can.showPage()

# How long to hold pricing (line 67)
can.setFont("Helvetica", 10)
can.drawString(400, 640, "30 days")

# Delivery days (line 68)
can.drawString(450, 625, "14-21 days")

# Minimum order (line 69)
can.drawString(300, 610, "No minimum")

# Penalty for ordering less (line 70)
can.drawString(300, 595, "N/A")

# Payment discounts (line 71-72)
can.drawString(400, 580, "X")  # NO checkbox
can.drawString(300, 565, "N/A")

# Return policy (line 73)
can.drawString(300, 550, "Standard manufacturer warranty applies")

# Page 3 - Signature section
can.showPage()

# Leave signature line blank for manual signing
can.setFont("Helvetica", 10)
# Email
can.drawString(300, 660, "info@deedavis.biz")

# Print Name
can.drawString(72, 640, "Dee Davis")

# Date (leave blank or current date)
can.drawString(300, 640, "February 5, 2026")

# Bottom company info repeat
can.drawString(72, 620, "DEE DAVIS INC")
can.drawString(200, 620, "755 W Big Beaver Rd, Suite 2020")
can.drawString(450, 620, "Troy")

can.drawString(72, 605, "MI, 48084")
can.drawString(200, 605, "248-376-4550")
can.drawString(450, 605, "www.deedavis.biz")

can.save()

# Move to the beginning of the BytesIO buffer
packet.seek(0)

# Read the existing PDF
existing_pdf = PdfReader(open("this is 7802.pdf", "rb"))
output = PdfWriter()

# Read the overlay PDF
overlay_pdf = PdfReader(packet)

# Merge overlay with existing PDF
for i in range(len(existing_pdf.pages)):
    page = existing_pdf.pages[i]
    if i < len(overlay_pdf.pages):
        page.merge_page(overlay_pdf.pages[i])
    output.add_page(page)

# Write output
with open("RCOC_7802_COMPLETED_RFQ.pdf", "wb") as outputStream:
    output.write(outputStream)

print("✓ Generated: RCOC_7802_COMPLETED_RFQ.pdf")
print("  Company information filled in")
print("  Signature line LEFT BLANK for you to sign")
print("  Ready to print and sign!")
