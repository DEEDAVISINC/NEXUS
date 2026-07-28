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
    CLAIM_STATUS_DENIED,
    CLAIM_STATUS_DRAFT,
    CLAIM_STATUS_INVOICED,
    CLAIM_STATUS_SUBMITTED,
    HAP_CARESOURCE_CONTRACT_RATES,
    HAP_CARESOURCE_MILEAGE_PER_MILE,
    MICHIGAN_MCO_PAYERS,
    MOLINA_LTSS_CONTRACT_RATES,
    MOLINA_LTSS_AMBULATORY_MILEAGE_PER_MILE,
    apply_hap_intake_defaults,
    mark_claim_denied,
    mark_claim_submitted,
)
from vertex_payer_profiles import (  # noqa: E402
    claim_clocks_for_payer,
    clearinghouse_snapshot,
    resolve_profile_key,
    timely_filing_days,
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


class TestPayerProfiles(unittest.TestCase):
    def test_resolve_hap_and_molina(self):
        self.assertEqual(resolve_profile_key("HAP CareSource"), "hap_caresource")
        self.assertEqual(resolve_profile_key("Molina Healthcare Michigan"), "molina_mi_ltss")

    def test_timely_from_json(self):
        self.assertEqual(timely_filing_days("HAP CareSource"), 365)
        self.assertEqual(timely_filing_days("Molina Healthcare Michigan"), 365)

    def test_molina_dispute_appeal(self):
        clocks = claim_clocks_for_payer("Molina Healthcare Michigan")
        self.assertEqual(clocks["dispute_days"], 120)
        self.assertEqual(clocks["appeal_days"], 90)
        self.assertEqual(clocks["clearinghouse"]["payer_ids"].get("electronic"), "38334")

    def test_hap_clearinghouse_ids(self):
        ch = clearinghouse_snapshot("HAP CareSource")
        self.assertEqual(ch["payer_ids"].get("medicaid"), "MIMCDCS1")
        self.assertEqual(ch["payer_ids"].get("mi_coordinated_health"), "MIMCRCS1")

    def test_scrub_attaches_payer_clocks(self):
        from vertex_medical_billing_scrub import scrub_nemt_trip_for_claim

        trip = {
            "trip_id": "T-PROF-1",
            "payer": "Molina Healthcare Michigan",
            "member_medicaid_id": "A123456789",
            "pickup_address": "1 Main St",
            "dropoff_address": "2 Oak",
            "hcpcs_code": "T2003",
            "mileage": 5.0,
            "pickup_time": date.today().isoformat() + "T14:00:00",
            "provider_npi": "1538939111",
        }
        r = scrub_nemt_trip_for_claim(trip)
        self.assertIn("payer_clocks", r)
        self.assertEqual(r["payer_clocks"]["profile_key"], "molina_mi_ltss")
        self.assertEqual(r["timely_filing"]["limit_days"], 365)


class TestClaimStatusMachine(unittest.TestCase):
    def setUp(self):
        import nemt_billing as nb

        self._orig_data = nb._data_file
        self._tmp = ROOT / ".test_nemt_billing_data_tmp.json"
        if self._tmp.exists():
            self._tmp.unlink()
        nb._data_file = lambda: str(self._tmp)  # type: ignore
        self.nb = nb

    def tearDown(self):
        self.nb._data_file = self._orig_data
        if self._tmp.exists():
            self._tmp.unlink()

    def test_log_trip_starts_draft_with_profile(self):
        trip = self.nb.log_trip(
            None,
            member_medicaid_id="A999",
            pickup_time=date.today().isoformat() + "T12:00:00",
            dropoff_time=date.today().isoformat() + "T13:00:00",
            pickup_address="A",
            dropoff_address="B",
            mileage=3.0,
            trip_purpose="medical",
            hcpcs_code="T2002",
            payer="HAP CareSource",
        )
        self.assertEqual(trip["claim_status"], CLAIM_STATUS_DRAFT)
        self.assertEqual(trip.get("payer_profile_key"), "hap_caresource")
        self.assertTrue(
            trip.get("clearinghouse_payer_id") in ("MIMCDCS1", "MIMCRCS1")
            or trip.get("clearinghouse")
        )

    def test_submit_and_deny_sets_clocks(self):
        trip = self.nb.log_trip(
            None,
            member_medicaid_id="A888",
            pickup_time=date.today().isoformat() + "T12:00:00",
            dropoff_time=date.today().isoformat() + "T13:00:00",
            pickup_address="A",
            dropoff_address="B",
            mileage=4.0,
            trip_purpose="medical",
            hcpcs_code="T2003",
            payer="Molina Healthcare Michigan",
        )
        trip_id = trip["trip_id"]
        # Simulate invoiced without Airtable
        state = self.nb._load_state()
        state["trips"][trip_id]["invoice_id"] = "inv-test"
        state["trips"][trip_id]["claim_status"] = CLAIM_STATUS_INVOICED
        self.nb._save_state(state)

        submitted = mark_claim_submitted(trip_id, submission_ref="AVAIL-1")
        self.assertEqual(submitted["claim_status"], CLAIM_STATUS_SUBMITTED)

        denied = mark_claim_denied(
            trip_id,
            denial_reason="CO-16",
            remittance_date=date.today().isoformat(),
        )
        self.assertEqual(denied["claim_status"], CLAIM_STATUS_DENIED)
        self.assertEqual(denied.get("dispute_days"), 120)
        self.assertEqual(denied.get("appeal_days"), 90)
        self.assertTrue(denied.get("dispute_due_date"))
        self.assertTrue(denied.get("appeal_due_date"))


if __name__ == "__main__":
    unittest.main()
