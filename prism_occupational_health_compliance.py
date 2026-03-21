"""
PRISM Occupational Health Compliance Module
============================================
DOT physicals, respirator evaluations, fit testing,
audiometric testing, and OSHA medical surveillance.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, List, Optional

prism_occ_health = Blueprint('prism_occ_health', __name__)


# =============================================================================
# DOT PHYSICAL EXAMINATION
# =============================================================================

DOT_PHYSICAL_REQUIREMENTS = {
    "authority": "FMCSA (Federal Motor Carrier Safety Administration)",
    "regulation": "49 CFR Part 391",
    "purpose": "Determine if driver is medically qualified to operate CMV",
    "examiner_requirement": "Must be on FMCSA National Registry of Certified Medical Examiners",
    "components": {
        "vision": {
            "acuity": "20/40 or better in each eye (with or without correction)",
            "acuity_both": "20/40 or better both eyes together",
            "field_of_vision": "70 degrees horizontal in each eye",
            "color_vision": "Distinguish traffic signal colors (red, green, amber)"
        },
        "hearing": {
            "whispered_voice": "Perceive whisper at 5 feet or more (best ear)",
            "audiometric": "Average ≤40 dB at 500, 1000, 2000 Hz (best ear)"
        },
        "blood_pressure": {
            "full_2_year": "Below 140/90",
            "1_year_cert": "140-159 systolic OR 90-99 diastolic",
            "conditional": "160-179 systolic OR 100-109 diastolic (one-time only)",
            "disqualified": "≥180 systolic OR ≥110 diastolic"
        },
        "urinalysis": {
            "tests": ["Protein", "Blood", "Sugar"],
            "purpose": "Screen for diabetes, kidney disease"
        },
        "physical_exam": {
            "areas": [
                "General appearance",
                "Eyes", "Ears", "Mouth/throat",
                "Heart/vascular", "Lungs/chest",
                "Abdomen", "Spine/musculoskeletal",
                "Extremities", "Neurological"
            ]
        }
    }
}

DOT_BLOOD_PRESSURE_DECISION = {
    "below_140_90": {
        "systolic_range": "< 140",
        "diastolic_range": "< 90",
        "certification": "Up to 24 months",
        "recert_required": False
    },
    "stage_1": {
        "systolic_range": "140-159",
        "diastolic_range": "90-99",
        "certification": "Up to 12 months",
        "guidance": "Counsel on lifestyle modifications, consider treatment"
    },
    "stage_2": {
        "systolic_range": "160-179",
        "diastolic_range": "100-109",
        "certification": "One-time 12-month certification",
        "requirement": "Must be below 140/90 at next exam for certification",
        "warning": "If still in this range at recert, cannot certify"
    },
    "stage_3": {
        "systolic_range": "≥ 180",
        "diastolic_range": "≥ 110",
        "certification": "DISQUALIFIED",
        "action": "Cannot certify until BP controlled below 140/90"
    }
}

DOT_DISQUALIFYING_CONDITIONS = {
    "absolute_disqualifiers": [
        {
            "condition": "Loss of hand, arm, foot, or leg",
            "exception": "SPE (Skill Performance Evaluation) certificate may allow"
        },
        {
            "condition": "Insulin-treated diabetes mellitus",
            "exception": "ITDM exemption program may allow"
        },
        {
            "condition": "Epilepsy or seizure disorder",
            "exception": "Seizure-free for specific period with exemption"
        },
        {
            "condition": "Current use of Schedule I drugs",
            "exception": "None"
        },
        {
            "condition": "Positive DOT drug test",
            "exception": "Completion of SAP process"
        },
        {
            "condition": "Mental, nervous, organic, or functional condition likely to interfere with safe driving",
            "exception": "Individual assessment"
        }
    ],
    "temporary_disqualifiers": [
        {"condition": "Recent heart attack", "waiting_period": "Per cardiology clearance"},
        {"condition": "Recent stroke", "waiting_period": "Per neurology clearance"},
        {"condition": "Unstable angina", "waiting_period": "Until stable"},
        {"condition": "Uncontrolled hypertension", "waiting_period": "Until controlled"},
        {"condition": "Medication side effects affecting alertness", "waiting_period": "Until resolved"}
    ]
}


def evaluate_blood_pressure(systolic: int, diastolic: int) -> dict:
    """
    Evaluate blood pressure and return certification guidance.
    """
    result = {
        "systolic": systolic,
        "diastolic": diastolic,
        "reading": f"{systolic}/{diastolic}"
    }
    
    if systolic < 140 and diastolic < 90:
        result.update({
            "stage": "Normal",
            "certification_period": "Up to 24 months",
            "action": "Full certification",
            "counseling": None
        })
    elif (140 <= systolic <= 159) or (90 <= diastolic <= 99):
        result.update({
            "stage": "Stage 1 Hypertension",
            "certification_period": "Up to 12 months",
            "action": "Certify with annual recertification",
            "counseling": "Counsel on lifestyle modifications, treatment options"
        })
    elif (160 <= systolic <= 179) or (100 <= diastolic <= 109):
        result.update({
            "stage": "Stage 2 Hypertension",
            "certification_period": "One-time 12 months",
            "action": "May certify ONE TIME at this level",
            "requirement": "Must be below 140/90 at next recertification",
            "warning": "Cannot recertify at this BP level"
        })
    else:  # >= 180 or >= 110
        result.update({
            "stage": "Stage 3 Hypertension",
            "certification_period": "DISQUALIFIED",
            "action": "CANNOT CERTIFY",
            "requirement": "Refer for treatment, recertify when below 140/90"
        })
    
    return result


def evaluate_vision(acuity_od: str, acuity_os: str, acuity_ou: str, 
                   field_od: int, field_os: int, color_vision: bool) -> dict:
    """
    Evaluate vision requirements.
    
    acuity: "20/20", "20/40", etc.
    field: degrees of peripheral vision
    color_vision: can distinguish red/green/amber
    """
    result = {
        "meets_requirements": True,
        "requires_correction": False,
        "deficiencies": []
    }
    
    def parse_acuity(acuity: str) -> int:
        """Convert acuity string to denominator (20/40 -> 40)"""
        if '/' in acuity:
            return int(acuity.split('/')[1])
        return 999  # Fail if can't parse
    
    # Check acuity (20/40 or better required)
    od_denom = parse_acuity(acuity_od)
    os_denom = parse_acuity(acuity_os)
    ou_denom = parse_acuity(acuity_ou)
    
    if od_denom > 40:
        result["deficiencies"].append(f"Right eye acuity {acuity_od} does not meet 20/40 standard")
    if os_denom > 40:
        result["deficiencies"].append(f"Left eye acuity {acuity_os} does not meet 20/40 standard")
    if ou_denom > 40:
        result["deficiencies"].append(f"Both eyes acuity {acuity_ou} does not meet 20/40 standard")
    
    # Check field of vision (70 degrees required each eye)
    if field_od < 70:
        result["deficiencies"].append(f"Right eye field of vision {field_od}° below 70° requirement")
    if field_os < 70:
        result["deficiencies"].append(f"Left eye field of vision {field_os}° below 70° requirement")
    
    # Check color vision
    if not color_vision:
        result["deficiencies"].append("Cannot distinguish traffic signal colors")
    
    if result["deficiencies"]:
        result["meets_requirements"] = False
    
    return result


# =============================================================================
# RESPIRATOR MEDICAL EVALUATION
# =============================================================================

RESPIRATOR_MEDICAL_EVAL = {
    "regulation": "29 CFR 1910.134(e)",
    "when_required": [
        "Before employee is fit tested",
        "Before employee uses respirator on the job"
    ],
    "evaluation_process": {
        "step_1": {
            "action": "OSHA Respirator Medical Evaluation Questionnaire",
            "completed_by": "Employee",
            "confidential": True
        },
        "step_2": {
            "action": "PLHCP Review",
            "who": "Physician or Licensed Health Care Professional",
            "determines": "If additional evaluation needed"
        },
        "step_3": {
            "action": "Follow-up Examination (if needed)",
            "triggers": [
                "Questionnaire indicates potential health concerns",
                "PLHCP determines additional evaluation needed"
            ]
        },
        "step_4": {
            "action": "Written Recommendation",
            "must_include": [
                "Medical ability to use respirator",
                "Any limitations on use",
                "Need for follow-up evaluation"
            ]
        }
    },
    "determination_outcomes": {
        "cleared": "Employee can use respirator",
        "cleared_with_restrictions": "Can use certain respirator types only",
        "not_cleared": "Cannot use respirator - must use alternative protection",
        "requires_additional_evaluation": "Need more testing before determination"
    }
}

RESPIRATOR_QUESTIONNAIRE_TRIGGERS = {
    "require_followup": [
        "History of heart disease or heart attack",
        "History of stroke",
        "Current seizure disorder",
        "Emphysema or chronic bronchitis",
        "Current use of certain medications",
        "Claustrophobia",
        "Previous problems with respirator use",
        "High blood pressure (if uncontrolled)",
        "Diabetes (if uncontrolled)"
    ],
    "may_require_followup": [
        "Shortness of breath with exertion",
        "Chest pain",
        "History of asthma",
        "History of broken ear drums"
    ]
}


# =============================================================================
# RESPIRATOR FIT TESTING
# =============================================================================

FIT_TEST_REQUIREMENTS = {
    "regulation": "29 CFR 1910.134(f)",
    "when_required": [
        "Before first use of tight-fitting respirator",
        "Annually thereafter",
        "When respirator type or size changes",
        "When physical changes may affect fit (weight change >10%, dental work, facial scarring)"
    ],
    "methods": {
        "qualitative": {
            "description": "Pass/fail based on wearer's detection of test agent",
            "agents": [
                {"name": "Saccharin", "detection": "Sweet taste"},
                {"name": "Bitrex", "detection": "Bitter taste"},
                {"name": "Irritant smoke", "detection": "Cough"},
                {"name": "Isoamyl acetate", "detection": "Banana smell"}
            ],
            "suitable_for": "Half-mask respirators"
        },
        "quantitative": {
            "description": "Measured fit factor using instruments",
            "methods": [
                "Ambient aerosol CNC",
                "Controlled negative pressure (CNP)",
                "Generated aerosol"
            ],
            "suitable_for": "All tight-fitting respirators"
        }
    }
}

FIT_TEST_EXERCISES = [
    {"exercise": "Normal breathing", "duration": "1 minute"},
    {"exercise": "Deep breathing", "duration": "1 minute"},
    {"exercise": "Head side to side", "duration": "1 minute"},
    {"exercise": "Head up and down", "duration": "1 minute"},
    {"exercise": "Talking (Rainbow Passage)", "duration": "1 minute"},
    {"exercise": "Grimace (QNFT only)", "duration": "15 seconds"},
    {"exercise": "Bending over", "duration": "1 minute"},
    {"exercise": "Normal breathing", "duration": "1 minute"}
]


def record_fit_test(employee_name: str, respirator_make: str, respirator_model: str,
                   respirator_size: str, test_type: str, result: str,
                   test_date: datetime = None, administrator: str = None) -> dict:
    """
    Create fit test record.
    """
    return {
        "record_type": "respirator_fit_test",
        "employee_name": employee_name,
        "test_date": (test_date or datetime.now()).strftime("%Y-%m-%d"),
        "respirator": {
            "make": respirator_make,
            "model": respirator_model,
            "size": respirator_size
        },
        "test_type": test_type,  # 'QLFT' or 'QNFT'
        "result": result,  # 'PASS' or 'FAIL' (or fit factor for QNFT)
        "administrator": administrator,
        "expiration": (test_date or datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
        "next_test_due": (test_date or datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    }


# =============================================================================
# AUDIOMETRIC TESTING
# =============================================================================

AUDIOMETRIC_TESTING = {
    "regulation": "29 CFR 1910.95",
    "when_required": "Workers exposed to 85 dB TWA or above",
    "baseline_timing": "Within 6 months of first exposure",
    "annual_timing": "Within 12 months of previous test",
    "frequencies_tested": [500, 1000, 2000, 3000, 4000, 6000],
    "baseline_requirements": {
        "quiet_period": "14 hours without workplace noise exposure before test",
        "hearing_protection": "May be used during quiet period"
    }
}

STANDARD_THRESHOLD_SHIFT = {
    "definition": "Average shift of 10 dB or more at 2000, 3000, and 4000 Hz in either ear",
    "calculation": "(Threshold_2000 + Threshold_3000 + Threshold_4000) / 3",
    "comparison": "Current audiogram vs baseline audiogram",
    "age_correction": "May apply age correction per OSHA tables",
    "if_sts_detected": {
        "notify_employee": "Within 21 days",
        "actions": [
            "Fit or refit hearing protection",
            "Train on proper use",
            "Refer for audiological evaluation if needed",
            "Consider additional engineering controls"
        ]
    }
}


def calculate_sts(baseline: dict, current: dict, apply_age_correction: bool = False,
                 age_at_baseline: int = None, age_at_current: int = None) -> dict:
    """
    Calculate if Standard Threshold Shift has occurred.
    
    baseline and current should have keys: '2000', '3000', '4000' with dB values
    """
    result = {
        "sts_detected": False,
        "left_ear": {},
        "right_ear": {}
    }
    
    for ear in ['left', 'right']:
        baseline_avg = (
            baseline.get(ear, {}).get('2000', 0) +
            baseline.get(ear, {}).get('3000', 0) +
            baseline.get(ear, {}).get('4000', 0)
        ) / 3
        
        current_avg = (
            current.get(ear, {}).get('2000', 0) +
            current.get(ear, {}).get('3000', 0) +
            current.get(ear, {}).get('4000', 0)
        ) / 3
        
        shift = current_avg - baseline_avg
        
        result[f"{ear}_ear"] = {
            "baseline_average": round(baseline_avg, 1),
            "current_average": round(current_avg, 1),
            "shift": round(shift, 1),
            "sts": shift >= 10
        }
        
        if shift >= 10:
            result["sts_detected"] = True
    
    if result["sts_detected"]:
        result["required_actions"] = STANDARD_THRESHOLD_SHIFT["if_sts_detected"]["actions"]
        result["notification_deadline"] = "Within 21 days"
    
    return result


# =============================================================================
# PRE-EMPLOYMENT / FITNESS FOR DUTY
# =============================================================================

PRE_EMPLOYMENT_ADA_COMPLIANCE = {
    "before_conditional_offer": {
        "cannot": [
            "Require medical examination",
            "Ask disability-related questions",
            "Inquire about workers' comp history"
        ],
        "can": [
            "Ask about ability to perform job functions",
            "Require demonstration of job skills",
            "Conduct background check"
        ]
    },
    "after_conditional_offer": {
        "can": [
            "Require medical examination",
            "Exam must be same for all entering employees in job category",
            "Make offer conditional on passing exam"
        ],
        "cannot": [
            "Withdraw offer unless condition prevents essential job functions AND no reasonable accommodation exists"
        ]
    }
}

FITNESS_FOR_DUTY_EVAL = {
    "when_used": [
        "After injury or illness",
        "After extended absence",
        "When behavior suggests impairment",
        "Per employer policy"
    ],
    "evaluation_focus": [
        "Ability to perform essential job functions",
        "Any restrictions needed",
        "Accommodations required"
    ],
    "documentation_required": [
        "Cleared to return (yes/no)",
        "Restrictions (if any)",
        "Duration of restrictions",
        "Follow-up date (if needed)",
        "Accommodations recommended"
    ]
}


# =============================================================================
# CERTIFICATE TRACKING
# =============================================================================

def check_dot_physical_validity(cert_date: datetime, cert_period_months: int) -> dict:
    """
    Check if DOT physical is still valid and when it expires.
    """
    expiration = cert_date + timedelta(days=cert_period_months * 30)
    today = datetime.now()
    days_remaining = (expiration - today).days
    
    result = {
        "cert_date": cert_date.strftime("%Y-%m-%d"),
        "cert_period_months": cert_period_months,
        "expiration_date": expiration.strftime("%Y-%m-%d"),
        "days_remaining": days_remaining,
        "status": "valid" if days_remaining > 0 else "expired"
    }
    
    if days_remaining <= 0:
        result["action"] = "RECERTIFICATION REQUIRED - Certificate expired"
    elif days_remaining <= 30:
        result["action"] = "URGENT - Schedule recertification immediately"
        result["warning"] = True
    elif days_remaining <= 60:
        result["action"] = "Schedule recertification soon"
        result["warning"] = True
    else:
        result["action"] = None
    
    return result


# =============================================================================
# API ENDPOINTS
# =============================================================================

@prism_occ_health.route('/prism/occ-health/dot-physical/requirements', methods=['GET'])
def get_dot_requirements():
    """Get DOT physical examination requirements."""
    return jsonify(DOT_PHYSICAL_REQUIREMENTS)


@prism_occ_health.route('/prism/occ-health/dot-physical/bp-evaluate', methods=['GET'])
def evaluate_bp():
    """Evaluate blood pressure for DOT certification."""
    systolic = request.args.get('systolic', type=int)
    diastolic = request.args.get('diastolic', type=int)
    
    if not systolic or not diastolic:
        return jsonify({"error": "Must provide 'systolic' and 'diastolic' parameters"}), 400
    
    result = evaluate_blood_pressure(systolic, diastolic)
    return jsonify(result)


@prism_occ_health.route('/prism/occ-health/dot-physical/vision-evaluate', methods=['POST'])
def evaluate_vision_endpoint():
    """Evaluate vision for DOT certification."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Must provide vision data"}), 400
    
    result = evaluate_vision(
        acuity_od=data.get('acuity_od', '20/20'),
        acuity_os=data.get('acuity_os', '20/20'),
        acuity_ou=data.get('acuity_ou', '20/20'),
        field_od=data.get('field_od', 70),
        field_os=data.get('field_os', 70),
        color_vision=data.get('color_vision', True)
    )
    return jsonify(result)


@prism_occ_health.route('/prism/occ-health/dot-physical/disqualifying', methods=['GET'])
def get_disqualifying():
    """Get DOT disqualifying conditions."""
    return jsonify(DOT_DISQUALIFYING_CONDITIONS)


@prism_occ_health.route('/prism/occ-health/dot-physical/check-validity', methods=['GET'])
def check_validity():
    """Check DOT physical certificate validity."""
    cert_date_str = request.args.get('cert_date')
    cert_period = request.args.get('cert_period_months', 24, type=int)
    
    if not cert_date_str:
        return jsonify({"error": "Must provide 'cert_date' parameter (YYYY-MM-DD)"}), 400
    
    try:
        cert_date = datetime.strptime(cert_date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    result = check_dot_physical_validity(cert_date, cert_period)
    return jsonify(result)


@prism_occ_health.route('/prism/occ-health/respirator/medical-eval', methods=['GET'])
def get_respirator_eval():
    """Get respirator medical evaluation requirements."""
    return jsonify({
        "evaluation": RESPIRATOR_MEDICAL_EVAL,
        "questionnaire_triggers": RESPIRATOR_QUESTIONNAIRE_TRIGGERS
    })


@prism_occ_health.route('/prism/occ-health/respirator/fit-test', methods=['GET'])
def get_fit_test_info():
    """Get fit test requirements and exercises."""
    return jsonify({
        "requirements": FIT_TEST_REQUIREMENTS,
        "exercises": FIT_TEST_EXERCISES
    })


@prism_occ_health.route('/prism/occ-health/respirator/fit-test/record', methods=['POST'])
def create_fit_test_record():
    """Create fit test record."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Must provide fit test data"}), 400
    
    result = record_fit_test(
        employee_name=data.get('employee_name'),
        respirator_make=data.get('respirator_make'),
        respirator_model=data.get('respirator_model'),
        respirator_size=data.get('respirator_size'),
        test_type=data.get('test_type'),
        result=data.get('result'),
        administrator=data.get('administrator')
    )
    return jsonify(result)


@prism_occ_health.route('/prism/occ-health/audiometric', methods=['GET'])
def get_audiometric_info():
    """Get audiometric testing requirements."""
    return jsonify({
        "testing_requirements": AUDIOMETRIC_TESTING,
        "standard_threshold_shift": STANDARD_THRESHOLD_SHIFT
    })


@prism_occ_health.route('/prism/occ-health/audiometric/calculate-sts', methods=['POST'])
def calculate_sts_endpoint():
    """Calculate Standard Threshold Shift."""
    data = request.get_json()
    if not data or 'baseline' not in data or 'current' not in data:
        return jsonify({"error": "Must provide 'baseline' and 'current' audiogram data"}), 400
    
    result = calculate_sts(data['baseline'], data['current'])
    return jsonify(result)


@prism_occ_health.route('/prism/occ-health/pre-employment', methods=['GET'])
def get_pre_employment_info():
    """Get pre-employment physical and ADA compliance info."""
    return jsonify({
        "ada_compliance": PRE_EMPLOYMENT_ADA_COMPLIANCE,
        "fitness_for_duty": FITNESS_FOR_DUTY_EVAL
    })


if __name__ == '__main__':
    print("PRISM Occupational Health Compliance Module loaded")
    print(f"DOT BP stages defined: {len(DOT_BLOOD_PRESSURE_DECISION)}")
    print(f"Fit test exercises: {len(FIT_TEST_EXERCISES)}")
