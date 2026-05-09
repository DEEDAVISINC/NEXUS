"""
HAVEN Disaster Watch System
Real-time monitoring of FEMA declarations and NWS alerts for FL, TX, LA, MI.

Data Sources (all free, no API key):
  - FEMA Disaster Declarations API: /v2/DisasterDeclarationsSummaries
  - NWS Alerts API: api.weather.gov/alerts/active
  - NWS Hurricane/Tropical API: api.weather.gov (tropical storms)

This module provides:
  1. Active FEMA disaster declarations in HAVEN target states
  2. Active NWS weather alerts (hurricanes, floods, tornadoes, severe storms)
  3. Severity classification and threat assessment
  4. Auto-event creation recommendations for HAVEN
"""

import json
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

HAVEN_STATES = ['FL', 'TX', 'LA', 'MI']

FEMA_STATE_MAP = {
    'FL': 'Florida', 'TX': 'Texas', 'LA': 'Louisiana', 'MI': 'Michigan',
}

# NWS uses state FIPS / UGC zone codes, but we filter by state in the response
NWS_AREA_CODES = {
    'FL': 'FL', 'TX': 'TX', 'LA': 'LA', 'MI': 'MI',
}

FEMA_API_BASE = 'https://www.fema.gov/api/open/v2'
NWS_API_BASE = 'https://api.weather.gov'

NWS_HEADERS = {
    'User-Agent': '(Dee Davis Inc HAVEN System, info@deedavis.biz)',
    'Accept': 'application/geo+json',
}

# Threat level mapping for NWS events
NWS_SEVERITY_MAP = {
    'Extreme': 'Major Disaster',
    'Severe': 'Emergency',
    'Moderate': 'Warning',
    'Minor': 'Watch',
    'Unknown': 'Watch',
}

# Hurricane-specific event types
HURRICANE_EVENTS = [
    'Hurricane Warning', 'Hurricane Watch', 'Hurricane Force Wind Warning',
    'Tropical Storm Warning', 'Tropical Storm Watch', 'Storm Surge Warning',
    'Storm Surge Watch', 'Extreme Wind Warning', 'Hurricane Local Statement',
]

FLOOD_EVENTS = [
    'Flash Flood Warning', 'Flash Flood Watch', 'Flood Warning', 'Flood Watch',
    'Flood Advisory', 'Coastal Flood Warning', 'Coastal Flood Watch',
    'River Flood Warning', 'Lakeshore Flood Warning',
]

TORNADO_EVENTS = [
    'Tornado Warning', 'Tornado Watch', 'Tornado Emergency',
]

SEVERE_STORM_EVENTS = [
    'Severe Thunderstorm Warning', 'Severe Thunderstorm Watch',
    'Severe Weather Statement', 'Special Weather Statement',
]

WINTER_EVENTS = [
    'Blizzard Warning', 'Winter Storm Warning', 'Winter Storm Watch',
    'Ice Storm Warning', 'Winter Weather Advisory',
]

FIRE_EVENTS = [
    'Red Flag Warning', 'Fire Weather Watch', 'Fire Warning',
]

def _event_category(event_name: str) -> str:
    if any(h in event_name for h in HURRICANE_EVENTS):
        return 'Hurricane'
    if any(f in event_name for f in FLOOD_EVENTS):
        return 'Flood'
    if any(t in event_name for t in TORNADO_EVENTS):
        return 'Tornado'
    if any(w in event_name for w in WINTER_EVENTS):
        return 'Winter Storm'
    if any(f in event_name for f in FIRE_EVENTS):
        return 'Wildfire'
    if any(s in event_name for s in SEVERE_STORM_EVENTS):
        return 'Severe Storm'
    return 'Other'


class DisasterWatch:
    """
    Monitors FEMA and NWS for active disasters in HAVEN target states.
    Caches results for 15 minutes to avoid hammering the APIs.
    """

    def __init__(self, cache_ttl_seconds: int = 900):
        self.cache_ttl = cache_ttl_seconds
        self._fema_cache: dict[str, Any] = {}
        self._fema_cache_time: float = 0
        self._nws_cache: dict[str, Any] = {}
        self._nws_cache_time: float = 0

    # ─── FEMA DISASTER DECLARATIONS ──────────────────────────────────

    def get_fema_disasters(self, days_back: int = 365) -> list[dict]:
        """
        Fetch recent FEMA disaster declarations for HAVEN states.
        Returns disasters declared within `days_back` days.
        """
        if self._fema_cache and (time.time() - self._fema_cache_time) < self.cache_ttl:
            return self._fema_cache.get('disasters', [])

        cutoff = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime('%Y-%m-%dT00:00:00.000z')
        disasters = []

        for state_abbr, state_name in FEMA_STATE_MAP.items():
            try:
                url = (
                    f"{FEMA_API_BASE}/DisasterDeclarationsSummaries"
                    f"?$filter=state eq '{state_abbr}' and declarationDate gt '{cutoff}'"
                    f"&$orderby=declarationDate desc"
                    f"&$top=20"
                )
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get('DisasterDeclarationsSummaries', []):
                        disasters.append(self._parse_fema_disaster(item))
            except requests.RequestException:
                continue

        # Deduplicate by disaster number
        seen = set()
        unique = []
        for d in disasters:
            key = d['fema_number']
            if key not in seen:
                seen.add(key)
                unique.append(d)
                
        unique.sort(key=lambda x: x.get('declaration_date', ''), reverse=True)
        self._fema_cache = {'disasters': unique, 'fetched_at': datetime.now(timezone.utc).isoformat()}
        self._fema_cache_time = time.time()
        return unique

    def _parse_fema_disaster(self, item: dict) -> dict:
        dec_type = item.get('declarationType', '')
        if dec_type == 'DR':
            severity = 'Major Disaster'
        elif dec_type == 'EM':
            severity = 'Emergency'
        elif dec_type == 'FM':
            severity = 'Warning'
        else:
            severity = 'Watch'

        incident_type = item.get('incidentType', 'Other')
        category = 'Hurricane'
        if 'hurricane' in incident_type.lower():
            category = 'Hurricane'
        elif 'flood' in incident_type.lower():
            category = 'Flood'
        elif 'tornado' in incident_type.lower() or 'severe storm' in incident_type.lower():
            category = 'Tornado'
        elif 'fire' in incident_type.lower():
            category = 'Wildfire'
        elif 'snow' in incident_type.lower() or 'ice' in incident_type.lower() or 'winter' in incident_type.lower():
            category = 'Winter Storm'
        else:
            category = incident_type

        dec_date = item.get('declarationDate', '')
        if dec_date:
            try:
                dec_date = datetime.fromisoformat(dec_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                pass

        begin_date = item.get('incidentBeginDate', '')
        if begin_date:
            try:
                begin_date = datetime.fromisoformat(begin_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                pass

        end_date = item.get('incidentEndDate', '')
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                pass

        close_date = item.get('disasterCloseoutDeadline', '')
        is_active = not bool(end_date)

        return {
            'source': 'FEMA',
            'fema_number': f"DR-{item.get('disasterNumber', 'N/A')}",
            'disaster_number': item.get('disasterNumber'),
            'declaration_type': dec_type,
            'title': item.get('declarationTitle', 'Unknown'),
            'state': item.get('state', ''),
            'state_name': FEMA_STATE_MAP.get(item.get('state', ''), item.get('state', '')),
            'category': category,
            'incident_type': incident_type,
            'severity': severity,
            'declaration_date': dec_date,
            'begin_date': begin_date,
            'end_date': end_date,
            'close_date': close_date,
            'is_active': is_active,
            'designated_area': item.get('designatedArea', ''),
            'programs_declared': {
                'individual_assistance': bool(item.get('ihProgramDeclared')),
                'public_assistance': bool(item.get('paProgramDeclared')),
                'hazard_mitigation': bool(item.get('hmProgramDeclared')),
            },
            'fema_url': f"https://www.fema.gov/disaster/{item.get('disasterNumber', '')}",
        }

    # ─── NWS WEATHER ALERTS ──────────────────────────────────────────

    def get_nws_alerts(self) -> list[dict]:
        """
        Fetch active NWS weather alerts for HAVEN states.
        Focuses on hurricane, flood, tornado, and severe weather events.
        """
        if self._nws_cache and (time.time() - self._nws_cache_time) < self.cache_ttl:
            return self._nws_cache.get('alerts', [])

        alerts = []
        for state_abbr in HAVEN_STATES:
            try:
                url = f"{NWS_API_BASE}/alerts/active?area={state_abbr}"
                resp = requests.get(url, headers=NWS_HEADERS, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    for feature in data.get('features', []):
                        parsed = self._parse_nws_alert(feature, state_abbr)
                        if parsed:
                            alerts.append(parsed)
            except requests.RequestException:
                continue

        alerts.sort(key=lambda x: x.get('severity_rank', 0), reverse=True)
        self._nws_cache = {'alerts': alerts, 'fetched_at': datetime.now(timezone.utc).isoformat()}
        self._nws_cache_time = time.time()
        return alerts

    def _parse_nws_alert(self, feature: dict, state: str) -> dict | None:
        props = feature.get('properties', {})
        event = props.get('event', '')
        severity = props.get('severity', 'Unknown')

        severity_rank = {'Extreme': 4, 'Severe': 3, 'Moderate': 2, 'Minor': 1, 'Unknown': 0}

        haven_severity = NWS_SEVERITY_MAP.get(severity, 'Watch')
        category = _event_category(event)

        onset = props.get('onset', '')
        if onset:
            try:
                onset = datetime.fromisoformat(onset).strftime('%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
                pass

        expires = props.get('expires', '')
        if expires:
            try:
                expires = datetime.fromisoformat(expires).strftime('%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
                pass

        affected = props.get('areaDesc', '')
        headline = props.get('headline', '')
        description = props.get('description', '')
        instruction = props.get('instruction', '')

        return {
            'source': 'NWS',
            'alert_id': props.get('id', ''),
            'event': event,
            'category': category,
            'severity': haven_severity,
            'severity_nws': severity,
            'severity_rank': severity_rank.get(severity, 0),
            'certainty': props.get('certainty', ''),
            'urgency': props.get('urgency', ''),
            'state': state,
            'affected_areas': affected,
            'headline': headline,
            'description': description[:500] if description else '',
            'instruction': instruction[:500] if instruction else '',
            'onset': onset,
            'expires': expires,
            'sender': props.get('senderName', ''),
            'status': props.get('status', ''),
            'message_type': props.get('messageType', ''),
        }

    # ─── COMBINED THREAT ASSESSMENT ──────────────────────────────────

    def get_threat_assessment(self) -> dict:
        """
        Combined threat assessment for all HAVEN states.
        Returns overall threat level, active alerts by state, and recommendations.
        """
        fema = self.get_fema_disasters(days_back=90)
        nws = self.get_nws_alerts()

        active_fema = [d for d in fema if d.get('is_active')]

        # Threat level per state
        state_threats: dict[str, dict] = {}
        for st in HAVEN_STATES:
            st_fema = [d for d in active_fema if d['state'] == st]
            st_nws = [a for a in nws if a['state'] == st]

            # Highest severity
            max_sev = 'None'
            sev_order = ['None', 'Watch', 'Warning', 'Emergency', 'Major Disaster']
            for d in st_fema:
                if sev_order.index(d['severity']) > sev_order.index(max_sev):
                    max_sev = d['severity']
            for a in st_nws:
                if sev_order.index(a['severity']) > sev_order.index(max_sev):
                    max_sev = a['severity']

            # Categorize NWS alerts
            hurricane_alerts = [a for a in st_nws if a['category'] == 'Hurricane']
            flood_alerts = [a for a in st_nws if a['category'] == 'Flood']
            tornado_alerts = [a for a in st_nws if a['category'] == 'Tornado']
            other_alerts = [a for a in st_nws if a['category'] not in ('Hurricane', 'Flood', 'Tornado')]

            state_threats[st] = {
                'state': st,
                'state_name': FEMA_STATE_MAP.get(st, st),
                'threat_level': max_sev,
                'active_fema_declarations': len(st_fema),
                'active_nws_alerts': len(st_nws),
                'hurricane_alerts': len(hurricane_alerts),
                'flood_alerts': len(flood_alerts),
                'tornado_alerts': len(tornado_alerts),
                'other_alerts': len(other_alerts),
                'fema_disasters': st_fema[:5],
                'top_alerts': st_nws[:10],
            }

        # Overall threat level
        overall = 'None'
        sev_order = ['None', 'Watch', 'Warning', 'Emergency', 'Major Disaster']
        for st_data in state_threats.values():
            if sev_order.index(st_data['threat_level']) > sev_order.index(overall):
                overall = st_data['threat_level']

        total_alerts = len(nws)
        total_fema = len(active_fema)

        # Recommendations
        recommendations = []
        if overall == 'Major Disaster':
            recommendations.append('ACTIVATE HAVEN — Major disaster declaration in effect. Begin member outreach immediately.')
        elif overall == 'Emergency':
            recommendations.append('PRE-ACTIVATE — Emergency conditions detected. Notify network partners and stand by for activation.')
        elif overall == 'Warning':
            recommendations.append('MONITOR CLOSELY — Active warnings in HAVEN states. Review partner readiness.')
        elif overall == 'Watch':
            recommendations.append('STANDBY — Weather watches active. No action required but stay informed.')
        else:
            recommendations.append('ALL CLEAR — No active threats in HAVEN states.')

        hurricane_count = sum(st['hurricane_alerts'] for st in state_threats.values())
        if hurricane_count > 0:
            recommendations.append(f'HURRICANE ACTIVITY — {hurricane_count} hurricane-related alerts active. Review evacuation transport capacity.')

        flood_count = sum(st['flood_alerts'] for st in state_threats.values())
        if flood_count > 0:
            recommendations.append(f'FLOOD RISK — {flood_count} flood alerts active. Confirm housing partner availability.')

        return {
            'overall_threat_level': overall,
            'total_nws_alerts': total_alerts,
            'total_active_fema': total_fema,
            'states': state_threats,
            'recommendations': recommendations,
            'fetched_at': datetime.now(timezone.utc).isoformat(),
            'cache_ttl_seconds': self.cache_ttl,
        }

    def get_watch_feed(self) -> dict:
        """
        Full disaster watch feed — everything HAVEN needs on one screen.
        """
        fema = self.get_fema_disasters(days_back=90)
        nws = self.get_nws_alerts()
        assessment = self.get_threat_assessment()

        # Merge into a unified feed sorted by severity
        feed_items = []

        for d in fema:
            if d.get('is_active'):
                feed_items.append({
                    'source': 'FEMA',
                    'type': 'declaration',
                    'title': f"FEMA {d['fema_number']}: {d['title']}",
                    'category': d['category'],
                    'severity': d['severity'],
                    'state': d['state'],
                    'date': d['declaration_date'],
                    'detail': f"{d['incident_type']} — {d['designated_area']}",
                    'url': d.get('fema_url', ''),
                    'programs': d.get('programs_declared', {}),
                })

        for a in nws:
            feed_items.append({
                'source': 'NWS',
                'type': 'alert',
                'title': a['headline'] or a['event'],
                'category': a['category'],
                'severity': a['severity'],
                'state': a['state'],
                'date': a['onset'],
                'expires': a['expires'],
                'detail': a['affected_areas'],
                'instruction': a.get('instruction', ''),
                'urgency': a.get('urgency', ''),
                'certainty': a.get('certainty', ''),
            })

        sev_order = {'Major Disaster': 4, 'Emergency': 3, 'Warning': 2, 'Watch': 1, 'None': 0}
        feed_items.sort(key=lambda x: sev_order.get(x.get('severity', 'None'), 0), reverse=True)

        return {
            'threat_level': assessment['overall_threat_level'],
            'total_alerts': len(nws),
            'total_fema_active': len([d for d in fema if d.get('is_active')]),
            'recommendations': assessment['recommendations'],
            'states': assessment['states'],
            'feed': feed_items,
            'recent_fema': fema[:10],
            'fetched_at': assessment['fetched_at'],
        }

    def clear_cache(self):
        self._fema_cache = {}
        self._fema_cache_time = 0
        self._nws_cache = {}
        self._nws_cache_time = 0


# Singleton instance
_watch = DisasterWatch()

def get_watch_feed() -> dict:
    return _watch.get_watch_feed()

def get_threat_assessment() -> dict:
    return _watch.get_threat_assessment()

def get_fema_disasters(days_back: int = 90) -> list[dict]:
    return _watch.get_fema_disasters(days_back)

def get_nws_alerts() -> list[dict]:
    return _watch.get_nws_alerts()

def clear_cache():
    _watch.clear_cache()


if __name__ == '__main__':
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'feed'

    if cmd == 'feed':
        feed = get_watch_feed()
        print(f"\n{'='*60}")
        print(f"  HAVEN DISASTER WATCH — {feed['threat_level']}")
        print(f"{'='*60}")
        print(f"  NWS Alerts: {feed['total_alerts']}  |  Active FEMA: {feed['total_fema_active']}")
        print()
        for rec in feed['recommendations']:
            print(f"  >> {rec}")
        print()
        for st, data in feed['states'].items():
            print(f"  {st} ({data['state_name']}): {data['threat_level']}")
            print(f"     FEMA: {data['active_fema_declarations']} | NWS: {data['active_nws_alerts']} | Hurricane: {data['hurricane_alerts']} | Flood: {data['flood_alerts']}")
        print()
        print(f"  Feed items: {len(feed['feed'])}")
        for item in feed['feed'][:10]:
            print(f"    [{item['severity']}] {item['source']} | {item['state']} | {item['title'][:80]}")
        print()

    elif cmd == 'fema':
        disasters = get_fema_disasters(days_back=365)
        print(f"\nFEMA Disasters (last 365 days): {len(disasters)}")
        for d in disasters[:15]:
            print(f"  {d['fema_number']} | {d['state']} | {d['severity']} | {d['title']} | {d['declaration_date']}")

    elif cmd == 'nws':
        alerts = get_nws_alerts()
        print(f"\nNWS Active Alerts: {len(alerts)}")
        for a in alerts[:20]:
            print(f"  [{a['severity']}] {a['state']} | {a['event']} | {a['headline'][:70]}")

    elif cmd == 'assess':
        assessment = get_threat_assessment()
        print(json.dumps(assessment, indent=2, default=str))
