"""
PRISM DNA Testing Compliance Module
====================================
Chain of custody workflows, legal vs informational testing,
collection procedures, and quality control for DNA relationship testing.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib

prism_dna = Blueprint('prism_dna', __name__)


# =============================================================================
# DNA COLLECTION WORKFLOWS
# =============================================================================

DNA_LEGAL_COLLECTION_WORKFLOW = {
    "type": "legal_dna_collection",
    "description": "Chain of custody collection for court-admissible DNA testing",
    "critical_note": "Legal testing requires STRICT chain of custody - any break voids the test",
    "steps": [
        {
            "step": 1,
            "action": "VERIFY APPOINTMENT",
            "details": "Confirm all participants are present. If testing alleged father + mother + child, ALL must be present.",
            "documentation": "Note who is present, relationship claimed, any absent participants"
        },
        {
            "step": 2,
            "action": "VERIFY IDENTITY",
            "details": "Check government-issued photo ID for ALL participants",
            "acceptable_ids": ["Driver's license", "State ID", "Passport", "Military ID"],
            "record": ["ID type", "ID number", "Expiration date", "Name exactly as shown"],
            "for_minors": "Legal guardian must present their ID and sign consent"
        },
        {
            "step": 3,
            "action": "PHOTOGRAPH PARTICIPANTS",
            "details": "Take photograph of each participant with their identification sheet",
            "requirements": [
                "Face clearly visible",
                "Name placard or form visible in photo",
                "Photo must be suitable for identity verification"
            ]
        },
        {
            "step": 4,
            "action": "EXPLAIN PROCESS",
            "details": "Describe what will happen, answer any questions",
            "points_to_cover": [
                "Buccal swab collection (not painful)",
                "30 minutes no food/drink/smoke requirement",
                "Results timeline",
                "Where results will be sent"
            ]
        },
        {
            "step": 5,
            "action": "COMPLETE CONSENT FORMS",
            "details": "Each participant signs consent and chain of custody form",
            "for_minors": "Legal guardian signs on behalf of minor",
            "requirement": "SIGNATURES REQUIRED BEFORE COLLECTION"
        },
        {
            "step": 6,
            "action": "PREPARE COLLECTION AREA",
            "details": "Clean surface, organize materials, ensure proper lighting"
        },
        {
            "step": 7,
            "action": "DON FRESH GLOVES",
            "details": "Put on new gloves before touching ANY collection materials",
            "critical": "CHANGE GLOVES BETWEEN EACH PARTICIPANT"
        },
        {
            "step": 8,
            "action": "OPEN COLLECTION KIT",
            "details": "Open kit IN PARTICIPANT'S PRESENCE",
            "verify": "Kit seal is intact before opening"
        },
        {
            "step": 9,
            "action": "COLLECT BUCCAL SWABS",
            "technique": [
                "Rub swab firmly against inside of cheek",
                "Rotate swab to collect cells from multiple areas",
                "Duration: 30-60 seconds per swab (follow lab instructions)",
                "Typically 4 swabs per participant"
            ],
            "critical": "WATCH ENTIRE COLLECTION - participant collects under observation"
        },
        {
            "step": 10,
            "action": "AIR DRY SWABS",
            "details": "Allow swabs to air dry 1-2 minutes before packaging",
            "reason": "Prevents mold growth, DNA degradation"
        },
        {
            "step": 11,
            "action": "LABEL ENVELOPE",
            "critical": "Label envelope DURING collection, NOT pre-labeled",
            "reason": "Pre-labeling creates sample switching risk",
            "label_info": ["Participant name", "Collection date", "Collector initials"]
        },
        {
            "step": 12,
            "action": "PLACE SWABS IN ENVELOPE",
            "critical": "Use PAPER envelope only - NEVER plastic",
            "reason": "Plastic causes moisture damage and DNA degradation"
        },
        {
            "step": 13,
            "action": "SEAL ENVELOPE",
            "details": "Apply tamper-evident seal",
            "requirement": "PARTICIPANT INITIALS THE SEAL"
        },
        {
            "step": 14,
            "action": "REPEAT FOR EACH PARTICIPANT",
            "reminder": "CHANGE GLOVES between each participant",
            "document": "Complete same process for each person tested"
        },
        {
            "step": 15,
            "action": "COMPLETE ALL PAPERWORK",
            "requirements": [
                "All participants signed all forms",
                "Collector signed all forms",
                "Photographs attached",
                "ID information recorded"
            ]
        },
        {
            "step": 16,
            "action": "PACKAGE FOR SHIPPING",
            "details": "Sealed outer packaging with chain of custody form inside"
        },
        {
            "step": 17,
            "action": "SHIP VIA TRACKED CARRIER",
            "acceptable": ["FedEx", "UPS", "USPS Priority"],
            "requirement": "KEEP TRACKING NUMBER",
            "note": "Samples must remain in collector's possession until shipped"
        },
        {
            "step": 18,
            "action": "PROVIDE RECEIPT",
            "details": "Give participant copy of chain of custody form",
            "for_records": "Participant can track their sample"
        }
    ]
}

DNA_INFORMATIONAL_COLLECTION_WORKFLOW = {
    "type": "informational_dna_collection",
    "description": "Non-legal DNA collection - results NOT court-admissible",
    "note": "Simpler process, faster turnaround, but NOT valid for legal purposes",
    "steps": [
        {
            "step": 1,
            "action": "EXPLAIN LIMITATIONS",
            "critical": "Participant MUST understand results are NOT court-admissible",
            "get_acknowledgment": True
        },
        {
            "step": 2,
            "action": "COLLECT SAMPLE",
            "details": "Same buccal swab technique as legal",
            "chain_of_custody": "NOT required for informational"
        },
        {
            "step": 3,
            "action": "PACKAGE AND SHIP",
            "details": "Follow lab instructions for packaging"
        }
    ]
}


# =============================================================================
# FATAL FLAWS - DNA TESTING
# =============================================================================

DNA_FATAL_FLAWS = [
    {
        "id": "DNA_FATAL_001",
        "flaw": "No collector signature on chain of custody",
        "impact": "Cannot verify who collected sample",
        "action": "COLLECTION REJECTED - must recollect"
    },
    {
        "id": "DNA_FATAL_002",
        "flaw": "No participant signatures on consent/COC",
        "impact": "No documented consent",
        "action": "COLLECTION REJECTED - must recollect"
    },
    {
        "id": "DNA_FATAL_003",
        "flaw": "Broken tamper-evident seal",
        "impact": "Chain of custody compromised",
        "action": "COLLECTION REJECTED - must recollect"
    },
    {
        "id": "DNA_FATAL_004",
        "flaw": "Samples in plastic container/bag",
        "impact": "DNA degradation from moisture",
        "action": "COLLECTION REJECTED - must recollect"
    },
    {
        "id": "DNA_FATAL_005",
        "flaw": "Pre-labeled envelopes used",
        "impact": "Sample switching risk",
        "action": "COLLECTION REJECTED - must recollect"
    },
    {
        "id": "DNA_FATAL_006",
        "flaw": "No photo ID verification documented",
        "impact": "Cannot confirm participant identity",
        "action": "COLLECTION REJECTED - must recollect"
    },
    {
        "id": "DNA_FATAL_007",
        "flaw": "No photographs taken",
        "impact": "Cannot verify participant identity",
        "action": "COLLECTION REJECTED - must recollect"
    },
    {
        "id": "DNA_FATAL_008",
        "flaw": "Collector related to participant",
        "impact": "Conflict of interest",
        "action": "COLLECTION REJECTED - must recollect with neutral collector"
    },
    {
        "id": "DNA_FATAL_009",
        "flaw": "Samples left with participant before shipping",
        "impact": "Chain of custody broken",
        "action": "COLLECTION REJECTED - must recollect"
    },
    {
        "id": "DNA_FATAL_010",
        "flaw": "Collection not observed by collector",
        "impact": "Cannot verify correct participant provided sample",
        "action": "COLLECTION REJECTED - must recollect"
    }
]

DNA_CORRECTABLE_FLAWS = [
    {
        "id": "DNA_CORR_001",
        "flaw": "Incomplete paperwork (non-critical fields)",
        "correction": "Lab contacts collector to complete missing info"
    },
    {
        "id": "DNA_CORR_002",
        "flaw": "Missing collection date",
        "correction": "Lab contacts collector to provide"
    },
    {
        "id": "DNA_CORR_003",
        "flaw": "Insufficient sample",
        "correction": "Request recollection - sample too small to test"
    }
]


# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def detect_dna_collection_errors(collection_data: dict) -> dict:
    """
    Analyze DNA collection data for fatal and correctable flaws.
    
    collection_data should include:
    - collector_signed: bool
    - participant_signed: bool
    - seal_intact: bool
    - container_type: str ('paper' or 'plastic')
    - pre_labeled: bool
    - id_verified: bool
    - photographs_taken: bool
    - collector_related: bool
    - samples_in_collector_possession: bool
    - collection_observed: bool
    """
    result = {
        "collection_valid": True,
        "fatal_flaws": [],
        "correctable_flaws": [],
        "warnings": [],
        "recommendation": None
    }
    
    # Check fatal flaws
    if not collection_data.get('collector_signed', False):
        result["fatal_flaws"].append({
            "flaw_id": "DNA_FATAL_001",
            "description": "No collector signature on chain of custody"
        })
    
    if not collection_data.get('participant_signed', False):
        result["fatal_flaws"].append({
            "flaw_id": "DNA_FATAL_002",
            "description": "No participant signatures on consent/COC"
        })
    
    if not collection_data.get('seal_intact', True):
        result["fatal_flaws"].append({
            "flaw_id": "DNA_FATAL_003",
            "description": "Broken tamper-evident seal"
        })
    
    if collection_data.get('container_type', 'paper').lower() == 'plastic':
        result["fatal_flaws"].append({
            "flaw_id": "DNA_FATAL_004",
            "description": "Samples in plastic container - will degrade"
        })
    
    if collection_data.get('pre_labeled', False):
        result["fatal_flaws"].append({
            "flaw_id": "DNA_FATAL_005",
            "description": "Pre-labeled envelopes used"
        })
    
    if not collection_data.get('id_verified', False):
        result["fatal_flaws"].append({
            "flaw_id": "DNA_FATAL_006",
            "description": "No photo ID verification documented"
        })
    
    if not collection_data.get('photographs_taken', False):
        result["fatal_flaws"].append({
            "flaw_id": "DNA_FATAL_007",
            "description": "No photographs taken"
        })
    
    if collection_data.get('collector_related', False):
        result["fatal_flaws"].append({
            "flaw_id": "DNA_FATAL_008",
            "description": "Collector is related to participant"
        })
    
    if not collection_data.get('samples_in_collector_possession', True):
        result["fatal_flaws"].append({
            "flaw_id": "DNA_FATAL_009",
            "description": "Samples left with participant before shipping"
        })
    
    if not collection_data.get('collection_observed', True):
        result["fatal_flaws"].append({
            "flaw_id": "DNA_FATAL_010",
            "description": "Collection not observed by collector"
        })
    
    # Determine validity
    if result["fatal_flaws"]:
        result["collection_valid"] = False
        result["recommendation"] = "RECOLLECT REQUIRED - Fatal flaws detected that void chain of custody"
    else:
        result["recommendation"] = "Collection meets chain of custody requirements"
    
    return result


def check_legal_vs_informational(test_purpose: str) -> dict:
    """
    Determine if test requires legal chain of custody.
    
    test_purpose: 'immigration', 'court', 'child_support', 'custody', 
                  'inheritance', 'personal', 'curiosity'
    """
    legal_purposes = ['immigration', 'court', 'child_support', 'custody', 'inheritance']
    informational_purposes = ['personal', 'curiosity', 'peace_of_mind']
    
    purpose_lower = test_purpose.lower()
    
    if purpose_lower in legal_purposes:
        return {
            "requires_legal": True,
            "chain_of_custody": "REQUIRED",
            "workflow": "DNA_LEGAL_COLLECTION_WORKFLOW",
            "requirements": [
                "Third-party collector required",
                "Photo ID verification required",
                "Photographs of all participants required",
                "Full chain of custody documentation",
                "AABB-accredited laboratory required",
                "Tamper-evident seals required"
            ],
            "note": f"Purpose '{test_purpose}' requires court-admissible results"
        }
    elif purpose_lower in informational_purposes:
        return {
            "requires_legal": False,
            "chain_of_custody": "NOT REQUIRED",
            "workflow": "DNA_INFORMATIONAL_COLLECTION_WORKFLOW",
            "requirements": [
                "Collection can be simpler",
                "ID verification optional",
                "Faster turnaround typical"
            ],
            "warnings": [
                "Results NOT court-admissible",
                "Cannot be used for immigration",
                "Cannot be used for legal proceedings"
            ],
            "note": f"Purpose '{test_purpose}' does not require chain of custody"
        }
    else:
        return {
            "requires_legal": None,
            "recommendation": "CLARIFY PURPOSE - Unable to determine if legal chain of custody required",
            "legal_purposes": legal_purposes,
            "informational_purposes": informational_purposes
        }


def validate_participant_requirements(participants: List[dict]) -> dict:
    """
    Validate all participants meet requirements for DNA testing.
    
    Each participant dict should include:
    - name: str
    - relationship: str ('alleged_father', 'mother', 'child', etc.)
    - age: int (or None if adult)
    - has_guardian: bool (for minors)
    - guardian_name: str (if minor)
    - id_type: str
    - id_verified: bool
    """
    result = {
        "all_requirements_met": True,
        "participant_status": [],
        "issues": [],
        "missing_participants": []
    }
    
    for p in participants:
        status = {
            "name": p.get('name'),
            "relationship": p.get('relationship'),
            "valid": True,
            "issues": []
        }
        
        # Check minor requirements
        age = p.get('age')
        if age is not None and age < 18:
            if not p.get('has_guardian', False):
                status["valid"] = False
                status["issues"].append("Minor without legal guardian present")
            if not p.get('guardian_name'):
                status["valid"] = False
                status["issues"].append("Guardian name not provided for minor")
        
        # Check ID verification
        if not p.get('id_verified', False):
            status["valid"] = False
            status["issues"].append("ID not verified")
        
        if not status["valid"]:
            result["all_requirements_met"] = False
        
        result["participant_status"].append(status)
    
    # Check for standard paternity test participants
    relationships = [p.get('relationship', '').lower() for p in participants]
    
    if 'alleged_father' not in relationships and 'father' not in relationships:
        result["missing_participants"].append("Alleged father not present - consider implications for test accuracy")
    
    return result


def calculate_relationship_probability(test_type: str, participants_available: List[str]) -> dict:
    """
    Estimate expected probability ranges based on test type and participants.
    
    test_type: 'paternity', 'maternity', 'sibling', 'grandparent', 'avuncular'
    participants_available: list of relationships present
    """
    probability_info = {
        "paternity": {
            "with_mother": {
                "exclusion": "100% (if not the father)",
                "inclusion": "99.99%+ typical",
                "minimum_for_legal": "99.0%"
            },
            "without_mother": {
                "exclusion": "100% (if not the father)",
                "inclusion": "99.9%+ typical (slightly lower than with mother)",
                "minimum_for_legal": "99.0%"
            }
        },
        "maternity": {
            "standard": {
                "exclusion": "100%",
                "inclusion": "99.99%+ typical"
            }
        },
        "sibling": {
            "full_sibling": {
                "typical_range": "90-99%",
                "note": "More complex than paternity - depends on shared alleles"
            },
            "half_sibling": {
                "typical_range": "70-90%",
                "note": "Lower certainty due to shared parent only"
            }
        },
        "grandparent": {
            "standard": {
                "typical_range": "90-99%",
                "note": "Best when both grandparents tested"
            }
        },
        "avuncular": {
            "standard": {
                "typical_range": "85-95%",
                "note": "Aunt/uncle testing has inherent limitations"
            }
        }
    }
    
    test_lower = test_type.lower()
    
    if test_lower in probability_info:
        return {
            "test_type": test_type,
            "probability_expectations": probability_info[test_lower],
            "immigration_minimum": "99.5% required for USCIS",
            "court_minimum": "99.0% typically required"
        }
    else:
        return {
            "test_type": test_type,
            "note": "Consult lab for probability expectations for this test type"
        }


# =============================================================================
# API ENDPOINTS
# =============================================================================

@prism_dna.route('/prism/dna/workflow/<workflow_type>', methods=['GET'])
def get_dna_workflow(workflow_type):
    """Get DNA collection workflow by type."""
    workflows = {
        'legal': DNA_LEGAL_COLLECTION_WORKFLOW,
        'informational': DNA_INFORMATIONAL_COLLECTION_WORKFLOW
    }
    
    workflow = workflows.get(workflow_type.lower())
    if workflow:
        return jsonify(workflow)
    return jsonify({"error": f"Unknown workflow type: {workflow_type}"}), 404


@prism_dna.route('/prism/dna/fatal-flaws', methods=['GET'])
def get_dna_fatal_flaws():
    """Get list of all DNA collection fatal flaws."""
    return jsonify({
        "fatal_flaws": DNA_FATAL_FLAWS,
        "correctable_flaws": DNA_CORRECTABLE_FLAWS
    })


@prism_dna.route('/prism/dna/check-collection', methods=['POST'])
def check_dna_collection():
    """Check DNA collection data for fatal and correctable flaws."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No collection data provided"}), 400
    
    result = detect_dna_collection_errors(data)
    return jsonify(result)


@prism_dna.route('/prism/dna/legal-check', methods=['GET'])
def check_if_legal_required():
    """Determine if test purpose requires legal chain of custody."""
    purpose = request.args.get('purpose')
    if not purpose:
        return jsonify({"error": "Must provide 'purpose' parameter"}), 400
    
    result = check_legal_vs_informational(purpose)
    return jsonify(result)


@prism_dna.route('/prism/dna/validate-participants', methods=['POST'])
def validate_participants():
    """Validate participant requirements for DNA testing."""
    data = request.get_json()
    if not data or 'participants' not in data:
        return jsonify({"error": "Must provide 'participants' list"}), 400
    
    result = validate_participant_requirements(data['participants'])
    return jsonify(result)


@prism_dna.route('/prism/dna/probability-info', methods=['GET'])
def get_probability_info():
    """Get expected probability ranges for test type."""
    test_type = request.args.get('test_type', 'paternity')
    participants = request.args.getlist('participants')
    
    result = calculate_relationship_probability(test_type, participants)
    return jsonify(result)


# =============================================================================
# IMMIGRATION DNA SPECIFICS
# =============================================================================

IMMIGRATION_DNA_REQUIREMENTS = {
    "authority": "USCIS (United States Citizenship and Immigration Services)",
    "lab_requirement": "AABB-accredited laboratory ONLY",
    "chain_of_custody": "MANDATORY - no exceptions",
    "probability_minimum": "99.5%+ to establish relationship",
    "results_sent_to": "USCIS or US Embassy/Consulate (NOT to family)",
    "process": [
        "1. Petitioner in US requests DNA testing through USCIS",
        "2. USCIS approves and specifies AABB-accredited lab",
        "3. Petitioner tested at AABB-accredited facility in US",
        "4. Beneficiary tested at US Embassy/Consulate approved facility abroad",
        "5. Lab analyzes both samples",
        "6. Results sent DIRECTLY to USCIS or Embassy"
    ],
    "common_relationships_tested": [
        "Parent-child (paternity/maternity)",
        "Sibling (full or half)",
        "Grandparent-grandchild",
        "Aunt/Uncle-Niece/Nephew"
    ],
    "important_notes": [
        "Family does NOT receive results directly",
        "Results go to government only",
        "Testing abroad coordinated through Embassy",
        "Both tests must be through same lab"
    ]
}

@prism_dna.route('/prism/dna/immigration-requirements', methods=['GET'])
def get_immigration_requirements():
    """Get USCIS immigration DNA testing requirements."""
    return jsonify(IMMIGRATION_DNA_REQUIREMENTS)


if __name__ == '__main__':
    print("PRISM DNA Compliance Module loaded")
    print(f"Legal collection workflow: {len(DNA_LEGAL_COLLECTION_WORKFLOW['steps'])} steps")
    print(f"Fatal flaws defined: {len(DNA_FATAL_FLAWS)}")
