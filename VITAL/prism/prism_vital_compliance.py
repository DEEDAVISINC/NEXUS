"""
PRISM VITAL — Compliance & QC Checklist Module
Program: VITAL (Verified Integrated Transport And Logistics)
Built to spec: University Health RFP-226-03-068-SVC + RFP-226-04-073-SVC
"""

from datetime import datetime
from typing import Optional
from prism_vital_orders import ServiceLane, VITALOrder


# ─────────────────────────────────────────────
# CHECKLIST ITEM
# ─────────────────────────────────────────────

class ChecklistItem:
    def __init__(
        self,
        item_id: str,
        description: str,
        required: bool = True,
        conditional_on: Optional[str] = None  # attribute name on VITALOrder
    ):
        self.item_id        = item_id
        self.description    = description
        self.required       = required
        self.conditional_on = conditional_on
        self.passed         = None  # None = not yet evaluated
        self.notes          = ""
        self.checked_at     = None
        self.checked_by     = None

    def check(self, passed: bool, checked_by: str = "system", notes: str = ""):
        self.passed     = passed
        self.checked_by = checked_by
        self.checked_at = datetime.utcnow()
        self.notes      = notes

    def is_applicable(self, order: VITALOrder) -> bool:
        """Evaluate whether this item applies to the given order."""
        if self.conditional_on is None:
            return True
        return bool(getattr(order, self.conditional_on, False))

    def to_dict(self) -> dict:
        return {
            "item_id":        self.item_id,
            "description":    self.description,
            "required":       self.required,
            "conditional_on": self.conditional_on,
            "passed":         self.passed,
            "notes":          self.notes,
            "checked_at":     self.checked_at.isoformat() if self.checked_at else None,
            "checked_by":     self.checked_by,
        }


# ─────────────────────────────────────────────
# PHARMACY QC CHECKLIST (7 items)
# ─────────────────────────────────────────────

PHARMACY_QC_TEMPLATE = [
    ChecklistItem(
        item_id="rx_label_verified",
        description="Medication label matches order — patient name, medication, dose confirmed",
        required=True
    ),
    ChecklistItem(
        item_id="recipient_verified",
        description="Recipient name and address verified against order",
        required=True
    ),
    ChecklistItem(
        item_id="cold_chain_verified",
        description="Ice packs present and sealed if cold chain required (pharmacy provides)",
        required=True,
        conditional_on="ice_pack_provided"
    ),
    ChecklistItem(
        item_id="controlled_substance_logged",
        description="DEA chain of custody form completed — Schedule, quantity, seal intact",
        required=True,
        conditional_on="controlled_substance"
    ),
    ChecklistItem(
        item_id="signature_captured",
        description="Recipient or authorized representative signature captured",
        required=True
    ),
    ChecklistItem(
        item_id="photo_proof",
        description="Delivery photo captured (package at door or in recipient's hand)",
        required=True
    ),
    ChecklistItem(
        item_id="timestamp_logged",
        description="Delivery timestamp recorded in VITAL dashboard",
        required=True
    ),
]


# ─────────────────────────────────────────────
# LAB QC CHECKLIST (8 items)
# ─────────────────────────────────────────────

LAB_QC_TEMPLATE = [
    ChecklistItem(
        item_id="specimen_integrity",
        description="Specimen container sealed, labeled, and free of leaks or damage",
        required=True
    ),
    ChecklistItem(
        item_id="biohazard_compliance",
        description="Biohazard packaging verified (DOT 49 CFR 173.196 compliant)",
        required=True
    ),
    ChecklistItem(
        item_id="temperature_verified",
        description="Temperature control method verified (ambient / refrigerated / frozen)",
        required=True
    ),
    ChecklistItem(
        item_id="ice_pack_present",
        description="Ice packs present, intact, and not melted — cold chain maintained",
        required=True,
        conditional_on="ice_pack_provided"
    ),
    ChecklistItem(
        item_id="dry_ice_handled",
        description="Dry ice properly handled per IATA P650 — ventilated container, gloves used",
        required=True,
        conditional_on="dry_ice_required"
    ),
    ChecklistItem(
        item_id="chain_of_custody",
        description="Chain of custody form completed at pickup and delivery",
        required=True
    ),
    ChecklistItem(
        item_id="delivery_confirmed",
        description="Lab receiving staff confirmed receipt — name and time recorded",
        required=True
    ),
    ChecklistItem(
        item_id="ice_pack_returned",
        description="Ice packs returned to Pathology department after delivery",
        required=True,
        conditional_on="ice_pack_return_required"
    ),
]


# ─────────────────────────────────────────────
# QC CHECKLIST ENGINE
# ─────────────────────────────────────────────

class VITALQCChecklist:
    def __init__(self, order: VITALOrder):
        self.order      = order
        self.order_id   = order.order_id
        self.lane       = order.service_lane
        self.created_at = datetime.utcnow()
        self.completed  = False
        self.items      = self._build_checklist()

    def _build_checklist(self) -> list[ChecklistItem]:
        """Select and filter checklist items applicable to this order."""
        import copy

        if self.lane == ServiceLane.PHARMACY:
            template = PHARMACY_QC_TEMPLATE
        else:
            template = LAB_QC_TEMPLATE

        applicable = []
        for item in template:
            item_copy = copy.deepcopy(item)
            if item_copy.is_applicable(self.order):
                applicable.append(item_copy)

        return applicable

    def check_item(self, item_id: str, passed: bool, checked_by: str = "driver", notes: str = ""):
        """Mark a specific checklist item as passed or failed."""
        for item in self.items:
            if item.item_id == item_id:
                item.check(passed=passed, checked_by=checked_by, notes=notes)
                return
        raise ValueError(f"Checklist item '{item_id}' not found for order {self.order_id}")

    def check_all_pass(self, checked_by: str = "driver"):
        """Mark all applicable items as passed (for testing / simulation)."""
        for item in self.items:
            item.check(passed=True, checked_by=checked_by)
        self.completed = True

    @property
    def passed(self) -> bool:
        """Checklist passes only if all applicable required items are marked passed."""
        for item in self.items:
            if item.required and item.passed is not True:
                return False
        return True

    @property
    def pending_items(self) -> list[ChecklistItem]:
        return [i for i in self.items if i.passed is None]

    @property
    def failed_items(self) -> list[ChecklistItem]:
        return [i for i in self.items if i.passed is False]

    def summary(self) -> dict:
        return {
            "order_id":      self.order_id,
            "lane":          self.lane,
            "total_items":   len(self.items),
            "passed_count":  sum(1 for i in self.items if i.passed is True),
            "failed_count":  len(self.failed_items),
            "pending_count": len(self.pending_items),
            "checklist_passed": self.passed,
            "completed":     self.completed,
            "items":         [i.to_dict() for i in self.items],
        }

    def print_summary(self):
        s = self.summary()
        status = "✅ PASS" if s["checklist_passed"] else "❌ FAIL"
        print(f"\n{'─'*55}")
        print(f"  QC CHECKLIST — {self.order_id} [{self.lane.upper()}]")
        print(f"  Result  : {status}")
        print(f"  Items   : {s['passed_count']}/{s['total_items']} passed")
        if s["failed_count"]:
            print(f"  FAILED  : {[i['item_id'] for i in s['items'] if i['passed'] is False]}")
        if s["pending_count"]:
            print(f"  PENDING : {[i['item_id'] for i in s['items'] if i['passed'] is None]}")
        print(f"{'─'*55}\n")


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    from prism_vital_orders import (
        VITALOrderRegistry, ServiceLane, ServiceType,
        ItemType, Temperature, DEASchedule, Location
    )

    registry = VITALOrderRegistry()

    pharm_loc = Location("UH-PH-01", "UH Main Pharmacy", "4502 Medical Dr",
                         "San Antonio", "TX", "78229", "Coordinator", "210-555-0100")
    patient_loc = Location("UH-PT-5", "Patient Discharge", "4502 Medical Dr",
                           "San Antonio", "TX", "78229", "Nursing", "210-555-0200")

    # Pharmacy order — controlled substance
    cs_order = registry.create(
        service_lane=ServiceLane.PHARMACY,
        service_type=ServiceType.STAT,
        item_type=ItemType.CONTROLLED_SUBSTANCE,
        temperature=Temperature.AMBIENT,
        pickup=pharm_loc,
        delivery=patient_loc,
        recipient_name="Test Patient",
        recipient_phone="210-555-9999",
        controlled_substance=True,
        dea_schedule=DEASchedule.II,
    )

    qc1 = VITALQCChecklist(cs_order)
    qc1.check_all_pass(checked_by="driver_001")
    qc1.print_summary()

    # Lab order — refrigerated specimen, ice pack return required
    lab_loc = Location("UH-CLINIC-3", "UH Clinic 3", "303 W Houston St",
                       "San Antonio", "TX", "78205", "Lab Coord", "210-555-0300")
    lab_drop = Location("UH-LAB-01", "UH Main Lab", "4502 Medical Dr",
                        "San Antonio", "TX", "78229", "Lab Receiving", "210-555-0400")

    lab_order = registry.create(
        service_lane=ServiceLane.LAB,
        service_type=ServiceType.ROUTINE,
        item_type=ItemType.SPECIMEN,
        temperature=Temperature.REFRIGERATED,
        pickup=lab_loc,
        delivery=lab_drop,
        recipient_name="Lab Receiving",
        recipient_phone="210-555-0400",
        ice_pack_provided=True,
        ice_pack_return_required=True,
    )

    qc2 = VITALQCChecklist(lab_order)
    # Simulate a failed item
    qc2.check_item("specimen_integrity", passed=True, checked_by="driver_002")
    qc2.check_item("biohazard_compliance", passed=True, checked_by="driver_002")
    qc2.check_item("temperature_verified", passed=True, checked_by="driver_002")
    qc2.check_item("ice_pack_present", passed=False, checked_by="driver_002",
                   notes="Ice pack found melted on arrival — cold chain compromised")
    qc2.check_item("chain_of_custody", passed=True, checked_by="driver_002")
    qc2.check_item("delivery_confirmed", passed=True, checked_by="driver_002")
    qc2.check_item("ice_pack_returned", passed=True, checked_by="driver_002")
    qc2.print_summary()
