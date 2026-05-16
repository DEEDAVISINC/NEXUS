"""
PRISM VITAL — Driver & Vehicle Credentialing Module
Program: VITAL (Verified Integrated Transport And Logistics)
Built to spec: University Health RFP-226-03-068-SVC + RFP-226-04-073-SVC
Credentialing platform: Symplr (symplr.com)
"""

from datetime import datetime, date
from typing import Optional
from enum import Enum


# ─────────────────────────────────────────────
# CREDENTIAL STATUS
# ─────────────────────────────────────────────

class CredentialStatus(str, Enum):
    VERIFIED  = "verified"
    PENDING   = "pending"
    EXPIRED   = "expired"
    MISSING   = "missing"
    WAIVED    = "waived"   # Not required for this assignment type


# ─────────────────────────────────────────────
# INDIVIDUAL CREDENTIAL
# ─────────────────────────────────────────────

class Credential:
    def __init__(
        self,
        credential_id: str,
        name: str,
        required: bool = True,
        conditional_on: Optional[str] = None,  # e.g. "controlled_substance", "dry_ice"
        expiry_date: Optional[date] = None,
        issuing_body: str = "",
        document_url: str = "",
    ):
        self.credential_id  = credential_id
        self.name           = name
        self.required       = required
        self.conditional_on = conditional_on
        self.expiry_date    = expiry_date
        self.issuing_body   = issuing_body
        self.document_url   = document_url
        self.status         = CredentialStatus.PENDING
        self.verified_at    = None
        self.verified_by    = None
        self.notes          = ""

    @property
    def is_expired(self) -> bool:
        if self.expiry_date is None:
            return False
        return self.expiry_date < date.today()

    def verify(self, verified_by: str = "system", notes: str = ""):
        if self.is_expired:
            self.status = CredentialStatus.EXPIRED
        else:
            self.status     = CredentialStatus.VERIFIED
            self.verified_at = datetime.utcnow()
            self.verified_by = verified_by
            self.notes       = notes

    def waive(self, reason: str = ""):
        self.status = CredentialStatus.WAIVED
        self.notes  = reason

    def to_dict(self) -> dict:
        return {
            "credential_id":  self.credential_id,
            "name":           self.name,
            "required":       self.required,
            "conditional_on": self.conditional_on,
            "status":         self.status,
            "expiry_date":    self.expiry_date.isoformat() if self.expiry_date else None,
            "is_expired":     self.is_expired,
            "issuing_body":   self.issuing_body,
            "document_url":   self.document_url,
            "verified_at":    self.verified_at.isoformat() if self.verified_at else None,
            "verified_by":    self.verified_by,
            "notes":          self.notes,
        }


# ─────────────────────────────────────────────
# DRIVER CREDENTIAL TEMPLATES
# ─────────────────────────────────────────────

def build_driver_credentials(
    controlled_substance: bool = False,
    dry_ice: bool = False
) -> list[Credential]:
    """
    Build the required credential list for a VITAL driver.
    Conditional credentials are added based on order type.
    """
    credentials = [
        Credential("drv-license",   "Valid Driver's License",           required=True, issuing_body="State DMV"),
        Credential("drv-bg-check",  "Background Check (Criminal + MVR)", required=True, issuing_body="Third-Party Screener"),
        Credential("drv-oig",       "OIG/SAM Exclusion Check",          required=True, issuing_body="HHS OIG / GSA SAM"),
        Credential("drv-hipaa",     "HIPAA Privacy & Security Training", required=True, issuing_body="DDI/Uber Health"),
        Credential("drv-bbp",       "Bloodborne Pathogens Training (OSHA 29 CFR 1910.1030)", required=True, issuing_body="DDI"),
        Credential("drv-badge",     "University Health Contractor Badge (Symplr)", required=True, issuing_body="Symplr / University Health"),
        Credential("drv-insurance", "Valid Auto Insurance",              required=True, issuing_body="Insurer"),
    ]

    if controlled_substance:
        credentials.append(
            Credential(
                "drv-dea-aware",
                "DEA Controlled Substance Awareness Training",
                required=True,
                conditional_on="controlled_substance",
                issuing_body="DDI / ScriptDrop"
            )
        )

    if dry_ice:
        credentials.append(
            Credential(
                "drv-iata-p650",
                "IATA P650 Dry Ice Handling Certification",
                required=True,
                conditional_on="dry_ice",
                issuing_body="IATA"
            )
        )

    return credentials


# ─────────────────────────────────────────────
# VEHICLE CREDENTIAL TEMPLATES
# ─────────────────────────────────────────────

def build_vehicle_credentials() -> list[Credential]:
    return [
        Credential("veh-registration", "Valid Vehicle Registration",          required=True, issuing_body="State DMV"),
        Credential("veh-insurance",     "Commercial Auto Insurance",           required=True, issuing_body="Insurer"),
        Credential("veh-temp-capable",  "Temperature Monitoring Capable (cooler/ice pack)", required=True, issuing_body="DDI Inspection"),
        Credential("veh-inspection",    "Annual Vehicle Safety Inspection",    required=True, issuing_body="State"),
    ]


# ─────────────────────────────────────────────
# DRIVER PROFILE
# ─────────────────────────────────────────────

class VITALDriverProfile:
    def __init__(
        self,
        driver_id: str,
        full_name: str,
        phone: str,
        email: str,
        fulfillment_partner: str,
        controlled_substance_authorized: bool = False,
        dry_ice_authorized: bool = False,
    ):
        self.driver_id                       = driver_id
        self.full_name                       = full_name
        self.phone                           = phone
        self.email                           = email
        self.fulfillment_partner             = fulfillment_partner
        self.controlled_substance_authorized = controlled_substance_authorized
        self.dry_ice_authorized              = dry_ice_authorized
        self.enrolled_at                     = datetime.utcnow()

        self.driver_credentials  = build_driver_credentials(
            controlled_substance=controlled_substance_authorized,
            dry_ice=dry_ice_authorized
        )
        self.vehicle_credentials = build_vehicle_credentials()

    @property
    def all_credentials(self) -> list[Credential]:
        return self.driver_credentials + self.vehicle_credentials

    @property
    def is_cleared(self) -> bool:
        """Driver is cleared to work when all required credentials are verified and not expired."""
        for cred in self.all_credentials:
            if cred.required and cred.status not in (CredentialStatus.VERIFIED, CredentialStatus.WAIVED):
                return False
            if cred.status == CredentialStatus.EXPIRED:
                return False
        return True

    @property
    def blocking_credentials(self) -> list[Credential]:
        """Returns credentials preventing clearance."""
        blocking = []
        for cred in self.all_credentials:
            if cred.required and cred.status not in (CredentialStatus.VERIFIED, CredentialStatus.WAIVED):
                blocking.append(cred)
            elif cred.status == CredentialStatus.EXPIRED:
                blocking.append(cred)
        return blocking

    def verify_all(self, verified_by: str = "compliance_team", expiry: Optional[date] = None):
        """Bulk verify all credentials (for onboarding simulation)."""
        for cred in self.all_credentials:
            cred.expiry_date = expiry
            cred.verify(verified_by=verified_by)

    def symplr_status(self) -> dict:
        """Symplr credentialing portal summary."""
        badge_cred = next((c for c in self.driver_credentials if c.credential_id == "drv-badge"), None)
        return {
            "driver_id":          self.driver_id,
            "full_name":          self.full_name,
            "symplr_badge_status": badge_cred.status if badge_cred else "unknown",
            "badge_expiry":       badge_cred.expiry_date.isoformat() if badge_cred and badge_cred.expiry_date else None,
            "portal":             "https://www.symplr.com",
            "contact":            "GC@symplr.com",
            "note":               "Badge required for clinical area access. Not required for pickup/dropoff only.",
        }

    def print_profile(self):
        cleared = "✅ CLEARED" if self.is_cleared else "❌ NOT CLEARED"
        print(f"\n{'─'*55}")
        print(f"  DRIVER: {self.full_name} ({self.driver_id})  [{cleared}]")
        print(f"  Partner: {self.fulfillment_partner}")
        print(f"  CS Auth: {'Yes' if self.controlled_substance_authorized else 'No'}")
        print(f"\n  Credentials ({len(self.all_credentials)} total):")
        for cred in self.all_credentials:
            icon = {"verified": "✅", "pending": "⏳", "expired": "🔴", "missing": "❌", "waived": "➖"}.get(cred.status, "?")
            exp  = f" (exp: {cred.expiry_date})" if cred.expiry_date else ""
            print(f"    {icon} {cred.name}{exp}")
        if self.blocking_credentials:
            print(f"\n  ⚠️  BLOCKING: {[c.credential_id for c in self.blocking_credentials]}")
        print(f"{'─'*55}\n")

    def to_dict(self) -> dict:
        return {
            "driver_id":                     self.driver_id,
            "full_name":                     self.full_name,
            "phone":                         self.phone,
            "email":                         self.email,
            "fulfillment_partner":           self.fulfillment_partner,
            "controlled_substance_authorized": self.controlled_substance_authorized,
            "dry_ice_authorized":            self.dry_ice_authorized,
            "is_cleared":                    self.is_cleared,
            "enrolled_at":                   self.enrolled_at.isoformat(),
            "symplr":                        self.symplr_status(),
            "driver_credentials":            [c.to_dict() for c in self.driver_credentials],
            "vehicle_credentials":           [c.to_dict() for c in self.vehicle_credentials],
        }


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    from datetime import date, timedelta

    # Standard Uber Health pharmacy driver
    driver1 = VITALDriverProfile(
        driver_id="DRV-0042",
        full_name="Carlos Reyes",
        phone="210-555-4200",
        email="creyes@fulfillment.com",
        fulfillment_partner="uber_health",
    )
    driver1.print_profile()

    # Verify all credentials
    driver1.verify_all(
        verified_by="compliance_team",
        expiry=date.today() + timedelta(days=365)
    )
    driver1.print_profile()

    # CS-authorized ScriptDrop driver
    driver2 = VITALDriverProfile(
        driver_id="DRV-0099",
        full_name="Ana Gutierrez",
        phone="210-555-9900",
        email="agutierrez@scriptdrop.com",
        fulfillment_partner="scriptdrop",
        controlled_substance_authorized=True,
    )
    driver2.verify_all(
        verified_by="compliance_team",
        expiry=date.today() + timedelta(days=365)
    )
    driver2.print_profile()
    print("Symplr status:", driver2.symplr_status())
