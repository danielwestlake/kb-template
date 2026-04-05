---
tags: [index, navigation]
date: 2026-04-05
sources: 0
---

# Knowledge Base — Index

This is the company-wide business knowledge base. It captures intelligence from proposals, meeting notes, helpdesk issues, client feedback, and process documentation — synthesised into actionable insight across four strategic focus areas.

## How to use this index

The LLM reads this file first when answering queries. Each section lists the wiki pages available, with a one-line summary. Pages are organised by category.

---

## Clients

*Per-client entity pages. Each page covers: services used, engagement history, pain points, opportunities, and NPS trend.*

*(No client pages yet — add your first source to `raw/meeting-notes/`, `raw/helpdesk/`, or `raw/client-feedback/` and run the ingest workflow.)*

---

## Process Improvements

*Identified process failure patterns and proposed improvements, cross-referenced with helpdesk and meeting note sources.*

*(No process improvement pages yet — run `_prompts/process-improvement.md` after ingesting helpdesk and meeting note sources.)*

---

## Content Marketing

*Content calendar, audience personas, and content brief pages for the automated content marketing workflow.*

*(No content marketing pages yet — run `_prompts/content-marketing.md` after ingesting proposals, meeting notes, and client feedback.)*

---

## Sales

*Proposal patterns, win/loss analysis, service offering pages, and pricing strategy notes.*

*(No sales pages yet — run `_prompts/sales-proposal.md` after ingesting proposals and meeting notes.)*

---

## Sources

*Per-source summary pages generated during ingest.*

*(No source summaries yet — ingest your first source to populate this section.)*

---

## Overview

- [[wiki/overview]] — Top-level narrative synthesis of all themes and findings

## Log

- [[wiki/log]] — Chronological record of all operations (ingests, queries, lint passes)
