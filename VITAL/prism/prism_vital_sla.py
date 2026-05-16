"""
PRISM VITAL — SLA Tracking Module
Program: VITAL (Verified Integrated Transport And Logistics)
Built to spec: University Health RFP-226-03-068-SVC + RFP-226-04-073-SVC

SLA Rule: 85% Delivery Completion Success Rate
Success = driver arrives at destination within required delivery window
Note: If driver arrives on time but recipient is unavailable = still SUCCESS
"""

from datetime import datetime
from typing import Optional
from prism_vital_orders import ServiceType, VITALOrder


# ─────────────────────────────────────────────
# SLA CONFIGURATION
# ─────────────────────────────────────────────

SLA_THRESHOLDS = {
    ServiceType.STAT:        {"max_minutes": 60,  "alert_at_minutes": 45},
    ServiceType.ROUTINE:     {"max_minutes": 120, "alert_at_minutes": 90},
    ServiceType.SCHEDULED:   {"max_minutes": 120, "alert_at_minutes": 90},
    ServiceType.AFTER_HOURS: {"max_minutes": 120, "alert_at_minutes": 90},
    ServiceType.AD_HOC:      {"max_minutes": 240, "alert_at_minutes": 180},
}

SUCCESS_RATE_TARGET = 0.85  # University Health contract requirement


# ─────────────────────────────────────────────
# DELIVERY EVENT
# ─────────────────────────────────────────────

class DeliveryEvent:
    def __init__(
        self,
        order: VITALOrder,
        request_time: datetime,
        arrival_time: Optional[datetime] = None,
        recipient_available: bool = True,
        cancelled: bool = False,
        cancellation_reason: str = ""
    ):
        self.order_id           = order.order_id
        self.service_type       = order.service_type
        self.service_lane       = order.service_lane
        self.request_time       = request_time
        self.arrival_time       = arrival_time
        self.recipient_available = recipient_available
        self.cancelled          = cancelled
        self.cancellation_reason = cancellation_reason

        self.max_minutes   = SLA_THRESHOLDS[order.service_type]["max_minutes"]
        self.alert_minutes = SLA_THRESHOLDS[order.service_type]["alert_at_minutes"]

    @property
    def elapsed_minutes(self) -> Optional[float]:
        if self.arrival_time is None:
            return None
        return (self.arrival_time - self.request_time).total_seconds() / 60

    @property
    def is_success(self) -> bool:
        """
        SUCCESS criteria:
        - Cancelled = always FAILURE (dry run counts as failed)
        - Driver arrived within window = SUCCESS (even if recipient unavailable)
        - Driver arrived late = FAILURE
        - No arrival recorded = FAILURE (incomplete)
        """
        if self.cancelled:
            return False
        if self.arrival_time is None:
            return False
        return self.elapsed_minutes <= self.max_minutes

    @property
    def alert_triggered(self) -> bool:
        """True if elapsed time has crossed the alert threshold but not yet failed."""
        if self.arrival_time is None:
            return False
        return self.alert_minutes <= self.elapsed_minutes < self.max_minutes

    def to_dict(self) -> dict:
        return {
            "order_id":            self.order_id,
            "service_type":        self.service_type,
            "service_lane":        self.service_lane,
            "request_time":        self.request_time.isoformat(),
            "arrival_time":        self.arrival_time.isoformat() if self.arrival_time else None,
            "elapsed_minutes":     round(self.elapsed_minutes, 1) if self.elapsed_minutes else None,
            "max_minutes":         self.max_minutes,
            "is_success":          self.is_success,
            "recipient_available": self.recipient_available,
            "cancelled":           self.cancelled,
            "cancellation_reason": self.cancellation_reason,
        }


# ─────────────────────────────────────────────
# SLA TRACKER
# ─────────────────────────────────────────────

class VITALSLATracker:
    """
    Tracks delivery events and computes on-time success rate.
    Scope: per period (daily, weekly, monthly, quarterly).
    """

    def __init__(self, label: str = ""):
        self.label  = label
        self.events: list[DeliveryEvent] = []

    def record(self, event: DeliveryEvent):
        self.events.append(event)

    @property
    def total(self) -> int:
        return len(self.events)

    @property
    def successes(self) -> int:
        return sum(1 for e in self.events if e.is_success)

    @property
    def failures(self) -> int:
        return sum(1 for e in self.events if not e.is_success)

    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.successes / self.total

    @property
    def on_target(self) -> bool:
        return self.success_rate >= SUCCESS_RATE_TARGET

    def success_rate_by_type(self) -> dict:
        results = {}
        for stype in ServiceType:
            typed = [e for e in self.events if e.service_type == stype]
            if not typed:
                continue
            rate = sum(1 for e in typed if e.is_success) / len(typed)
            results[stype] = {
                "total":        len(typed),
                "successes":    sum(1 for e in typed if e.is_success),
                "success_rate": round(rate, 4),
                "on_target":    rate >= SUCCESS_RATE_TARGET,
            }
        return results

    def average_elapsed_minutes(self) -> Optional[float]:
        completed = [e.elapsed_minutes for e in self.events if e.elapsed_minutes is not None]
        if not completed:
            return None
        return round(sum(completed) / len(completed), 1)

    def quarterly_report(self) -> dict:
        """Format required by University Health Quality Services Department (4x/year)."""
        return {
            "label":                  self.label,
            "total_deliveries":       self.total,
            "on_time_successes":      self.successes,
            "failures":               self.failures,
            "success_rate":           round(self.success_rate, 4),
            "success_rate_pct":       f"{self.success_rate * 100:.1f}%",
            "target_rate":            f"{SUCCESS_RATE_TARGET * 100:.0f}%",
            "on_target":              self.on_target,
            "avg_elapsed_minutes":    self.average_elapsed_minutes(),
            "breakdown_by_type":      self.success_rate_by_type(),
            "corrective_actions":     [] if self.on_target else ["Review partner SLA performance", "Identify high-delay routes"],
        }

    def print_report(self):
        r = self.quarterly_report()
        status = "✅ ON TARGET" if r["on_target"] else "⚠️  BELOW TARGET"
        print(f"\n{'═'*55}")
        print(f"  VITAL SLA REPORT — {r['label']}")
        print(f"{'═'*55}")
        print(f"  Total deliveries   : {r['total_deliveries']}")
        print(f"  On-time successes  : {r['on_time_successes']}")
        print(f"  Failures           : {r['failures']}")
        print(f"  Success rate       : {r['success_rate_pct']}  (target: {r['target_rate']})")
        print(f"  Status             : {status}")
        print(f"  Avg elapsed        : {r['avg_elapsed_minutes']} min")
        print(f"\n  Breakdown by type:")
        for stype, data in r["breakdown_by_type"].items():
            flag = "✅" if data["on_target"] else "⚠️ "
            print(f"    {flag} {stype:<14} {data['success_rate']*100:.1f}%  ({data['successes']}/{data['total']})")
        if r["corrective_actions"]:
            print(f"\n  Corrective actions:")
            for action in r["corrective_actions"]:
                print(f"    → {action}")
        print(f"{'═'*55}\n")


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    from prism_vital_orders import (
        VITALOrderRegistry, ServiceLane, ServiceType,
        ItemType, Temperature, Location
    )

    registry = VITALOrderRegistry()
    tracker  = VITALSLATracker(label="May 2026 — University Health Pharmacy")

    pharm = Location("UH-PH-01", "UH Main Pharmacy", "4502 Medical Dr",
                     "San Antonio", "TX", "78229", "Coord", "210-555-0100")
    pt    = Location("UH-PT-01", "Patient Discharge", "4502 Medical Dr",
                     "San Antonio", "TX", "78229", "Nursing", "210-555-0200")

    from datetime import timedelta

    scenarios = [
        # (service_type, elapsed_minutes, cancelled)
        (ServiceType.SCHEDULED,   95,  False),   # PASS — under 120
        (ServiceType.SCHEDULED,  115,  False),   # PASS — under 120
        (ServiceType.SCHEDULED,  125,  False),   # FAIL — over 120
        (ServiceType.STAT,        55,  False),   # PASS — under 60
        (ServiceType.STAT,        65,  False),   # FAIL — over 60
        (ServiceType.ROUTINE,    100,  False),   # PASS
        (ServiceType.ROUTINE,    130,  False),   # FAIL
        (ServiceType.AFTER_HOURS, 90,  False),   # PASS
        (ServiceType.SCHEDULED,   80,  False),   # PASS
        (ServiceType.SCHEDULED,  110,  False),   # PASS
    ]

    base_time = datetime(2026, 5, 16, 8, 0, 0)

    for i, (stype, elapsed, cancelled) in enumerate(scenarios):
        order = registry.create(
            service_lane=ServiceLane.PHARMACY,
            service_type=stype,
            item_type=ItemType.MEDICATION,
            temperature=Temperature.AMBIENT,
            pickup=pharm,
            delivery=pt,
            recipient_name=f"Patient {i+1}",
            recipient_phone="210-555-0000",
        )
        request_time = base_time + timedelta(hours=i)
        arrival_time = request_time + timedelta(minutes=elapsed) if not cancelled else None

        event = DeliveryEvent(
            order=order,
            request_time=request_time,
            arrival_time=arrival_time,
            cancelled=cancelled
        )
        tracker.record(event)

    tracker.print_report()
