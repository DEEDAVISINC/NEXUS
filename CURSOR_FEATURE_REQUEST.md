# Feature Request: Enforced Rules with Guaranteed Triggers

**Submitted by:** Dee Davis  
**Date:** March 20, 2026  
**Cursor Plan:** [Your plan level]

---

## Summary

Rules defined in `.cursorrules` and `.cursor/rules/*.mdc` files with `alwaysApply: true` are not reliably followed by the AI. They act as suggestions, not guarantees. I need rules that actually trigger specific behavior — every time, every chat, no exceptions.

---

## Current Behavior (Problem)

1. I create a rule file (`.cursorrules` or `.cursor/rules/my-rule.mdc`) with `alwaysApply: true`
2. The rule specifies: "When user says 'good morning', do X, Y, Z"
3. I start a new chat in the same workspace
4. I say "good morning"
5. **The AI does NOT follow the rule** — it responds generically or ignores the defined behavior

This happens inconsistently. Sometimes the rule is followed, sometimes it isn't. There's no reliability.

---

## Expected Behavior (Request)

I need **enforced rules** that guarantee specific behavior:

1. **Trigger phrases** — When I define "if user says X, do Y", the AI MUST do Y. Not "might" — MUST.

2. **Mandatory context injection** — Rules marked `alwaysApply: true` should be loaded into EVERY chat, EVERY time, with priority over the AI's default behavior.

3. **Deterministic, not probabilistic** — Rules should function like code, not suggestions. If I write a rule, it runs.

---

## Use Case

I run a business using Cursor as my primary workspace. I have defined:

- **Morning briefing rule**: When I say "good morning", the AI should read specific files and present my daily agenda, deadlines, and priorities.

- **End-of-day rule**: When I say "goodnight", the AI should commit code to git, present a revenue pipeline summary, and plan tomorrow.

- **Business protection rules**: Never reveal client names to suppliers, always verify company contact info on generated documents, etc.

These rules are critical to my workflow. When they don't fire, I lose time, miss context, and have to manually re-explain things every chat.

**I'm paying for Cursor Pro/Business specifically to have a customized AI assistant that follows MY rules.** If the rules don't actually work, the value proposition breaks down.

---

## Proposed Solution

### Option A: Rule Priority Levels
Allow rules to be marked with enforcement levels:
- `enforcement: suggest` — Current behavior (AI considers but may ignore)
- `enforcement: required` — AI MUST follow, no exceptions
- `enforcement: trigger` — Specific phrases trigger specific actions deterministically

### Option B: Scripted Triggers
Allow users to define actual triggers that run code/actions:
```yaml
triggers:
  - phrase: "good morning"
    action: run_script("morning_briefing.py")
  - phrase: "goodnight"
    action: run_script("end_of_day.py")
```

### Option C: Guaranteed Context Loading
Ensure that `.cursorrules` and `alwaysApply: true` rules are:
- Loaded FIRST in every chat
- Given highest priority in the context window
- Never truncated or summarized away

---

## Impact

- **Current state**: Rules are unreliable, forcing users to repeat instructions or manually trigger behavior
- **Desired state**: Rules work as advertised — define once, works every time
- **Business impact**: Time lost, workflow disruption, reduced trust in the platform

---

## Additional Context

I have 59 rule files in `.cursor/rules/` and a `.cursorrules` file in my workspace root. All have `alwaysApply: true` where appropriate. The rules are well-formatted and follow Cursor's documentation. Despite this, they do not reliably trigger in new chats.

This is not a formatting issue — it's an enforcement issue. The AI sees the rules but doesn't consistently follow them.

---

## Request

Please implement a mechanism for **guaranteed rule enforcement** so that workspace rules actually function as rules, not suggestions.

Thank you.

---

**To submit:** Go to https://forum.cursor.com or https://github.com/getcursor/cursor/issues and post this as a feature request.
