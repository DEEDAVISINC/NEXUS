#!/usr/bin/env python3
"""Regression tests — VERTEX medical billing ironclad gates."""

from __future__ import annotations

import os
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from vertex_medical_billing_scrub import (  # noqa: E402
    assert_claim_scrub_pass,
    check_timely_filing,
    scrub_nemt_trip_for_claim,
)
from nemt_billing import (  # noqa: E402
    HAP_CARESOURCE_CONTRACT_RATES,
    HAP_CARESOURCE_MILEAGE_PER_MILE,
    MICHIGAN_MCO_PAYERS,
    MOLINA_LTSS_CONTRACT_RATES,
    MOLINA_LTSS_AMBULATORY_MILEAGE_PER_MILE,
    apply_hap_intake_defaults,
)


class TestPayerDirectoryIronclad(unittest.TestCase):
    def test_molina_payer_id_is_38334(self):
        self.assertEqual(
            MICHIGAN_MCO_PAYERS["Molina Healthcare Michigan"]["payer_id"],
            "38334",
        )

    def test_priority_not_colliding_with_molina(self):
        molina = MICHIGAN_MCO_PAYERS["Molina Healthcare Michigan"]["payer_id"]
        priority = MICHIGAN_MCO_PAYERS["Priority Health"]["payer_id"]
        self.assertNotEqual(molina, priority)

    def test_hap_contract_rates(self):
        self.assertEqual(HAP_CARESOURCE_CONTRACT_RATES["T2002"], 28.0)
        self.assertEqual(HAP_CARESOURCE_CONTRACT_RATES["A0130"], 35.0)
        self.assertEqual(HAP_CARESOURCE_MILEAGE_PER_MILE, 1.85)

    def test_molina_contract_rates(self):
        self.assertEqual(MOLINA_LTSS_CONTRACT_RATES["T2003"], 27.0)
        self.assertEqual(MOLINA_LTSS_CONTRACT_RATES["A0130"], 35.0)
        self.assertEqual(MOLINA_LTSS_AMBULATORY_MILEAGE_PER_MILE, 0.67)


class TestTimelyFiling(unittest.TestCase):
    def test_within_window(self):
        dos = date.today() - timedelta(days=10)
        r = check_timely_filing(payer="Molina Healthcare Michigan", date_of_service=dos.isoformat())
        self.assertTrue(r["ok"])
        self.assertEqual(r["limit_days"], 365)

    def test_expired(self):
        dos = date.today() - timedelta(days=400)
        r = check_timely_filing(payer="Molina Healthcare Michigan", date_of_service=dos.isoformat())
        self.assertFalse(r["ok"])
        self.assertIn("Timely filing expired", r["error"])


class TestClaimScrub(unittest.TestCase):
    def _good_trip(self, **overrides):
        t = {
            "trip_id": "T-TEST-1",
            "payer": "HAP CareSource",
            "member_medicaid_id": "A123456789",
            "pickup_address": "1 Main St, Detroit, MI",
            "dropoff_address": "2 Oak Ave, Detroit, MI",
            "hcpcs_code": "T2002",
            "mileage": 12.5,
            "pickup_time": date.today().isoformat() + "T14:00:00",
            "provider_npi": "1538939111",
            "eligibility_verification_method": "HAP portal check",
            "eligibility_verified_at": date.today().isoformat() + "T12:00:00Z",
            "eligibility_portal_confirmed": True,
        }
        t.update(overrides)
        return t

    def test_good_trip_passes(self):
        r = scrub_nemt_trip_for_claim(self._good_trip())
        self.assertTrue(r["ok"], r["blocking"])

    def test_missing_medicaid_blocks(self):
        r = scrub_nemt_trip_for_claim(self._good_trip(member_medicaid_id=""))
        self.assertFalse(r["ok"])
        self.assertTrue(any("Medicaid" in b for b in r["blocking"]))

    def test_insane_mileage_blocks(self):
        r = scrub_nemt_trip_for_claim(self._good_trip(mileage=9999))
        self.assertFalse(r["ok"])

    def test_timely_filing_blocks_old_dos(self):
        old = (date.today() - timedelta(days=400)).isoformat() + "T10:00:00"
        r = scrub_nemt_trip_for_claim(self._good_trip(pickup_time=old))
        self.assertFalse(r["ok"])

    def test_duplicate_invoiced_trip_blocks(self):
        trip = self._good_trip()
        other = {
            **trip,
            "trip_id": "T-OTHER",
            "invoice_id": "inv123",
        }
        r = scrub_nemt_trip_for_claim(trip, existing_trips={"T-OTHER": other})
        self.assertFalse(r["ok"])
        self.assertTrue(any("Duplicate" in b for b in r["blocking"]))

    def test_assert_raises(self):
        with self.assertRaises(ValueError):
            assert_claim_scrub_pass(self._good_trip(member_medicaid_id=""))


class TestHapIntakeAudit(unittest.TestCase):
    def test_hap_defaults_do_not_auto_confirm_portal(self):
        order = {"payer": "HAP CareSource"}
        apply_hap_intake_defaults(order)
        self.assertTrue(order["eligibility_verified"])
        self.assertFalse(order["eligibility_portal_confirmed"])
        self.assertTrue(order.get("eligibility_verification_method"))
        self.assertTrue(order.get("eligibility_verified_at"))


class TestQcLegacyGate(unittest.TestCase):
    def test_no_record_blocks_by_default(self):
        os.environ.pop("VERTEX_QC_ALLOW_LEGACY", None)
        from nexus_qc_engine import assert_vertex_billing_gate

        with self.assertRaises(ValueError) as ctx:
            assert_vertex_billing_gate(vertex_trip_id="nonexistent-trip-xyz")
        self.assertIn("no qc record", str(ctx.exception).lower())

    def test_legacy_opt_out(self):
        os.environ["VERTEX_QC_ALLOW_LEGACY"] = "1"
        try:
            from nexus_qc_engine import assert_vertex_billing_gate

            r = assert_vertex_billing_gate(vertex_trip_id="nonexistent-trip-xyz")
            self.assertTrue(r.get("skipped"))
        finally:
            os.environ.pop("VERTEX_QC_ALLOW_LEGACY", None)


if __name__ == "__main__":
    unittest.main()
