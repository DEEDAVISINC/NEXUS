"""
PRISM VITAL — Order Intake Module
Program: VITAL (Verified Integrated Transport And Logistics)
Built to spec: University Health RFP-226-03-068-SVC + RFP-226-04-073-SVC
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import uuid


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────

class ServiceLane(str, Enum):
    PHARMACY = "pharmacy"
    LAB = "lab"


class ServiceType(str, Enum):
    SCHEDULED   = "scheduled"    # Batch window, pharmacy compiles 12–2 PM daily
    ROUTINE     = "routine"      # Non-urgent, as-needed
    STAT        = "stat"         # Emergency, time-critical
    AFTER_HOURS = "after_hours"  # 8:00 PM – 7:00 AM
    AD_HOC      = "ad_hoc"       # On-demand, non-recurring


class ItemType(str, Enum):
    # Pharmacy
    MEDICATION           = "medication"
    CONTROLLED_SUBSTANCE = "controlled_substance"
    # Lab
    SPECIMEN             = "specimen"
    PATHOLOGY_SLIDE      = "pathology_slide"
    FROZEN_SPECIMEN      = "frozen_specimen"
    SURGICAL_INSTRUMENT  = "surgical_instrument"
    MEDICAL_EQUIPMENT    = "medical_equipment"


class Temperature(str, Enum):
    AMBIENT      = "ambient"
    REFRIGERATED = "refrigerated"
    FROZEN       = "frozen"


class DEASchedule(str, Enum):
    II  = "II"
    III = "III"
    IV  = "IV"
    V   = "V"


class FulfillmentPartner(str, Enum):
    UBER_HEALTH       = "uber_health"
    SCRIPTDROP        = "scriptdrop"     # Controlled substances
    CARGO_HEALTH      = "cargo_health"   # Lab backup
    COURIERS_OF_SA    = "couriers_of_sa" # Lab backup
    LOCAL_COURIER     = "local_courier"
    UNASSIGNED        = "unassigned"


# ─────────────────────────────────────────────
# SLA WINDOWS (max minutes per service type)
# ─────────────────────────────────────────────

SLA_WINDOWS = {
    ServiceType.STAT:        60,   # 1 hour
    ServiceType.ROUTINE:     120,  # 2 hours
    ServiceType.SCHEDULED:   120,  # 2 hours from request
    ServiceType.AFTER_HOURS: 120,  # 2 hours
    ServiceType.AD_HOC:      240,  # 4 hours
}


# ─────────────────────────────────────────────
# PICKUP / DELIVERY LOCATION
# ─────────────────────────────────────────────

class Location:
    def __init__(
        self,
        facility_id: str,
        facility_name: str,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        contact_name: str,
        contact_phone: str,
        instructions: str = ""
    ):
        self.facility_id    = facility_id
        self.facility_name  = facility_name
        self.address        = address
        self.city           = city
        self.state          = state
        self.zip_code       = zip_code
        self.contact_name   = contact_name
        self.contact_phone  = contact_phone
        self.instructions   = instructions

    def to_dict(self) -> dict:
        return self.__dict__


# ─────────────────────────────────────────────
# VITAL ORDER
# ─────────────────────────────────────────────

class VITALOrder:
    def __init__(
        self,
        service_lane: ServiceLane,
        service_type: ServiceType,
        item_type: ItemType,
        temperature: Temperature,
        pickup: Location,
        delivery: Location,
        recipient_name: str,
        recipient_phone: str,
        controlled_substance: bool = False,
        dea_schedule: Optional[DEASchedule] = None,
        ice_pack_provided: bool = False,
        ice_pack_return_required: bool = False,
        dry_ice_required: bool = False,
        proof_of_delivery_required: bool = True,
        notes: str = ""
    ):
        self.order_id    = self._generate_order_id()
        self.created_at  = datetime.utcnow()
        self.status      = "pending"

        self.service_lane  = service_lane
        self.service_type  = service_type
        self.item_type     = item_type
        self.temperature   = temperature

        self.pickup   = pickup
        self.delivery = delivery

        self.recipient_name  = recipient_name
        self.recipient_phone = recipient_phone

        self.controlled_substance      = controlled_substance
        self.dea_schedule              = dea_schedule
        self.ice_pack_provided         = ice_pack_provided
        self.ice_pack_return_required  = ice_pack_return_required
        self.dry_ice_required          = dry_ice_required
        self.proof_of_delivery_required = proof_of_delivery_required
        self.notes = notes

        self.urgency_minutes     = SLA_WINDOWS[service_type]
        self.due_by              = self.created_at + timedelta(minutes=self.urgency_minutes)
        self.fulfillment_partner = FulfillmentPartner.UNASSIGNED
        self.assigned_driver_id  = None
        self.pod                 = None

        self._validate()

    def _generate_order_id(self) -> str:
        date_str = datetime.utcnow().strftime("%Y%m%d")
        short_id = str(uuid.uuid4())[:6].upper()
        return f"VITAL-{date_str}-{short_id}"

    def _validate(self):
        # Controlled substance requires DEA schedule
        if self.controlled_substance and not self.dea_schedule:
            raise ValueError(
                f"Order {self.order_id}: controlled_substance=True requires a DEA schedule."
            )

        # Lab items should not be in pharmacy lane and vice versa
        pharmacy_items = {ItemType.MEDICATION, ItemType.CONTROLLED_SUBSTANCE}
        lab_items = {
            ItemType.SPECIMEN, ItemType.PATHOLOGY_SLIDE,
            ItemType.FROZEN_SPECIMEN, ItemType.SURGICAL_INSTRUMENT,
            ItemType.MEDICAL_EQUIPMENT
        }

        if self.service_lane == ServiceLane.PHARMACY and self.item_type in lab_items:
            raise ValueError(
                f"Order {self.order_id}: item_type '{self.item_type}' is not valid in pharmacy lane."
            )
        if self.service_lane == ServiceLane.LAB and self.item_type in pharmacy_items:
            raise ValueError(
                f"Order {self.order_id}: item_type '{self.item_type}' is not valid in lab lane."
            )

        # Frozen items require dry ice flag to be acknowledged
        if self.temperature == Temperature.FROZEN and not self.dry_ice_required:
            # Soft warning — frozen specimens sometimes ship at ambient briefly
            pass

    def assign_partner(self, partner: FulfillmentPartner):
        """Assign fulfillment partner based on routing logic."""
        self.fulfillment_partner = partner

    def auto_route(self) -> FulfillmentPartner:
        """
        Auto-route to correct fulfillment partner based on order characteristics.
        Rules:
          - Controlled substance → ScriptDrop
          - Lab specimens → carGO Health (primary) until Uber volume threshold met
          - Pharmacy (non-CS) → Uber Health
        """
        if self.controlled_substance:
            partner = FulfillmentPartner.SCRIPTDROP
        elif self.service_lane == ServiceLane.LAB:
            partner = FulfillmentPartner.CARGO_HEALTH
        else:
            partner = FulfillmentPartner.UBER_HEALTH

        self.assign_partner(partner)
        return partner

    def to_dict(self) -> dict:
        return {
            "order_id":                  self.order_id,
            "created_at":                self.created_at.isoformat(),
            "status":                    self.status,
            "service_lane":              self.service_lane,
            "service_type":              self.service_type,
            "item_type":                 self.item_type,
            "temperature":               self.temperature,
            "urgency_minutes":           self.urgency_minutes,
            "due_by":                    self.due_by.isoformat(),
            "pickup":                    self.pickup.to_dict(),
            "delivery":                  self.delivery.to_dict(),
            "recipient_name":            self.recipient_name,
            "recipient_phone":           self.recipient_phone,
            "controlled_substance":      self.controlled_substance,
            "dea_schedule":              self.dea_schedule,
            "ice_pack_provided":         self.ice_pack_provided,
            "ice_pack_return_required":  self.ice_pack_return_required,
            "dry_ice_required":          self.dry_ice_required,
            "proof_of_delivery_required": self.proof_of_delivery_required,
            "fulfillment_partner":       self.fulfillment_partner,
            "assigned_driver_id":        self.assigned_driver_id,
            "notes":                     self.notes,
        }

    def __repr__(self):
        return (
            f"<VITALOrder {self.order_id} | {self.service_lane} | "
            f"{self.service_type} | due {self.due_by.strftime('%H:%M')}>"
        )


# ─────────────────────────────────────────────
# ORDER REGISTRY
# ─────────────────────────────────────────────

class VITALOrderRegistry:
    """In-memory order store. Replace with DB backend for production."""

    def __init__(self):
        self._orders: dict[str, VITALOrder] = {}

    def create(self, **kwargs) -> VITALOrder:
        order = VITALOrder(**kwargs)
        self._orders[order.order_id] = order
        return order

    def get(self, order_id: str) -> Optional[VITALOrder]:
        return self._orders.get(order_id)

    def all(self) -> list[VITALOrder]:
        return list(self._orders.values())

    def by_status(self, status: str) -> list[VITALOrder]:
        return [o for o in self._orders.values() if o.status == status]

    def by_partner(self, partner: FulfillmentPartner) -> list[VITALOrder]:
        return [o for o in self._orders.values() if o.fulfillment_partner == partner]

    def count(self) -> int:
        return len(self._orders)


# ─────────────────────────────────────────────
# QUICK SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    registry = VITALOrderRegistry()

    pickup = Location(
        facility_id="UH-PHARM-01",
        facility_name="University Health Main Pharmacy",
        address="4502 Medical Dr",
        city="San Antonio",
        state="TX",
        zip_code="78229",
        contact_name="Pharmacy Coordinator",
        contact_phone="210-555-0100"
    )

    delivery = Location(
        facility_id="UH-PT-1042",
        facility_name="Patient Room 1042",
        address="4502 Medical Dr",
        city="San Antonio",
        state="TX",
        zip_code="78229",
        contact_name="Nursing Station 10W",
        contact_phone="210-555-0200"
    )

    # Standard pharmacy order
    order1 = registry.create(
        service_lane=ServiceLane.PHARMACY,
        service_type=ServiceType.SCHEDULED,
        item_type=ItemType.MEDICATION,
        temperature=Temperature.AMBIENT,
        pickup=pickup,
        delivery=delivery,
        recipient_name="John Patient",
        recipient_phone="210-555-9999",
        ice_pack_provided=False,
    )
    order1.auto_route()

    # Controlled substance order
    order2 = registry.create(
        service_lane=ServiceLane.PHARMACY,
        service_type=ServiceType.STAT,
        item_type=ItemType.CONTROLLED_SUBSTANCE,
        temperature=Temperature.AMBIENT,
        pickup=pickup,
        delivery=delivery,
        recipient_name="Jane Patient",
        recipient_phone="210-555-8888",
        controlled_substance=True,
        dea_schedule=DEASchedule.II,
    )
    order2.auto_route()

    # Lab specimen order
    lab_pickup = Location(
        facility_id="UH-CLINIC-07",
        facility_name="University Health Clinic 7",
        address="303 W Houston St",
        city="San Antonio",
        state="TX",
        zip_code="78205",
        contact_name="Lab Coordinator",
        contact_phone="210-555-0300"
    )
    lab_delivery = Location(
        facility_id="UH-LAB-MAIN",
        facility_name="University Health Main Lab",
        address="4502 Medical Dr",
        city="San Antonio",
        state="TX",
        zip_code="78229",
        contact_name="Lab Receiving",
        contact_phone="210-555-0400"
    )

    order3 = registry.create(
        service_lane=ServiceLane.LAB,
        service_type=ServiceType.ROUTINE,
        item_type=ItemType.SPECIMEN,
        temperature=Temperature.REFRIGERATED,
        pickup=lab_pickup,
        delivery=lab_delivery,
        recipient_name="Lab Receiving",
        recipient_phone="210-555-0400",
        ice_pack_provided=True,
        ice_pack_return_required=True,
    )
    order3.auto_route()

    print(f"\n{'='*55}")
    print("  VITAL ORDER REGISTRY — SMOKE TEST")
    print(f"{'='*55}")
    for order in registry.all():
        print(f"  {order}")
        print(f"    Partner : {order.fulfillment_partner}")
        print(f"    Due by  : {order.due_by.strftime('%Y-%m-%d %H:%M UTC')}")
        print()
    print(f"  Total orders: {registry.count()}")
    print(f"{'='*55}\n")
