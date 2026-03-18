 # NEXUS AutoBuilder Operating Patterns (System-Wide)
 
 **Purpose:** Apply rapid-builder UX and automation patterns across ALL NEXUS systems, not only PRISM.
 
 **Created:** March 9, 2026
 
 ---
 
 ## Scope
 
 This standard applies to:
 - GPSS (opportunity mining + bid workflows)
 - DDCSS (blueprint sales + client onboarding)
 - PRISM (service delivery + QA)
 - ATLAS (project execution)
 - VERTEX (invoicing + margin controls)
 - COMPASS (quality scoring)
 - Any future NEXUS module
 
 ---
 
 ## 1) Universal Builder Pattern
 
 Every module must support:
 
 1. **Prompt -> Plan**
 - User intent is converted into a structured workflow plan.
 
 2. **Plan -> Artifacts**
 - System auto-generates all required outputs:
   - checklists
   - emails/templates
   - forms/doc packets
   - task assignments
 
 3. **Artifacts -> Execution**
 - One-click launch into execution pipeline with statuses and owners.
 
 4. **Execution -> Measurement**
 - Track SLA, blocker, margin, and completion metrics.
 
 5. **Measurement -> Learning**
 - Feed results back into templates, routing, and scoring logic.
 
 ---
 
 ## 2) Module-Neutral Building Blocks
 
 Reusable blocks every system can compose:
 - **Intake Wizard**
 - **Rules Engine**
 - **Template Factory**
 - **Task Orchestrator**
 - **QA/Release Gates**
 - **Compliance Packet Generator**
 - **Scorecard Dashboard**
 - **Next Best Action Panel**
 - **Clone Workflow**
 - **Postmortem/Learning Capture**
 
 ---
 
 ## 3) Non-Negotiable UX Standards
 
 1. **Single command, multiple outputs**
 - One user action should create all downstream required artifacts.
 
 2. **No dead-end screens**
 - Every page must end in an executable next action.
 
 3. **Operator-first design**
 - Optimize for speed, clarity, and blocker removal.
 
 4. **Status transparency**
 - Every object has state, owner, due date, and escalation path.
 
 5. **Copyable by default**
 - Operational outputs should be immediately usable in chat/email/forms.
 
 ---
 
 ## 4) Universal Health Model
 
 Every module tracks:
 - Throughput (items completed)
 - Quality (first-pass success / rejection rate)
 - Financial impact (revenue + margin movement)
 - Cycle time (request-to-complete)
 - Blockers (count + aging)
 - Responsiveness (vendor/partner/CO latency)
 
 ---
 
 ## 5) Cross-System Data Contracts
 
 Required shared IDs and context:
 - `opportunity_id`
 - `client_id`
 - `contract_id`
 - `workflow_stage`
 - `owner`
 - `compliance_state`
 - `risk_score`
 - `margin_score`
 
 No module should operate without referencing these shared fields.
 
 ---
 
 ## 6) Release-Gate Model (All Systems)
 
 Before any item is marked complete:
 - Required docs present
 - Required approvals captured
 - Compliance checks passed
 - Financial checks passed (if applicable)
 - Handoff package generated
 
 If any gate fails, item cannot close.
 
 ---
 
 ## 7) Implementation Sequence
 
 1. Add module-specific Intake Wizards
 2. Add Template Factory outputs per module
 3. Add Next Best Action panel globally
 4. Add health scorecards + blocker aging
 5. Add clone-and-retarget workflow
 6. Add post-execution learning loop
 
 ---
 
 ## 8) Success Criteria
 
 NEXUS is compliant with this standard when:
 - Every module can convert prompt -> executable workflow
 - Every workflow has measurable business outcome
 - Every system reports blockers and next best actions daily
 - Every completed cycle improves the next cycle
 
 ---
 
 ## Bottom Line
 
 This is how NEXUS becomes an execution operating system, not a collection of tools.
