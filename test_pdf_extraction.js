// Simple test to verify PDF extraction works
const testPDFExtraction = async () => {
  try {
    // Create a simple test file (not a real PDF, just for testing)
    const testContent = "Test PDF content with contact: john.doe@agency.gov";
    
    const response = await fetch('http://127.0.0.1:8000/extract-contacts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        document_text: testContent,
        document_name: "test.pdf"
      })
    });
    
    const result = await response.json();
    console.log("✅ PDF extraction test result:", result);
    return result;
  } catch (error) {
    console.error("❌ PDF extraction test failed:", error);
    return { error: error.message };
  }
};

testPDFExtraction();
