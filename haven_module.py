"""
HAVEN Module — Housing, Assistance, Vital Emergency Network
Disaster Response TPA System for Dee Davis Inc.

Integrates with:
- NEXUS Backend (AirtableClient, AnthropicClient)
- GPSS (opportunity tracking, MCO relationships)
- PRISM (credentialing, compliance)
- ProposalBio (MCO pitch generation)
"""

from __future__ import annotations

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

HAVEN_BASE_ID = os.environ.get("HAVEN_BASE_ID", "")
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY", "")

# Table names
TABLES = {
    "transport": "Transport_Partners",
    "housing": "Housing_Partners",
    "medical": "Medical_Partners",
    "mco": "MCO_Contracts",
    "events": "Disaster_Events",
    "cases": "Cases",
    "activations": "Service_Activations",
}

# States served by HAVEN
HAVEN_STATES = ["FL", "TX", "LA", "MI"]

# Partner types
class PartnerType(Enum):
    # Transport
    RIDESHARE = "Rideshare"
    NEMT_FLEET = "NEMT Fleet"
    CHARTER_BUS = "Charter Bus"
    MEDICAL_TRANSPORT = "Medical Transport"
    COURIER = "Courier"
    # Housing
    HOTEL = "Hotel"
    EXTENDED_STAY = "Extended Stay"
    CORPORATE_HOUSING = "Corporate Housing"
    PROPERTY_MANAGER = "Property Manager"
    FEMA_TRAILER = "FEMA Trailer"
    # Medical
    HOME_HEALTH = "Home Health Agency"
    DME = "DME Supplier"
    PHARMACY = "Pharmacy"
    MEDICAL_COURIER = "Medical Courier"
    HOSPICE = "Hospice"

class AgreementStatus(Enum):
    PROSPECT = "Prospect"
    OUTREACH = "Outreach"
    NEGOTIATING = "Negotiating"
    SIGNED = "Signed"
    ACTIVE = "Active"

class EventStatus(Enum):
    PRE_EVENT = "Pre-Event"
    ACTIVE = "Active"
    RECOVERY = "Recovery"
    CLOSED = "Closed"

class CaseStatus(Enum):
    INTAKE = "Intake"
    ACTIVE = "Active"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class ServiceStatus(Enum):
    REQUESTED = "Requested"
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


# ═══════════════════════════════════════════════════════════════════════════════
# HAVEN AIRTABLE CLIENT
# ═══════════════════════════════════════════════════════════════════════════════

class HavenAirtableClient:
    """Airtable client specifically for HAVEN_Network base"""

    def __init__(self):
        if not AIRTABLE_API_KEY:
            raise ValueError("AIRTABLE_API_KEY not set")
        if not HAVEN_BASE_ID:
            raise ValueError("HAVEN_BASE_ID not set — run create_haven_airtable_base.py first")
        
        self.api = Api(AIRTABLE_API_KEY)
        self.base_id = HAVEN_BASE_ID

    def get_table(self, table_key: str):
        """Get table by key (transport, housing, medical, mco, events, cases, activations)"""
        table_name = TABLES.get(table_key, table_key)
        return self.api.table(self.base_id, table_name)

    def create_record(self, table_key: str, fields: Dict) -> Dict:
        """Create a new record"""
        return self.get_table(table_key).create(fields)

    def update_record(self, table_key: str, record_id: str, fields: Dict) -> Dict:
        """Update existing record"""
        return self.get_table(table_key).update(record_id, fields)

    def get_record(self, table_key: str, record_id: str) -> Dict:
        """Get a single record by ID"""
        return self.get_table(table_key).get(record_id)

    def delete_record(self, table_key: str, record_id: str) -> Dict:
        """Delete a record"""
        return self.get_table(table_key).delete(record_id)

    def get_all(self, table_key: str, **kwargs) -> List[Dict]:
        """Get all records from a table"""
        return self.get_table(table_key).all(**kwargs)

    def search(self, table_key: str, formula: str) -> List[Dict]:
        """Search records with Airtable formula"""
        return self.get_table(table_key).all(formula=formula)


# ═══════════════════════════════════════════════════════════════════════════════
# HAVEN NETWORK MANAGER — Partner Network Operations
# ═══════════════════════════════════════════════════════════════════════════════

class HavenNetworkManager:
    """Manage the HAVEN partner network (Transport, Housing, Medical)"""

    def __init__(self):
        self.db = HavenAirtableClient()

    # ─── TRANSPORT PARTNERS ─────────────────────────────────────────────────

    def get_transport_partners(
        self,
        state: Optional[str] = None,
        partner_type: Optional[str] = None,
        status: Optional[str] = None,
        ready_only: bool = False,
    ) -> List[Dict]:
        """Get transport partners with optional filters"""
        filters = []
        if state:
            filters.append(f"FIND('{state}', ARRAYJOIN({{states_served}}, ','))")
        if partner_type:
            filters.append(f"{{partner_type}} = '{partner_type}'")
        if status:
            filters.append(f"{{agreement_status}} = '{status}'")
        if ready_only:
            filters.append("{activation_status} = '🟢 Ready'")

        formula = f"AND({', '.join(filters)})" if filters else ""
        return self.db.search("transport", formula) if formula else self.db.get_all("transport")

    def get_stretcher_providers(self, state: str) -> List[Dict]:
        """Get stretcher-capable transport providers in a state"""
        all_partners = self.get_transport_partners(state=state, partner_type="NEMT Fleet")
        return [p for p in all_partners if "STRETCHER" in (p["fields"].get("notes", "").upper())]

    def get_bariatric_providers(self, state: str) -> List[Dict]:
        """Get bariatric-capable transport providers in a state"""
        all_partners = self.get_transport_partners(state=state, partner_type="NEMT Fleet")
        return [p for p in all_partners if "BARIATRIC" in (p["fields"].get("notes", "").upper())]

    # ─── HOUSING PARTNERS ───────────────────────────────────────────────────

    def get_housing_partners(
        self,
        state: Optional[str] = None,
        partner_type: Optional[str] = None,
        chain_brand: Optional[str] = None,
        fema_approved: Optional[bool] = None,
    ) -> List[Dict]:
        """Get housing partners with optional filters"""
        filters = []
        if state:
            filters.append(f"{{state}} = '{state}'")
        if partner_type:
            filters.append(f"{{partner_type}} = '{partner_type}'")
        if chain_brand:
            filters.append(f"{{chain_brand}} = '{chain_brand}'")
        if fema_approved is not None:
            filters.append(f"{{fema_approved}} = {1 if fema_approved else 0}")

        formula = f"AND({', '.join(filters)})" if filters else ""
        return self.db.search("housing", formula) if formula else self.db.get_all("housing")

    def get_extended_stay_options(self, state: str) -> List[Dict]:
        """Get extended stay properties in a state"""
        return self.get_housing_partners(state=state, partner_type="Extended Stay")

    def get_disaster_housing_specialists(self) -> List[Dict]:
        """Get housing partners with disaster/FEMA experience"""
        all_partners = self.db.get_all("housing")
        keywords = ["DISASTER", "FEMA", "EMERGENCY", "HURRICANE", "RELOCATION"]
        return [
            p for p in all_partners
            if any(kw in (p["fields"].get("notes", "").upper()) for kw in keywords)
        ]

    # ─── MEDICAL PARTNERS ───────────────────────────────────────────────────

    def get_medical_partners(
        self,
        state: Optional[str] = None,
        partner_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict]:
        """Get medical partners with optional filters"""
        filters = []
        if state:
            filters.append(f"FIND('{state}', ARRAYJOIN({{states_served}}, ','))")
        if partner_type:
            filters.append(f"{{partner_type}} = '{partner_type}'")
        if status:
            filters.append(f"{{agreement_status}} = '{status}'")

        formula = f"AND({', '.join(filters)})" if filters else ""
        return self.db.search("medical", formula) if formula else self.db.get_all("medical")

    def get_home_health_agencies(self, state: str) -> List[Dict]:
        """Get home health agencies in a state"""
        return self.get_medical_partners(state=state, partner_type="Home Health Agency")

    def get_dme_suppliers(self, state: str) -> List[Dict]:
        """Get DME suppliers in a state"""
        return self.get_medical_partners(state=state, partner_type="DME Supplier")

    def get_pharmacies(self, state: str) -> List[Dict]:
        """Get pharmacies in a state"""
        return self.get_medical_partners(state=state, partner_type="Pharmacy")

    # ─── NETWORK STATS ──────────────────────────────────────────────────────

    def get_network_stats(self) -> Dict:
        """Get summary statistics for the HAVEN network"""
        transport = self.db.get_all("transport")
        housing = self.db.get_all("housing")
        medical = self.db.get_all("medical")
        mcos = self.db.get_all("mco")

        def count_by_status(records: List[Dict]) -> Dict[str, int]:
            counts = {}
            for r in records:
                status = r["fields"].get("agreement_status", "Unknown")
                counts[status] = counts.get(status, 0) + 1
            return counts

        def count_by_state(records: List[Dict], state_field: str = "states_served") -> Dict[str, int]:
            counts = {s: 0 for s in HAVEN_STATES}
            for r in records:
                states = r["fields"].get(state_field, [])
                if isinstance(states, str):
                    states = [states]
                for s in states:
                    if s in counts:
                        counts[s] += 1
                    elif s == "National":
                        for st in HAVEN_STATES:
                            counts[st] += 1
            return counts

        return {
            "total_partners": len(transport) + len(housing) + len(medical),
            "total_mcos": len(mcos),
            "transport": {
                "total": len(transport),
                "by_status": count_by_status(transport),
                "by_state": count_by_state(transport),
            },
            "housing": {
                "total": len(housing),
                "by_status": count_by_status(housing),
            },
            "medical": {
                "total": len(medical),
                "by_status": count_by_status(medical),
                "by_state": count_by_state(medical),
            },
            "mcos": {
                "total": len(mcos),
                "by_status": count_by_status([{"fields": {"agreement_status": m["fields"].get("contract_status")}} for m in mcos]),
                "by_state": count_by_state([{"fields": {"states_served": [m["fields"].get("state")]}} for m in mcos]),
            },
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }


# ═══════════════════════════════════════════════════════════════════════════════
# HAVEN MCO MANAGER — MCO Relationships
# ═══════════════════════════════════════════════════════════════════════════════

class HavenMCOManager:
    """Manage MCO contracts and relationships for HAVEN"""

    def __init__(self):
        self.db = HavenAirtableClient()

    def get_all_mcos(self) -> List[Dict]:
        """Get all MCO contracts"""
        return self.db.get_all("mco")

    def get_mcos_by_state(self, state: str) -> List[Dict]:
        """Get MCOs in a specific state"""
        return self.db.search("mco", f"{{state}} = '{state}'")

    def get_mcos_by_parent(self, parent_company: str) -> List[Dict]:
        """Get MCOs by parent company (e.g., Centene, Anthem)"""
        return self.db.search("mco", f"FIND('{parent_company}', {{parent_company}})")

    def get_active_mcos(self) -> List[Dict]:
        """Get MCOs with active contracts"""
        return self.db.search("mco", "{contract_status} = 'Active'")

    def get_target_mcos(self) -> List[Dict]:
        """Get MCOs being targeted for outreach"""
        return self.db.search("mco", "{contract_status} = 'Target'")

    def get_credentialing_in_progress(self) -> List[Dict]:
        """Get MCOs with credentialing in progress"""
        return self.db.search("mco", "{credentialing_status} = 'In Progress'")

    def update_mco_contact(self, record_id: str, contact_name: str, contact_email: str, contact_phone: str = "") -> Dict:
        """Update MCO contact information"""
        fields = {
            "contact_name": contact_name,
            "contact_email": contact_email,
            "last_contact": datetime.now().strftime("%Y-%m-%d"),
        }
        if contact_phone:
            fields["contact_phone"] = contact_phone
        return self.db.update_record("mco", record_id, fields)

    def log_outreach(self, record_id: str, notes: str) -> Dict:
        """Log outreach activity to an MCO"""
        record = self.db.get_record("mco", record_id)
        existing_notes = record["fields"].get("notes", "")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_notes = f"{existing_notes}\n\n[{timestamp}] {notes}".strip()
        return self.db.update_record("mco", record_id, {
            "notes": new_notes,
            "last_contact": datetime.now().strftime("%Y-%m-%d"),
        })

    def get_mco_stats(self) -> Dict:
        """Get MCO pipeline statistics"""
        mcos = self.get_all_mcos()
        by_state = {}
        by_parent = {}
        by_status = {}
        total_members = 0

        for mco in mcos:
            fields = mco["fields"]
            state = fields.get("state", "Unknown")
            parent = fields.get("parent_company", "Unknown")
            status = fields.get("contract_status", "Unknown")
            members = fields.get("member_count", 0) or 0

            by_state[state] = by_state.get(state, 0) + 1
            by_parent[parent] = by_parent.get(parent, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1
            total_members += members

        return {
            "total_mcos": len(mcos),
            "total_members": total_members,
            "by_state": by_state,
            "by_parent": by_parent,
            "by_status": by_status,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# HAVEN EVENT MANAGER — Disaster Event Operations
# ═══════════════════════════════════════════════════════════════════════════════

class HavenEventManager:
    """Manage disaster events and network activation"""

    def __init__(self):
        self.db = HavenAirtableClient()
        self.network = HavenNetworkManager()

    def create_event(
        self,
        event_name: str,
        event_type: str,
        states_affected: List[str],
        fema_declaration: Optional[str] = None,
    ) -> Dict:
        """Create a new disaster event"""
        fields = {
            "event_name": event_name,
            "event_type": event_type,
            "states_affected": states_affected,
            "event_status": EventStatus.PRE_EVENT.value,
            "activation_date": datetime.now().strftime("%Y-%m-%d"),
        }
        if fema_declaration:
            fields["fema_declaration"] = fema_declaration
            fields["declaration_date"] = datetime.now().strftime("%Y-%m-%d")

        return self.db.create_record("events", fields)

    def activate_event(self, event_id: str) -> Dict:
        """Activate a disaster event (move from Pre-Event to Active)"""
        return self.db.update_record("events", event_id, {
            "event_status": EventStatus.ACTIVE.value,
            "activation_date": datetime.now().strftime("%Y-%m-%d"),
        })

    def close_event(self, event_id: str) -> Dict:
        """Close a disaster event"""
        return self.db.update_record("events", event_id, {
            "event_status": EventStatus.CLOSED.value,
            "deactivation_date": datetime.now().strftime("%Y-%m-%d"),
        })

    def get_active_events(self) -> List[Dict]:
        """Get all active disaster events"""
        return self.db.search("events", "{event_status} = 'Active'")

    def get_event(self, event_id: str) -> Dict:
        """Get a specific event by ID"""
        return self.db.get_record("events", event_id)

    def get_available_partners_for_event(self, event_id: str) -> Dict:
        """Get all available partners for states affected by an event"""
        event = self.get_event(event_id)
        states = event["fields"].get("states_affected", [])

        transport = []
        housing = []
        medical = []

        for state in states:
            transport.extend(self.network.get_transport_partners(state=state, status="Active"))
            housing.extend(self.network.get_housing_partners(state=state))
            medical.extend(self.network.get_medical_partners(state=state, status="Active"))

        return {
            "event_id": event_id,
            "event_name": event["fields"].get("event_name"),
            "states_affected": states,
            "available_partners": {
                "transport": transport,
                "housing": housing,
                "medical": medical,
            },
            "counts": {
                "transport": len(transport),
                "housing": len(housing),
                "medical": len(medical),
            },
        }


# ═══════════════════════════════════════════════════════════════════════════════
# HAVEN CASE MANAGER — Member Case Operations
# ═══════════════════════════════════════════════════════════════════════════════

class HavenCaseManager:
    """Manage individual member cases during disaster events"""

    def __init__(self):
        self.db = HavenAirtableClient()

    def create_case(
        self,
        event_id: str,
        mco_id: str,
        member_id: str,
        member_name: str,
        member_phone: str,
        home_address: str,
        current_location: str,
        family_size: int = 1,
        special_needs: Optional[List[str]] = None,
        needs_housing: bool = False,
        needs_transport: bool = False,
        needs_medical: bool = False,
        needs_rx: bool = False,
        needs_dme: bool = False,
    ) -> Dict:
        """Create a new case for a displaced member"""
        fields = {
            "event_id": [event_id],  # Link field
            "mco_id": [mco_id],  # Link field
            "member_id": member_id,
            "member_name": member_name,
            "member_phone": member_phone,
            "home_address": home_address,
            "current_location": current_location,
            "family_size": family_size,
            "case_status": CaseStatus.INTAKE.value,
            "intake_date": datetime.now().strftime("%Y-%m-%d"),
            "needs_housing": needs_housing,
            "needs_transport": needs_transport,
            "needs_medical": needs_medical,
            "needs_rx": needs_rx,
            "needs_dme": needs_dme,
        }
        if special_needs:
            fields["special_needs"] = special_needs

        return self.db.create_record("cases", fields)

    def update_case_status(self, case_id: str, status: CaseStatus) -> Dict:
        """Update case status"""
        fields = {"case_status": status.value}
        if status == CaseStatus.RESOLVED:
            fields["resolution_date"] = datetime.now().strftime("%Y-%m-%d")
        return self.db.update_record("cases", case_id, fields)

    def get_case(self, case_id: str) -> Dict:
        """Get a specific case"""
        return self.db.get_record("cases", case_id)

    def get_active_cases(self) -> List[Dict]:
        """Get all active cases"""
        return self.db.search("cases", "{case_status} = 'Active'")

    def get_cases_for_event(self, event_id: str) -> List[Dict]:
        """Get all cases for a specific event"""
        return self.db.search("cases", f"FIND('{event_id}', ARRAYJOIN({{event_id}}, ','))")

    def get_cases_for_mco(self, mco_id: str) -> List[Dict]:
        """Get all cases for a specific MCO"""
        return self.db.search("cases", f"FIND('{mco_id}', ARRAYJOIN({{mco_id}}, ','))")

    def add_case_note(self, case_id: str, note: str) -> Dict:
        """Add a note to a case"""
        case = self.get_case(case_id)
        existing_notes = case["fields"].get("notes", "")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_notes = f"{existing_notes}\n\n[{timestamp}] {note}".strip()
        return self.db.update_record("cases", case_id, {"notes": new_notes})


# ═══════════════════════════════════════════════════════════════════════════════
# HAVEN SERVICE ACTIVATION — Service Dispatch Operations
# ═══════════════════════════════════════════════════════════════════════════════

class HavenServiceManager:
    """Manage service activations (dispatching transport, housing, medical)"""

    def __init__(self):
        self.db = HavenAirtableClient()

    def create_activation(
        self,
        case_id: str,
        service_type: str,
        partner_id: str,
        service_description: str,
        scheduled_date: str,
        scheduled_time: str = "",
        pickup_address: str = "",
        destination_address: str = "",
    ) -> Dict:
        """Create a new service activation"""
        fields = {
            "case_id": [case_id],  # Link field
            "service_type": service_type,
            "partner_id": partner_id,  # Note: This should link to appropriate partner table
            "service_description": service_description,
            "scheduled_date": scheduled_date,
            "service_status": ServiceStatus.REQUESTED.value,
        }
        if scheduled_time:
            fields["scheduled_time"] = scheduled_time
        if pickup_address:
            fields["pickup_address"] = pickup_address
        if destination_address:
            fields["destination_address"] = destination_address

        return self.db.create_record("activations", fields)

    def update_activation_status(self, activation_id: str, status: ServiceStatus) -> Dict:
        """Update activation status"""
        fields = {"service_status": status.value}
        if status == ServiceStatus.COMPLETED:
            fields["completion_date"] = datetime.now().strftime("%Y-%m-%d")
        return self.db.update_record("activations", activation_id, fields)

    def complete_activation(self, activation_id: str, vendor_cost: float, billable_amount: float) -> Dict:
        """Mark activation as complete with costs"""
        return self.db.update_record("activations", activation_id, {
            "service_status": ServiceStatus.COMPLETED.value,
            "completion_date": datetime.now().strftime("%Y-%m-%d"),
            "vendor_cost": vendor_cost,
            "billable_amount": billable_amount,
        })

    def get_activations_for_case(self, case_id: str) -> List[Dict]:
        """Get all activations for a case"""
        return self.db.search("activations", f"FIND('{case_id}', ARRAYJOIN({{case_id}}, ','))")

    def get_pending_activations(self) -> List[Dict]:
        """Get all pending activations"""
        return self.db.search("activations", "OR({service_status} = 'Requested', {service_status} = 'Scheduled')")

    def get_activations_by_date(self, date: str) -> List[Dict]:
        """Get activations scheduled for a specific date"""
        return self.db.search("activations", f"{{scheduled_date}} = '{date}'")


# ═══════════════════════════════════════════════════════════════════════════════
# HAVEN DASHBOARD — Unified System View
# ═══════════════════════════════════════════════════════════════════════════════

class HavenDashboard:
    """Unified dashboard for HAVEN system status"""

    def __init__(self):
        self.network = HavenNetworkManager()
        self.mco = HavenMCOManager()
        self.events = HavenEventManager()
        self.cases = HavenCaseManager()
        self.services = HavenServiceManager()

    def get_system_status(self) -> Dict:
        """Get complete HAVEN system status"""
        network_stats = self.network.get_network_stats()
        mco_stats = self.mco.get_mco_stats()
        active_events = self.events.get_active_events()
        active_cases = self.cases.get_active_cases()
        pending_activations = self.services.get_pending_activations()

        return {
            "system": "HAVEN",
            "status": "OPERATIONAL",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "network": network_stats,
            "mcos": mco_stats,
            "operations": {
                "active_events": len(active_events),
                "active_cases": len(active_cases),
                "pending_activations": len(pending_activations),
                "events": [
                    {
                        "id": e["id"],
                        "name": e["fields"].get("event_name"),
                        "type": e["fields"].get("event_type"),
                        "states": e["fields"].get("states_affected"),
                    }
                    for e in active_events
                ],
            },
        }

    def get_readiness_report(self) -> Dict:
        """Get HAVEN readiness report for hurricane season"""
        network_stats = self.network.get_network_stats()

        # Count active/signed partners
        transport_ready = network_stats["transport"]["by_status"].get("Active", 0) + \
                         network_stats["transport"]["by_status"].get("Signed", 0)
        housing_ready = network_stats["housing"]["by_status"].get("Active", 0) + \
                       network_stats["housing"]["by_status"].get("Signed", 0)
        medical_ready = network_stats["medical"]["by_status"].get("Active", 0) + \
                       network_stats["medical"]["by_status"].get("Signed", 0)

        active_mcos = len(self.mco.get_active_mcos())

        # Determine readiness level
        readiness_score = 0
        if transport_ready >= 3:
            readiness_score += 25
        if housing_ready >= 2:
            readiness_score += 25
        if medical_ready >= 2:
            readiness_score += 25
        if active_mcos >= 1:
            readiness_score += 25

        if readiness_score >= 75:
            readiness_level = "🟢 READY"
        elif readiness_score >= 50:
            readiness_level = "🟡 PARTIAL"
        else:
            readiness_level = "🔴 NOT READY"

        return {
            "readiness_level": readiness_level,
            "readiness_score": readiness_score,
            "transport_partners_ready": transport_ready,
            "housing_partners_ready": housing_ready,
            "medical_partners_ready": medical_ready,
            "active_mco_contracts": active_mcos,
            "total_partners": network_stats["total_partners"],
            "total_mcos": network_stats["total_mcos"],
            "gaps": {
                "transport": transport_ready < 3,
                "housing": housing_ready < 2,
                "medical": medical_ready < 2,
                "mcos": active_mcos < 1,
            },
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION WITH NEXUS SYSTEMS
# ═══════════════════════════════════════════════════════════════════════════════

class HavenNexusIntegration:
    """Integration layer connecting HAVEN to other NEXUS systems"""

    def __init__(self):
        self.dashboard = HavenDashboard()
        self.network = HavenNetworkManager()
        self.mco = HavenMCOManager()

    def get_gpss_opportunities(self) -> List[Dict]:
        """Get HAVEN-relevant opportunities from GPSS"""
        # This would integrate with the main NEXUS GPSS system
        # For now, return MCO targets as "opportunities"
        mcos = self.mco.get_target_mcos()
        return [
            {
                "opportunity_id": m["id"],
                "opportunity_name": f"HAVEN Contract — {m['fields'].get('mco_name')}",
                "client": m["fields"].get("mco_name"),
                "state": m["fields"].get("state"),
                "estimated_value": m["fields"].get("contract_value", 0),
                "status": "Target",
                "source": "HAVEN",
            }
            for m in mcos
        ]

    def sync_with_prism(self, partner_id: str, table_type: str) -> Dict:
        """Sync partner credentialing status with PRISM"""
        # Placeholder for PRISM integration
        # Would update credentialing status, insurance verification, etc.
        return {
            "partner_id": partner_id,
            "table_type": table_type,
            "prism_sync": "pending",
            "message": "PRISM integration pending implementation",
        }

    def generate_proposal_bio_context(self, mco_id: str) -> Dict:
        """Generate ProposalBio context for MCO pitch"""
        mco = self.mco.db.get_record("mco", mco_id)
        stats = self.network.get_network_stats()

        return {
            "client_name": mco["fields"].get("mco_name"),
            "agency": mco["fields"].get("parent_company"),
            "agency_type": "Managed Care Organization",
            "state": mco["fields"].get("state"),
            "service_type": "Disaster Response TPA",
            "network_stats": {
                "transport_partners": stats["transport"]["total"],
                "housing_partners": stats["housing"]["total"],
                "medical_partners": stats["medical"]["total"],
            },
            "key_differentiators": [
                "Pre-staged disaster response network",
                "Active HAP CareSource NEMT contract (Michigan)",
                "EDWOSB certification",
                "Single TPA for housing, transport, medical continuity",
            ],
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_haven_status() -> Dict:
    """Quick status check for HAVEN system"""
    dashboard = HavenDashboard()
    return dashboard.get_system_status()

def get_haven_readiness() -> Dict:
    """Quick readiness check for hurricane season"""
    dashboard = HavenDashboard()
    return dashboard.get_readiness_report()

def get_network_summary() -> Dict:
    """Quick network summary"""
    network = HavenNetworkManager()
    return network.get_network_stats()

def get_mco_pipeline() -> Dict:
    """Quick MCO pipeline summary"""
    mco = HavenMCOManager()
    return mco.get_mco_stats()


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("HAVEN Module — Dee Davis Inc.")
        print("\nUsage:")
        print("  python haven_module.py status     — System status")
        print("  python haven_module.py readiness  — Hurricane readiness report")
        print("  python haven_module.py network    — Network summary")
        print("  python haven_module.py mcos       — MCO pipeline")
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "status":
        result = get_haven_status()
        print(json.dumps(result, indent=2))
    elif command == "readiness":
        result = get_haven_readiness()
        print(json.dumps(result, indent=2))
    elif command == "network":
        result = get_network_summary()
        print(json.dumps(result, indent=2))
    elif command == "mcos":
        result = get_mco_pipeline()
        print(json.dumps(result, indent=2))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
