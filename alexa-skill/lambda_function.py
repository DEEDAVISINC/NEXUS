"""
Alexis Nexus - Comprehensive Voice-Enabled AI Executive Assistant for DEE DAVIS INC
AWS Lambda function handling 86 Alexa intents across all business systems

Intent Categories:
  - Core System (GetProjectStatus, DictateMeetingNotes, GetComplianceLandscape, GetInvoiceStatus, GetFinancialMetrics)
  - Executive Assistant (ExplainNexusFeature, GetReminders, ManageContacts, CreateTask, GetNotifications, SendMessage, UpdateCalendar)
  - Operations (GenerateReport, TrackExpenses, RequestApproval, LogActivity, ManageVendorRelationships, GetBudgetStatus)
  - Government Contracting (GPSS - 19 intents for federal opportunities, contracts, compliance, bidding)
  - Project Management (ATLAS PM - 17 intents for tasks, resources, budget, risks, milestones)
  - Market Intelligence (DDCSS - 14 intents for problem discovery, MVP validation, market analysis)
  - Division Operations (GetFederalComplianceConsulting, GetFactoringConsultation)
  - Strategic Intelligence (GetExecutiveBriefing, GetContractOpportunitiesAlert, GetStrategicInitiativeStatus, PrepareForMeeting, GetGovernmentContractPipeline)
  - AI Learning & Intelligence (10 intents for decision support, insights, learning, document extraction)
  - Grants (SearchGrantOpportunities)
"""

import json
import logging
import os
import time
import urllib.error
import urllib.request

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

NEXUS_API_URL = os.environ.get("NEXUS_API_URL", "https://nexus-backend.onrender.com")
ALEXA_SKILL_ID = os.environ.get("ALEXA_SKILL_ID", "")
ALEXIS_DDB_TABLE = os.environ.get("ALEXIS_DDB_TABLE", "")

_jwt_token = None
_ddb_table = boto3.resource("dynamodb").Table(ALEXIS_DDB_TABLE) if ALEXIS_DDB_TABLE else None


# =============================================================================
# Response & HTTP Helpers
# =============================================================================

def _build_response(text: str, should_end_session: bool = True):
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "PlainText", "text": text},
            "shouldEndSession": should_end_session,
        },
    }


def _post_json(path: str, headers: dict | None = None, body: dict | None = None, timeout: int = 10):
    url = f"{NEXUS_API_URL}{path}"
    payload = json.dumps(body or {}).encode("utf-8")
    merged_headers = {"Content-Type": "application/json"}
    if headers:
        merged_headers.update(headers)

    req = urllib.request.Request(url, data=payload, headers=merged_headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8") or "{}"
            return resp.getcode(), json.loads(raw)
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", "ignore")
        except Exception:
            detail = ""
        return e.code, {"error": detail}
    except Exception as e:
        return 0, {"error": str(e)}


def _get_jwt_token():
    global _jwt_token
    if _jwt_token:
        return _jwt_token

    code, data = _post_json("/auth/alexa", headers={"Alexa-Skill-Id": ALEXA_SKILL_ID})
    if code == 200:
        _jwt_token = data.get("token")
        return _jwt_token
    return None


def _call_nexus_api(command: str):
    """Generic NEXUS API caller - sends command string to backend"""
    token = _get_jwt_token()
    if not token:
        return "Sorry, I couldn't authenticate with NEXUS."

    code, data = _post_json(
        "/alexa/command",
        headers={"Authorization": f"Bearer {token}"},
        body={"command": command, "source": "alexa"},
        timeout=10,
    )
    if code == 200:
        return data.get("response") or "Done."
    return "Sorry, I had trouble connecting to NEXUS."


def _log_event(intent_name: str, slots: dict):
    """Log intent invocations to DynamoDB for learning"""
    if not _ddb_table:
        return
    try:
        _ddb_table.put_item(
            Item={
                "pk": "alexa",
                "sk": str(int(time.time() * 1000)),
                "intent": intent_name,
                "slots": json.dumps({k: (v or {}).get("value") for k, v in (slots or {}).items()}),
            }
        )
    except Exception as e:
        logger.error("DynamoDB log failed: %s", e)


# =============================================================================
# Intent Handler Router
# =============================================================================

def handle_intent(intent_name: str, slots: dict = None) -> str:
    """
    Route all 86 intents to NEXUS backend with appropriate command strings.
    The backend will parse and execute the commands against Airtable/systems.
    """
    
    # Map intent names to NEXUS command strings
    intent_commands = {
        # Core System Intents
        "HelloWorldIntent": "hello",
        "GetProjectStatus": "nexus: system-wide status",
        "DictateMeetingNotes": "meeting notes: dictate",
        "GetComplianceLandscape": "compliance: landscape overview",
        "GetInvoiceStatus": "invoices: status all divisions",
        "GetFinancialMetrics": "financial: metrics dashboard",
        
        # Executive Assistant
        "ExplainNexusFeature": "nexus: explain features",
        "GetReminders": "reminders: list all",
        "ManageContacts": "contacts: manage",
        "CreateTask": "task: create new",
        "GetNotifications": "notifications: show all",
        "SendMessage": "message: send",
        "UpdateCalendar": "calendar: update event",
        "GenerateReport": "report: generate",
        "TrackExpenses": "expenses: track",
        "RequestApproval": "approval: request",
        "LogActivity": "activity: log",
        
        # Vendor & Budget Management
        "ManageVendorRelationships": "vendors: manage relationships",
        "GetBudgetStatus": "budget: status overview",
        
        # GPSS - Government Contracting (19 intents)
        "SearchGovernmentContracts": "gpss: search contracts",
        "GetContractorRequirements": "gpss: contractor requirements",
        "TrackFederalContractProgress": "gpss: track contract progress",
        "AnalyzeGPSSPipeline": "gpss: analyze pipeline",
        "GetContractDetails": "gpss: contract details",
        "IdentifyBidOpportunities": "gpss: identify bid opportunities",
        "GetFederalBuyerInfo": "gpss: federal buyer info",
        "GetContractComplianceRequirements": "gpss: compliance requirements",
        "GetContractDeadlines": "gpss: contract deadlines",
        "AnalyzeBidWinProbability": "gpss: analyze win probability",
        "GetContractModifications": "gpss: contract modifications",
        "TrackContractPerformance": "gpss: track performance",
        "GetSubcontractorOpportunities": "gpss: subcontractor opportunities",
        
        # ATLAS PM - Project Management (17 intents)
        "ManageProjectTasks": "atlas: manage tasks",
        "UpdateProjectStatus": "atlas: update status",
        "GetProjectMetrics": "atlas: project metrics",
        "AssignResources": "atlas: assign resources",
        "TrackProjectBudget": "atlas: track budget",
        "ManageDependencies": "atlas: manage dependencies",
        "GetMilestoneStatus": "atlas: milestone status",
        "TrackProjectRisks": "atlas: track risks",
        "GetTeamCapacity": "atlas: team capacity",
        "LogProjectTime": "atlas: log time",
        "GetProjectDocumentation": "atlas: project documentation",
        "ManageProjectCommunications": "atlas: project communications",
        "GetProjectHealth": "atlas: project health",
        
        # DDCSS - Market Intelligence (14 intents)
        "SearchMarketProblems": "ddcss: search market problems",
        "GetMVPStatus": "ddcss: mvp status",
        "AnalyzeProblemSolution": "ddcss: analyze problem solution",
        "GetMarketOpportunityAnalysis": "ddcss: market opportunity analysis",
        "ValidateProblemHypothesis": "ddcss: validate problem hypothesis",
        "GetMarketSize": "ddcss: market size",
        "GetCompetitorAnalysis": "ddcss: competitor analysis",
        "GetProblemSeverityRating": "ddcss: problem severity rating",
        "IdentifyTargetAudience": "ddcss: identify target audience",
        "GetSolutionFeasibility": "ddcss: solution feasibility",
        "GetProblemTrends": "ddcss: problem trends",
        "AnalyzeProblemToRevenuePotential": "ddcss: revenue potential",
        "RankProblemsByOpportunity": "ddcss: rank problems by opportunity",
        
        # Division Operations
        "GetFederalComplianceConsulting": "division: federal compliance consulting status",
        "GetFactoringConsultation": "division: factoring consultation status",
        
        # Strategic Intelligence (5 intents)
        "GetExecutiveBriefing": "executive: daily briefing",
        "GetContractOpportunitiesAlert": "executive: contract opportunities alert",
        "GetStrategicInitiativeStatus": "executive: strategic initiative status",
        "PrepareForMeeting": "executive: prepare for meeting",
        "GetGovernmentContractPipeline": "executive: government contract pipeline",
        
        # Email & Communications
        "ReadEmails": "email: read and summarize",
        
        # AI Learning & Intelligence (10 intents)
        "ContextAwareDecisionSupport": "ai: decision support",
        "AutonomousReportGeneration": "ai: generate report",
        "ProactiveInsightsGeneration": "ai: proactive insights",
        "ContractAnalysisIntelligence": "ai: contract analysis",
        "RevenueOptimizationRecommendations": "ai: revenue optimization",
        "DocumentIntelligenceExtraction": "ai: document extraction",
        "TeachAlexisAboutBusiness": "ai: learn business context",
        "SearchForProductsOrServices": "ai: search products services",
        "ContextualBusinessQuestion": "ai: contextual business question",
        "LearnFromOutcomes": "ai: learn from outcomes",
        "UnderstandBusinessContex": "ai: understand business context",
        "RememberStrategicDecision": "ai: remember strategic decision",
        "ApplyBusinessKnowledge": "ai: apply business knowledge",
        
        # Grants
        "SearchGrantOpportunities": "grants: search opportunities",
    }
    
    # Get the command for this intent
    command = intent_commands.get(intent_name)
    
    if command:
        return _call_nexus_api(command)
    else:
        # Fallback for unmapped intents
        return f"I recognized the {intent_name} intent, but it's not fully configured yet. Please contact support."


def handle_help() -> str:
    return (
        "I'm Alexis Nexus, your comprehensive executive assistant. "
        "I can help with government contracts, project management, market intelligence, "
        "compliance tracking, financial metrics, meeting notes, strategic briefings, and much more. "
        "Try asking: give me my executive briefing, show me contract opportunities, "
        "what's my project status, or search for market problems."
    )


# =============================================================================
# Main Lambda Handler
# =============================================================================

def lambda_handler(event, context):
    req = event.get("request") or {}
    req_type = req.get("type")

    if req_type == "LaunchRequest":
        return _build_response(
            "Welcome to Alexis Nexus, your comprehensive executive assistant for DEE DAVIS INC. "
            "I can help with government contracts, projects, compliance, financials, and strategic intelligence. "
            "What would you like to know?",
            should_end_session=False
        )

    if req_type == "IntentRequest":
        intent = req.get("intent") or {}
        intent_name = intent.get("name", "")
        slots = intent.get("slots") or {}
        
        # Log every intent invocation for learning
        _log_event(intent_name, slots)

        # Amazon built-in intents
        if intent_name == "AMAZON.HelpIntent":
            return _build_response(handle_help(), should_end_session=False)

        if intent_name in ("AMAZON.StopIntent", "AMAZON.CancelIntent"):
            return _build_response("Goodbye. I'm here whenever you need me.")

        if intent_name == "AMAZON.FallbackIntent":
            return _build_response(
                "I didn't quite catch that. Try asking about contracts, projects, compliance, or financial metrics.",
                should_end_session=False
            )

        # Handle all custom intents through the router
        response_text = handle_intent(intent_name, slots)
        return _build_response(response_text)

    if req_type == "SessionEndedRequest":
        return _build_response("Session ended. Goodbye.")

    return _build_response("OK.")
