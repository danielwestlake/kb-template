# ClickUp Integration

This document explains how to import ClickUp data (spaces, lists, tasks, and
comments) into your knowledge base as raw markdown sources.

## Overview

The script `scripts/clickup_to_raw.py` connects to the ClickUp API, fetches
your workspace content, and writes one markdown file per space into
`raw/articles/`. Each file follows the standard naming convention
`YYYY-MM-DD_clickup-<space-slug>.md` and includes YAML frontmatter so it can
be ingested by the LLM wiki workflow.

After the script runs, use `_prompts/ingest-clickup.md` to tell your LLM agent
how to integrate the new sources into the wiki.

## Prerequisites

- Python 3.8 or later
- A ClickUp personal API token (see below)

## Setup

### 1 — Get a ClickUp API token

1. Log in to ClickUp and go to **Settings → Apps**
   (`https://app.clickup.com/settings/apps`)
2. Under **API Token**, click **Generate** (or copy your existing token)
3. Keep the token secret — treat it like a password

### 2 — Install dependencies

```bash
pip install -r scripts/requirements.txt
```

### 3 — Set environment variables

```bash
export CLICKUP_API_TOKEN=pk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Optional — skip if you only have one team or want to be prompted
export CLICKUP_TEAM_ID=12345678
```

> **Tip:** Add these to a `.env` file in the repo root (already gitignored) and
> source it with `source .env` before running the script. Never commit your
> token to the repository.

## Running the importer

```bash
python scripts/clickup_to_raw.py
```

The script will:

1. Resolve your team (from env var or by prompting)
2. Fetch every space in the team
3. For each space, fetch folders, lists, tasks (all pages), and task comments
4. Write one markdown file per space to `raw/articles/`
5. Print a summary of what was saved

Example output:

```
Fetching spaces for team 12345678...
Found 2 space(s).

Processing space: Engineering (abc123)
  Fetching folders...
  Fetching folderless lists...
  Fetching lists for folder: Q2 Projects...
  Fetching tasks for list: Backlog...
  Fetching tasks for list: In Sprint...
  Saved: raw/articles/2026-04-05_clickup-engineering.md

Processing space: Marketing (def456)
  ...
  Saved: raw/articles/2026-04-05_clickup-marketing.md

Done! Imported 2 space(s) to raw/articles/
```

## Output format

Each generated file looks like this:

```markdown
---
source: clickup
space: Engineering
space_id: abc123
date: 2026-04-05
tags: [clickup, tasks]
---

# Engineering (ClickUp)

## List: Backlog

### Fix login timeout bug

**Status:** open  
**Assignees:** alice  
**Due Date:** 2026-04-10  
**Created:** 2026-03-15  
**URL:** https://app.clickup.com/t/xxxxx  

Reproduce: log in and leave the tab idle for 30 minutes.

#### Comments

- **bob** (2026-03-20): Confirmed on Chrome 124. Looks like the JWT refresh is missing.
- **alice** (2026-03-22): Will fix in the next sprint.

## Folder: Q2 Projects

## List: Website Relaunch

...

## Sources

- ClickUp Space: Engineering (ID: abc123)
- Exported: 2026-04-05
```

## Ingesting into the wiki

After the import, use the LLM prompt in `_prompts/ingest-clickup.md`:

1. Open your LLM agent (e.g. Claude Code) in the repo folder
2. Copy-paste `_prompts/ingest-clickup.md` as your prompt (or say
   "ingest the new ClickUp files")
3. The LLM will create source summaries, project pages, and update the index

## Keeping data fresh

Run the script periodically (daily, weekly) to refresh the raw sources. Each
run overwrites the previous file for the same space (same filename), so the wiki
update workflow will pick up changes on the next ingest.

For automated refresh, add a cron job or a CI scheduled workflow:

```yaml
# .github/workflows/clickup-sync.yml (example)
on:
  schedule:
    - cron: "0 6 * * 1"   # every Monday at 06:00 UTC
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r scripts/requirements.txt
      - run: python scripts/clickup_to_raw.py
        env:
          CLICKUP_API_TOKEN: ${{ secrets.CLICKUP_API_TOKEN }}
          CLICKUP_TEAM_ID: ${{ secrets.CLICKUP_TEAM_ID }}
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: refresh ClickUp raw sources"
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `CLICKUP_API_TOKEN not set` | Missing env var | Export the token (see Setup) |
| `401 Unauthorized` | Invalid token | Re-generate token in ClickUp settings |
| `requests` not found | Missing dependency | `pip install -r scripts/requirements.txt` |
| `No teams found` | Token has no workspace access | Check token permissions in ClickUp |
| Empty file (no tasks) | List has no tasks | Expected — the list section will say "_No tasks found._" |
