# Helpdesk Issues

Support tickets, bug reports, feature requests, and incident logs from your helpdesk system.

## What to store here

- Resolved support tickets (exported as markdown or CSV)
- Bug reports and root cause analyses
- Feature request summaries
- Recurring issue patterns
- Incident post-mortems
- FAQs derived from support volume

## Naming convention

```
YYYY-MM-DD_ticket-id_short-description.md
```

Or for batched exports:

```
YYYY-MM-DD_helpdesk-export_system-or-period.md
```

## Examples

| File | Description |
|------|-------------|
| `2026-03-01_T-4521_login-sso-failure.md` | SSO login failure ticket |
| `2026-03-15_helpdesk-export_q1-2026.md` | Q1 2026 batch ticket export |
| `2026-02-20_incident_payment-gateway-outage.md` | Payment gateway incident post-mortem |

## Recommended structure per ticket

```markdown
# Ticket [ID]: [Title]
Date: YYYY-MM-DD
Client: [client name or "internal"]
Severity: [low | medium | high | critical]
Category: [bug | feature-request | how-to | incident | billing | other]
Status: resolved | escalated | wont-fix

## Description

What the client reported.

## Root cause

What caused the issue (for bugs/incidents).

## Resolution

How it was resolved.

## Follow-up

Any process changes, documentation updates, or product improvements triggered by this ticket.
```

## Tips

- Bulk exports from helpdesk systems (Zendesk, Freshdesk, Intercom, etc.) work well — export as CSV and convert to markdown.
- The LLM can identify the top recurring issues and suggest FAQ content and process improvements.
- High-severity incidents are especially valuable for the process improvement workflow.
