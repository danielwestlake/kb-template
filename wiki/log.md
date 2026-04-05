# Knowledge Base — Operation Log

An append-only chronological record of all operations: ingests, queries, lint passes, and updates.

Each entry uses the format `## [YYYY-MM-DD] type | Title` where type is one of: `ingest`, `query`, `lint`, `update`.

Parse with: `grep "^## \[" wiki/log.md | tail -5`

---

## [2026-04-05] update | Knowledge base initialised

Initial setup of the company-wide business knowledge base. Created directory structure for business-specific raw input types (proposals, meeting-notes, helpdesk, client-feedback, process-docs). Created wiki structure (index, overview, log), business intelligence prompt templates (client-value-analysis, process-improvement, content-marketing, sales-proposal), and updated schema (CLAUDE.md) and documentation.

No sources ingested yet. Ready for first ingest.
