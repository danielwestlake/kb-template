# Business Knowledge Base — Guide

A practical guide to using this knowledge base to generate client value, improve processes, fuel content marketing, and streamline sales.

## What this is

This is a company-wide intelligence system built on the LLM knowledge base pattern. It works by:

1. **You** drop raw business documents into `raw/` — proposals, meeting notes, helpdesk tickets, client feedback, process docs
2. **The LLM** reads them, extracts the key information, and integrates it into a structured, interlinked wiki
3. **You** query the wiki to get analysis, drafts, and recommendations — which are filed back in, compounding over time

The more you feed in, the more useful it becomes. A year of meeting notes, proposals, and support tickets becomes a navigable intelligence asset that no individual on your team could hold in their head.

---

## The four focus areas

### 1. Client value

**Goal:** Identify opportunities to deliver more value to existing clients before they ask.

**Inputs:** Meeting notes, helpdesk tickets, client feedback, proposals
**Output:** `output/reports/client-value-analysis-YYYY-MM-DD.md`
**Prompt:** `_prompts/client-value-analysis.md`

**What you get:**
- Per-client opportunity tables (quick wins, expansion, proactive interventions)
- Cross-client patterns — recurring needs that signal a new offering
- Underserved accounts flagged for attention

**When to run:** Monthly or quarterly; before QBRs; when reviewing an account for renewal.

---

### 2. Process improvement

**Goal:** Identify recurring failures and high-leverage fixes in your systems and processes.

**Inputs:** Helpdesk issues (especially recurring ones), meeting notes (especially retrospectives), process docs
**Output:** `output/reports/process-improvement-YYYY-MM-DD.md`
**Prompt:** `_prompts/process-improvement.md`

**What you get:**
- Top recurring issues ranked by frequency × impact
- Root cause analysis and proposed fixes for each
- Automation and tooling opportunities
- A prioritised backlog of process improvements

**When to run:** Quarterly; after major incidents; after a wave of similar support tickets.

---

### 3. Content marketing

**Goal:** Mine real expertise and client outcomes to generate content that attracts new clients.

**Inputs:** Proposals, meeting notes, client feedback, helpdesk questions, process docs
**Output:** `output/reports/content-draft-TITLE-YYYY-MM-DD.md` + `wiki/content-marketing/content-calendar.md`
**Prompt:** `_prompts/content-marketing.md`

**What you get:**
- A prioritised content calendar based on what you actually know and clients actually care about
- Full first drafts of top-priority pieces (blog posts, case studies, how-to guides, LinkedIn posts)
- Repurposing suggestions for existing content

**When to run:** Monthly; at the start of a content sprint; when planning a campaign.

---

### 4. Sales proposals

**Goal:** Win more proposals by learning from history, and generate better proposals faster.

**Inputs:** Proposals (won and lost), meeting notes from discovery and sales calls
**Output:** `output/reports/proposal-draft-PROSPECT-YYYY-MM-DD.md` or `output/reports/proposal-analysis-YYYY-MM-DD.md`
**Prompt:** `_prompts/sales-proposal.md`

**What you get:**
- New proposals drafted from historical evidence (faster, more consistent, more persuasive)
- Win/loss analysis identifying the real drivers behind outcomes
- Recommended changes to proposal templates and process

**When to run:** On demand for new proposals; quarterly for win/loss analysis.

---

## Key inputs — what to feed the knowledge base

### Proposals (`raw/proposals/`)

Every proposal sent — won, lost, or no decision. Include a brief outcome note at the top. Proposals contain your clearest picture of what clients want, how you've priced things, and what language resonates.

### Meeting notes (`raw/meeting-notes/`)

Discovery calls, QBRs, retrospectives, project check-ins, sales calls. Even rough bullet points are useful. Meetings are where clients reveal their real concerns, not just the ones in the brief.

### Helpdesk issues (`raw/helpdesk/`)

Support tickets, incident reports, bug reports. The helpdesk is a continuous stream of process failure signals. Patterns across tickets reveal systemic issues that no individual ticket makes obvious.

### Client feedback (`raw/client-feedback/`)

NPS surveys, testimonials, reviews, churn interviews. Verbatim quotes are especially valuable — for both content marketing and understanding what clients actually think. Churn interviews are the most honest feedback you'll ever get.

### Process docs (`raw/process-docs/`)

SOPs, runbooks, system architecture docs. These define your current operating state. Cross-referenced with helpdesk data, they reveal where process and reality have diverged.

---

## Daily workflow

1. **After every client meeting** — drop a brief note into `raw/meeting-notes/`
2. **Weekly** — export or paste significant helpdesk tickets into `raw/helpdesk/`
3. **After every proposal** — add the proposal + outcome note to `raw/proposals/`
4. **When feedback arrives** — file it into `raw/client-feedback/`
5. **Periodically** — run the LLM to ingest new sources (`_prompts/update-wiki.md`)
6. **Monthly/quarterly** — run one of the four business intelligence prompts

---

## Getting started

1. Fork or copy this repository
2. If not using Claude Code, rename `CLAUDE.md` to match your agent (e.g. `AGENTS.md` for Codex)
3. Open the folder as an Obsidian vault
4. Drop your first sources into the appropriate `raw/` subdirectories
5. Tell the LLM to compile the wiki: paste `_prompts/compile-wiki.md` as your prompt
6. Browse the results in Obsidian — follow links, check the graph view
7. Run your first business intelligence analysis

---

## Tips

- **Start with what you have.** Even a handful of old proposals and some meeting notes is enough to begin. The wiki compounds — it gets more valuable as you add more.
- **Consistency beats completeness.** Brief, consistent notes (even bullet points) are more useful than occasional comprehensive write-ups. Make it a habit.
- **Use Obsidian's graph view** to see which clients are well-documented vs. which are thin.
- **File back the outputs.** When an analysis surfaces a genuinely useful insight, tell the LLM to add it to the wiki as a new page. Your queries should compound, not disappear into chat history.
- **Treat the wiki as a team asset.** If your team adds sources and reads the outputs, the knowledge base becomes a shared intelligence layer — not just a personal research tool.
