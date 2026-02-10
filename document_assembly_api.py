#!/usr/bin/env python3
"""
Document Assembly API Integration for NEXUS
Add these functions to api_server.py to enable document package assembly from NEXUS dashboard.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import base64
from typing import Dict, List, Any

# Import the local assemble_bid_package module
from assemble_bid_package import (
    check_document_exists,
    get_document_info,
    DOCS_BASE,
    STANDARD_DOCS
)

def assemble_package_for_airtable(opportunity_title: str, opportunity_id: str) -> Dict[str, Any]:
    """
    Assemble bid package and prepare for Airtable upload.
    
    Args:
        opportunity_title: Title of the opportunity (used for folder name)
        opportunity_id: Airtable record ID
        
    Returns:
        Dictionary with success status, documents list, missing docs, and attachment data
    """
    # Create output directory
    output_dir = Path(f"/Users/deedavis/NEXUS BACKEND/photos_and_videos/{opportunity_title}/BID_PACKAGE")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    copied_docs = []
    missing_docs = []
    attachments = []
    
    # Gather all documents (required + often required)
    all_docs = STANDARD_DOCS["always_required"] + STANDARD_DOCS["often_required"]
    
    for doc in all_docs:
        full_path = DOCS_BASE / doc
        if full_path.exists():
            # Copy to bid package folder
            dest_name = full_path.name
            dest_path = output_dir / dest_name
            shutil.copy2(full_path, dest_path)
            copied_docs.append(dest_name)
            
            # Prepare for Airtable attachment
            with open(dest_path, 'rb') as f:
                file_content = f.read()
                attachments.append({
                    "filename": dest_name,
                    "content_base64": base64.b64encode(file_content).decode('utf-8'),
                    "type": "application/pdf"
                })
        else:
            missing_docs.append(doc)
    
    # Create manifest
    manifest_path = output_dir / "PACKAGE_MANIFEST.txt"
    with open(manifest_path, 'w') as f:
        f.write(f"BID PACKAGE MANIFEST\n")
        f.write(f"Opportunity: {opportunity_title}\n")
        f.write(f"Opportunity ID: {opportunity_id}\n")
        f.write(f"Assembled: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Location: {output_dir}\n\n")
        f.write(f"INCLUDED DOCUMENTS ({len(copied_docs)}):\n")
        for doc in copied_docs:
            f.write(f"  ✅ {doc}\n")
        if missing_docs:
            f.write(f"\nMISSING DOCUMENTS ({len(missing_docs)}):\n")
            for doc in missing_docs:
                f.write(f"  ❌ {doc}\n")
    
    return {
        "success": len(missing_docs) == 0,
        "opportunity_title": opportunity_title,
        "opportunity_id": opportunity_id,
        "output_dir": str(output_dir),
        "copied": copied_docs,
        "missing": missing_docs,
        "attachments": attachments,
        "manifest_path": str(manifest_path)
    }


def get_documents_checklist_from_files(file_list: List[str]) -> List[str]:
    """
    Convert file names to Airtable checklist values.
    
    Args:
        file_list: List of file names
        
    Returns:
        List of checklist values for Airtable
    """
    checklist_mapping = {
        "W-9": ["W-9", "w-9", "w9"],
        "EDWOSB": ["EDWOSB", "edwosb"],
        "WOSB": ["WOSB", "wosb"],
        "MBE": ["MBE", "mbe"],
        "Insurance": ["Insurance", "Liability", "insurance"],
        "SAM": ["SAM", "sam"],
        "CAGE": ["CAGE", "cage"],
        "CapStatement": ["CapStatement", "Capability", "capability"],
        "References": ["References", "references"],
        "Banking": ["Banking", "ACH", "banking"],
        "WorkersComp": ["Workers", "Comp", "workers"]
    }
    
    checklist = []
    for file_name in file_list:
        file_lower = file_name.lower()
        for checklist_item, keywords in checklist_mapping.items():
            if any(keyword.lower() in file_lower for keyword in keywords):
                if checklist_item not in checklist:
                    checklist.append(checklist_item)
    
    return checklist


def determine_package_status(copied: List[str], missing: List[str]) -> str:
    """
    Determine package status based on what was copied and what's missing.
    
    Args:
        copied: List of copied document names
        missing: List of missing document paths
        
    Returns:
        Package status: "Attached", "Incomplete", or "Ready"
    """
    if len(missing) == 0 and len(copied) > 0:
        return "Attached"
    elif len(missing) > 0 and len(copied) > 0:
        return "Incomplete"
    elif len(copied) > 0:
        return "Ready"
    else:
        return "Not Needed"


# Flask endpoint to add to api_server.py
def create_assemble_package_endpoint():
    """
    This is the Flask endpoint code to add to api_server.py
    
    Add this after the other GPSS endpoints (around line 1500-2000):
    """
    endpoint_code = '''
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
    
    Returns:
        JSON with success status, documents list, and missing documents
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
        
        # 2. Get opportunity title for folder name
        opp_title = opportunity.get('Title') or opportunity.get('Solicitation Title') or f'Opportunity_{opportunity_id}'
        
        # Clean title for folder name (remove special characters)
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
        
        # Note: Airtable attachment upload requires special handling
        # For now, we just update the status and checklist
        # User can manually upload from the local folder
        
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
    
    Returns:
        JSON with document availability status
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
        
        # Count totals
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
'''
    
    return endpoint_code


if __name__ == "__main__":
    # Test the assembly function
    print("Testing document assembly...")
    result = assemble_package_for_airtable("TEST_OPPORTUNITY", "rec_test_123")
    print(f"Success: {result['success']}")
    print(f"Copied: {result['copied']}")
    print(f"Missing: {result['missing']}")
    print(f"Output: {result['output_dir']}")
    
    # Test checklist conversion
    checklist = get_documents_checklist_from_files(result['copied'])
    print(f"Checklist: {checklist}")
    
    # Test status determination
    status = determine_package_status(result['copied'], result['missing'])
    print(f"Status: {status}")
