#!/bin/bash
# Install Document Integration into NEXUS
# This script adds the document assembly endpoint to api_server.py

echo "======================================================================="
echo "NEXUS DOCUMENT INTEGRATION INSTALLER"
echo "======================================================================="
echo ""

# Check if api_server.py exists
if [ ! -f "api_server.py" ]; then
    echo "❌ Error: api_server.py not found"
    echo "   Please run this script from the NEXUS BACKEND directory"
    exit 1
fi

echo "✅ Found api_server.py"

# Check if document_assembly_api.py exists
if [ ! -f "document_assembly_api.py" ]; then
    echo "❌ Error: document_assembly_api.py not found"
    echo "   Please ensure all files are in place"
    exit 1
fi

echo "✅ Found document_assembly_api.py"

# Check if COMPANY_DOCUMENTS folder exists
if [ ! -d "COMPANY_DOCUMENTS" ]; then
    echo "⚠️  Warning: COMPANY_DOCUMENTS folder not found"
    echo "   Creating folder structure..."
    mkdir -p COMPANY_DOCUMENTS/{CERTIFICATIONS,TAX_LEGAL,INSURANCE,COMPANY_INFO,CAPABILITY_STATEMENTS}
    echo "✅ Created COMPANY_DOCUMENTS folder structure"
else
    echo "✅ Found COMPANY_DOCUMENTS folder"
fi

# Backup api_server.py
echo ""
echo "Creating backup of api_server.py..."
cp api_server.py api_server.py.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backup created"

# Check if document assembly endpoint already exists
if grep -q "assemble-package" api_server.py; then
    echo ""
    echo "⚠️  Document assembly endpoint already exists in api_server.py"
    echo "   Skipping API installation"
else
    echo ""
    echo "Adding document assembly endpoints to api_server.py..."
    
    # Add the endpoint code at the end of the file (before if __name__ == "__main__")
    python3 << 'EOF'
import re

# Read the api_server.py file
with open('api_server.py', 'r') as f:
    content = f.read()

# Find the location to insert (before if __name__ == "__main__")
insertion_point = content.rfind('if __name__ == "__main__"')

if insertion_point == -1:
    # If no main block, just append at the end
    insertion_point = len(content)

# The code to insert
new_endpoint_code = '''

# ============================================================================
# DOCUMENT ASSEMBLY ENDPOINTS - Added by install_document_integration.sh
# ============================================================================

@app.post("/api/gpss/opportunities/<opportunity_id>/assemble-package")
def assemble_bid_package_for_opportunity(opportunity_id: str):
    """
    Assemble bid package for a specific GPSS opportunity.
    
    Workflow:
    1. Get opportunity details from Airtable
    2. Gather documents from COMPANY_DOCUMENTS/
    3. Create package folder
    4. Prepare for Airtable upload
    5. Update opportunity record
    """
    try:
        from document_assembly_api import (
            assemble_package_for_airtable,
            get_documents_checklist_from_files,
            determine_package_status
        )
        
        # 1. Get opportunity from Airtable
        airtable = AirtableClient()
        opportunity = airtable.get_record('Opportunities', opportunity_id)
        
        if not opportunity:
            return jsonify({"error": "Opportunity not found"}), 404
        
        # 2. Get opportunity title
        opp_title = opportunity.get('Title') or opportunity.get('Solicitation Title') or f'Opportunity_{opportunity_id}'
        
        # Clean title for folder name
        import re
        opp_title_clean = re.sub(r'[^\w\s-]', '', opp_title).strip().replace(' ', '_')
        
        # 3. Assemble package
        result = assemble_package_for_airtable(opp_title_clean, opportunity_id)
        
        # 4. Determine checklist and status
        checklist = get_documents_checklist_from_files(result["copied"])
        status = determine_package_status(result["copied"], result["missing"])
        
        # 5. Update Airtable record
        update_data = {
            "Package Status": status,
            "Documents Checklist": checklist,
            "Package Assembled Date": datetime.now().isoformat(),
            "Package Assembled By": "NEXUS API"
        }
        
        airtable.update_record('Opportunities', opportunity_id, update_data)
        
        return jsonify({
            "success": result["success"],
            "opportunityTitle": result["opportunity_title"],
            "documents": result["copied"],
            "missing": result["missing"],
            "packagePath": result["output_dir"],
            "checklist": checklist,
            "status": status,
            "message": f"Package assembled at {result['output_dir']}" if result["success"] else f"Package incomplete. Missing: {', '.join(result['missing'])}"
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error assembling package: {error_details}")
        return jsonify({
            "error": str(e),
            "details": error_details
        }), 500


@app.get("/api/gpss/documents/status")
def check_documents_status():
    """
    Check status of all company documents.
    """
    try:
        from document_assembly_api import DOCS_BASE, STANDARD_DOCS, check_document_exists, get_document_info
        
        status = {
            "always_required": {},
            "often_required": {},
            "optional": {}
        }
        
        for category, docs in STANDARD_DOCS.items():
            for doc in docs:
                info = get_document_info(doc)
                status[category][doc] = info
        
        total_found = sum(1 for cat in status.values() for doc_info in cat.values() if doc_info.get("exists"))
        total_required = len(STANDARD_DOCS["always_required"])
        
        return jsonify({
            "status": status,
            "totalFound": total_found,
            "totalRequired": total_required,
            "ready": total_found >= total_required
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# END DOCUMENT ASSEMBLY ENDPOINTS
# ============================================================================

'''

# Insert the code
new_content = content[:insertion_point] + new_endpoint_code + content[insertion_point:]

# Write back
with open('api_server.py', 'w') as f:
    f.write(new_content)

print("✅ API endpoints added successfully")
EOF
fi

echo ""
echo "======================================================================="
echo "INSTALLATION COMPLETE!"
echo "======================================================================="
echo ""
echo "✅ Document assembly API installed"
echo "✅ COMPANY_DOCUMENTS folder ready"
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Upload your documents to COMPANY_DOCUMENTS/"
echo "   - W-9 → TAX_LEGAL/W-9_Form_2026.pdf"
echo "   - EDWOSB → CERTIFICATIONS/EDWOSB_Certificate.pdf"
echo "   - WOSB → CERTIFICATIONS/WOSB_Certificate.pdf"
echo "   - Insurance → INSURANCE/General_Liability_Certificate.pdf"
echo ""
echo "2. Update Airtable 'Opportunities' table with these fields:"
echo "   - Documents Package (Attachment)"
echo "   - Documents Checklist (Multiple Select: W-9, EDWOSB, WOSB, Insurance, SAM, CAGE)"
echo "   - Package Status (Single Select: Not Needed, Incomplete, Ready, Attached)"
echo "   - Package Assembled Date (Date)"
echo "   - Package Assembled By (Single Line Text)"
echo ""
echo "3. Add the frontend button to GPSSSystem.tsx"
echo "   - See gpss_frontend_document_button.tsx for code"
echo ""
echo "4. Test the integration:"
echo "   python3 assemble_bid_package.py --check-docs"
echo ""
echo "5. Start the API server:"
echo "   PORT=8000 python3 api_server.py"
echo ""
echo "======================================================================="
echo "DOCUMENTATION:"
echo "  - Full guide: NEXUS_DOCUMENT_INTEGRATION_GUIDE.md"
echo "  - API code: document_assembly_api.py"
echo "  - Frontend code: gpss_frontend_document_button.tsx"
echo "======================================================================="
