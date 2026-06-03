"""
DDI Company Information — Single Source of Truth

Every generator, validator, and template in the NEXUS ecosystem imports from
here. If something changes, change it HERE and everything downstream updates.

DO NOT hardcode company info anywhere else. Import from this module.
"""

# ─────────────────────────────────────────────────────────────────────────────
# CONTACT
# ─────────────────────────────────────────────────────────────────────────────
COMPANY_NAME = "Dee Davis Inc."
DBA = "The Professionals' Professionals"
ADDRESS_STREET = "755 W. Big Beaver Rd., Suite 2020"
ADDRESS_CITY = "Troy"
ADDRESS_STATE = "Michigan"
ADDRESS_ZIP = "48084"
ADDRESS_FULL = f"{ADDRESS_STREET}, {ADDRESS_CITY}, {ADDRESS_STATE} {ADDRESS_ZIP}"

PHONE_PRIMARY = "248.376.4550"
PHONE_ALT = "734.413.8310"
EMAIL = "info@deedavis.biz"
WEBSITE = "deedavis.biz"

OWNER_NAME = "Dee Davis"
# Formal legal name — signatures, government documents, buyer-facing email intro
OWNER_FULL_NAME = "Dieasha D. Davis"
OWNER_TITLE = "President & CEO"

# ─────────────────────────────────────────────────────────────────────────────
# HEALTHCARE PROVIDER IDS (MDHHS / CHAMPS / billing)
# ─────────────────────────────────────────────────────────────────────────────
NPI = "1538939111"
CHAMPS_PROVIDER_ID = "6309049"

# ─────────────────────────────────────────────────────────────────────────────
# FEDERAL CREDENTIALS
# ─────────────────────────────────────────────────────────────────────────────
EIN = "84-4114181"
CAGE_CODE = "8UMX3"
UEI = "HJB4KNYJVGZ1"
DUNS = "002636755"
MC_NUMBER = "1647572"
US_DOT = "4250594"
SAM_STATUS = "Active"

# ─────────────────────────────────────────────────────────────────────────────
# HEALTHCARE LOGISTICS / MEDICAL COURIER — TERMINOLOGY (both in system)
# ─────────────────────────────────────────────────────────────────────────────
# Preferred buyer-facing umbrella: "healthcare logistics" (coordination, compliance,
# chain of custody, transport). "Medical courier" stays as RFP/solicitation keyword —
# mirror buyer language when the RFx uses that exact phrase. Miners and keyword lists
# include both.
HEALTHCARE_LOGISTICS_PRIMARY_LABEL = "healthcare logistics"
MEDICAL_COURIER_RFP_KEYWORD = "medical courier"
HEALTHCARE_LOGISTICS_SEARCH_KEYWORDS = [
    "healthcare logistics",
    "medical courier",
    "specimen transport",
    "laboratory courier",
    "chain of custody",
    "medical delivery",
    "healthcare transportation logistics",
]

# ─────────────────────────────────────────────────────────────────────────────
# NEMT / PATIENT TRANSPORT — TERMINOLOGY (both in system)
# ─────────────────────────────────────────────────────────────────────────────
# Preferred spell-out: "non-emergency medical transportation"; shorthand "NEMT" is
# standard in Medicaid/government. "Patient transport," "medical transport,"
# "paratransit," "wheelchair/stretcher" — mirror solicitation / MCO language.
NEMT_PRIMARY_LABEL = "non-emergency medical transportation"
NEMT_SHORT = "NEMT"
NEMT_SEARCH_KEYWORDS = [
    "NEMT",
    "non-emergency medical transportation",
    "non-emergency medical transport",
    "patient transport",
    "patient transportation",
    "medical transport",
    "medical transportation",
    "paratransit",
    "wheelchair transport",
    "stretcher transport",
    "ambulatory transport",
    "special needs transportation",
    "Medicaid transportation",
    "Medicaid transport",
]

# ─────────────────────────────────────────────────────────────────────────────
# BIOMETRICS / FINGERPRINTING — TERMINOLOGY (both in system)
# ─────────────────────────────────────────────────────────────────────────────
# Preferred umbrella: "biometrics" for buyer-facing positioning. "Fingerprinting,"
# "livescan," "electronic fingerprinting," "FD-258," "criminal history" — mirror RFx.
# Submission channel is per contract; do not claim DCSA SWFT unless master file says so.
BIOMETRICS_PRIMARY_LABEL = "biometrics"
FINGERPRINTING_RFX_KEYWORD = "fingerprinting"
BIOMETRICS_FINGERPRINTING_SEARCH_KEYWORDS = [
    "biometrics",
    "biometric",
    "biometric fingerprinting",
    "biometric identity",
    "fingerprinting",
    "fingerprint",
    "fingerprinting services",
    "livescan",
    "live scan",
    "electronic fingerprinting",
    "digital fingerprinting",
    "ink fingerprint",
    "rolled fingerprint",
    "FD-258",
    "ten-print",
    "criminal history fingerprinting",
    "applicant fingerprint",
    "fingerprint capture",
    "identity verification",
]

# ─────────────────────────────────────────────────────────────────────────────
# DRUG & ALCOHOL TESTING — TERMINOLOGY (both in system)
# ─────────────────────────────────────────────────────────────────────────────
# Preferred umbrella: "drug and alcohol testing" / occupational testing. RFx may say
# "workplace," "DOT," "SAMHSA," "C/TPA," "consortium," "random," "pre-employment" — mirror buyer.
DRUG_ALCOHOL_TESTING_PRIMARY_LABEL = "drug and alcohol testing"
DRUG_TESTING_RFX_KEYWORD = "drug testing"
DRUG_ALCOHOL_TESTING_SEARCH_KEYWORDS = [
    "drug and alcohol testing",
    "drug testing",
    "alcohol testing",
    "workplace drug testing",
    "occupational drug testing",
    "DOT drug testing",
    "DOT drug and alcohol testing",
    "49 CFR Part 40",
    "Part 40",
    "SAMHSA",
    "C/TPA",
    "consortium",
    "third party administrator",
    "TPA",
    "random drug testing",
    "pre-employment drug testing",
    "post-accident testing",
    "reasonable suspicion",
    "return-to-duty",
    "follow-up testing",
    "urine drug screen",
    "oral fluid drug testing",
    "hair drug testing",
    "breath alcohol",
    "BAT",
    "substance abuse screening",
    "toxicology",
    "specimen collection",
]

# ─────────────────────────────────────────────────────────────────────────────
# NOTARY, AUTHENTICATION, WITNESSING & CREDENTIALING — TERMINOLOGY (both in system)
# ─────────────────────────────────────────────────────────────────────────────
# Notary / legal doc lane: lead with "notarial services"; mirror "notary," "RON,"
# "signing agent," "apostille," "acknowledgment/jurat" per RFx. Witnessing rules
# vary by state — mirror solicitation language.
NOTARY_PRIMARY_LABEL = "notarial services"
NOTARY_RFX_KEYWORD = "notary"
NOTARY_AUTHENTICATION_WITNESSING_SEARCH_KEYWORDS = [
    "notary",
    "notary public",
    "notarization",
    "notarial",
    "notarial act",
    "mobile notary",
    "RON",
    "remote online notarization",
    "online notary",
    "loan signing",
    "signing agent",
    "document authentication",
    "authentication of documents",
    "acknowledgment",
    "jurat",
    "apostille",
    "apostille coordination",
    "witness",
    "witnessing",
    "subscribing witness",
    "witness signature",
    "copy certification",
]

# Credentialing: workforce / healthcare / provider enrollment — umbrella "credentialing";
# mirror "primary source verification," "enrollment," "privileging" when buyer uses them.
CREDENTIALING_PRIMARY_LABEL = "credentialing"
CREDENTIALING_SEARCH_KEYWORDS = [
    "credentialing",
    "healthcare credentialing",
    "workforce credentialing",
    "provider credentialing",
    "enrollment and credentialing",
    "credentialing verification",
    "primary source verification",
    "PSV",
    "privileging",
    "licensure verification",
    "license verification",
    "badge",
    "badging",
    "identity credentialing",
    "employment credentialing",
]

# ─────────────────────────────────────────────────────────────────────────────
# COMMONWEALTH OF PENNSYLVANIA — PROCUREMENT (DGS / eMarketplace)
# Registered PA Supplier / SRM vendor — use on PA bids and invoices as required.
# ─────────────────────────────────────────────────────────────────────────────
PA_VENDOR_NUMBER = "0000569615"
PA_SUPPLIER_USER_ID = "DEEDAVISINC"
PA_SUPPLIER_PORTAL_URL = "https://www.pasupplierportal.state.pa.us/irj/portal"
PA_SUPPLIER_PORTAL_PHONE = "1-877-435-7363"
PA_SUPPLIER_PORTAL_EMAIL = "ra-pscsrmportal@pa.gov"
PA_SRM_EMAIL = "SRMRFC@pa.gov"
PA_DGS_EALERTS_URL = "http://www.dgs.internet.state.pa.us/EAlerts_V2/Login.aspx"
PA_JAGGAER_SUPPORT_PHONE = "1-800-233-1121"

# ─────────────────────────────────────────────────────────────────────────────
# CAUSE WE CARE — affiliated 501(c)(3) (Dieasha D. Davis, Executive Director)
# Source of truth: COMPANY_INFO_MASTER.md — use CWC footers/grant apps as required.
# ─────────────────────────────────────────────────────────────────────────────
CWC_LEGAL_NAME = "Cause We Care"
CWC_EIN = "92-3602670"
CWC_UEI = "VEJMFMVV6PQ1"  # UEI assigned — full SAM.gov registration NOT complete yet
CWC_DBA = ""  # None on SAM
CWC_ADDRESS_STREET = "755 W. Big Beaver Rd., Suite 2020"
CWC_ADDRESS_CITY_STATE_ZIP = "Troy, Michigan 48084-4925"
CWC_ADDRESS_FULL = f"{CWC_ADDRESS_STREET}, {CWC_ADDRESS_CITY_STATE_ZIP}"
CWC_EMAIL_EXECUTIVE = "ddavis@cwecare.org"  # ED / primary — Dieasha D. Davis
CWC_EMAIL_GENERAL = "info@cwecare.org"  # General org inbox
CWC_PHONE = "248.376.4550"  # Same main line as DDI per master

# ─────────────────────────────────────────────────────────────────────────────
# CERTIFICATIONS
# ─────────────────────────────────────────────────────────────────────────────
CERTIFICATIONS = [
    "EDWOSB",
    "WOSB",
    "WBENC WBE",
    "MBE",
    "SBE",
    "E-Verify",
    "SWFT Authorized",
]

CERT_LINE = "EDWOSB | WOSB | WBENC | MBE | SBE | SWFT Authorized"

# ─────────────────────────────────────────────────────────────────────────────
# SIGNATURE BLOCK (for emails)
# ─────────────────────────────────────────────────────────────────────────────
SIGNATURE_BLOCK = f"""{OWNER_FULL_NAME}
{OWNER_TITLE}
{COMPANY_NAME}
{ADDRESS_FULL}
{PHONE_PRIMARY} | {EMAIL}
{CERT_LINE}"""

# Full email footer: confidentiality + org line (paste below signature when required)
EMAIL_FOOTER_CONFIDENTIAL_DDI = """CONFIDENTIALITY NOTICE: This message and any attachments are intended solely for the use of the individual or entity to which it is addressed and may contain confidential or proprietary information. If you have received this communication in error, please notify the sender immediately by return email and permanently delete this message and any attachments. Any unauthorized review, use, disclosure, or distribution is prohibited.

Dee Davis Inc. | 755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084 | info@deedavis.biz | 248.376.4550"""

EMAIL_FOOTER_CONFIDENTIAL_CWC = """CONFIDENTIALITY NOTICE: This message and any attachments are intended solely for the use of the individual or entity to which it is addressed and may contain confidential or proprietary information. If you have received this communication in error, please notify the sender immediately by return email and permanently delete this message and any attachments. Any unauthorized review, use, disclosure, or distribution is prohibited.

Cause We Care | 755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084 | info@cwecare.org | 248.376.4550 | EIN: 92-3602670 | 501(c)(3) Nonprofit"""

# ─────────────────────────────────────────────────────────────────────────────
# BANNED VALUES — known-wrong info from old templates
# ─────────────────────────────────────────────────────────────────────────────
BANNED_PHONES = [
    "248.247.5020",
    "248-247-5020",
    "(248) 247-5020",
    "2482475020",
]

BANNED_ZIPS = ["48083"]

BANNED_EMAILS = [
    "bids@deedavisinc.com",
    "bids@deedavis.com",
]

BANNED_EINS = ["47-3015027"]

BANNED_WEBSITES = [
    "deedavisinc.com",
]
