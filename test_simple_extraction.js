// Test the simplified extraction flow
const testSimpleExtraction = async () => {
  try {
    console.log("Testing simplified PDF extraction...");
    
    // Simulate the document text that would be sent
    const testContent = `PDF Document: sample-rfp.pdf
Size: 245760 bytes
Type: application/pdf
Upload Date: 2026-01-10T12:00:00.000Z

[Note: This is a simplified PDF extraction. The full document content will be processed by our AI contact extraction system. For best results, ensure your PDF contains text-based contact information rather than image-based content.]

Document Structure Analysis:
• Document appears to be a government RFP/contract document
• Looking for email addresses (@.gov, @.mil, @agency domains)
• Searching for phone numbers and contact names
• Identifying titles like Contracting Officer, Program Manager, POC

Please ensure the PDF contains contact information in text format.

Contact: john.smith@defense.gov
Phone: (202) 555-0123
Title: Contracting Officer`;

    const response = await fetch('http://127.0.0.1:8000/extract-contacts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        document_text: testContent,
        document_name: "test-rfp.pdf"
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    console.log("✅ Extraction successful:", result);
    return result;
    
  } catch (error) {
    console.error("❌ Extraction failed:", error);
    return { error: error.message };
  }
};

testSimpleExtraction();
