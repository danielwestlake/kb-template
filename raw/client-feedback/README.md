# Client Feedback

NPS surveys, testimonials, review excerpts, and structured feedback from clients.

## What to store here

- NPS survey responses (anonymised or attributed as appropriate)
- Client testimonials and case study quotes
- Review platform excerpts (G2, Trustpilot, Capterra, Google, etc.)
- Post-project feedback forms
- Churn interviews and exit surveys
- Expansion / upsell conversation notes

## Naming convention

```
YYYY-MM-DD_feedback-type_client-or-campaign.md
```

## Examples

| File | Description |
|------|-------------|
| `2026-Q1_nps-survey-results.md` | Q1 NPS survey aggregated results |
| `2026-03-20_testimonial_acme-corp.md` | Testimonial from Acme Corp |
| `2026-02-15_churn-interview_globex.md` | Exit interview with Globex |
| `2026-04-01_g2-reviews-export_march-2026.md` | G2 review export for March 2026 |

## Recommended structure

```markdown
# Feedback: [Type] — [Client / Campaign]
Date: YYYY-MM-DD
Type: [nps | testimonial | review | churn-interview | post-project | expansion]
Client: [client name or anonymous]
Sentiment: [positive | neutral | negative | mixed]

## Feedback content

Verbatim or summarised feedback.

## Key themes

- Theme 1
- Theme 2

## Action items (if any)

- [ ] Action (Owner)
```

## Tips

- Verbatim quotes are gold for content marketing — the LLM can surface the best ones.
- Churn interviews reveal the most honest feedback about where the product or service falls short.
- Aggregate NPS data over time to track trajectory, not just point-in-time scores.
