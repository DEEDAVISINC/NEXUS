"""
PRISM Notary Compliance Module
==============================
Notarial acts, identity verification, RON (Remote Online Notarization),
journal requirements, and state-specific compliance.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, List, Optional

prism_notary = Blueprint('prism_notary', __name__)


# =============================================================================
# NOTARIAL ACTS
# =============================================================================

NOTARIAL_ACTS = {
    "acknowledgment": {
        "name": "Acknowledgment",
        "purpose": "Signer acknowledges they signed the document voluntarily",
        "requirements": [
            "Signer personally appears before notary",
            "Notary verifies signer's identity",
            "Signer acknowledges the signature (may have signed earlier)",
            "Notary completes acknowledgment certificate"
        ],
        "signer_must_sign_in_presence": False,
        "common_uses": [
            "Deeds and real estate transfers",
            "Powers of attorney",
            "Trusts",
            "Corporate documents",
            "Affidavits of identity"
        ],
        "certificate_elements": [
            "State and county",
            "Date",
            "Signer name",
            "Statement of acknowledgment",
            "Notary signature",
            "Notary seal",
            "Commission expiration date"
        ]
    },
    "jurat": {
        "name": "Jurat (Oath/Affirmation)",
        "purpose": "Signer swears or affirms the contents of the document are true",
        "requirements": [
            "Signer MUST sign in notary's presence",
            "Notary administers verbal oath or affirmation",
            "Signer swears/affirms under penalty of perjury",
            "Notary completes jurat certificate"
        ],
        "signer_must_sign_in_presence": True,
        "common_uses": [
            "Affidavits",
            "Sworn statements",
            "Depositions",
            "Financial statements",
            "Immigration forms"
        ],
        "oath_language": "Do you solemnly swear (or affirm) that the statements in this document are true and correct to the best of your knowledge?",
        "certificate_elements": [
            "State and county",
            "Date",
            "Statement that signer subscribed and swore/affirmed",
            "Notary signature",
            "Notary seal",
            "Commission expiration date"
        ]
    },
    "copy_certification": {
        "name": "Copy Certification",
        "purpose": "Certify that a copy is a true copy of an original document",
        "requirements": [
            "Notary compares copy to original",
            "Original is NOT a public record",
            "Notary certifies copy is accurate reproduction"
        ],
        "prohibited_documents": [
            "Birth certificates",
            "Death certificates",
            "Marriage certificates",
            "Divorce decrees",
            "Court orders (certified copies from court only)",
            "Any document where certified copies must come from issuing agency"
        ],
        "allowed_documents": [
            "Diplomas",
            "Passports (informational)",
            "Personal documents",
            "Business records",
            "Contracts"
        ]
    },
    "signature_witnessing": {
        "name": "Signature Witnessing",
        "purpose": "Notary witnesses signer signing the document",
        "requirements": [
            "Signer signs in notary's presence",
            "No oath required (unlike jurat)",
            "Notary notes they witnessed the signature"
        ],
        "signer_must_sign_in_presence": True,
        "common_uses": [
            "Wills (in some states)",
            "Contracts requiring witnessed signatures",
            "Medical directives"
        ]
    }
}


def determine_notarial_act(document_type: str, purpose: str = None) -> dict:
    """
    Determine which notarial act is appropriate.
    
    document_type: 'deed', 'affidavit', 'power_of_attorney', etc.
    purpose: optional context for the notarization
    """
    document_type_lower = document_type.lower()
    
    # Acknowledgment documents
    acknowledgment_docs = ['deed', 'power of attorney', 'poa', 'trust', 'mortgage', 
                          'corporate resolution', 'articles of incorporation']
    
    # Jurat documents
    jurat_docs = ['affidavit', 'sworn statement', 'deposition', 'financial statement',
                 'immigration form', 'declaration under penalty of perjury']
    
    # Copy certification
    copy_cert_docs = ['diploma', 'passport copy', 'personal document copy']
    
    if any(doc in document_type_lower for doc in acknowledgment_docs):
        return {
            "recommended_act": "acknowledgment",
            "details": NOTARIAL_ACTS["acknowledgment"],
            "note": "Signer acknowledges the signature - does NOT need to sign in your presence"
        }
    elif any(doc in document_type_lower for doc in jurat_docs):
        return {
            "recommended_act": "jurat",
            "details": NOTARIAL_ACTS["jurat"],
            "note": "Signer MUST sign in your presence and take an oath/affirmation"
        }
    elif any(doc in document_type_lower for doc in copy_cert_docs):
        return {
            "recommended_act": "copy_certification",
            "details": NOTARIAL_ACTS["copy_certification"],
            "warning": "Cannot certify copies of vital records (birth, death, marriage certificates)"
        }
    else:
        return {
            "recommendation": "Review document for notarial language",
            "guidance": [
                "Look for 'subscribed and sworn' = JURAT",
                "Look for 'acknowledged before me' = ACKNOWLEDGMENT",
                "If document has both, follow document instructions",
                "When in doubt, contact requesting party for clarification"
            ],
            "available_acts": list(NOTARIAL_ACTS.keys())
        }


# =============================================================================
# IDENTITY VERIFICATION
# =============================================================================

ACCEPTABLE_IDS = {
    "primary": {
        "description": "Generally accepted in all states",
        "ids": [
            {"type": "State driver's license", "must_be": "Current (not expired)"},
            {"type": "State ID card", "must_be": "Current (not expired)"},
            {"type": "US Passport", "must_be": "Current (not expired)"},
            {"type": "US Military ID", "must_be": "Current"}
        ]
    },
    "secondary": {
        "description": "May require additional verification",
        "ids": [
            {"type": "Foreign passport with US visa", "note": "Acceptability varies by state"},
            {"type": "Permanent resident card (green card)", "must_be": "Current"},
            {"type": "Tribal ID", "note": "Some states accept"}
        ]
    },
    "not_acceptable_alone": {
        "description": "Usually NOT sufficient as sole identification",
        "ids": [
            {"type": "Student ID", "reason": "No government verification"},
            {"type": "Employee ID", "reason": "No government verification"},
            {"type": "Credit card", "reason": "No photo typically"},
            {"type": "Social Security card", "reason": "No photo"}
        ]
    }
}

ID_VERIFICATION_REQUIREMENTS = {
    "photo": "Must be present and recognizable (person should look like photo)",
    "expiration": "Must be current - expired ID is NOT acceptable",
    "physical_description": "Should reasonably match signer",
    "signature": "If present, should match how signer signs"
}

CREDIBLE_WITNESS_RULES = {
    "when_used": "When signer lacks acceptable ID",
    "one_witness_states": {
        "requirements": [
            "Witness must have acceptable ID",
            "Witness must personally know the signer",
            "Witness must personally know the notary (some states)",
            "Witness swears to signer's identity"
        ]
    },
    "two_witness_states": {
        "requirements": [
            "Both witnesses must have acceptable ID",
            "Both witnesses must personally know the signer",
            "Witnesses cannot have financial interest in document",
            "Both witnesses swear to signer's identity"
        ]
    }
}


def verify_id_acceptability(id_type: str, is_current: bool, state: str = "MI") -> dict:
    """
    Verify if ID is acceptable for notarization.
    """
    result = {
        "id_type": id_type,
        "is_current": is_current,
        "state": state,
        "acceptable": False,
        "notes": []
    }
    
    if not is_current:
        result["notes"].append("EXPIRED ID IS NOT ACCEPTABLE - signer must provide current ID")
        return result
    
    id_lower = id_type.lower()
    
    # Check primary IDs
    primary_types = ['driver', 'license', 'state id', 'passport', 'military']
    if any(pt in id_lower for pt in primary_types):
        result["acceptable"] = True
        result["category"] = "Primary ID"
        return result
    
    # Check secondary IDs
    secondary_types = ['green card', 'permanent resident', 'foreign passport']
    if any(st in id_lower for st in secondary_types):
        result["acceptable"] = True
        result["category"] = "Secondary ID"
        result["notes"].append("Additional verification may be required in some states")
        return result
    
    # Not acceptable alone
    not_acceptable = ['student', 'employee', 'credit card', 'social security']
    if any(na in id_lower for na in not_acceptable):
        result["acceptable"] = False
        result["category"] = "Not acceptable as sole ID"
        result["notes"].append("This ID type is not sufficient for notarization")
        result["alternative"] = "Signer must provide government-issued photo ID or use credible witnesses"
        return result
    
    result["notes"].append("ID type not recognized - verify with state requirements")
    return result


# =============================================================================
# REMOTE ONLINE NOTARIZATION (RON)
# =============================================================================

RON_REQUIREMENTS = {
    "definition": "Notarization via live audio-video communication",
    "key_elements": [
        "Signer and notary in different physical locations",
        "Live, synchronous audio-video session",
        "Electronic document, electronic signature, electronic seal",
        "Session recorded for compliance"
    ],
    "states_allowing_ron": [
        "Michigan", "Texas", "Florida", "Virginia", "Ohio", "Nevada",
        "Arizona", "Colorado", "Idaho", "Indiana", "Iowa", "Kentucky",
        "Maryland", "Minnesota", "Montana", "Nebraska", "North Dakota",
        "Oklahoma", "Tennessee", "Utah", "Washington", "Wisconsin"
    ],
    "identity_proofing": {
        "KBA": {
            "name": "Knowledge-Based Authentication",
            "description": "Questions generated from public records that only signer should know",
            "requirements": "5 questions, signer must answer 4 correctly within 2 minutes"
        },
        "credential_analysis": {
            "description": "Automated verification of government-issued ID",
            "checks": ["ID authenticity", "Photo match", "Expiration", "Tampering"]
        }
    }
}

RON_WORKFLOW = {
    "type": "remote_online_notarization",
    "description": "RON session workflow",
    "steps": [
        {
            "step": 1,
            "action": "SCHEDULE SESSION",
            "details": "Signer books through RON platform"
        },
        {
            "step": 2,
            "action": "IDENTITY PROOFING - KBA",
            "details": "Signer answers knowledge-based authentication questions",
            "requirement": "4 of 5 correct within 2 minutes"
        },
        {
            "step": 3,
            "action": "CREDENTIAL ANALYSIS",
            "details": "Signer's ID scanned and verified by system",
            "checks": ["Authenticity", "Not expired", "Not tampered"]
        },
        {
            "step": 4,
            "action": "CONNECT LIVE SESSION",
            "details": "Audio-video connection established",
            "requirement": "Both audio AND video required throughout"
        },
        {
            "step": 5,
            "action": "NOTARY VERIFIES IDENTITY",
            "details": "Notary confirms signer matches ID and KBA",
            "ask": "Confirm name, confirm you are the person who completed identity proofing"
        },
        {
            "step": 6,
            "action": "REVIEW DOCUMENT",
            "details": "Notary can see document on screen",
            "ensure": "Signer understands what they're signing"
        },
        {
            "step": 7,
            "action": "ADMINISTER OATH (if jurat)",
            "details": "Verbal oath/affirmation on camera",
            "record": "Must be captured in recording"
        },
        {
            "step": 8,
            "action": "SIGNER APPLIES E-SIGNATURE",
            "details": "Electronic signature applied to document"
        },
        {
            "step": 9,
            "action": "NOTARY COMPLETES CERTIFICATE",
            "details": "E-signature and e-seal applied",
            "include": "RON-specific notarial certificate language"
        },
        {
            "step": 10,
            "action": "SESSION ENDS",
            "details": "Recording saved per retention requirements",
            "retention": "Per state law (often 5-10 years)"
        }
    ]
}

RON_LIMITATIONS = [
    {
        "limitation": "Real estate",
        "details": "Some states/counties don't accept RON for property transfers",
        "action": "Check with title company and county recorder"
    },
    {
        "limitation": "Wet signatures required",
        "details": "Some documents specifically require original ink signature",
        "action": "Check document requirements"
    },
    {
        "limitation": "Signer comfort",
        "details": "Not all signers comfortable with technology",
        "action": "Offer in-person alternative"
    },
    {
        "limitation": "International acceptance",
        "details": "RON may not be accepted in other countries",
        "action": "Verify with receiving country/entity"
    }
]


# =============================================================================
# JOURNAL REQUIREMENTS
# =============================================================================

JOURNAL_REQUIREMENTS = {
    "mandatory_states": [
        "California", "Colorado", "Arizona", "Missouri", "Texas"
    ],
    "recommended_even_if_not_required": True,
    "reasons_to_keep_journal": [
        "Protects notary in disputes",
        "Provides evidence of proper procedure",
        "Professional standard",
        "May be required by E&O insurance"
    ],
    "required_entry_elements": {
        "always_required": [
            "Date and time of notarization",
            "Type of notarial act performed",
            "Type of document",
            "Signer's name",
            "How identity was verified"
        ],
        "often_required": [
            "Signer's address",
            "ID type and number",
            "Signer's signature in journal",
            "Fee charged"
        ],
        "optional_but_recommended": [
            "Document reference number",
            "Notes about circumstances",
            "Thumbprint (California requires for certain documents)"
        ]
    }
}


def create_journal_entry(entry_data: dict) -> dict:
    """
    Create a properly formatted journal entry.
    
    entry_data should include:
    - date_time: datetime
    - notarial_act: str
    - document_type: str
    - signer_name: str
    - signer_address: str (optional)
    - id_type: str
    - id_number: str (optional)
    - fee_charged: float (optional)
    - notes: str (optional)
    """
    entry = {
        "entry_id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "date_time": entry_data.get('date_time', datetime.now()).isoformat() if isinstance(entry_data.get('date_time'), datetime) else entry_data.get('date_time'),
        "notarial_act": entry_data.get('notarial_act'),
        "document_type": entry_data.get('document_type'),
        "signer": {
            "name": entry_data.get('signer_name'),
            "address": entry_data.get('signer_address', '')
        },
        "identification": {
            "type": entry_data.get('id_type'),
            "number": entry_data.get('id_number', 'On file')
        },
        "fee_charged": entry_data.get('fee_charged', 0),
        "notes": entry_data.get('notes', ''),
        "complete": True
    }
    
    # Validate required fields
    required = ['notarial_act', 'document_type', 'signer_name', 'id_type']
    missing = [f for f in required if not entry_data.get(f.replace('signer_', ''))]
    
    if missing:
        entry["complete"] = False
        entry["missing_fields"] = missing
    
    return entry


# =============================================================================
# COMMON ERRORS
# =============================================================================

NOTARY_FATAL_ERRORS = [
    {
        "error": "Notarizing without signer present",
        "why_fatal": "Fundamental violation of notary law",
        "consequence": "Notarization void, potential criminal charges"
    },
    {
        "error": "Not verifying identity",
        "why_fatal": "Cannot confirm who signed",
        "consequence": "Notarization void, liability for fraud"
    },
    {
        "error": "Incomplete certificate",
        "why_fatal": "Missing required elements",
        "consequence": "Document may be rejected, need re-notarization"
    },
    {
        "error": "Notarizing own signature",
        "why_fatal": "Conflict of interest - cannot be neutral",
        "consequence": "Notarization void"
    },
    {
        "error": "Notarizing for prohibited family member",
        "why_fatal": "Financial interest or conflict",
        "consequence": "Notarization void (rules vary by state)"
    },
    {
        "error": "Acting with expired commission",
        "why_fatal": "No authority to notarize",
        "consequence": "Notarization void, potential fines"
    },
    {
        "error": "Notarizing outside jurisdiction",
        "why_fatal": "No authority in that state",
        "consequence": "Notarization void"
    },
    {
        "error": "Backdating notarization",
        "why_fatal": "Falsifying official record",
        "consequence": "Criminal fraud, commission revocation"
    }
]

NOTARY_CORRECTABLE_ISSUES = [
    {
        "issue": "Wrong date on certificate",
        "correction": "Do NOT alter - re-notarize with correct date"
    },
    {
        "issue": "Incomplete certificate (signer available)",
        "correction": "Complete certificate, have signer acknowledge"
    },
    {
        "issue": "Missing seal (document available)",
        "correction": "Affix seal to document"
    },
    {
        "issue": "Wrong county/venue",
        "correction": "Re-notarize with correct venue"
    }
]


# =============================================================================
# STATE FEE LIMITS
# =============================================================================

STATE_FEE_LIMITS = {
    "MI": {"max_per_act": 10, "state": "Michigan"},
    "CA": {"max_per_signature": 15, "state": "California"},
    "FL": {"max_per_act": 10, "state": "Florida"},
    "TX": {"max_per_act": 6, "state": "Texas"},
    "NY": {"max_per_signature": 2, "state": "New York"},
    "OH": {"max_per_act": 5, "state": "Ohio"},
    "note": "Travel fees are separate and typically not regulated"
}


# =============================================================================
# API ENDPOINTS
# =============================================================================

@prism_notary.route('/prism/notary/acts', methods=['GET'])
def get_notarial_acts():
    """Get all notarial act types and requirements."""
    return jsonify(NOTARIAL_ACTS)


@prism_notary.route('/prism/notary/determine-act', methods=['GET'])
def determine_act():
    """Determine appropriate notarial act for document type."""
    document_type = request.args.get('document_type')
    purpose = request.args.get('purpose')
    
    if not document_type:
        return jsonify({"error": "Must provide 'document_type' parameter"}), 400
    
    result = determine_notarial_act(document_type, purpose)
    return jsonify(result)


@prism_notary.route('/prism/notary/verify-id', methods=['GET'])
def verify_id():
    """Verify ID acceptability."""
    id_type = request.args.get('id_type')
    is_current = request.args.get('is_current', 'true').lower() == 'true'
    state = request.args.get('state', 'MI')
    
    if not id_type:
        return jsonify({"error": "Must provide 'id_type' parameter"}), 400
    
    result = verify_id_acceptability(id_type, is_current, state)
    return jsonify(result)


@prism_notary.route('/prism/notary/acceptable-ids', methods=['GET'])
def get_acceptable_ids():
    """Get list of acceptable identification types."""
    return jsonify({
        "acceptable_ids": ACCEPTABLE_IDS,
        "verification_requirements": ID_VERIFICATION_REQUIREMENTS,
        "credible_witness_rules": CREDIBLE_WITNESS_RULES
    })


@prism_notary.route('/prism/notary/ron-requirements', methods=['GET'])
def get_ron_requirements():
    """Get RON (Remote Online Notarization) requirements."""
    return jsonify({
        "requirements": RON_REQUIREMENTS,
        "workflow": RON_WORKFLOW,
        "limitations": RON_LIMITATIONS
    })


@prism_notary.route('/prism/notary/journal-entry', methods=['POST'])
def create_journal():
    """Create a journal entry."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Must provide entry data"}), 400
    
    result = create_journal_entry(data)
    return jsonify(result)


@prism_notary.route('/prism/notary/journal-requirements', methods=['GET'])
def get_journal_requirements():
    """Get journal keeping requirements."""
    return jsonify(JOURNAL_REQUIREMENTS)


@prism_notary.route('/prism/notary/errors', methods=['GET'])
def get_notary_errors():
    """Get common notary errors and corrections."""
    return jsonify({
        "fatal_errors": NOTARY_FATAL_ERRORS,
        "correctable_issues": NOTARY_CORRECTABLE_ISSUES
    })


@prism_notary.route('/prism/notary/fee-limits', methods=['GET'])
def get_fee_limits():
    """Get state fee limits."""
    state = request.args.get('state')
    
    if state:
        state_upper = state.upper()
        if state_upper in STATE_FEE_LIMITS:
            return jsonify({state_upper: STATE_FEE_LIMITS[state_upper]})
        return jsonify({"error": f"State {state} not in database"}), 404
    
    return jsonify(STATE_FEE_LIMITS)


if __name__ == '__main__':
    print("PRISM Notary Compliance Module loaded")
    print(f"Notarial acts defined: {len(NOTARIAL_ACTS)}")
    print(f"RON workflow steps: {len(RON_WORKFLOW['steps'])}")
