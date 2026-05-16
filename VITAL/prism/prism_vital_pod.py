"""
PRISM VITAL — Proof of Delivery Module
Program: VITAL (Verified Integrated Transport And Logistics)
Built to spec: University Health RFP-226-03-068-SVC + RFP-226-04-073-SVC
"""

from datetime import datetime
from typing import Optional
from prism_vital_orders import ServiceLane, VITALOrder


# ─────────────────────────────────────────────
# POD EVENT (pickup scan)
# ─────────────────────────────────────────────

class PickupScan:
    def __init__(
        self,
        order_id: str,
        driver_id: str,
        facility_name: str,
        item_count: int,
        temperature_ok: bool,
        signature_or_scan: str,   # driver badge scan, dispatcher code, or "signed"
        timestamp: Optional[datetime] = None,
        notes: str = ""
    ):
        self.order_id          = order_id
        self.driver_id         = driver_id
        self.facility_name     = facility_name
        self.item_count        = item_count
        self.temperature_ok    = temperature_ok
        self.signature_or_scan = signature_or_scan
        self.timestamp         = timestamp or datetime.utcnow()
        self.notes             = notes

    def to_dict(self) -> dict:
        return {
            "event":              "pickup",
            "order_id":           self.order_id,
            "driver_id":          self.driver_id,
            "facility_name":      self.facility_name,
            "item_count":         self.item_count,
            "temperature_ok":     self.temperature_ok,
            "signature_or_scan":  self.signature_or_scan,
            "timestamp":          self.timestamp.isoformat(),
            "notes":              self.notes,
        }


# ─────────────────────────────────────────────
# POD EVENT (delivery confirmation)
# ─────────────────────────────────────────────

class DeliveryConfirmation:
    def __init__(
        self,
        order_id: str,
        driver_id: str,
        recipient_name: str,
        delivery_address: str,
        recipient_signature: str,   # "captured" | "refused" | "unavailable"
        photo_proof_url: str,       # URL or file path to photo
        timestamp: Optional[datetime] = None,
        notes: str = ""
    ):
        self.order_id            = order_id
        self.driver_id           = driver_id
        self.recipient_name      = recipient_name
        self.delivery_address    = delivery_address
        self.recipient_signature = recipient_signature
        self.photo_proof_url     = photo_proof_url
        self.timestamp           = timestamp or datetime.utcnow()
        self.notes               = notes

    @property
    def is_complete(self) -> bool:
        """POD is complete when all required fields are populated."""
        return all([
            self.driver_id,
            self.recipient_name,
            self.delivery_address,
            self.recipient_signature,
            self.photo_proof_url,
            self.timestamp,
        ])

    def to_dict(self) -> dict:
        return {
            "event":               "delivery",
            "order_id":            self.order_id,
            "driver_id":           self.driver_id,
            "recipient_name":      self.recipient_name,
            "delivery_address":    self.delivery_address,
            "recipient_signature": self.recipient_signature,
            "photo_proof_url":     self.photo_proof_url,
            "timestamp":           self.timestamp.isoformat(),
            "complete":            self.is_complete,
            "notes":               self.notes,
        }


# ─────────────────────────────────────────────
# FULL POD RECORD
# ─────────────────────────────────────────────

class VITALProofOfDelivery:
    def __init__(self, order: VITALOrder):
        self.order_id    = order.order_id
        self.service_lane = order.service_lane
        self.created_at  = datetime.utcnow()
        self.pickup_scan: Optional[PickupScan] = None
        self.delivery_confirmation: Optional[DeliveryConfirmation] = None

    def record_pickup(self, **kwargs) -> PickupScan:
        self.pickup_scan = PickupScan(order_id=self.order_id, **kwargs)
        return self.pickup_scan

    def record_delivery(self, **kwargs) -> DeliveryConfirmation:
        self.delivery_confirmation = DeliveryConfirmation(order_id=self.order_id, **kwargs)
        return self.delivery_confirmation

    @property
    def is_complete(self) -> bool:
        return (
            self.pickup_scan is not None
            and self.delivery_confirmation is not None
            and self.delivery_confirmation.is_complete
        )

    @property
    def elapsed_minutes(self) -> Optional[float]:
        if self.pickup_scan and self.delivery_confirmation:
            delta = self.delivery_confirmation.timestamp - self.pickup_scan.timestamp
            return round(delta.total_seconds() / 60, 1)
        return None

    def to_dict(self) -> dict:
        return {
            "order_id":             self.order_id,
            "service_lane":         self.service_lane,
            "created_at":           self.created_at.isoformat(),
            "pod_complete":         self.is_complete,
            "elapsed_minutes":      self.elapsed_minutes,
            "pickup_scan":          self.pickup_scan.to_dict() if self.pickup_scan else None,
            "delivery_confirmation": self.delivery_confirmation.to_dict() if self.delivery_confirmation else None,
        }

    def print_summary(self):
        status = "✅ COMPLETE" if self.is_complete else "⏳ INCOMPLETE"
        print(f"\n{'─'*55}")
        print(f"  POD — {self.order_id}  [{status}]")
        if self.pickup_scan:
            print(f"  Pickup  : {self.pickup_scan.timestamp.strftime('%H:%M')} — {self.pickup_scan.facility_name}")
        if self.delivery_confirmation:
            print(f"  Delivery: {self.delivery_confirmation.timestamp.strftime('%H:%M')} — {self.delivery_confirmation.recipient_name}")
            print(f"  Photo   : {self.delivery_confirmation.photo_proof_url}")
            print(f"  Sig     : {self.delivery_confirmation.recipient_signature}")
        if self.elapsed_minutes:
            print(f"  Elapsed : {self.elapsed_minutes} min")
        print(f"{'─'*55}\n")


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    from datetime import timedelta
    from prism_vital_orders import (
        VITALOrderRegistry, ServiceLane, ServiceType,
        ItemType, Temperature, Location
    )

    registry = VITALOrderRegistry()

    pharm = Location("UH-PH-01", "UH Main Pharmacy", "4502 Medical Dr",
                     "San Antonio", "TX", "78229", "Coord", "210-555-0100")
    pt    = Location("UH-PT-01", "Patient Room 401", "4502 Medical Dr",
                     "San Antonio", "TX", "78229", "Nursing", "210-555-0200")

    order = registry.create(
        service_lane=ServiceLane.PHARMACY,
        service_type=ServiceType.STAT,
        item_type=ItemType.MEDICATION,
        temperature=Temperature.REFRIGERATED,
        pickup=pharm,
        delivery=pt,
        recipient_name="Maria Santos",
        recipient_phone="210-555-7777",
        ice_pack_provided=True,
    )

    pod = VITALProofOfDelivery(order)
    t0  = datetime(2026, 5, 16, 14, 0, 0)

    pod.record_pickup(
        driver_id="DRV-0042",
        facility_name="UH Main Pharmacy",
        item_count=1,
        temperature_ok=True,
        signature_or_scan="PHARM-SCAN-7723",
        timestamp=t0,
    )

    pod.record_delivery(
        driver_id="DRV-0042",
        recipient_name="Maria Santos",
        delivery_address="4502 Medical Dr, Room 401, San Antonio TX 78229",
        recipient_signature="captured",
        photo_proof_url="https://vital.deedavis.biz/pod/VITAL-20260516-DEMO.jpg",
        timestamp=t0 + timedelta(minutes=38),
        notes="Ice pack intact on delivery. Recipient signed in person."
    )

    pod.print_summary()
    print("POD complete:", pod.is_complete)
