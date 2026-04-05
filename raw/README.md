# Raw Sources — Naming Convention

All source files added to `raw/` should follow this naming pattern:

```
YYYY-MM-DD_short-slug.ext
```

## Rules

- **Date**: Use the publication date if known, otherwise the date you clipped/added it.
- **Slug**: Lowercase, hyphen-separated, 3-5 words that capture the topic. No spaces or special characters.
- **Extension**: `.md` for articles and notes. PDFs keep `.pdf`. Images keep their original extension.

## Examples

| File | Location |
|------|----------|
| `2026-04-01_supply-chain-risk-overview.md` | `raw/articles/` |
| `2025-11-15_market-dynamics-q3-report.pdf` | `raw/papers/` |
| `2026-03-20_system-architecture-diagram.png` | `raw/images/` |

## Subdirectory Guide

| Directory | Contents |
|-----------|----------|
| `raw/articles/` | Web-clipped articles, blog posts, tutorials |
| `raw/papers/` | Academic papers, whitepapers (PDF or markdown) |
| `raw/images/` | Diagrams, screenshots, figures referenced by articles |
| `raw/assets/` | Downloaded image attachments (via Obsidian hotkey) |
| `raw/proposals/` | Sales proposals, quotes, and scopes of work — see `raw/proposals/README.md` |
| `raw/meeting-notes/` | Client and internal meeting notes — see `raw/meeting-notes/README.md` |
| `raw/helpdesk/` | Support tickets, incident reports, bug reports — see `raw/helpdesk/README.md` |
| `raw/client-feedback/` | NPS surveys, testimonials, reviews, churn interviews — see `raw/client-feedback/README.md` |
| `raw/process-docs/` | SOPs, runbooks, system architecture docs — see `raw/process-docs/README.md` |

Each business-specific subdirectory has its own README with naming conventions and recommended file structure.
