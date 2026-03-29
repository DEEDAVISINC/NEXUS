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
