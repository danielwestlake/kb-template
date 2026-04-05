# Process Documentation

Internal process guides, SOPs, runbooks, and system documentation.

## What to store here

- Standard Operating Procedures (SOPs)
- Onboarding and offboarding checklists
- Runbooks for recurring tasks
- System architecture and integration documentation
- Service delivery workflows
- Quality assurance checklists
- Pricing and packaging guidelines

## Naming convention

```
YYYY-MM-DD_process-type_short-description.md
```

## Examples

| File | Description |
|------|-------------|
| `2026-01-15_sop_client-onboarding.md` | Client onboarding SOP |
| `2026-03-01_runbook_monthly-reporting.md` | Monthly client reporting runbook |
| `2025-11-10_sop_support-escalation.md` | Support escalation procedure |
| `2026-02-20_architecture_crm-integration.md` | CRM integration system architecture |

## Recommended structure

```markdown
# [Process Name]
Date: YYYY-MM-DD
Type: [sop | runbook | architecture | checklist | guideline]
Owner: [team or person responsible]
Last reviewed: YYYY-MM-DD

## Purpose

What this process achieves and why it exists.

## Steps

1. Step one
2. Step two
3. Step three

## Notes and exceptions

Edge cases, dependencies, and gotchas.

## Related processes

- [[other-process]]
```

## Tips

- Document processes *after* you've run them a few times, not before — real-world steps differ from theory.
- The LLM can cross-reference process docs with helpdesk issues to identify process gaps and improvement opportunities.
- Outdated process docs are worse than no docs — add a `Last reviewed` date and lint the wiki regularly.
