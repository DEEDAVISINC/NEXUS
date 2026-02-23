"""
GovCon AI Prompt Library — Integrated into NEXUS
Source: Govcon Giants Federal Contracting AI Prompt Library (Dec 2025)

70 prompts across 8 categories, mapped to NEXUS systems for contextual use
during proposal writing, capture planning, post-award ops, and debriefs.
"""

PROMPT_LIBRARY = {

    # ─────────────────────────────────────────────────────────────────
    # PAST PERFORMANCE — Used by GPSS Evaluator & Proposal Builder
    # ─────────────────────────────────────────────────────────────────
    "past_performance": {
        "system": "GPSS",
        "context": "proposal_writing",
        "description": "Transform and strengthen past performance narratives for federal proposals",
        "prompts": [
            {
                "id": "pp-01",
                "name": "Problem-Solution-Results Format",
                "prompt": "Transform this past performance into a problem-solution-results format that demonstrates our ability to overcome challenges and deliver measurable outcomes for the government client.",
                "use_when": "Writing or rewriting past performance narratives",
                "input_needed": "Raw past performance text",
            },
            {
                "id": "pp-02",
                "name": "Federal Evaluator Relevancy Score",
                "prompt": "Act as a federal evaluator reviewing past performance for relevancy. Score this narrative against the solicitation's requirements and explain what strengths to emphasize and what gaps need addressing to achieve a higher confidence rating.",
                "use_when": "Self-scoring before submission",
                "input_needed": "Past performance narrative + solicitation requirements",
            },
            {
                "id": "pp-03",
                "name": "One-Page Summary",
                "prompt": "Condense this lengthy past performance into a compelling one-page summary that captures contract scope, key deliverables, innovations implemented, and quantified benefits to the agency.",
                "use_when": "Past performance is too long or unfocused",
                "input_needed": "Full past performance text",
            },
            {
                "id": "pp-04",
                "name": "Gap Identifier & Metrics Filler",
                "prompt": "Identify gaps in this past performance narrative where metrics, timelines, or customer satisfaction data should be added, then rewrite with those elements incorporated.",
                "use_when": "Past performance feels vague or lacks numbers",
                "input_needed": "Past performance narrative",
            },
            {
                "id": "pp-05",
                "name": "Certifications & Expertise Showcase",
                "prompt": "Rewrite this past performance to showcase our team's relevant certifications, clearances, technical expertise, and lessons learned that apply to the target opportunity.",
                "use_when": "Need to highlight qualifications",
                "input_needed": "Past performance + target opportunity description",
            },
            {
                "id": "pp-06",
                "name": "Active Voice Conversion",
                "prompt": "Convert this past performance from passive voice to active voice, emphasizing our proactive contributions, leadership role, and specific actions that led to mission success.",
                "use_when": "Narrative sounds weak or passive",
                "input_needed": "Past performance text",
            },
            {
                "id": "pp-07",
                "name": "Tailored Relevancy Match",
                "prompt": "Create a tailored version of this past performance that emphasizes similar contract vehicles, comparable dollar values, matching geographical locations, and parallel technical challenges to the opportunity we're pursuing.",
                "use_when": "Adapting existing past performance for a new bid",
                "input_needed": "Past performance + target solicitation details",
            },
            {
                "id": "pp-08",
                "name": "Format Standardizer",
                "prompt": "Review this past performance for consistency in formatting, verb tense, and structure across all project examples, then standardize the presentation to create a polished, professional submission.",
                "use_when": "Multiple past performances need uniform formatting",
                "input_needed": "Multiple past performance narratives",
            },
            {
                "id": "pp-09",
                "name": "Recency & Relevance Assessment",
                "prompt": "Act as a federal evaluator assessing recency and relevance. Determine if this past performance demonstrates current capabilities within the last 3-5 years and involves comparable scope, and recommend which examples to prioritize or replace.",
                "use_when": "Deciding which past performances to include",
                "input_needed": "List of past performances with dates and scope",
            },
            {
                "id": "pp-10",
                "name": "High-Impact Credibility Extraction",
                "prompt": "Extract the most compelling customer testimonial quotes, performance metrics, and award fee scores from this past performance, then reorganize the narrative to lead with these high-impact credibility indicators.",
                "use_when": "Need strongest possible opening",
                "input_needed": "Full past performance with metrics/quotes",
            },
        ]
    },

    # ─────────────────────────────────────────────────────────────────
    # TECHNICAL PROPOSAL REVIEW — Used by GPSS Evaluator
    # ─────────────────────────────────────────────────────────────────
    "technical_proposal": {
        "system": "GPSS",
        "context": "evaluator",
        "description": "Review and strengthen technical proposals before submission",
        "prompts": [
            {
                "id": "tp-01",
                "name": "Compliance Check",
                "prompt": "Review this technical proposal section against the solicitation requirements and all amendments to identify any non-compliant, missing, or incomplete responses that could result in point deductions or disqualification.",
                "use_when": "Final compliance review before submission",
                "input_needed": "Technical proposal + solicitation requirements",
            },
            {
                "id": "tp-02",
                "name": "Federal Evaluator Scoring",
                "prompt": "Act as a federal evaluator scoring this technical proposal. Provide a detailed assessment of strengths, weaknesses, and deficiencies based on the evaluation criteria, then assign a confidence rating with justification.",
                "use_when": "Self-evaluation before submission",
                "input_needed": "Technical proposal + Section M evaluation criteria",
            },
            {
                "id": "tp-03",
                "name": "Prohibited Language Scanner",
                "prompt": "Analyze this technical section for prohibited language including proprietary claims, unsupported assertions, vague commitments, and any statements that could be perceived as non-compliant or unsubstantiated.",
                "use_when": "Cleaning up technical writing",
                "input_needed": "Technical narrative section",
            },
            {
                "id": "tp-04",
                "name": "Active Voice & Strong Verbs",
                "prompt": "Rewrite this technical narrative to replace passive voice, weak verbs, and generic statements with active voice, strong action verbs, and specific, quantifiable commitments that demonstrate capability.",
                "use_when": "Strengthening weak writing",
                "input_needed": "Technical narrative",
            },
            {
                "id": "tp-05",
                "name": "Terminology Alignment",
                "prompt": "Check this proposal for consistent use of government terminology, acronyms, and nomenclature as specified in the solicitation, and flag any deviations or commercial language that should be aligned.",
                "use_when": "Ensuring language matches the RFP",
                "input_needed": "Proposal text + solicitation text",
            },
            {
                "id": "tp-06",
                "name": "PWS Coverage Audit",
                "prompt": "Evaluate whether this technical approach adequately addresses all performance work statement tasks, deliverables, and performance standards, then identify any gaps or areas requiring more detail.",
                "use_when": "Verifying full PWS coverage",
                "input_needed": "Technical approach + PWS",
            },
            {
                "id": "tp-07",
                "name": "Discriminator Finder",
                "prompt": "Act as a federal evaluator looking for discriminators. Compare this technical solution to what a competitor might propose and identify where we need stronger differentiators, innovations, or proof points.",
                "use_when": "Finding competitive advantages",
                "input_needed": "Technical solution narrative",
            },
            {
                "id": "tp-08",
                "name": "Section L Format Compliance",
                "prompt": "Review this proposal for compliance with page limits, font requirements, margin specifications, and formatting instructions across all volumes and attachments as stated in Section L.",
                "use_when": "Final formatting check",
                "input_needed": "Proposal document + Section L instructions",
            },
            {
                "id": "tp-09",
                "name": "Mission Alignment Strengthener",
                "prompt": "Assess whether this technical narrative demonstrates a thorough understanding of the agency's mission, challenges, and objectives, then strengthen the customer focus and mission alignment throughout.",
                "use_when": "Making proposal more customer-focused",
                "input_needed": "Technical narrative + agency mission info",
            },
            {
                "id": "tp-10",
                "name": "Evidence & Proof Point Audit",
                "prompt": "Identify all claims, commitments, and assertions in this technical proposal that lack supporting evidence, then provide recommendations for adding metrics, case studies, certifications, or past performance examples as proof.",
                "use_when": "Backing up claims with evidence",
                "input_needed": "Technical proposal text",
            },
        ]
    },

    # ─────────────────────────────────────────────────────────────────
    # CAPABILITY STATEMENT — Used by Cap Statement Generator
    # ─────────────────────────────────────────────────────────────────
    "capability_statement": {
        "system": "GPSS",
        "context": "cap_statement",
        "description": "Create and improve capability statements for federal audiences",
        "prompts": [
            {
                "id": "cs-01",
                "name": "Federal Cap Statement Builder",
                "prompt": "Create a one-page capability statement for a company with these core competencies, certifications, and past performance highlights, formatted for federal government audiences with clear sections for company overview, core capabilities, differentiators, and contact information.",
                "use_when": "Building a new cap statement from scratch",
                "input_needed": "Company info, competencies, certs, past performance",
            },
            {
                "id": "cs-02",
                "name": "Federal Compliance Review",
                "prompt": "Review this capability statement for compliance with standard federal formatting expectations including NAICS codes, CAGE code, UEI number, certifications, and socioeconomic status, then identify any missing or incorrect elements.",
                "use_when": "Auditing existing cap statement",
                "input_needed": "Capability statement document",
            },
            {
                "id": "cs-03",
                "name": "CO Memorability Assessment",
                "prompt": "Act as a federal contracting officer reviewing capability statements. Evaluate this document for clarity, relevance, and impact, then provide feedback on what makes it memorable versus generic.",
                "use_when": "Testing if cap statement stands out",
                "input_needed": "Capability statement",
            },
            {
                "id": "cs-04",
                "name": "Jargon to Benefits Rewrite",
                "prompt": "Rewrite this capability statement to replace industry jargon and technical language with clear, benefit-focused statements that communicate value to government buyers unfamiliar with our industry.",
                "use_when": "Cap statement is too technical",
                "input_needed": "Capability statement text",
            },
            {
                "id": "cs-05",
                "name": "Agency-Specific Tailoring",
                "prompt": "Analyze this capability statement against the target agency's mission and priorities, then tailor the language, examples, and capabilities to align with their specific needs and pain points.",
                "use_when": "Customizing cap statement for specific agency",
                "input_needed": "Cap statement + target agency info",
            },
            {
                "id": "cs-06",
                "name": "Visual One-Pager Condensation",
                "prompt": "Transform this lengthy company profile into a concise, visually appealing one-page capability statement that highlights our top three differentiators and most relevant contract vehicles or past performance.",
                "use_when": "Condensing too much content",
                "input_needed": "Full company profile",
            },
            {
                "id": "cs-07",
                "name": "Weak Language Eliminator",
                "prompt": "Review this capability statement for weak language such as 'we strive to,' 'we aim to,' or vague claims, then rewrite with confident, specific statements supported by credentials, metrics, or proven results.",
                "use_when": "Strengthening confidence in language",
                "input_needed": "Capability statement text",
            },
            {
                "id": "cs-08",
                "name": "Multi-Audience Versioning",
                "prompt": "Create three versions of this capability statement tailored to different agencies or market segments, adjusting the emphasized capabilities, keywords, and past performance examples for each audience.",
                "use_when": "Need sector-specific versions",
                "input_needed": "Base cap statement + target audiences",
            },
            {
                "id": "cs-09",
                "name": "Value Proposition Strengthener",
                "prompt": "Evaluate whether this capability statement effectively communicates our unique value proposition and competitive advantages, then strengthen the differentiators section with specific proof points that set us apart.",
                "use_when": "Differentiators section feels weak",
                "input_needed": "Capability statement",
            },
            {
                "id": "cs-10",
                "name": "Teaming Partner Pitch",
                "prompt": "Act as a small business seeking teaming partners. Assess whether this capability statement clearly communicates what we bring to a team, our niche expertise, and why a prime contractor should select us over competitors.",
                "use_when": "Using cap statement for teaming outreach",
                "input_needed": "Capability statement",
            },
        ]
    },

    # ─────────────────────────────────────────────────────────────────
    # CAPTURE PLANNING — Used by GPSS Pipeline & Opportunity Scoring
    # ─────────────────────────────────────────────────────────────────
    "capture_planning": {
        "system": "GPSS",
        "context": "capture",
        "description": "Strategic capture planning, competitive analysis, and win theme development",
        "prompts": [
            {
                "id": "cp-01",
                "name": "Win Probability Assessment",
                "prompt": "Analyze this opportunity announcement and create a comprehensive capture assessment that evaluates our win probability based on incumbent status, past performance relevance, technical capability gaps, competitive positioning, and relationship strength with the customer.",
                "use_when": "Initial opportunity assessment",
                "input_needed": "Opportunity announcement + DDI capabilities",
            },
            {
                "id": "cp-02",
                "name": "Agency Pain Point Identifier",
                "prompt": "Act as a federal program manager for this requirement. Identify the agency's top pain points, mission priorities, and hot buttons that should drive our solution design and win themes throughout the capture process.",
                "use_when": "Understanding what the agency really wants",
                "input_needed": "Solicitation + agency background research",
            },
            {
                "id": "cp-03",
                "name": "Competitive Analysis",
                "prompt": "Conduct a competitive analysis by comparing our strengths and weaknesses against the likely incumbent and two other probable competitors, then identify our discriminators and areas where we're vulnerable and need mitigation strategies.",
                "use_when": "Understanding the competition",
                "input_needed": "Opportunity details + known competitors",
            },
            {
                "id": "cp-04",
                "name": "Win Theme Developer",
                "prompt": "Develop five compelling win themes for this opportunity that connect our unique capabilities to the customer's mission needs, are defensible against competition, and can be consistently woven throughout our technical, management, and past performance narratives.",
                "use_when": "Building proposal strategy",
                "input_needed": "Opportunity requirements + DDI strengths",
            },
            {
                "id": "cp-05",
                "name": "Teaming Strategy Builder",
                "prompt": "Create a detailed teaming strategy for this opportunity by identifying capability gaps we need to fill, potential teaming partners with complementary strengths, and the optimal team structure that maximizes our win probability and work share.",
                "use_when": "Deciding on teaming approach",
                "input_needed": "Solicitation requirements + DDI capabilities + gaps",
            },
            {
                "id": "cp-06",
                "name": "Intelligence Gap Analysis",
                "prompt": "Review our customer intelligence for this opportunity and identify critical information gaps about decision-makers, budget constraints, evaluation priorities, and competitor activities, then recommend specific actions to gather missing intelligence before RFP release.",
                "use_when": "Pre-RFP intelligence gathering",
                "input_needed": "Known intelligence about the opportunity",
            },
            {
                "id": "cp-07",
                "name": "Bid/No-Bid Decision",
                "prompt": "Act as a capture manager performing a bid/no-bid analysis. Evaluate this opportunity against our strategic priorities, technical qualifications, competitive position, available resources, and estimated P-win, then provide a go/no-go recommendation with supporting rationale.",
                "use_when": "Go/no-go decision point",
                "input_needed": "Opportunity details + company resources/capabilities",
            },
            {
                "id": "cp-08",
                "name": "Price-to-Win Strategy",
                "prompt": "Develop a price-to-win strategy by analyzing the agency's budget, historical contract values, competitor pricing approaches, and our cost structure, then recommend a pricing positioning that balances competitiveness with profitability and technical credibility.",
                "use_when": "Pricing strategy development",
                "input_needed": "Budget info, historical pricing, cost structure",
            },
            {
                "id": "cp-09",
                "name": "Capture Timeline Builder",
                "prompt": "Create a capture timeline with milestones for relationship development, solution refinement, teaming finalization, color review schedules, and key decision points from now until proposal submission that ensures adequate preparation time.",
                "use_when": "Planning the capture schedule",
                "input_needed": "Proposal deadline + current capture status",
            },
            {
                "id": "cp-10",
                "name": "Strategic Questions for Pre-Proposal",
                "prompt": "Identify all compliance risks, technical uncertainties, and contractual concerns in this draft solicitation, then draft strategic questions for submission during the pre-proposal conference that clarify requirements without revealing our solution approach to competitors.",
                "use_when": "Preparing for industry day or Q&A period",
                "input_needed": "Draft solicitation text",
            },
        ]
    },

    # ─────────────────────────────────────────────────────────────────
    # QA/QC PLANS — Used by COMPASS Post-Award Operations
    # ─────────────────────────────────────────────────────────────────
    "qaqc_plan": {
        "system": "COMPASS",
        "context": "quality_management",
        "description": "Build and review QA/QC plans for contract execution",
        "prompts": [
            {
                "id": "qa-01",
                "name": "PWS QA/QC Compliance Review",
                "prompt": "Review this QA/QC plan to ensure it addresses all performance work statement requirements with appropriate inspection methods, acceptance criteria, performance metrics, and corrective action procedures, then identify any gaps or missing elements.",
                "use_when": "Reviewing QA/QC plan against PWS",
                "input_needed": "QA/QC plan + PWS",
            },
            {
                "id": "qa-02",
                "name": "Measurable Process Rewrite",
                "prompt": "Rewrite this QA/QC narrative to eliminate vague quality commitments and replace them with specific, measurable processes including inspection frequencies, sampling methods, documentation requirements, and quantifiable performance thresholds.",
                "use_when": "QA/QC plan is too vague",
                "input_needed": "QA/QC narrative",
            },
            {
                "id": "qa-03",
                "name": "COR Evaluation Simulation",
                "prompt": "Act as a federal Contracting Officer's Representative evaluating this QA/QC plan. Assess whether the proposed surveillance methods, inspection frequencies, and performance thresholds provide adequate government oversight and protection against substandard performance.",
                "use_when": "Testing QA/QC from government perspective",
                "input_needed": "QA/QC plan",
            },
            {
                "id": "qa-04",
                "name": "Deliverable-Specific QA/QC Tailoring",
                "prompt": "Transform this generic quality management narrative into a tailored QA/QC plan that directly addresses each deliverable and performance standard in the PWS with specific inspection procedures, responsible personnel, and measurable acceptance criteria.",
                "use_when": "Customizing QA/QC for specific deliverables",
                "input_needed": "Generic QA/QC + PWS deliverables list",
            },
            {
                "id": "qa-05",
                "name": "KPI Dashboard Builder",
                "prompt": "Develop a quality metrics dashboard for this contract that includes Key Performance Indicators (KPIs), measurement methodologies, reporting frequencies, and threshold levels for green/yellow/red status that align with the government's mission objectives.",
                "use_when": "Building performance tracking system",
                "input_needed": "Contract requirements + performance standards",
            },
            {
                "id": "qa-06",
                "name": "QC vs QA Distinction Clarity",
                "prompt": "Rewrite this QA/QC section to clearly distinguish between our internal quality control processes performed by company personnel and the quality assurance surveillance activities performed by the government, demonstrating understanding of the distinction.",
                "use_when": "Evaluator feedback about QC/QA confusion",
                "input_needed": "QA/QC section text",
            },
            {
                "id": "qa-07",
                "name": "CAPA & Continuous Improvement",
                "prompt": "Create a defect prevention and continuous improvement process for this contract that includes root cause analysis procedures, corrective and preventive action (CAPA) workflows, lessons learned integration, and metrics trending for proactive quality management.",
                "use_when": "Building continuous improvement framework",
                "input_needed": "Contract type and quality requirements",
            },
            {
                "id": "qa-08",
                "name": "Roles & Responsibilities Strengthener",
                "prompt": "Act as a quality assurance professional reviewing this plan. Identify where quality roles and responsibilities are unclear or inadequately defined, then strengthen the narrative with specific position titles, authorities, independence from production, and escalation procedures.",
                "use_when": "Quality org chart is unclear",
                "input_needed": "QA/QC plan with roles section",
            },
            {
                "id": "qa-09",
                "name": "Inspection & Test Plan Matrix",
                "prompt": "Analyze this technical approach and create a QA/QC inspection and test plan (ITP) matrix that maps each deliverable to specific quality control checkpoints, inspection methods, acceptance standards, and documentation requirements throughout the production lifecycle.",
                "use_when": "Building formal ITP",
                "input_needed": "Technical approach + deliverables",
            },
            {
                "id": "qa-10",
                "name": "Security & Risk Integration",
                "prompt": "Review this QA/QC plan for integration with our risk management and cybersecurity approaches, ensuring quality processes include security controls verification, data integrity checks, and compliance validation for all contract deliverables and systems.",
                "use_when": "Contracts with security requirements",
                "input_needed": "QA/QC plan + security requirements",
            },
        ]
    },

    # ─────────────────────────────────────────────────────────────────
    # DEBRIEFS & LESSONS LEARNED — Used by NEXUS Learning Engine / Advisor
    # ─────────────────────────────────────────────────────────────────
    "debriefs_lessons": {
        "system": "ADVISOR",
        "context": "learning",
        "description": "Analyze win/loss debriefs and extract actionable lessons",
        "prompts": [
            {
                "id": "dl-01",
                "name": "Debrief Score Impact Analysis",
                "prompt": "Analyze this debrief feedback to identify the specific weaknesses, deficiencies, and gaps that cost us points in the technical, management, past performance, and price evaluation areas, then prioritize them by impact on our overall score.",
                "use_when": "After receiving a loss debrief",
                "input_needed": "Government debrief feedback",
            },
            {
                "id": "dl-02",
                "name": "Corrective Action Plan",
                "prompt": "Act as a proposal improvement consultant reviewing this loss debrief. Translate the government's feedback into actionable corrective measures and process improvements we can implement before our next proposal submission.",
                "use_when": "Turning loss into improvement",
                "input_needed": "Debrief feedback",
            },
            {
                "id": "dl-03",
                "name": "Proposal vs Feedback Gap Analysis",
                "prompt": "Compare this debrief feedback against our original proposal content to pinpoint where our writing failed to communicate our capabilities effectively, where we missed requirements, or where evaluators misunderstood our approach.",
                "use_when": "Understanding where proposal failed",
                "input_needed": "Debrief feedback + original proposal",
            },
            {
                "id": "dl-04",
                "name": "Systemic Pattern Detector",
                "prompt": "Review this debrief for patterns or recurring themes across multiple evaluation factors that indicate systemic issues in our proposal development process, capture planning, solution design, or competitive positioning.",
                "use_when": "Looking for root causes across losses",
                "input_needed": "Debrief feedback (ideally multiple debriefs)",
            },
            {
                "id": "dl-05",
                "name": "Lessons Learned Document",
                "prompt": "Create a lessons learned summary from this debrief that documents what worked well, what didn't work, root causes of deficiencies, and specific recommendations for improving our win rate on similar future opportunities.",
                "use_when": "Documenting lessons for future bids",
                "input_needed": "Debrief feedback",
            },
            {
                "id": "dl-06",
                "name": "Winner Reverse Engineering",
                "prompt": "Act as a federal evaluator and reverse-engineer what the winning proposal likely included based on this debrief feedback about our weaknesses and the winner's strengths, then identify capability or teaming gaps we need to address.",
                "use_when": "Understanding what the winner did better",
                "input_needed": "Debrief feedback with winner comparison",
            },
            {
                "id": "dl-07",
                "name": "Pricing Strategy Post-Mortem",
                "prompt": "Analyze the pricing feedback from this debrief to determine if we lost on cost realism, cost reasonableness, or best value trade-offs, then recommend pricing strategy adjustments for future proposals in this market segment.",
                "use_when": "Price was a factor in the loss",
                "input_needed": "Pricing feedback from debrief",
            },
            {
                "id": "dl-08",
                "name": "Protest Grounds Assessment",
                "prompt": "Review this debrief feedback for any evaluation inconsistencies, scoring discrepancies, or potential grounds for protest or GAO filing, assessing whether the government's rationale aligns with the solicitation's stated evaluation criteria.",
                "use_when": "Evaluating whether to protest",
                "input_needed": "Full debrief feedback + solicitation criteria",
            },
            {
                "id": "dl-09",
                "name": "After-Action Report Builder",
                "prompt": "Transform this raw debrief notes into a structured after-action report that captures evaluator comments by proposal section, our self-assessment of what happened, contributing factors, and corrective action plans with ownership and timelines.",
                "use_when": "Formalizing debrief into AAR",
                "input_needed": "Raw debrief notes",
            },
            {
                "id": "dl-10",
                "name": "Intelligence Gap Plan",
                "prompt": "Identify knowledge gaps revealed by this debrief regarding the customer's priorities, evaluation preferences, technical hot buttons, or competitive landscape, then develop an intelligence-gathering plan to better position us for the re-compete or similar opportunities.",
                "use_when": "Planning for re-compete or similar bid",
                "input_needed": "Debrief feedback",
            },
        ]
    },

    # ─────────────────────────────────────────────────────────────────
    # TEAMING & SUBCONTRACTOR MGMT — Used by GPSS + Subcontractor Framework
    # ─────────────────────────────────────────────────────────────────
    "teaming_subcontractor": {
        "system": "GPSS",
        "context": "subcontractor",
        "description": "Teaming partner evaluation, outreach, and subcontractor management",
        "prompts": [
            {
                "id": "ts-01",
                "name": "Partner Outreach Review",
                "prompt": "Review this email outreach to a potential teaming partner for professionalism, clarity of our value proposition, specific role definition, and compelling reasons why they should partner with us, then suggest improvements to increase response rates.",
                "use_when": "Before sending teaming outreach",
                "input_needed": "Draft outreach email",
            },
            {
                "id": "ts-02",
                "name": "Sub Perspective Review",
                "prompt": "Act as a potential subcontractor receiving this teaming invitation. Evaluate whether the message clearly communicates the opportunity scope, our team structure, expected work share, timeline for teaming decisions, and next steps, then identify any missing information that would prevent a quick response.",
                "use_when": "Testing outreach effectiveness",
                "input_needed": "Teaming invitation email/document",
            },
            {
                "id": "ts-03",
                "name": "Compelling Outreach Rewrite",
                "prompt": "Rewrite this subcontractor outreach email to be more compelling by emphasizing mutual benefits, our track record as a reliable prime contractor, payment terms advantages, and the strategic value of this partnership beyond just this single opportunity.",
                "use_when": "Outreach isn't getting responses",
                "input_needed": "Current outreach email",
            },
            {
                "id": "ts-04",
                "name": "Teaming Partner Evaluation Matrix",
                "prompt": "Create a teaming partner evaluation matrix that scores potential teammates across criteria such as past performance relevance, technical capability strength, small business status, geographic presence, pricing competitiveness, and cultural fit to help prioritize partnership decisions.",
                "use_when": "Comparing multiple potential partners",
                "input_needed": "List of potential partners with basic info",
            },
            {
                "id": "ts-05",
                "name": "Best-Fit Sub Recommendation",
                "prompt": "Analyze this list of potential subcontractors and recommend which companies offer the strongest complementary capabilities, competitive advantages, and strategic alignment with our solution approach for this specific opportunity.",
                "use_when": "Selecting from a sub shortlist",
                "input_needed": "Sub candidate list + opportunity requirements",
            },
            {
                "id": "ts-06",
                "name": "Sub Management Narrative",
                "prompt": "Develop a subcontractor management narrative for our proposal that demonstrates how we'll integrate subcontractor work, maintain quality oversight, ensure communication flow, handle performance issues, and protect the government's interests throughout contract execution.",
                "use_when": "Writing management approach for proposal",
                "input_needed": "Team structure + contract requirements",
            },
            {
                "id": "ts-07",
                "name": "Teaming Approach Strengthener",
                "prompt": "Review this teaming approach description for our proposal and strengthen it by adding specific collaboration tools, integration processes, key personnel interaction points, and risk mitigation strategies that prove we're a cohesive team rather than disconnected entities.",
                "use_when": "Teaming section needs more substance",
                "input_needed": "Current teaming approach text",
            },
            {
                "id": "ts-08",
                "name": "CO Sub Management Evaluation",
                "prompt": "Act as a contracting officer evaluating subcontractor management plans. Assess whether this narrative adequately addresses subcontractor oversight, deliverable integration, payment flow-down timing, quality control of subcontractor work, and resolution of performance disputes.",
                "use_when": "Testing sub management plan quality",
                "input_needed": "Sub management plan",
            },
            {
                "id": "ts-09",
                "name": "Roles & Responsibilities Matrix",
                "prompt": "Create a teaming roles and responsibilities matrix for this proposal that clearly delineates prime and subcontractor duties by PWS task, percentage of effort, key personnel assignments, and deliverable ownership to demonstrate a well-organized team structure.",
                "use_when": "Building R&R matrix for proposal",
                "input_needed": "PWS tasks + team members",
            },
            {
                "id": "ts-10",
                "name": "Teammate Profile Builder",
                "prompt": "Transform this generic subcontractor description into a compelling teammate profile that highlights their unique qualifications, relevant past performance, certifications, key personnel credentials, and specific value they bring to our solution that strengthens our competitive position.",
                "use_when": "Writing teammate descriptions for proposals",
                "input_needed": "Sub company info + capabilities",
            },
        ]
    },

    # ─────────────────────────────────────────────────────────────────
    # TRANSITION / PHASE-IN PLANS — Used by COMPASS
    # ─────────────────────────────────────────────────────────────────
    "transition_plan": {
        "system": "COMPASS",
        "context": "transition",
        "description": "Develop and refine contract transition and phase-in plans",
        "prompts": [
            {
                "id": "tr-01",
                "name": "Transition Compliance Review",
                "prompt": "Review this transition plan to ensure it addresses all phase-in requirements from the solicitation including knowledge transfer activities, incumbent coordination, personnel retention, equipment/asset transfer, security clearances, and schedule milestones with measurable success criteria.",
                "use_when": "Verifying transition plan completeness",
                "input_needed": "Transition plan + solicitation phase-in requirements",
            },
            {
                "id": "tr-02",
                "name": "Risk & Disruption Assessment",
                "prompt": "Act as a federal program manager evaluating this transition approach. Assess whether the plan adequately mitigates risks of service disruption, demonstrates realistic timelines, and provides sufficient visibility into progress through status reporting and contingency measures.",
                "use_when": "Testing transition plan robustness",
                "input_needed": "Transition plan",
            },
            {
                "id": "tr-03",
                "name": "Communication Strategy Enhancement",
                "prompt": "Rewrite this transition narrative to emphasize our proactive communication strategy with the incumbent contractor, government stakeholders, and end users, demonstrating how we'll maintain continuity of operations while implementing improvements during the phase-in period.",
                "use_when": "Transition plan lacks communication detail",
                "input_needed": "Transition narrative",
            },
            {
                "id": "tr-04",
                "name": "Weekly Phase-In Schedule Builder",
                "prompt": "Transform this generic transition plan into a detailed phase-in schedule that breaks down activities by week with specific tasks, responsible personnel, dependencies, decision points, and early win deliverables that build government confidence during the critical startup period.",
                "use_when": "Need detailed week-by-week timeline",
                "input_needed": "Transition plan + phase-in duration",
            },
            {
                "id": "tr-05",
                "name": "Operational Readiness Gap Check",
                "prompt": "Analyze this transition plan for potential gaps in addressing personnel onboarding, training completion, facility access, IT system access, documentation handover, and operational readiness verification before assuming full contract responsibility, then recommend additions to strengthen the approach.",
                "use_when": "Final review of transition plan",
                "input_needed": "Transition plan",
            },
        ]
    },

    # ─────────────────────────────────────────────────────────────────
    # ORAL PRESENTATIONS — Used by GPSS
    # ─────────────────────────────────────────────────────────────────
    "oral_presentation": {
        "system": "GPSS",
        "context": "oral_presentation",
        "description": "Prepare for oral proposal presentations",
        "prompts": [
            {
                "id": "op-01",
                "name": "Written to Oral Conversion",
                "prompt": "Convert this written technical proposal section into a compelling oral presentation script with clear talking points, transition phrases, and speaker notes that can be delivered within the allotted time while emphasizing our key differentiators and win themes.",
                "use_when": "Converting proposal to presentation",
                "input_needed": "Written proposal section + time limit",
            },
            {
                "id": "op-02",
                "name": "Evaluator Question Predictor",
                "prompt": "Act as a federal evaluation panel reviewing oral presentations. Identify the top five questions evaluators are likely to ask based on this solicitation's evaluation criteria, our technical approach, and potential areas of concern, then provide strong response frameworks for each.",
                "use_when": "Preparing for Q&A session",
                "input_needed": "Solicitation criteria + our technical approach",
            },
            {
                "id": "op-03",
                "name": "Pacing & Flow Optimizer",
                "prompt": "Review this oral presentation outline for appropriate pacing, logical flow, and audience engagement strategies, ensuring we allocate sufficient time to address the highest-weighted evaluation factors while avoiding information overload or rushed delivery.",
                "use_when": "Optimizing presentation timing",
                "input_needed": "Presentation outline + evaluation weights",
            },
            {
                "id": "op-04",
                "name": "Visual & Interactive Elements",
                "prompt": "Analyze our oral presentation content and identify opportunities to incorporate visuals, demonstrations, props, or interactive elements that will make our solution more memorable and differentiate us from competitors using standard slide presentations.",
                "use_when": "Making presentation more engaging",
                "input_needed": "Presentation content",
            },
            {
                "id": "op-05",
                "name": "Slide Deck Optimization",
                "prompt": "Transform this slide deck from text-heavy content into presenter-focused visuals with minimal on-screen text, powerful graphics, and clear takeaway messages that support rather than duplicate what the speaker will say, ensuring evaluators focus on our team's delivery and expertise.",
                "use_when": "Improving visual presentation",
                "input_needed": "Current slide deck content",
            },
        ]
    },
}


# ─────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS — Used by API endpoints and other NEXUS modules
# ─────────────────────────────────────────────────────────────────────

SYSTEM_MAP = {
    "GPSS": ["past_performance", "technical_proposal", "capability_statement", "capture_planning", "teaming_subcontractor", "oral_presentation"],
    "COMPASS": ["qaqc_plan", "transition_plan"],
    "ADVISOR": ["debriefs_lessons"],
}

CONTEXT_MAP = {
    "proposal_writing": ["past_performance", "technical_proposal"],
    "evaluator": ["technical_proposal", "past_performance"],
    "cap_statement": ["capability_statement"],
    "capture": ["capture_planning"],
    "quality_management": ["qaqc_plan"],
    "learning": ["debriefs_lessons"],
    "subcontractor": ["teaming_subcontractor"],
    "transition": ["transition_plan"],
    "oral_presentation": ["oral_presentation"],
}


def get_prompts_by_system(system_name: str) -> list:
    """Get all prompts relevant to a NEXUS system."""
    system_upper = system_name.upper()
    categories = SYSTEM_MAP.get(system_upper, [])
    results = []
    for cat_key in categories:
        cat = PROMPT_LIBRARY[cat_key]
        results.append({
            "category": cat_key,
            "description": cat["description"],
            "context": cat["context"],
            "prompts": cat["prompts"],
        })
    return results


def get_prompts_by_context(context: str) -> list:
    """Get prompts relevant to a specific workflow context."""
    categories = CONTEXT_MAP.get(context, [])
    results = []
    for cat_key in categories:
        cat = PROMPT_LIBRARY[cat_key]
        results.append({
            "category": cat_key,
            "description": cat["description"],
            "prompts": cat["prompts"],
        })
    return results


def get_prompts_by_category(category: str) -> dict:
    """Get all prompts in a specific category."""
    return PROMPT_LIBRARY.get(category, {})


def get_prompt_by_id(prompt_id: str) -> dict | None:
    """Find a specific prompt by its ID."""
    for cat in PROMPT_LIBRARY.values():
        for p in cat["prompts"]:
            if p["id"] == prompt_id:
                return {**p, "category": cat["description"], "system": cat["system"]}
    return None


def get_all_categories() -> list:
    """Return summary of all categories."""
    return [
        {
            "key": key,
            "system": cat["system"],
            "context": cat["context"],
            "description": cat["description"],
            "count": len(cat["prompts"]),
        }
        for key, cat in PROMPT_LIBRARY.items()
    ]


def suggest_prompts(situation: str) -> list:
    """Suggest relevant prompts based on what the user is doing."""
    situation_lower = situation.lower()

    keyword_map = {
        "past performance": ["past_performance"],
        "technical": ["technical_proposal"],
        "proposal": ["technical_proposal", "past_performance", "capture_planning"],
        "capability": ["capability_statement"],
        "cap statement": ["capability_statement"],
        "capture": ["capture_planning"],
        "bid": ["capture_planning", "technical_proposal"],
        "go no go": ["capture_planning"],
        "win": ["capture_planning"],
        "quality": ["qaqc_plan"],
        "qa": ["qaqc_plan"],
        "qc": ["qaqc_plan"],
        "debrief": ["debriefs_lessons"],
        "lesson": ["debriefs_lessons"],
        "loss": ["debriefs_lessons"],
        "won": ["debriefs_lessons"],
        "team": ["teaming_subcontractor"],
        "subcontract": ["teaming_subcontractor"],
        "partner": ["teaming_subcontractor"],
        "transition": ["transition_plan"],
        "phase-in": ["transition_plan"],
        "oral": ["oral_presentation"],
        "presentation": ["oral_presentation"],
        "pricing": ["capture_planning"],
        "compete": ["capture_planning", "debriefs_lessons"],
    }

    matched_categories = set()
    for keyword, cats in keyword_map.items():
        if keyword in situation_lower:
            matched_categories.update(cats)

    if not matched_categories:
        return []

    results = []
    for cat_key in matched_categories:
        cat = PROMPT_LIBRARY.get(cat_key, {})
        if cat:
            results.extend([
                {**p, "category_key": cat_key, "system": cat["system"]}
                for p in cat["prompts"]
            ])
    return results


def get_stats() -> dict:
    """Return library statistics."""
    total = sum(len(cat["prompts"]) for cat in PROMPT_LIBRARY.values())
    by_system = {}
    for cat in PROMPT_LIBRARY.values():
        sys = cat["system"]
        by_system[sys] = by_system.get(sys, 0) + len(cat["prompts"])

    return {
        "total_prompts": total,
        "categories": len(PROMPT_LIBRARY),
        "by_system": by_system,
        "source": "Govcon Giants Federal Contracting AI Prompt Library (Dec 2025)",
    }
