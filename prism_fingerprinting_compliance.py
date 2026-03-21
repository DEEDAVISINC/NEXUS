"""
PRISM Fingerprinting Compliance Module
======================================
Livescan workflows, quality control, ORI management,
and SWFT submission for FBI/state fingerprinting.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, List, Optional

prism_fingerprint = Blueprint('prism_fingerprint', __name__)


# =============================================================================
# LIVESCAN COLLECTION WORKFLOW
# =============================================================================

LIVESCAN_COLLECTION_WORKFLOW = {
    "type": "livescan_fingerprint_collection",
    "description": "Electronic fingerprint capture for criminal background checks",
    "equipment": "Livescan terminal (SWFT-authorized)",
    "steps": [
        {
            "step": 1,
            "action": "VERIFY IDENTITY",
            "details": "Check government-issued photo ID",
            "acceptable_ids": [
                "State driver's license (current)",
                "State ID card (current)",
                "US Passport (current)",
                "US Military ID (current)",
                "Permanent Resident Card"
            ],
            "record": "ID type and number for system entry"
        },
        {
            "step": 2,
            "action": "CONFIRM ORI CODE",
            "critical": "WRONG ORI = RESULTS GO TO WRONG PLACE",
            "details": "Verify ORI code with client/applicant",
            "common_sources": [
                "Licensing board provides ORI",
                "Employer provides ORI",
                "State agency ORI list"
            ]
        },
        {
            "step": 3,
            "action": "ENTER APPLICANT DATA",
            "required_fields": [
                "Full legal name (as on ID)",
                "Date of birth",
                "Social Security Number (last 4 minimum)",
                "Address",
                "ORI code",
                "Reason for prints"
            ],
            "verify": "Spelling must match ID exactly"
        },
        {
            "step": 4,
            "action": "PREPARE HANDS",
            "requirements": [
                "Clean - wash if needed",
                "Dry - moisture causes poor capture",
                "No lotion - interferes with capture",
                "No bandages if possible"
            ],
            "for_dry_fingers": "Light moisture (breath on fingers) can help"
        },
        {
            "step": 5,
            "action": "POSITION HAND ON PLATEN",
            "technique": [
                "Hand flat on glass",
                "Centered on capture area",
                "Fingers together but not overlapping"
            ]
        },
        {
            "step": 6,
            "action": "CAPTURE 4-FINGER SLAPS",
            "sequence": ["Right 4-finger slap", "Left 4-finger slap"],
            "quality_check": "NFIQ score 3 or better for each"
        },
        {
            "step": 7,
            "action": "CAPTURE INDIVIDUAL ROLLS",
            "technique": [
                "Roll from nail to nail",
                "Smooth, consistent motion",
                "Full fingerprint captured"
            ],
            "sequence": "Right thumb through right little, left thumb through left little"
        },
        {
            "step": 8,
            "action": "CAPTURE FLAT THUMBS",
            "details": "Both thumbs flat (simultaneous)",
            "purpose": "Verification prints"
        },
        {
            "step": 9,
            "action": "REVIEW QUALITY",
            "standard": "NFIQ (NIST Fingerprint Image Quality) score 1-3",
            "minimum": "NFIQ 3 or better for acceptance",
            "reject_if": "NFIQ 4 or 5 (retake required)"
        },
        {
            "step": 10,
            "action": "RETAKE IF NEEDED",
            "max_attempts": "3 attempts per finger",
            "if_still_failing": "Document 'best effort' and note quality issues"
        },
        {
            "step": 11,
            "action": "TRANSMIT",
            "method": "SWFT secure transmission",
            "verify": "Confirmation receipt received"
        },
        {
            "step": 12,
            "action": "PROVIDE RECEIPT",
            "give_to_applicant": [
                "Transaction number/TCN",
                "Date of submission",
                "ORI submitted to",
                "Expected turnaround"
            ]
        }
    ]
}

FD258_INK_CARD_WORKFLOW = {
    "type": "ink_and_roll_fingerprint",
    "description": "Traditional rolled ink fingerprints on FD-258 card",
    "when_used": [
        "Immigration applications",
        "Some federal agencies",
        "When livescan unavailable",
        "Specific agency requirements"
    ],
    "steps": [
        {
            "step": 1,
            "action": "VERIFY IDENTITY",
            "details": "Same as livescan - government photo ID required"
        },
        {
            "step": 2,
            "action": "COMPLETE FD-258 HEADER",
            "fields": [
                "ORI (if known)",
                "Name (BLOCK letters)",
                "Aliases",
                "Citizenship",
                "Date of birth",
                "Place of birth",
                "Social Security Number",
                "Sex, Race, Height, Weight",
                "Hair color, Eye color",
                "Residence",
                "Employer",
                "Reason fingerprinted"
            ],
            "critical": "Use BLOCK LETTERS - must be legible"
        },
        {
            "step": 3,
            "action": "PREPARE INK PAD",
            "technique": "Even distribution of ink",
            "common_error": "Too much ink causes smudging"
        },
        {
            "step": 4,
            "action": "ROLL EACH FINGER",
            "sequence": [
                "Right thumb",
                "Right index",
                "Right middle",
                "Right ring",
                "Right little",
                "Left thumb",
                "Left index",
                "Left middle",
                "Left ring",
                "Left little"
            ],
            "technique": "Nail to nail, smooth rolling motion"
        },
        {
            "step": 5,
            "action": "TAKE FLAT IMPRESSIONS",
            "details": "Simultaneous impression boxes at bottom",
            "purpose": "Verification of rolled prints"
        },
        {
            "step": 6,
            "action": "REVIEW QUALITY",
            "check_for": [
                "Clear ridges visible",
                "No smudges",
                "Complete prints",
                "All boxes filled"
            ]
        },
        {
            "step": 7,
            "action": "SIGN AND DATE",
            "who_signs": "COLLECTOR signs - applicant does NOT sign",
            "where": "Signature of official taking fingerprints box"
        },
        {
            "step": 8,
            "action": "MAIL TO AGENCY",
            "packaging": "Do not fold card",
            "shipping": "Per agency instructions"
        }
    ]
}


# =============================================================================
# QUALITY STANDARDS
# =============================================================================

NFIQ_QUALITY_STANDARDS = {
    "scale": "1-5 (1=best, 5=worst)",
    "levels": {
        1: {"quality": "Excellent", "action": "Accept"},
        2: {"quality": "Very Good", "action": "Accept"},
        3: {"quality": "Good", "action": "Accept (minimum)"},
        4: {"quality": "Fair", "action": "RETAKE - below standard"},
        5: {"quality": "Poor", "action": "RETAKE - unacceptable"}
    },
    "minimum_accepted": 3,
    "target": "1-2 for clean submissions"
}

QUALITY_ISSUES = {
    "low_contrast": {
        "cause": "Dry fingers",
        "solutions": [
            "Light moisture (breath on fingers)",
            "Thin layer of hand lotion, wait 2 min, wipe off",
            "Room temperature water (not cold)"
        ]
    },
    "smudged": {
        "cause": "Movement during capture",
        "solutions": [
            "Steady hand - don't move until beep",
            "Slower rolling motion",
            "Ensure relaxed hand"
        ]
    },
    "incomplete": {
        "cause": "Finger not fully on platen",
        "solutions": [
            "Reposition finger",
            "Ensure centered on capture area",
            "Press slightly (not too hard)"
        ]
    },
    "excessive_pressure": {
        "cause": "Pressing too hard",
        "solutions": [
            "Lighter touch",
            "Relax hand",
            "Guide don't force"
        ]
    },
    "white_lines": {
        "cause": "Cuts, scars, peeling skin",
        "solutions": [
            "Document the condition",
            "Submit as 'best effort'",
            "May need additional documentation"
        ]
    },
    "no_ridges": {
        "cause": "Worn fingerprints (age, manual labor, medical)",
        "solutions": [
            "Apply lotion, wait, wipe off",
            "Multiple attempts at different pressures",
            "Document 'best effort'",
            "May require ink card backup"
        ]
    }
}


# =============================================================================
# ORI MANAGEMENT
# =============================================================================

MICHIGAN_COMMON_ORIS = {
    "teacher_certification": {
        "ori": "MIEDUCATE",
        "agency": "Michigan Department of Education",
        "turnaround": "24-72 hours"
    },
    "nursing_license": {
        "ori": "MILARA",
        "agency": "LARA - Michigan Licensing and Regulatory Affairs",
        "turnaround": "24-72 hours"
    },
    "real_estate_license": {
        "ori": "MILARA",
        "agency": "LARA - Michigan Licensing and Regulatory Affairs",
        "turnaround": "24-72 hours"
    },
    "child_care_licensing": {
        "ori": "MIDHS",
        "agency": "Michigan Department of Health and Human Services",
        "turnaround": "24-72 hours"
    },
    "concealed_pistol_license": {
        "ori": "COUNTY-SPECIFIC",
        "note": "Contact local sheriff for ORI",
        "turnaround": "Varies by county"
    }
}


# =============================================================================
# FBI ELECTRONIC SUBMISSION CHANNELS
# =============================================================================

FBI_SUBMISSION_CHANNELS = {
    "channelers": {
        "description": "FBI-approved private companies for direct FBI submission",
        "companies": [
            {"name": "IdentoGO (IDEMIA)", "services": "Livescan, ink card, mobile"},
            {"name": "Fieldprint", "services": "Education, healthcare, gaming"},
            {"name": "MorphoTrust", "services": "Government, healthcare, transportation"},
            {"name": "Accurate Biometrics", "services": "Livescan, card scan"},
            {"name": "Certifix", "services": "Livescan network"}
        ],
        "benefit": "Bypass state channeling, faster results"
    },
    "ngi": {
        "name": "Next Generation Identification",
        "description": "FBI's core biometric database",
        "records": "150M+ fingerprint records",
        "submission_types": {
            "CAR": "Criminal Ten-print (arrest/booking)",
            "CAP": "Civil Applicant (employment/licensing)",
            "LAT": "Latent Print (crime scene)",
            "NST": "NIST Special (federal employment)"
        }
    },
    "rap_back": {
        "name": "Rap Back (Retention & Ongoing Monitoring)",
        "description": "Proactive notification of subsequent arrests",
        "how_it_works": [
            "Initial fingerprint background check conducted",
            "Employer enrolls individual in Rap Back",
            "FBI retains fingerprints",
            "If individual is subsequently arrested, employer is notified"
        ],
        "use_cases": [
            "Schools (teachers, staff)",
            "Healthcare (patient access)",
            "Financial services",
            "Government contractors",
            "Childcare facilities"
        ]
    },
    "identity_history_summary": {
        "name": "Identity History Summary Check",
        "description": "Individual requests their own FBI record",
        "cost": "$18 (approximate)",
        "submission_methods": [
            "Electronic via approved channeler",
            "Mail ink card (FD-258) to FBI"
        ],
        "use_cases": ["Personal records", "Immigration", "Foreign visa", "Adoption"]
    },
    "swft": {
        "name": "Secure Web Fingerprint Transmission",
        "description": "State-level electronic submission",
        "ddi_status": "AUTHORIZED",
        "benefit": "Direct electronic submission to participating states"
    }
}

ELECTRONIC_VS_CARD_COMPARISON = {
    "electronic": {
        "submission_time": "Minutes",
        "results_time": "Hours to days",
        "quality_check": "Real-time, before submission",
        "cost": "Higher per submission",
        "confirmation": "Immediate",
        "preferred": True
    },
    "card": {
        "submission_time": "Days (mail)",
        "results_time": "Weeks to months",
        "quality_check": "At FBI, rejection if poor",
        "cost": "Lower per submission",
        "confirmation": "Manual tracking",
        "preferred": False,
        "when_used": ["Backup if livescan unavailable", "Immigration", "Some federal agencies"]
    }
}


def validate_ori_format(ori: str) -> dict:
    """
    Validate ORI format.
    Standard format: 2 letters + 7 alphanumeric (varies by state)
    """
    result = {
        "ori": ori,
        "format_valid": False,
        "warnings": []
    }
    
    if not ori:
        result["warnings"].append("ORI is empty")
        return result
    
    ori_upper = ori.upper().strip()
    
    # Most ORIs are 9 characters
    if len(ori_upper) < 5:
        result["warnings"].append(f"ORI seems too short: {len(ori_upper)} characters")
    elif len(ori_upper) > 15:
        result["warnings"].append(f"ORI seems too long: {len(ori_upper)} characters")
    else:
        result["format_valid"] = True
    
    # Check for common Michigan prefixes
    if ori_upper.startswith("MI"):
        result["state"] = "Michigan"
        result["format_valid"] = True
    
    # Check for test/sample ORIs
    if "TEST" in ori_upper or "SAMPLE" in ori_upper:
        result["warnings"].append("ORI appears to be a test/sample code")
        result["format_valid"] = False
    
    return result


# =============================================================================
# REJECTION HANDLING
# =============================================================================

REJECTION_REASONS = [
    {
        "code": "WRONG_ORI",
        "description": "Results sent to wrong agency",
        "cause": "Incorrect ORI code entered",
        "prevention": "Verify ORI with client before submission",
        "resolution": "Resubmit with correct ORI"
    },
    {
        "code": "NAME_MISMATCH",
        "description": "Name doesn't match other records",
        "cause": "Name entered differently than on file",
        "prevention": "Enter name exactly as shown on ID",
        "resolution": "Resubmit with corrected name"
    },
    {
        "code": "LOW_QUALITY",
        "description": "Prints don't meet NFIQ standards",
        "cause": "Poor print quality",
        "prevention": "Ensure NFIQ 3+ before submission",
        "resolution": "Recollect with improved technique"
    },
    {
        "code": "INCOMPLETE_SET",
        "description": "Missing fingers without documentation",
        "cause": "Not all 10 fingers captured",
        "prevention": "Document missing fingers with codes (AMP, XX)",
        "resolution": "Resubmit with proper documentation"
    },
    {
        "code": "INVALID_ID",
        "description": "Expired or unacceptable ID type",
        "cause": "ID verification failed",
        "prevention": "Require current government photo ID",
        "resolution": "Recollect with valid ID"
    },
    {
        "code": "SYSTEM_ERROR",
        "description": "Transmission failure",
        "cause": "Technical issue",
        "prevention": "Verify system connectivity before collection",
        "resolution": "Resubmit when system available"
    }
]


def handle_quality_rejection(rejection_type: str, finger_positions: List[int] = None) -> dict:
    """
    Generate guidance for handling quality rejections.
    
    rejection_type: 'single_finger', 'multiple_fingers', 'all_fingers'
    finger_positions: list of finger numbers (1-10) that failed
    """
    guidance = {
        "rejection_type": rejection_type,
        "steps": []
    }
    
    if rejection_type == "single_finger":
        guidance["steps"] = [
            "1. Contact applicant for recollection",
            "2. Focus on the specific finger(s) that failed",
            "3. Try different technique (pressure, moisture)",
            "4. If still failing after 3 attempts, document 'best effort'",
            "5. Resubmit with documentation of quality issues"
        ]
    elif rejection_type == "multiple_fingers":
        guidance["steps"] = [
            "1. Contact applicant for recollection",
            "2. Assess if systemic issue (dry hands, worn prints)",
            "3. Apply moisture/lotion technique if dry",
            "4. Consider ink card backup if livescan continues to fail",
            "5. Document all quality issues"
        ]
    elif rejection_type == "all_fingers":
        guidance["steps"] = [
            "1. This may indicate a medical condition or severe wear",
            "2. Document the condition thoroughly",
            "3. Consider ink card as alternative",
            "4. Contact receiving agency about 'best effort' submission",
            "5. Applicant may need to contact agency directly"
        ]
    
    if finger_positions:
        guidance["affected_fingers"] = finger_positions
        finger_names = {
            1: "Right Thumb", 2: "Right Index", 3: "Right Middle",
            4: "Right Ring", 5: "Right Little", 6: "Left Thumb",
            7: "Left Index", 8: "Left Middle", 9: "Left Ring", 10: "Left Little"
        }
        guidance["affected_finger_names"] = [finger_names.get(p, f"Position {p}") for p in finger_positions]
    
    return guidance


# =============================================================================
# MISSING FINGER DOCUMENTATION
# =============================================================================

MISSING_FINGER_CODES = {
    "XX": "Finger missing or amputated",
    "UP": "Unable to print (temporary - bandage, burn)",
    "SR": "Scarred - ridges not visible",
    "AMP": "Amputated"
}


def document_missing_finger(finger_position: int, reason_code: str, notes: str = None) -> dict:
    """
    Generate proper documentation for missing/unprintable finger.
    
    finger_position: 1-10 (1=right thumb, 10=left little)
    reason_code: 'XX', 'UP', 'SR', 'AMP'
    notes: additional documentation
    """
    finger_names = {
        1: "Right Thumb", 2: "Right Index", 3: "Right Middle",
        4: "Right Ring", 5: "Right Little", 6: "Left Thumb",
        7: "Left Index", 8: "Left Middle", 9: "Left Ring", 10: "Left Little"
    }
    
    if reason_code not in MISSING_FINGER_CODES:
        return {"error": f"Invalid reason code: {reason_code}. Valid codes: {list(MISSING_FINGER_CODES.keys())}"}
    
    return {
        "finger_position": finger_position,
        "finger_name": finger_names.get(finger_position, f"Position {finger_position}"),
        "reason_code": reason_code,
        "reason_description": MISSING_FINGER_CODES[reason_code],
        "notes": notes,
        "documentation_requirement": "Enter code in place of fingerprint in system",
        "may_require": "Written statement explaining missing finger"
    }


# =============================================================================
# SWFT TRANSACTION CODES
# =============================================================================

SWFT_TRANSACTION_CODES = {
    "ACK": {
        "meaning": "Acknowledged - processing",
        "action": "Wait for final result",
        "typical_time": "Minutes to hours"
    },
    "ERRT": {
        "meaning": "Error in transmission",
        "action": "Retry submission",
        "troubleshoot": ["Check internet connection", "Verify SWFT service status"]
    },
    "ERRP": {
        "meaning": "Error in processing",
        "action": "Check data and resubmit",
        "troubleshoot": ["Verify all required fields", "Check ORI validity"]
    },
    "OK": {
        "meaning": "Successfully submitted",
        "action": "Provide receipt to applicant",
        "note": "Results will go to receiving agency"
    }
}


# =============================================================================
# API ENDPOINTS
# =============================================================================

@prism_fingerprint.route('/prism/fingerprint/workflow/<workflow_type>', methods=['GET'])
def get_fingerprint_workflow(workflow_type):
    """Get fingerprint collection workflow by type."""
    workflows = {
        'livescan': LIVESCAN_COLLECTION_WORKFLOW,
        'ink': FD258_INK_CARD_WORKFLOW,
        'fd258': FD258_INK_CARD_WORKFLOW
    }
    
    workflow = workflows.get(workflow_type.lower())
    if workflow:
        return jsonify(workflow)
    return jsonify({"error": f"Unknown workflow type: {workflow_type}"}), 404


@prism_fingerprint.route('/prism/fingerprint/quality-standards', methods=['GET'])
def get_quality_standards():
    """Get NFIQ quality standards and common issues."""
    return jsonify({
        "nfiq_standards": NFIQ_QUALITY_STANDARDS,
        "quality_issues": QUALITY_ISSUES
    })


@prism_fingerprint.route('/prism/fingerprint/validate-ori', methods=['GET'])
def validate_ori():
    """Validate ORI format."""
    ori = request.args.get('ori')
    if not ori:
        return jsonify({"error": "Must provide 'ori' parameter"}), 400
    
    result = validate_ori_format(ori)
    return jsonify(result)


@prism_fingerprint.route('/prism/fingerprint/michigan-oris', methods=['GET'])
def get_michigan_oris():
    """Get common Michigan ORI codes."""
    return jsonify(MICHIGAN_COMMON_ORIS)


@prism_fingerprint.route('/prism/fingerprint/rejection-guidance', methods=['POST'])
def get_rejection_guidance():
    """Get guidance for handling quality rejections."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Must provide rejection data"}), 400
    
    rejection_type = data.get('rejection_type', 'single_finger')
    finger_positions = data.get('finger_positions', [])
    
    result = handle_quality_rejection(rejection_type, finger_positions)
    return jsonify(result)


@prism_fingerprint.route('/prism/fingerprint/missing-finger', methods=['POST'])
def document_missing():
    """Document missing or unprintable finger."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Must provide finger data"}), 400
    
    result = document_missing_finger(
        finger_position=data.get('finger_position'),
        reason_code=data.get('reason_code'),
        notes=data.get('notes')
    )
    return jsonify(result)


@prism_fingerprint.route('/prism/fingerprint/swft-codes', methods=['GET'])
def get_swft_codes():
    """Get SWFT transaction code meanings."""
    return jsonify(SWFT_TRANSACTION_CODES)


@prism_fingerprint.route('/prism/fingerprint/rejection-reasons', methods=['GET'])
def get_rejection_reasons():
    """Get all possible rejection reasons and resolutions."""
    return jsonify({"rejection_reasons": REJECTION_REASONS})


@prism_fingerprint.route('/prism/fingerprint/fbi-channels', methods=['GET'])
def get_fbi_channels():
    """Get FBI electronic submission channels information."""
    return jsonify(FBI_SUBMISSION_CHANNELS)


@prism_fingerprint.route('/prism/fingerprint/electronic-vs-card', methods=['GET'])
def get_electronic_vs_card():
    """Get comparison of electronic vs card submission."""
    return jsonify(ELECTRONIC_VS_CARD_COMPARISON)


@prism_fingerprint.route('/prism/fingerprint/channelers', methods=['GET'])
def get_fbi_channelers():
    """Get list of FBI approved channelers."""
    return jsonify({
        "channelers": FBI_SUBMISSION_CHANNELS["channelers"]["companies"],
        "description": FBI_SUBMISSION_CHANNELS["channelers"]["description"],
        "benefit": FBI_SUBMISSION_CHANNELS["channelers"]["benefit"]
    })


@prism_fingerprint.route('/prism/fingerprint/rap-back', methods=['GET'])
def get_rap_back_info():
    """Get Rap Back (ongoing monitoring) information."""
    return jsonify(FBI_SUBMISSION_CHANNELS["rap_back"])


if __name__ == '__main__':
    print("PRISM Fingerprinting Compliance Module loaded")
    print(f"Livescan workflow: {len(LIVESCAN_COLLECTION_WORKFLOW['steps'])} steps")
    print(f"Quality issues defined: {len(QUALITY_ISSUES)}")
