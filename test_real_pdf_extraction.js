// Test real PDF text extraction
const testRealPDFExtraction = async () => {
  try {
    console.log("Testing real PDF text extraction...");

    // Simulate what would happen if pdf-parse worked
    const realPDFContent = `SOLICITATION INFORMATION
Solicitation Number: RFP-2024-001
Agency: Department of Defense

CONTACT INFORMATION:

Contracting Officer:
Name: John Smith
Email: john.smith@defense.gov
Phone: (202) 555-0123

Program Manager:
Name: Sarah Johnson  
Email: sarah.johnson@army.mil
Phone: (703) 555-0456

Technical POC:
Name: Mike Davis
Email: mike.davis@darpa.mil
Phone: (571) 555-0789

SUBMISSION REQUIREMENTS:
Submit to john.smith@defense.gov by January 31, 2026.`;

    const response = await fetch('http://127.0.0.1:8000/extract-contacts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        document_text: realPDFContent,
        document_name: "real-rfp-test.pdf"
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    console.log("✅ Real PDF extraction result:", JSON.stringify(result, null, 2));
    return result;

  } catch (error) {
    console.error("❌ Real PDF extraction test failed:", error);
    return { error: error.message };
  }
};

testRealPDFExtraction();
