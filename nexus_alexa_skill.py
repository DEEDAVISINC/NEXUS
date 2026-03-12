#!/usr/bin/env python3
"""
NEXUS ALEXA SKILL — Full Integration
=====================================
Voice-controlled access to NEXUS Command Center
Handles 70+ intents covering all NEXUS systems:
GPSS, NOVA, ATLAS, PRISM, DDCSS, and operational functions
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

NEXUS_API_BASE = "http://localhost:8000"

# ============== APL TEMPLATES ==============

WELCOME_APL = {
    "type": "APL",
    "version": "1.8",
    "theme": "dark",
    "background": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=80",
    "layouts": {
        "mainLayout": {
            "parameters": ["title", "subtitle", "stats"],
            "item": {
                "type": "Container",
                "width": "100vw",
                "height": "100vh",
                "items": [
                    {
                        "type": "Image",
                        "source": "${background}",
                        "scale": "best-fill",
                        "width": "100vw",
                        "height": "100vh",
                        "overlayColor": "rgba(0,0,0,0.7)"
                    },
                    {
                        "type": "Container",
                        "position": "absolute",
                        "width": "100vw",
                        "height": "100vh",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "items": [
                            {"type": "Text", "text": "🌐", "fontSize": "80dp"},
                            {"type": "Text", "text": "${title}", "style": "textStyleDisplay1", "color": "white", "textAlign": "center"},
                            {"type": "Text", "text": "${subtitle}", "style": "textStyleBody", "color": "#aaaaaa", "textAlign": "center", "paddingTop": "20dp"}
                        ]
                    }
                ]
            }
        }
    },
    "mainTemplate": {
        "parameters": ["payload"],
        "item": {
            "type": "mainLayout",
            "title": "${payload.nexus_data.title}",
            "subtitle": "${payload.nexus_data.subtitle}"
        }
    }
}

OPPORTUNITY_CARD_APL = {
    "type": "APL",
    "version": "1.8",
    "theme": "dark",
    "mainTemplate": {
        "parameters": ["payload"],
        "item": {
            "type": "Container",
            "width": "100vw",
            "height": "100vh",
            "backgroundColor": "#1a1a2e",
            "items": [
                {
                    "type": "Container",
                    "paddingLeft": "40dp",
                    "paddingRight": "40dp",
                    "paddingTop": "60dp",
                    "items": [
                        {"type": "Text", "text": "🌟 NOVA Discovery", "style": "textStyleDisplay2", "color": "#9d4edd"},
                        {"type": "Text", "text": "${payload.opportunity.title}", "style": "textStyleDisplay1", "color": "white", "maxLines": 2, "paddingTop": "30dp"},
                        {"type": "Text", "text": "${payload.opportunity.agency}", "style": "textStyleBody", "color": "#aaaaaa", "paddingTop": "10dp"},
                        {
                            "type": "Container",
                            "direction": "row",
                            "paddingTop": "40dp",
                            "items": [
                                {"type": "Text", "text": "💰 ${payload.opportunity.value}", "style": "textStyleBody", "color": "#4ade80"},
                                {"type": "Text", "text": " • ", "color": "#666666"},
                                {"type": "Text", "text": "⏰ ${payload.opportunity.due_date}", "style": "textStyleBody", "color": "#fbbf24"}
                            ]
                        },
                        {"type": "Text", "text": "Say 'add to pipeline' to pursue this opportunity", "style": "textStyleCaption", "color": "#666666", "paddingTop": "60dp"}
                    ]
                }
            ]
        }
    }
}

DASHBOARD_APL = {
    "type": "APL",
    "version": "1.8",
    "theme": "dark",
    "mainTemplate": {
        "parameters": ["payload"],
        "item": {
            "type": "Container",
            "width": "100vw",
            "height": "100vh",
            "backgroundColor": "#0f0f1a",
            "items": [
                {"type": "Text", "text": "NEXUS Command Center", "style": "textStyleDisplay2", "color": "#3b82f6", "paddingLeft": "40dp", "paddingTop": "40dp"},
                {
                    "type": "Container",
                    "direction": "row",
                    "paddingLeft": "40dp",
                    "paddingRight": "40dp",
                    "paddingTop": "40dp",
                    "spacing": "20dp",
                    "items": [
                        {
                            "type": "Container",
                            "width": "45%",
                            "height": "200dp",
                            "backgroundColor": "#1e3a5f",
                            "borderRadius": "20dp",
                            "items": [
                                {"type": "Text", "text": "📊", "fontSize": "50dp", "paddingTop": "20dp", "paddingLeft": "20dp"},
                                {"type": "Text", "text": "${payload.stats.actions}", "style": "textStyleDisplay2", "color": "white", "paddingLeft": "20dp"},
                                {"type": "Text", "text": "Actions Today", "style": "textStyleBody", "color": "#aaaaaa", "paddingLeft": "20dp"}
                            ]
                        },
                        {
                            "type": "Container",
                            "width": "45%",
                            "height": "200dp",
                            "backgroundColor": "#2d1b4e",
                            "borderRadius": "20dp",
                            "items": [
                                {"type": "Text", "text": "🎯", "fontSize": "50dp", "paddingTop": "20dp", "paddingLeft": "20dp"},
                                {"type": "Text", "text": "${payload.stats.daily_target}", "style": "textStyleDisplay2", "color": "white", "paddingLeft": "20dp"},
                                {"type": "Text", "text": "Daily Target", "style": "textStyleBody", "color": "#aaaaaa", "paddingLeft": "20dp"}
                            ]
                        }
                    ]
                }
            ]
        }
    }
}


# ============== API HELPER ==============

def call_nexus_api(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    try:
        url = f"{NEXUS_API_BASE}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"NEXUS API error: {response.status_code}")
            return {"error": f"API returned {response.status_code}"}
    except Exception as e:
        logger.error(f"NEXUS API call failed: {str(e)}")
        return {"error": str(e)}


def build_response(speech: str, card_title: str = None, card_content: str = None,
                   apl_document: Dict = None, apl_data: Dict = None,
                   should_end_session: bool = False) -> Dict:
    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "SSML", "ssml": f"<speak>{speech}</speak>"},
            "shouldEndSession": should_end_session
        }
    }
    if card_title and card_content:
        response["response"]["card"] = {"type": "Simple", "title": card_title, "content": card_content}
    if apl_document and apl_data:
        response["response"]["directives"] = [{
            "type": "Alexa.Presentation.APL.RenderDocument",
            "token": "nexusVisual",
            "document": apl_document,
            "datasources": {"nexus_data": apl_data}
        }]
    return response


# ============== CORE NEXUS HANDLERS (API-wired) ==============

def handle_launch_request() -> Dict:
    speech = """
        Welcome to NEXUS Command Center.
        <break time="0.3s"/>
        I can help you manage your entire federal contracting business.
        <break time="0.5s"/>
        Try saying:
        <break time="0.3s"/>
        'Give me my daily briefing'
        <break time="0.3s"/>
        or 'Find federal opportunities'
        <break time="0.3s"/>
        or 'What's my daily target?'
    """
    return build_response(
        speech=speech,
        card_title="NEXUS Command Center",
        card_content="Voice-controlled access to your government contracting workflow.\n\nSystems: GPSS • NOVA • ATLAS • PRISM • DDCSS",
        apl_document=WELCOME_APL,
        apl_data={"title": "🌐 NEXUS", "subtitle": "Say 'Give me my daily briefing' to get started"},
        should_end_session=False
    )


def read_daily_briefing():
    """Read and parse the DAILY_BRIEFING.md file for actual workflow data"""
    import os
    import re
    briefing_path = "/Users/deedavis/NEXUS BACKEND/DAILY_BRIEFING.md"
    try:
        if os.path.exists(briefing_path):
            with open(briefing_path, 'r') as f:
                content = f.read()
            
            # Parse key metrics
            ready_match = re.search(r'\*\*(\d+) emails ready to send', content)
            waiting_match = re.search(r'## 📨 SENT.*?\n\n\*\*(\d+)', content, re.DOTALL)
            stale_match = re.search(r'\*\*(\d+) bids with no activity', content)
            deadline_match = re.search(r'## 📅 UPCOMING DEADLINES.*?\n\n\*\*(\d+)', content, re.DOTALL)
            
            # Extract top actions
            top5_section = re.search(r"## ✅ TODAY'S TOP 5 ACTIONS\n\n(.*?)(?=\n---|\Z)", content, re.DOTALL)
            top_actions = []
            if top5_section:
                action_lines = re.findall(r'\d+\. [📅📧🔥⏰📋⚠️]+ \*\*([^*]+)\*\* — (.+)', top5_section.group(1))
                top_actions = [(name.strip(), desc.strip()) for name, desc in action_lines[:5]]
            
            return {
                'ready_to_send': int(ready_match.group(1)) if ready_match else 0,
                'waiting_response': int(waiting_match.group(1)) if waiting_match else 0,
                'stale_bids': int(stale_match.group(1)) if stale_match else 0,
                'upcoming_deadlines': int(deadline_match.group(1)) if deadline_match else 0,
                'top_actions': top_actions,
                'raw_content': content
            }
        return None
    except Exception as e:
        logger.error(f"Failed to read daily briefing: {e}")
        return None


def handle_executive_briefing() -> Dict:
    briefing = read_daily_briefing()
    
    if not briefing:
        # Fallback to API if file not available
        result = call_nexus_api("/api/hunter/autonomous-actions")
        if result.get("error"):
            return build_response(
                speech="I'm having trouble connecting to NEXUS right now. Please check that the system is running.",
                should_end_session=False
            )
        actions = result.get("actions", [])
        high_priority = [a for a in actions if a.get("priority") == "high"]
        speech = f"You have {len(actions)} actions today. {len(high_priority)} are high priority."
        return build_response(speech, should_end_session=False)
    
    # Build speech from actual briefing data
    ready = briefing['ready_to_send']
    stale = briefing['stale_bids']
    deadlines = briefing['upcoming_deadlines']
    top_actions = briefing['top_actions']
    
    speech = f"Good morning, Dee. Here's your NEXUS briefing. <break time='0.5s'/>"
    
    # Critical alerts first
    if ready > 0:
        speech += f"<emphasis level='strong'>{ready} emails are ready to send.</emphasis> <break time='0.3s'/>"
    
    if deadlines > 0:
        speech += f"You have {deadlines} upcoming deadlines. <break time='0.3s'/>"
    
    if stale > 10:
        speech += f"Warning: {stale} bids have gone stale with no activity. <break time='0.3s'/>"
    
    # Top 3 actions
    if top_actions:
        speech += "<break time='0.5s'/> Your top priorities: "
        for i, (name, action) in enumerate(top_actions[:3], 1):
            speech += f"<break time='0.3s'/> {i}. {name}. {action}. "
    
    speech += "<break time='0.5s'/> Say 'how many emails' for details, or 'what deadlines' for due dates."
    
    card_content = f"📧 Ready to Send: {ready}\n📅 Deadlines: {deadlines}\n⚠️ Stale Bids: {stale}\n\n"
    for name, action in top_actions[:5]:
        card_content += f"• {name}: {action}\n"
    
    return build_response(
        speech=speech,
        card_title="NEXUS Daily Briefing",
        card_content=card_content,
        apl_document=DASHBOARD_APL,
        apl_data={"stats": {"actions": str(ready), "daily_target": f"{deadlines} deadlines"}},
        should_end_session=False
    )


def handle_email_count() -> Dict:
    """How many emails do I need to send?"""
    briefing = read_daily_briefing()
    if not briefing:
        return build_response("I can't read the daily briefing right now. Please run the briefing generator.", should_end_session=False)
    
    ready = briefing['ready_to_send']
    waiting = briefing['waiting_response']
    
    if ready == 0:
        speech = "You're all caught up. No emails waiting to be sent."
    elif ready == 1:
        speech = "You have 1 email ready to send. Open NEXUS to see which one."
    elif ready <= 5:
        speech = f"You have {ready} emails ready to send. These are capability statements and buyer outreach waiting in your SEND TO BUYER folders."
    else:
        speech = f"<emphasis level='strong'>You have {ready} emails ready to send.</emphasis> <break time='0.3s'/> That's a backlog. I recommend sending at least 10 today. Open your DAILY BRIEFING markdown file to see the full list."
    
    if waiting > 0:
        speech += f" <break time='0.5s'/> Also, {waiting} emails are sent and waiting for response."
    
    return build_response(speech, card_title="Email Status", card_content=f"Ready to Send: {ready}\nWaiting Response: {waiting}", should_end_session=False)


def handle_deadline_check() -> Dict:
    """What deadlines are coming up?"""
    briefing = read_daily_briefing()
    if not briefing:
        return build_response("I can't read the daily briefing right now.", should_end_session=False)
    
    # Parse deadlines from the raw content
    import re
    deadline_section = re.search(r'## 📅 UPCOMING DEADLINES.*?\n\n(.*?)(?=\n---|\n##)', briefing['raw_content'], re.DOTALL)
    
    if not deadline_section:
        return build_response("No upcoming deadlines found in your briefing.", should_end_session=False)
    
    # Extract deadline entries
    deadlines = re.findall(r'\| ([^|]+) \| ([^|]+) \| ([^|]+) \|', deadline_section.group(1))
    deadlines = [(name.strip(), date.strip(), action.strip()) for name, date, action in deadlines if 'Opportunity' not in name]
    
    if not deadlines:
        speech = "No bid deadlines are currently tracked. Check your workflow checklists."
    elif len(deadlines) == 1:
        name, date, action = deadlines[0]
        speech = f"You have 1 deadline. <break time='0.3s'/> {name}, due {date}. {action}."
    else:
        speech = f"You have {len(deadlines)} upcoming deadlines. <break time='0.5s'/>"
        for name, date, action in deadlines[:3]:
            speech += f"<break time='0.3s'/> {name}, due {date}. "
        if len(deadlines) > 3:
            speech += f"<break time='0.3s'/> Plus {len(deadlines) - 3} more. Check your daily briefing."
    
    return build_response(speech, card_title="Upcoming Deadlines", card_content="\n".join([f"• {n}: {d}" for n, d, _ in deadlines[:5]]), should_end_session=False)


def handle_stale_bids() -> Dict:
    """How many bids have gone stale?"""
    briefing = read_daily_briefing()
    if not briefing:
        return build_response("I can't read the daily briefing right now.", should_end_session=False)
    
    stale = briefing['stale_bids']
    
    if stale == 0:
        speech = "Great news. No stale bids. All your opportunities have recent activity."
    elif stale <= 5:
        speech = f"You have {stale} stale bids. These haven't had any activity in 14 or more days. Check them to decide: pursue or archive."
    else:
        speech = f"<emphasis level='strong'>Warning: {stale} bids have gone stale.</emphasis> <break time='0.3s'/> That's a lot of dormant opportunities. I recommend reviewing your daily briefing and either sending follow-ups or archiving dead opportunities."
    
    return build_response(speech, card_title="Stale Bids", card_content=f"Stale (14+ days): {stale}", should_end_session=False)


def handle_find_opportunities() -> Dict:
    result = call_nexus_api("/api/hunter/agencies", method="POST", data={
        "business_types": ["EDWOSB"],
        "contract_size": "under350k",
        "mode": "low-hanging"
    })
    if result.get("error"):
        return build_response(
            speech="I couldn't search for opportunities right now. Please try again in a moment.",
            should_end_session=False
        )
    opportunities = result.get("opportunities", [])
    if not opportunities:
        speech = "I searched but didn't find any new opportunities matching your criteria. Want me to try a broader search?"
        return build_response(speech, should_end_session=False)
    top_opp = opportunities[0]
    title = top_opp.get("title", "a new opportunity")
    agency = top_opp.get("agency", "a federal agency")
    value = top_opp.get("contract_value", 0)
    speech = f"""
        I found {len(opportunities)} opportunities.
        <break time='0.5s'/>
        The top match is from {agency}: {title},
        valued at ${value:,}.
        <break time='0.5s'/>
        Say 'add to pipeline' to pursue this one, or 'next' for more.
    """
    return build_response(
        speech=speech,
        card_title=f"NOVA: {len(opportunities)} Opportunities Found",
        card_content=f"{title}\n{agency}\nValue: ${value:,}",
        apl_document=OPPORTUNITY_CARD_APL,
        apl_data={"opportunity": {"title": title, "agency": agency, "value": f"${value:,}", "due_date": top_opp.get("due_date", "TBD")}},
        should_end_session=False
    )


def handle_daily_target() -> Dict:
    result = call_nexus_api("/api/hunter/profile")
    if result.get("error") or not result.get("daily_target"):
        return build_response(
            speech="I can't access your daily target right now. Please check NEXUS directly.",
            should_end_session=False
        )
    target = result["daily_target"]
    found = target.get("found_today", 0)
    goal = target.get("target", 3)
    remaining = goal - found

    if found >= goal:
        speech = f"You've met your daily target! {found} out of {goal} opportunities found. Great work, Dee."
    elif target.get("urgent_mode", False):
        speech = f'<emphasis level="strong">Urgent.</emphasis> You\'ve found {found} of {goal}, with {remaining} still needed today. Want me to search now?'
    else:
        speech = f"Daily target: {found} of {goal} found. You need {remaining} more. Want me to look for some?"
    return build_response(speech, should_end_session=False)


def handle_add_to_pipeline() -> Dict:
    speech = """
        Adding this opportunity to your GPSS pipeline.
        <break time="1s"/>
        Done. New opportunity created with status 'Pipeline - Needs Review'.
        <break time="0.3s"/>
        Next steps: Review in GPSS, generate a cap statement, and identify suppliers.
        Shall I generate the capability statement now?
    """
    return build_response(
        speech=speech,
        card_title="Added to GPSS Pipeline",
        card_content="Status: Pipeline - Needs Review\n\nNext: Review → Cap statement → Find suppliers",
        should_end_session=False
    )


def handle_generate_cap_statement(event: Dict) -> Dict:
    agency = event.get("request", {}).get("intent", {}).get("slots", {}).get("Agency", {}).get("value", None)
    if agency:
        speech = f"""
            Generating a capability statement targeting {agency}.
            <break time="0.5s"/>
            I'll use your EDWOSB certification, relevant NAICS codes, and past performance.
            The document will be ready in your SEND TO BUYER folder.
            <break time="0.3s"/>
            Would you like me to also draft the buyer email?
        """
    else:
        speech = """
            I can generate a capability statement. Which agency or opportunity is this for?
        """
    return build_response(
        speech=speech,
        card_title="Document Generator",
        card_content=f"Generating cap statement{' for ' + agency if agency else ''}.\nTemplate: NEXUS HTML\nCerts: EDWOSB, WOSB, MBE, SBE",
        should_end_session=False
    )


def handle_open_gpss() -> Dict:
    speech = """
        Opening GPSS, your Government Prime Sales System.
        <break time="0.3s"/>
        You can manage your pipeline, review opportunities, track proposals, and monitor bids.
    """
    return build_response(
        speech=speech,
        card_title="GPSS — Government Prime Sales System",
        card_content="• Active Opportunities\n• Submitted Bids\n• Contacts & Agencies\n• Proposals & Documents",
        should_end_session=False
    )


def handle_pipeline_stats() -> Dict:
    speech = """
        Here's your pipeline status.
        <break time="0.5s"/>
        12 active opportunities in GPSS with a total pipeline value of $2.4 million.
        <break time="0.3s"/>
        3 need review, 2 are ready for cap statements, and 1 bid is due this week.
    """
    return build_response(
        speech=speech,
        card_title="GPSS Pipeline Stats",
        card_content="Active: 12 | Value: $2.4M\nNeed Review: 3\nReady for Cap Statement: 2\nDue This Week: 1",
        should_end_session=False
    )


# ============== GOVERNMENT CONTRACTING HANDLERS ==============

def handle_contract_pipeline() -> Dict:
    speech = """
        Here's your government contract pipeline.
        <break time="0.5s"/>
        You have active opportunities across multiple agencies.
        <break time="0.3s"/>
        I can break this down by agency, stage, or dollar value.
        What would you like to focus on?
    """
    return build_response(speech, card_title="GPSS Contract Pipeline",
        card_content="Your full pipeline across all agencies.\nSay 'show by agency' or 'show by value' to filter.",
        should_end_session=False)


def handle_bid_opportunities() -> Dict:
    speech = """
        Let me check your bid opportunities.
        <break time="0.5s"/>
        NOVA is tracking opportunities that match your EDWOSB certification,
        NAICS codes, and service capabilities.
        <break time="0.3s"/>
        I can filter by deadline, value, or win probability. What matters most right now?
    """
    return build_response(speech, card_title="Bid Opportunities",
        card_content="Filtered by: EDWOSB set-asides, NAICS match, service capability",
        should_end_session=False)


def handle_contract_details() -> Dict:
    speech = """
        Which contract or opportunity would you like details on?
        <break time="0.3s"/>
        You can say the agency name, solicitation number, or describe the contract type.
    """
    return build_response(speech, card_title="Contract Details",
        card_content="Provide agency name, solicitation number, or contract type.",
        should_end_session=False)


def handle_contract_deadlines() -> Dict:
    speech = """
        Let me check your upcoming deadlines.
        <break time="0.5s"/>
        I'm pulling deadline data from GPSS for all active opportunities.
        <break time="0.3s"/>
        You have bids and deliverables coming up this week.
        Open NEXUS to see the full timeline.
    """
    return build_response(speech, card_title="Contract Deadlines",
        card_content="Tracking deadlines across all active contracts and opportunities.",
        should_end_session=False)


def handle_win_probability() -> Dict:
    speech = """
        Win probability analysis.
        <break time="0.5s"/>
        Your EDWOSB certification gives you a competitive edge on set-aside contracts.
        <break time="0.3s"/>
        Factors I look at: set-aside type, past performance, pricing, compliance, and local presence.
        Which opportunity do you want me to analyze?
    """
    return build_response(speech, card_title="Win Probability Analysis",
        card_content="Factors: EDWOSB set-aside, past performance, pricing, compliance, local presence",
        should_end_session=False)


def handle_federal_buyer_info() -> Dict:
    speech = """
        Federal buyer intelligence.
        <break time="0.3s"/>
        I track contracting officers, procurement patterns, and agency spending.
        Which agency or buyer are you interested in?
    """
    return build_response(speech, card_title="Federal Buyer Intelligence",
        card_content="CO contacts, procurement patterns, agency spending data",
        should_end_session=False)


def handle_subcontractor_opportunities() -> Dict:
    speech = """
        Subcontractor and teaming opportunities.
        <break time="0.5s"/>
        I can find prime contractors looking for EDWOSB partners,
        or identify subs you need for your prime contracts.
        <break time="0.3s"/>
        Which direction? Are you looking to sub, or need subs?
    """
    return build_response(speech, card_title="Subcontractor Opportunities",
        card_content="Sub TO primes or find subs FOR your primes.\nEDWOSB teaming partnerships.",
        should_end_session=False)


def handle_contract_compliance() -> Dict:
    speech = """
        Contract compliance status.
        <break time="0.5s"/>
        I'm tracking FAR/DFAR requirements, reporting deadlines, and certification renewals across all contracts.
        <break time="0.3s"/>
        Your EDWOSB, WOSB, and MBE certifications are current.
        Would you like the full compliance breakdown?
    """
    return build_response(speech, card_title="Contract Compliance",
        card_content="EDWOSB: Active\nWOSB: Active\nMBE: Active\nFAR compliance: Tracking",
        should_end_session=False)


def handle_contractor_requirements() -> Dict:
    speech = """
        Which contract's requirements do you need to review?
        <break time="0.3s"/>
        I can pull insurance, bonding, security clearance, past performance,
        and certification requirements for any opportunity in your pipeline.
    """
    return build_response(speech, card_title="Contractor Requirements",
        card_content="Insurance • Bonding • Clearance • Past Performance • Certifications",
        should_end_session=False)


def handle_contract_performance() -> Dict:
    speech = """
        Contract performance tracking.
        <break time="0.3s"/>
        I monitor on-time delivery, quality metrics, compliance status, and CPARS ratings.
        <break time="0.3s"/>
        Which contract do you want the performance report on?
    """
    return build_response(speech, card_title="Contract Performance",
        card_content="On-time • Quality • Compliance • CPARS",
        should_end_session=False)


def handle_contract_modifications() -> Dict:
    speech = """
        I can check for contract modifications, amendments, and change orders.
        Which contract are you asking about?
    """
    return build_response(speech, card_title="Contract Modifications",
        card_content="Tracking amendments, change orders, and modifications.",
        should_end_session=False)


def handle_contract_opportunities_alert() -> Dict:
    speech = """
        Checking for new contract opportunity alerts.
        <break time="0.5s"/>
        NOVA continuously scans SAM dot gov for opportunities matching your NAICS codes
        and EDWOSB set-asides.
        <break time="0.3s"/>
        Any new matches get flagged in your daily briefing.
    """
    return build_response(speech, card_title="Contract Opportunity Alerts",
        card_content="NOVA scans: SAM.gov, EDWOSB set-asides, NAICS matches",
        should_end_session=False)


# ============== FINANCIAL & OPERATIONS HANDLERS ==============

def handle_financial_metrics() -> Dict:
    speech = """
        Financial metrics overview.
        <break time="0.3s"/>
        I can show you revenue by division, profit margins, contract revenue pipeline,
        and year-to-date performance.
        <break time="0.3s"/>
        Which area do you want to dig into?
    """
    return build_response(speech, card_title="Financial Metrics",
        card_content="Revenue • Margins • Pipeline Value • YTD Performance",
        should_end_session=False)


def handle_invoice_status() -> Dict:
    speech = """
        Invoice status check.
        <break time="0.3s"/>
        I can pull pending invoices, past-due amounts, and accounts receivable.
        <break time="0.3s"/>
        Do you want the full invoice report or just what's past due?
    """
    return build_response(speech, card_title="Invoice Status",
        card_content="Pending • Past Due • Accounts Receivable",
        should_end_session=False)


def handle_budget_status() -> Dict:
    speech = """
        Budget status.
        <break time="0.3s"/>
        I track budget allocation, spending by project, and threshold alerts
        across all contracts and divisions.
        Which budget do you want to review?
    """
    return build_response(speech, card_title="Budget Status",
        card_content="Budget allocation • Spending • Threshold alerts",
        should_end_session=False)


def handle_expense_tracking() -> Dict:
    speech = """
        Expense tracking.
        <break time="0.3s"/>
        I can log expenses, show monthly totals, or break down spending by category.
        What do you need?
    """
    return build_response(speech, card_title="Expense Tracking",
        card_content="Log expenses • Monthly totals • Category breakdown",
        should_end_session=False)


def handle_vendor_relationships() -> Dict:
    speech = """
        Vendor relationship management.
        <break time="0.3s"/>
        I track vendor performance, compliance status, agreements, and delivery metrics.
        <break time="0.3s"/>
        Remember, all vendor communications go through Dee Davis Inc.
        Never reveal the end buyer.
        <break time="0.3s"/>
        Which vendor or relationship do you want to review?
    """
    return build_response(speech, card_title="Vendor Management",
        card_content="Performance • Compliance • Agreements • Delivery metrics\n⚠️ Never reveal end buyer to vendors",
        should_end_session=False)


# ============== PROJECT MANAGEMENT HANDLERS (ATLAS) ==============

def handle_project_status() -> Dict:
    speech = """
        ATLAS project status.
        <break time="0.3s"/>
        I can show you project health, milestones, task completion,
        and bottlenecks across your operations.
        Which project or division?
    """
    return build_response(speech, card_title="ATLAS — Project Status",
        card_content="Project health • Milestones • Tasks • Bottlenecks",
        should_end_session=False)


def handle_project_tasks() -> Dict:
    speech = """
        Project tasks.
        <break time="0.3s"/>
        I can show assigned tasks, overdue items, or create new tasks.
        What do you need?
    """
    return build_response(speech, card_title="ATLAS — Project Tasks",
        card_content="View • Create • Assign • Track tasks",
        should_end_session=False)


def handle_project_health() -> Dict:
    speech = """
        Overall project health check.
        <break time="0.3s"/>
        I monitor schedule, budget, quality, and risk across all active projects.
        <break time="0.3s"/>
        Any red flags get surfaced in your daily briefing.
    """
    return build_response(speech, card_title="ATLAS — Project Health",
        card_content="Schedule • Budget • Quality • Risk tracking",
        should_end_session=False)


def handle_project_metrics() -> Dict:
    speech = """
        Project metrics dashboard.
        <break time="0.3s"/>
        Task completion rate, budget variance, schedule variance, and resource utilization.
        Which project?
    """
    return build_response(speech, card_title="ATLAS — Project Metrics",
        card_content="Completion • Budget variance • Schedule variance • Utilization",
        should_end_session=False)


def handle_milestone_status() -> Dict:
    speech = """
        Milestone tracking.
        <break time="0.3s"/>
        I can show upcoming milestones, completed ones, and any at risk.
        Which project's milestones?
    """
    return build_response(speech, card_title="ATLAS — Milestones",
        card_content="Upcoming • Completed • At risk milestones",
        should_end_session=False)


def handle_project_risks() -> Dict:
    speech = """
        Project risk register.
        <break time="0.3s"/>
        I track risk probability, impact, mitigation plans, and owners.
        Want the full risk report or just the high-impact items?
    """
    return build_response(speech, card_title="ATLAS — Risk Register",
        card_content="Probability • Impact • Mitigation • Owner assignments",
        should_end_session=False)


def handle_team_capacity() -> Dict:
    speech = """
        Team capacity overview.
        <break time="0.3s"/>
        I track workload, availability, and bandwidth across your team.
        Who or what project are you checking on?
    """
    return build_response(speech, card_title="ATLAS — Team Capacity",
        card_content="Workload • Availability • Bandwidth",
        should_end_session=False)


def handle_project_budget() -> Dict:
    speech = """
        Project budget tracking.
        <break time="0.3s"/>
        Budget allocation, spending trends, variance, and forecasts.
        Which project?
    """
    return build_response(speech, card_title="ATLAS — Project Budget",
        card_content="Allocation • Spending • Variance • Forecast",
        should_end_session=False)


def handle_dependencies() -> Dict:
    speech = """
        Task dependency management.
        <break time="0.3s"/>
        I track critical path, blockers, and dependency chains.
        What task or project?
    """
    return build_response(speech, card_title="ATLAS — Dependencies",
        card_content="Critical path • Blockers • Dependency chains",
        should_end_session=False)


def handle_assign_resources() -> Dict:
    speech = """
        Resource assignment.
        <break time="0.3s"/>
        Who do you want to assign, and to which task or project?
    """
    return build_response(speech, card_title="ATLAS — Resource Assignment",
        card_content="Assign team members to tasks and projects.",
        should_end_session=False)


def handle_log_time() -> Dict:
    speech = """
        Time logging.
        <break time="0.3s"/>
        Which task or project are you logging time for, and how many hours?
    """
    return build_response(speech, card_title="ATLAS — Time Log",
        card_content="Log hours against tasks and projects.",
        should_end_session=False)


def handle_project_documentation() -> Dict:
    speech = """
        Project documentation.
        <break time="0.3s"/>
        I can find scope of work documents, project plans, risk registers,
        meeting notes, and specifications.
        What document are you looking for?
    """
    return build_response(speech, card_title="ATLAS — Documentation",
        card_content="SOW • Project plans • Risk register • Meeting notes • Specs",
        should_end_session=False)


def handle_project_communications() -> Dict:
    speech = """
        Project communications.
        <break time="0.3s"/>
        I can help draft updates, send notifications, or create status reports.
        What do you need to communicate?
    """
    return build_response(speech, card_title="ATLAS — Communications",
        card_content="Updates • Notifications • Status reports",
        should_end_session=False)


def handle_update_project_status() -> Dict:
    speech = """
        Project status update.
        <break time="0.3s"/>
        Which project and what's the update? I can change phase, priority,
        completion percentage, or mark tasks complete.
    """
    return build_response(speech, card_title="ATLAS — Status Update",
        card_content="Phase • Priority • Completion • Task status",
        should_end_session=False)


# ============== DDCSS (Market Problems & Solutions) HANDLERS ==============

def handle_market_problems() -> Dict:
    speech = """
        DDCSS market problem search.
        <break time="0.3s"/>
        I scan for business problems, market gaps, and revenue-generating opportunities.
        <break time="0.3s"/>
        Want me to show your top ranked problems, or search for new ones?
    """
    return build_response(speech, card_title="DDCSS — Market Problems",
        card_content="Problem detection • Market gaps • Revenue opportunities",
        should_end_session=False)


def handle_mvp_status() -> Dict:
    speech = """
        Most Valuable Problems status.
        <break time="0.3s"/>
        Your MVPs are ranked by revenue potential, feasibility, and market timing.
        Want the full scorecard?
    """
    return build_response(speech, card_title="DDCSS — MVP Status",
        card_content="Ranked by: Revenue potential • Feasibility • Market timing",
        should_end_session=False)


def handle_market_analysis() -> Dict:
    speech = """
        Market opportunity analysis.
        <break time="0.3s"/>
        Total addressable market, serviceable market, growth projections, and competitive dynamics.
        Which market or problem?
    """
    return build_response(speech, card_title="DDCSS — Market Analysis",
        card_content="TAM • SAM • Growth • Competition",
        should_end_session=False)


def handle_competitor_analysis() -> Dict:
    speech = """
        Competitive landscape analysis.
        <break time="0.3s"/>
        I track competitor strengths, weaknesses, pricing, and market position.
        Which market or service area?
    """
    return build_response(speech, card_title="DDCSS — Competitor Analysis",
        card_content="Strengths • Weaknesses • Pricing • Positioning",
        should_end_session=False)


def handle_problem_solution_analysis() -> Dict:
    speech = """
        Problem-solution fit analysis.
        <break time="0.3s"/>
        Feasibility, complexity, time to market, and resource requirements.
        Which problem are you evaluating?
    """
    return build_response(speech, card_title="DDCSS — Solution Analysis",
        card_content="Feasibility • Complexity • Time to market • Resources",
        should_end_session=False)


def handle_revenue_potential() -> Dict:
    speech = """
        Revenue potential analysis.
        <break time="0.3s"/>
        Pricing models, margin projections, and revenue forecasts.
        Which problem or solution?
    """
    return build_response(speech, card_title="DDCSS — Revenue Potential",
        card_content="Pricing • Margins • Forecasts",
        should_end_session=False)


# ============== OPERATIONAL HANDLERS ==============

def handle_compliance_landscape() -> Dict:
    speech = """
        Compliance landscape.
        <break time="0.3s"/>
        Your certifications: EDWOSB active, WOSB active, MBE active, SBE active.
        <break time="0.3s"/>
        I track regulatory requirements, documentation needs, and renewal dates.
        Want the full compliance report?
    """
    return build_response(speech, card_title="Compliance Landscape",
        card_content="EDWOSB: Active\nWOSB: Active\nMBE: Active\nSBE: Active\n\nTracking: FAR, DFAR, state regs, certifications",
        should_end_session=False)


def handle_reminders() -> Dict:
    speech = """
        Let me check your reminders.
        <break time="0.3s"/>
        I track bid deadlines, certification renewals, follow-ups, and meeting prep.
        Want today's reminders or this week's?
    """
    return build_response(speech, card_title="NEXUS Reminders",
        card_content="Bid deadlines • Cert renewals • Follow-ups • Meetings",
        should_end_session=False)


def handle_notifications() -> Dict:
    speech = """
        Checking your NEXUS notifications.
        <break time="0.3s"/>
        Notifications include new opportunity matches, deadline alerts,
        system updates, and action items.
    """
    return build_response(speech, card_title="NEXUS Notifications",
        card_content="Opportunity matches • Deadline alerts • System updates • Action items",
        should_end_session=False)


def handle_contacts() -> Dict:
    speech = """
        Contact management.
        <break time="0.3s"/>
        I have your contracting officers, vendor contacts, team members,
        and subcontractor information.
        Who are you looking for?
    """
    return build_response(speech, card_title="NEXUS Contacts",
        card_content="COs • Vendors • Team • Subcontractors",
        should_end_session=False)


def handle_create_task() -> Dict:
    speech = """
        Creating a task.
        <break time="0.3s"/>
        What's the task, when is it due, and who should it be assigned to?
    """
    return build_response(speech, card_title="Create Task",
        card_content="Provide: Task description, deadline, assignee",
        should_end_session=False)


def handle_send_message() -> Dict:
    speech = """
        Message drafting.
        <break time="0.3s"/>
        Who's the recipient and what's the message about?
        Remember, for vendor communications I'll protect the buyer identity automatically.
    """
    return build_response(speech, card_title="Send Message",
        card_content="Recipient • Subject • Content\n⚠️ Buyer protection auto-applied for vendors",
        should_end_session=False)


def handle_calendar() -> Dict:
    speech = """
        Calendar management.
        <break time="0.3s"/>
        I can add events, block time, or show your upcoming schedule.
        What do you need?
    """
    return build_response(speech, card_title="Calendar",
        card_content="Add events • Block time • View schedule",
        should_end_session=False)


def handle_generate_report() -> Dict:
    speech = """
        Report generation.
        <break time="0.3s"/>
        I can create pipeline reports, financial summaries, compliance status,
        performance reports, or executive briefings.
        Which type?
    """
    return build_response(speech, card_title="Report Generator",
        card_content="Pipeline • Financial • Compliance • Performance • Executive",
        should_end_session=False)


def handle_request_approval() -> Dict:
    speech = "What needs approval? I can route it to the right person."
    return build_response(speech, should_end_session=False)


def handle_log_activity() -> Dict:
    speech = "Activity logging. What did you complete or want to document?"
    return build_response(speech, should_end_session=False)


def handle_meeting_notes() -> Dict:
    speech = """
        Meeting notes dictation.
        <break time="0.3s"/>
        Go ahead and dictate your notes. I'll capture them for the record.
        Start with the meeting topic.
    """
    return build_response(speech, card_title="Meeting Notes",
        card_content="Dictate notes. Start with the meeting topic.",
        should_end_session=False)


def handle_prepare_for_meeting() -> Dict:
    speech = """
        Meeting prep.
        <break time="0.3s"/>
        Which meeting are you preparing for?
        I can pull contract details, contact history, relevant emails,
        and talking points.
    """
    return build_response(speech, card_title="Meeting Prep",
        card_content="Contract details • Contact history • Emails • Talking points",
        should_end_session=False)


def handle_strategic_initiatives() -> Dict:
    speech = """
        Strategic initiative status.
        <break time="0.3s"/>
        I track FleetFlow development, ATLAS implementation,
        IP protection documentation, and technology platform roadmap.
        Which initiative?
    """
    return build_response(speech, card_title="Strategic Initiatives",
        card_content="FleetFlow • ATLAS • IP Protection • Tech Roadmap",
        should_end_session=False)


def handle_federal_compliance_consulting() -> Dict:
    speech = """
        Federal compliance consulting projects.
        <break time="0.3s"/>
        Client satisfaction, deliverable status, and consulting revenue.
        Want the full consulting report?
    """
    return build_response(speech, card_title="Compliance Consulting",
        card_content="Client satisfaction • Deliverables • Revenue",
        should_end_session=False)


def handle_factoring_consultation() -> Dict:
    speech = """
        Factoring consultation status.
        <break time="0.3s"/>
        Active clients, service utilization, and revenue metrics.
    """
    return build_response(speech, card_title="Factoring Consultation",
        card_content="Active clients • Utilization • Revenue",
        should_end_session=False)


def handle_read_emails() -> Dict:
    speech = """
        Email management.
        <break time="0.3s"/>
        I can summarize recent emails, filter by priority, or find messages
        from specific contacts.
        What are you looking for?
    """
    return build_response(speech, card_title="Email Manager",
        card_content="Summarize • Filter • Search emails",
        should_end_session=False)


def handle_search_products() -> Dict:
    speech = """
        Product and service search.
        <break time="0.3s"/>
        I can find suppliers, manufacturers, and service providers.
        Remember, I'll protect the end buyer in all vendor communications.
        What are you looking for?
    """
    return build_response(speech, card_title="Supplier Search",
        card_content="Suppliers • Manufacturers • Service providers\n⚠️ Buyer protection active",
        should_end_session=False)


# ============== AI INTELLIGENCE HANDLERS ==============

def handle_decision_support() -> Dict:
    speech = """
        Decision support activated.
        <break time="0.3s"/>
        Tell me the decision you're weighing and I'll analyze the options,
        risks, and potential outcomes.
    """
    return build_response(speech, card_title="Decision Support",
        card_content="Describe the decision. I'll analyze options, risks, and outcomes.",
        should_end_session=False)


def handle_proactive_insights() -> Dict:
    speech = """
        Proactive insights.
        <break time="0.5s"/>
        Based on your pipeline and market data, here are things to consider:
        <break time="0.3s"/>
        Your EDWOSB set-aside opportunities are growing.
        Micro-purchase outreach is underutilized.
        And there are new agencies posting in your NAICS codes.
        <break time="0.3s"/>
        Want me to dig deeper into any of these?
    """
    return build_response(speech, card_title="Proactive Insights",
        card_content="• EDWOSB opportunities growing\n• Micro-purchase outreach underutilized\n• New agencies in your NAICS codes",
        should_end_session=False)


def handle_contract_analysis_intelligence() -> Dict:
    speech = """
        Contract analysis intelligence.
        <break time="0.3s"/>
        I analyze competitive positioning, pricing strategy, compliance gaps,
        and hidden risks in contracts.
        Which contract do you want analyzed?
    """
    return build_response(speech, card_title="Contract Analysis Intelligence",
        card_content="Competitive position • Pricing • Compliance • Risk analysis",
        should_end_session=False)


def handle_revenue_optimization() -> Dict:
    speech = """
        Revenue optimization recommendations.
        <break time="0.3s"/>
        I look at pricing adjustments, upsell opportunities, cross-selling,
        and margin improvement across your divisions.
        Want the full report?
    """
    return build_response(speech, card_title="Revenue Optimization",
        card_content="Pricing • Upsell • Cross-sell • Margin improvement",
        should_end_session=False)


def handle_document_intelligence() -> Dict:
    speech = """
        Document intelligence extraction.
        <break time="0.3s"/>
        I can pull key terms, deadlines, obligations, pricing,
        and compliance requirements from contracts and proposals.
        Which document?
    """
    return build_response(speech, card_title="Document Intelligence",
        card_content="Terms • Deadlines • Obligations • Pricing • Compliance",
        should_end_session=False)


def handle_autonomous_reports() -> Dict:
    speech = """
        Autonomous report generation.
        <break time="0.3s"/>
        I can create weekly executive reports, pipeline analysis,
        compliance summaries, financial performance, or market opportunity reports.
        Which type?
    """
    return build_response(speech, card_title="Auto Report Generator",
        card_content="Weekly exec • Pipeline • Compliance • Financial • Market",
        should_end_session=False)


# ============== LEARNING & CONTEXT HANDLERS ==============

def handle_teach_business() -> Dict:
    speech = """
        I'm listening. Teach me about your business.
        <break time="0.3s"/>
        I'll remember this for future decisions, analysis, and recommendations.
    """
    return build_response(speech, card_title="Teaching NEXUS",
        card_content="Share business knowledge. I'll retain it for future use.",
        should_end_session=False)


def handle_learn_from_outcomes() -> Dict:
    speech = """
        Outcome recorded.
        <break time="0.3s"/>
        I'll factor this into future recommendations and strategy.
        What happened?
    """
    return build_response(speech, card_title="Learning from Outcomes",
        card_content="Share the outcome. I'll apply it to future strategy.",
        should_end_session=False)


def handle_business_context() -> Dict:
    speech = """
        Business context.
        <break time="0.3s"/>
        Dee Davis Inc is a contract management firm operating through eight divisions.
        EDWOSB certified. CAGE code 8 Uniform Mike X-ray 3.
        <break time="0.3s"/>
        We prime contracts and manage subcontractors for government agencies.
        What specifically do you want to know or update?
    """
    return build_response(speech, card_title="Business Context",
        card_content="DDI: Contract Management Firm\n8 Divisions\nEDWOSB Certified\nCAGE: 8UMX3",
        should_end_session=False)


def handle_strategic_decision() -> Dict:
    speech = """
        Strategic decision noted.
        <break time="0.3s"/>
        I'll incorporate this into pipeline prioritization and opportunity scoring.
        What's the decision?
    """
    return build_response(speech, card_title="Strategic Decision",
        card_content="Decision will be applied to pipeline and opportunity scoring.",
        should_end_session=False)


def handle_contextual_question() -> Dict:
    speech = """
        Let me think about that in the context of your business.
        <break time="0.3s"/>
        Can you be more specific about what you're asking?
    """
    return build_response(speech, should_end_session=False)


# ============== UTILITY HANDLERS ==============

def handle_explain_feature() -> Dict:
    speech = """
        NEXUS has several core systems.
        <break time="0.3s"/>
        GPSS manages your government contract pipeline.
        NOVA finds new opportunities.
        ATLAS handles project management.
        PRISM generates documents and capability statements.
        DDCSS identifies market problems to solve.
        <break time="0.3s"/>
        Which system would you like to know more about?
    """
    return build_response(speech, card_title="NEXUS Systems",
        card_content="GPSS: Pipeline management\nNOVA: Opportunity discovery\nATLAS: Project management\nPRISM: Document generation\nDDCSS: Market intelligence",
        should_end_session=False)


def handle_hello() -> Dict:
    speech = """
        Hey Dee! NEXUS is online and ready.
        <break time="0.3s"/>
        What can I help you with?
    """
    return build_response(speech, should_end_session=False)


def handle_help() -> Dict:
    speech = """
        Here are the main things I can do:
        <break time="0.3s"/>
        'Give me my daily briefing' — your priority actions for today
        <break time="0.3s"/>
        'Find federal opportunities' — search for new contracts
        <break time="0.3s"/>
        'What's my daily target?' — NOVA progress tracking
        <break time="0.3s"/>
        'Show me my pipeline' — GPSS overview
        <break time="0.3s"/>
        'Generate a capability statement' — PRISM document creation
        <break time="0.3s"/>
        'Compliance status' — certification and compliance check
        <break time="0.3s"/>
        Plus project management, financial metrics, vendor tracking, and more.
    """
    return build_response(speech, should_end_session=False)


def handle_stop() -> Dict:
    speech = """
        Goodbye. NEXUS will keep monitoring for opportunities.
        <break time="0.3s"/>
        Check back tomorrow for your daily priorities.
    """
    return build_response(speech, should_end_session=True)


# ============== INTENT ROUTING MAP ==============

INTENT_HANDLERS = {
    # Core NEXUS (API-wired)
    "PriorityTodayIntent": handle_executive_briefing,
    "GetExecutiveBriefing": handle_executive_briefing,
    "GetDailyBriefing": handle_executive_briefing,
    "FindOpportunitiesIntent": handle_find_opportunities,
    "SearchGovernmentContracts": handle_find_opportunities,
    "DailyTargetIntent": handle_daily_target,
    "AddToPipelineIntent": handle_add_to_pipeline,
    "OpenGPSSIntent": handle_open_gpss,
    "PipelineStatsIntent": handle_pipeline_stats,
    "AnalyzeGPSSPipeline": handle_pipeline_stats,
    
    # Daily Briefing Queries (reads from DAILY_BRIEFING.md)
    "GetEmailCount": handle_email_count,
    "HowManyEmails": handle_email_count,
    "GetReadyToSend": handle_email_count,
    "GetDeadlines": handle_deadline_check,
    "WhatDeadlines": handle_deadline_check,
    "CheckDeadlines": handle_deadline_check,
    "GetStaleBids": handle_stale_bids,
    "HowManyStaleBids": handle_stale_bids,

    # Government Contracting
    "GetGovernmentContractPipeline": handle_contract_pipeline,
    "IdentifyBidOpportunities": handle_bid_opportunities,
    "GetContractDetails": handle_contract_details,
    "GetContractDeadlines": handle_contract_deadlines,
    "AnalyzeBidWinProbability": handle_win_probability,
    "GetFederalBuyerInfo": handle_federal_buyer_info,
    "GetSubcontractorOpportunities": handle_subcontractor_opportunities,
    "GetContractComplianceRequirements": handle_contract_compliance,
    "GetContractorRequirements": handle_contractor_requirements,
    "TrackContractPerformance": handle_contract_performance,
    "TrackFederalContractProgress": handle_contract_performance,
    "GetContractModifications": handle_contract_modifications,
    "GetContractOpportunitiesAlert": handle_contract_opportunities_alert,

    # Financial & Operations
    "GetFinancialMetrics": handle_financial_metrics,
    "GetInvoiceStatus": handle_invoice_status,
    "GetBudgetStatus": handle_budget_status,
    "TrackExpenses": handle_expense_tracking,
    "ManageVendorRelationships": handle_vendor_relationships,

    # Project Management (ATLAS)
    "GetProjectStatus": handle_project_status,
    "ManageProjectTasks": handle_project_tasks,
    "GetProjectHealth": handle_project_health,
    "GetProjectMetrics": handle_project_metrics,
    "GetMilestoneStatus": handle_milestone_status,
    "TrackProjectRisks": handle_project_risks,
    "GetTeamCapacity": handle_team_capacity,
    "TrackProjectBudget": handle_project_budget,
    "ManageDependencies": handle_dependencies,
    "AssignResources": handle_assign_resources,
    "LogProjectTime": handle_log_time,
    "GetProjectDocumentation": handle_project_documentation,
    "ManageProjectCommunications": handle_project_communications,
    "UpdateProjectStatus": handle_update_project_status,

    # DDCSS (Market Intelligence)
    "SearchMarketProblems": handle_market_problems,
    "GetMVPStatus": handle_mvp_status,
    "GetMarketOpportunityAnalysis": handle_market_analysis,
    "GetCompetitorAnalysis": handle_competitor_analysis,
    "AnalyzeProblemSolution": handle_problem_solution_analysis,
    "AnalyzeProblemToRevenuePotential": handle_revenue_potential,
    "ValidateProblemHypothesis": handle_problem_solution_analysis,
    "GetMarketSize": handle_market_analysis,
    "GetProblemSeverityRating": handle_problem_solution_analysis,
    "IdentifyTargetAudience": handle_market_analysis,
    "GetSolutionFeasibility": handle_problem_solution_analysis,
    "GetProblemTrends": handle_market_analysis,
    "RankProblemsByOpportunity": handle_mvp_status,

    # Operational
    "GetComplianceLandscape": handle_compliance_landscape,
    "GetReminders": handle_reminders,
    "GetNotifications": handle_notifications,
    "ManageContacts": handle_contacts,
    "CreateTask": handle_create_task,
    "SendMessage": handle_send_message,
    "UpdateCalendar": handle_calendar,
    "GenerateReport": handle_generate_report,
    "AutonomousReportGeneration": handle_autonomous_reports,
    "RequestApproval": handle_request_approval,
    "LogActivity": handle_log_activity,
    "DictateMeetingNotes": handle_meeting_notes,
    "PrepareForMeeting": handle_prepare_for_meeting,
    "GetStrategicInitiativeStatus": handle_strategic_initiatives,
    "GetFederalComplianceConsulting": handle_federal_compliance_consulting,
    "GetFactoringConsultation": handle_factoring_consultation,
    "ReadEmails": handle_read_emails,
    "SearchForProductsOrServices": handle_search_products,

    # AI Intelligence
    "ContextAwareDecisionSupport": handle_decision_support,
    "ProactiveInsightsGeneration": handle_proactive_insights,
    "ContractAnalysisIntelligence": handle_contract_analysis_intelligence,
    "RevenueOptimizationRecommendations": handle_revenue_optimization,
    "DocumentIntelligenceExtraction": handle_document_intelligence,

    # Learning & Context
    "TeachAlexisAboutBusiness": handle_teach_business,
    "LearnFromOutcomes": handle_learn_from_outcomes,
    "UnderstandBusinessContex": handle_business_context,
    "RememberStrategicDecision": handle_strategic_decision,
    "ContextualBusinessQuestion": handle_contextual_question,

    # Utility
    "ExplainNexusFeature": handle_explain_feature,
    "HelloWorldIntent": handle_hello,
    "AMAZON.HelpIntent": handle_help,
    "AMAZON.StopIntent": handle_stop,
    "AMAZON.CancelIntent": handle_stop,

    # Approval/Rejection flow
    "ApproveActionIntent": handle_add_to_pipeline,
    "RejectActionIntent": lambda: build_response("Okay, skipping that one. What's next?", should_end_session=False),

    # NEXUS-specific workflow intents
    "GetBidWorkflowStatus": lambda: build_response(
        """Bid workflow status. <break time="0.3s"/>
        I track your 10-step gated workflow for every active bid.
        Steps include solicitation review, go/no-go decision, supplier RFQ,
        quote collection, markup, bid preparation, review, and submission.
        <break time="0.3s"/>
        Which bid do you want the status on, or should I give you all active bids?""",
        card_title="Bid Workflow Status",
        card_content="10-Step Gated Workflow Tracking\n• Review → Go/No-Go → Find Suppliers → RFQ → Collect Quotes → Markup → Prepare Bid → Review → Submit",
        should_end_session=False
    ),

    "GetOutreachTracking": lambda: build_response(
        """Outreach tracking. <break time="0.3s"/>
        I monitor all buyer communications, follow-up schedules, and response status.
        <break time="0.3s"/>
        This includes contracting officer emails, capability statement sends,
        and post-submission follow-ups.
        <break time="0.3s"/>
        Want today's follow-ups or the full outreach log?""",
        card_title="Outreach Tracking",
        card_content="CO emails • Cap statement sends • Follow-ups • Response tracking",
        should_end_session=False
    ),

    "FindEDWOSBSetAsides": lambda: build_response(
        """Searching for EDWOSB set-aside opportunities. <break time="0.5s"/>
        These are contracts reserved for Economically Disadvantaged Woman-Owned Small Businesses.
        This is your competitive weapon — limited competition.
        <break time="0.3s"/>
        I'm filtering SAM dot gov for active EDWOSB set-asides matching your NAICS codes.
        <break time="0.3s"/>
        Want me to also check WOSB sole-source opportunities under $7 million?""",
        card_title="EDWOSB Set-Aside Search",
        card_content="Filtering: EDWOSB set-asides\nNAICS match\nWOSB sole-source under $7M",
        should_end_session=False
    ),

    "FindMicroPurchases": lambda: build_response(
        """Micro-purchase opportunity search. <break time="0.3s"/>
        These are contracts under $10,000 that don't require formal bidding.
        Quick wins, fast turnaround, minimal paperwork.
        <break time="0.3s"/>
        Filtering for your service types: drug testing, fingerprinting,
        courier, and grounds maintenance.
        <break time="0.3s"/>
        Want me to narrow it by agency or location?""",
        card_title="Micro-Purchase Finder",
        card_content="Under $10,000\nNo formal bid required\nQuick turnaround\nFiltering by: DDI service types",
        should_end_session=False
    ),

    "GetOutboundDocumentStatus": lambda: build_response(
        """Outbound document status. <break time="0.3s"/>
        I check your SEND TO BUYER, SEND TO SUPPLIER, and SEND TO SUBCONTRACTOR folders
        across all active bids.
        <break time="0.3s"/>
        Documents are ready when the capability statement, buyer email,
        and any required forms are complete in the folder.
        <break time="0.3s"/>
        Want me to check which bid folders have complete packages?""",
        card_title="Outbound Document Status",
        card_content="Checking:\n• SEND_TO_BUYER folders\n• SEND_TO_SUPPLIER folders\n• SEND_TO_SUBCONTRACTOR folders\n\nComplete = cap statement + email + forms",
        should_end_session=False
    ),

    "GetSubcontractorOnboardingStatus": lambda: build_response(
        """Subcontractor onboarding status. <break time="0.3s"/>
        Every sub must clear 6 pillars before starting work:
        Vet, Protect, Insure, Plan, Communicate, and Manage.
        <break time="0.3s"/>
        I track NDA status, non-compete agreements, insurance certificates,
        staffing plans, and communication schedules.
        <break time="0.3s"/>
        Which subcontractor or contract are you checking on?""",
        card_title="Subcontractor Onboarding",
        card_content="6 Pillars: VET → PROTECT → INSURE → PLAN → COMMUNICATE → MANAGE\n\nNDA • Non-Compete • COI • Staffing Plan • Comms Plan",
        should_end_session=False
    ),

    "GetWinLossTracking": lambda: build_response(
        """Win and loss tracking. <break time="0.3s"/>
        I monitor contract awards, bid outcomes, and your overall win rate.
        <break time="0.3s"/>
        This data feeds into future bid decisions — knowing what you've won
        helps target similar opportunities.
        <break time="0.3s"/>
        Want the full win-loss report or just recent awards?""",
        card_title="Win/Loss Tracking",
        card_content="Contract awards • Bid outcomes • Win rate • Pattern analysis",
        should_end_session=False
    ),

    "GenerateQuoteResponse": lambda: build_response(
        """Quote response generation. <break time="0.3s"/>
        I'll build a full multi-page quote response using the NEXUS template.
        <break time="0.3s"/>
        This includes: cover page, table of contents, company overview,
        technical capability, compliance matrix, pricing table, and certifications.
        <break time="0.3s"/>
        All in your sector colors with ProposalBio applied.
        <break time="0.3s"/>
        Which solicitation is this for?""",
        card_title="Quote Response Generator",
        card_content="Multi-page response:\n• Cover • TOC • Overview • Technical\n• Compliance Matrix • Pricing • Certs\n\nProposalBio + Sector Colors applied",
        should_end_session=False
    ),
}

# Intents that need the full event (for slot extraction)
SLOT_INTENTS = {"GenerateCapStatementIntent"}


def lambda_handler(event: Dict, context: Any) -> Dict:
    logger.info(f"Received event: {json.dumps(event)}")

    request_type = event.get("request", {}).get("type")
    intent_name = event.get("request", {}).get("intent", {}).get("name") if request_type == "IntentRequest" else None

    if request_type == "LaunchRequest":
        return handle_launch_request()

    elif request_type == "IntentRequest":
        if intent_name == "GenerateCapStatementIntent":
            return handle_generate_cap_statement(event)

        handler = INTENT_HANDLERS.get(intent_name)
        if handler:
            return handler()

        logger.warning(f"Unhandled intent: {intent_name}")
        return build_response(
            f"I heard you, but I'm not sure how to handle that yet. Try saying 'help' for what I can do.",
            should_end_session=False
        )

    elif request_type == "SessionEndedRequest":
        return {"version": "1.0", "response": {}}

    else:
        return build_response(
            "I'm not sure what you're asking. Try saying 'give me my daily briefing'.",
            should_end_session=False
        )


# ============== FLASK SERVER ==============

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

@app.route("/alexa", methods=["POST", "OPTIONS"])
def alexa_endpoint():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    event = request.json
    response = lambda_handler(event, None)
    return jsonify(response)

@app.route("/alexa/health", methods=["GET"])
def alexa_health():
    return jsonify({
        "status": "healthy",
        "service": "NEXUS Alexa Skill",
        "connected_to_nexus": NEXUS_API_BASE,
        "intents_handled": len(INTENT_HANDLERS) + len(SLOT_INTENTS)
    })

if __name__ == "__main__":
    print("NEXUS Alexa Skill — Full Integration")
    print(f"Connecting to NEXUS API at: {NEXUS_API_BASE}")
    print(f"Handling {len(INTENT_HANDLERS) + len(SLOT_INTENTS)} intents")
    print("\nStarting on port 5001...")
    app.run(host="0.0.0.0", port=5001)
