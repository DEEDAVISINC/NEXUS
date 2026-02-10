#!/usr/bin/env python3
"""
Bid Package Assembly Tool
Automatically assembles bid packages from company documents repository.

Usage:
    python3 assemble_bid_package.py --bid "RCOC Paper Products"
    python3 assemble_bid_package.py --check-docs
    python3 assemble_bid_package.py --list-missing
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import argparse

# Base path to company documents
DOCS_BASE = Path("/Users/deedavis/NEXUS BACKEND/COMPANY_DOCUMENTS")

# Standard document requirements by bid type
STANDARD_DOCS = {
    "always_required": [
        "TAX_LEGAL/W-9_Form_2026.pdf",
        "CERTIFICATIONS/EDWOSB_Certificate.pdf",
        "CERTIFICATIONS/WOSB_Certificate.pdf",
    ],
    "often_required": [
        "INSURANCE/General_Liability_Certificate.pdf",
        "TAX_LEGAL/SAM_Registration.pdf",
        "TAX_LEGAL/CAGE_Code_Documentation.pdf",
    ],
    "optional": [
        "CERTIFICATIONS/MBE_Certificate.pdf",
        "INSURANCE/Workers_Comp_Certificate.pdf",
        "COMPANY_INFO/References.pdf",
        "CAPABILITY_STATEMENTS/General_CapStatement.pdf",
    ]
}

def check_document_exists(doc_path):
    """Check if a document exists in the repository."""
    full_path = DOCS_BASE / doc_path
    return full_path.exists()

def get_document_info(doc_path):
    """Get information about a document."""
    full_path = DOCS_BASE / doc_path
    if full_path.exists():
        size = full_path.stat().st_size
        modified = datetime.fromtimestamp(full_path.stat().st_mtime)
        return {
            "exists": True,
            "path": str(full_path),
            "size": size,
            "size_mb": round(size / (1024 * 1024), 2),
            "modified": modified.strftime("%Y-%m-%d %H:%M:%S")
        }
    return {"exists": False}

def check_all_documents():
    """Check status of all standard documents."""
    print("\n" + "="*70)
    print("COMPANY DOCUMENTS STATUS CHECK")
    print("="*70)
    
    total_required = 0
    total_found = 0
    
    for category, docs in STANDARD_DOCS.items():
        print(f"\n📁 {category.upper().replace('_', ' ')}:")
        print("-" * 70)
        
        for doc in docs:
            info = get_document_info(doc)
            if info["exists"]:
                status = "✅ FOUND"
                print(f"  {status} - {doc}")
                print(f"           Size: {info['size_mb']} MB | Modified: {info['modified']}")
                total_found += 1
            else:
                status = "❌ MISSING"
                print(f"  {status} - {doc}")
            
            if category == "always_required":
                total_required += 1
    
    print("\n" + "="*70)
    print(f"SUMMARY: {total_found} documents found")
    print(f"REQUIRED: {total_required} essential documents")
    print(f"STATUS: {'✅ Ready for bid assembly' if total_found >= total_required else '⚠️  Missing required documents'}")
    print("="*70 + "\n")
    
    return total_found >= total_required

def list_missing_documents():
    """List all missing documents."""
    print("\n" + "="*70)
    print("MISSING DOCUMENTS REPORT")
    print("="*70)
    
    missing_required = []
    missing_optional = []
    
    for category, docs in STANDARD_DOCS.items():
        for doc in docs:
            if not check_document_exists(doc):
                if category == "always_required":
                    missing_required.append(doc)
                else:
                    missing_optional.append(doc)
    
    if missing_required:
        print("\n🚨 MISSING REQUIRED DOCUMENTS:")
        print("-" * 70)
        for doc in missing_required:
            print(f"  ❌ {doc}")
    else:
        print("\n✅ All required documents are uploaded!")
    
    if missing_optional:
        print("\n⚠️  MISSING OPTIONAL DOCUMENTS:")
        print("-" * 70)
        for doc in missing_optional:
            print(f"  ⚪ {doc}")
    
    print("\n" + "="*70 + "\n")

def assemble_bid_package(bid_name, output_dir=None):
    """Assemble a bid package with required documents."""
    if output_dir is None:
        output_dir = Path(f"/Users/deedavis/NEXUS BACKEND/photos_and_videos/{bid_name}/BID_PACKAGE")
    else:
        output_dir = Path(output_dir)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*70)
    print(f"ASSEMBLING BID PACKAGE: {bid_name}")
    print("="*70)
    
    copied_docs = []
    missing_docs = []
    
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
            print(f"  ✅ Copied: {dest_name}")
        else:
            missing_docs.append(doc)
            print(f"  ❌ Missing: {doc}")
    
    # Create package manifest
    manifest_path = output_dir / "PACKAGE_MANIFEST.txt"
    with open(manifest_path, 'w') as f:
        f.write(f"BID PACKAGE MANIFEST\n")
        f.write(f"Bid: {bid_name}\n")
        f.write(f"Assembled: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Location: {output_dir}\n\n")
        f.write(f"INCLUDED DOCUMENTS ({len(copied_docs)}):\n")
        for doc in copied_docs:
            f.write(f"  ✅ {doc}\n")
        if missing_docs:
            f.write(f"\nMISSING DOCUMENTS ({len(missing_docs)}):\n")
            for doc in missing_docs:
                f.write(f"  ❌ {doc}\n")
    
    print("\n" + "="*70)
    print(f"PACKAGE SUMMARY:")
    print(f"  Documents included: {len(copied_docs)}")
    print(f"  Documents missing: {len(missing_docs)}")
    print(f"  Output location: {output_dir}")
    print(f"  Manifest: {manifest_path}")
    print("="*70 + "\n")
    
    return {
        "bid_name": bid_name,
        "output_dir": str(output_dir),
        "copied": copied_docs,
        "missing": missing_docs,
        "success": len(missing_docs) == 0
    }

def main():
    parser = argparse.ArgumentParser(description="Assemble bid packages from company documents")
    parser.add_argument("--bid", help="Bid name to assemble package for")
    parser.add_argument("--output", help="Custom output directory")
    parser.add_argument("--check-docs", action="store_true", help="Check status of all documents")
    parser.add_argument("--list-missing", action="store_true", help="List missing documents")
    
    args = parser.parse_args()
    
    if args.check_docs:
        check_all_documents()
    elif args.list_missing:
        list_missing_documents()
    elif args.bid:
        result = assemble_bid_package(args.bid, args.output)
        if result["success"]:
            print("✅ Bid package assembled successfully!")
        else:
            print("⚠️  Bid package assembled with missing documents.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
