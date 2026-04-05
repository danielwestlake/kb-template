# Meeting Notes

Notes from client meetings, internal team meetings, discovery calls, and project check-ins.

## What to store here

- Client discovery and scoping calls
- Project kick-off and check-in meetings
- Quarterly business reviews (QBRs)
- Retrospectives and post-mortems
- Internal team syncs with relevant insights
- Sales calls and demos

## Naming convention

```
YYYY-MM-DD_meeting-type_client-or-topic.md
```

## Examples

| File | Description |
|------|-------------|
| `2026-03-10_discovery_acme-corp.md` | Discovery call with Acme Corp |
| `2026-04-02_qbr_globex.md` | Quarterly business review with Globex |
| `2026-03-28_retrospective_project-phoenix.md` | Post-project retrospective for Project Phoenix |
| `2026-04-01_internal_product-roadmap-sync.md` | Internal product roadmap discussion |

## Recommended structure for each note

```markdown
# Meeting: [Title]
Date: YYYY-MM-DD
Attendees: [names and roles]
Type: [discovery | check-in | QBR | retrospective | sales | internal]

## Summary

One paragraph overview of what was discussed and decided.

## Key points

- Point 1
- Point 2

## Action items

- [ ] Action (Owner, Due date)

## Follow-up notes

Any context added after the meeting.
```

## Tips

- Even brief bullet-point notes are valuable — the LLM can extract patterns across dozens of meetings.
- Flag meetings with `status: high-value-insight` in frontmatter when they contain especially actionable content.
- Sales calls often contain the clearest signal about client pain points and what language resonates.
