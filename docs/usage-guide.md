# Usage Guide

Step-by-step instructions for using kb-template.

## Setup

1. **Unzip** kb-template to a folder named for your topic (e.g. `my-research-kb/`)
2. **`git init`** inside the folder — gives you version history for free
3. **Rename schema file** if needed — `CLAUDE.md` is for Claude Code; rename to `AGENTS.md` for Codex, etc. The content is AI-agnostic
4. **Open as Obsidian vault** — wikilinks and attachment path are pre-configured
5. **Install plugins** (optional): Marp Slides, Dataview, Breadcrumbs, Excalidraw
6. **Install Obsidian Web Clipper** browser extension, configure it to save to `raw/articles/`
7. **Bind image download hotkey**: Obsidian Settings → Hotkeys → search "Download attachments for current file" → bind to Ctrl+Shift+D

## Daily workflow

### Adding sources

1. Clip a web article with Obsidian Web Clipper → lands in `raw/articles/`
2. Hit Ctrl+Shift+D to download its images to `raw/assets/`
3. Rename the file to `YYYY-MM-DD_short-slug.md` (per `raw/README.md` convention)
4. For PDFs, drop them in `raw/papers/`. For standalone images/diagrams, `raw/images/`

### First compilation (when you have a few sources ready)

1. Open your LLM agent (e.g. Claude Code) in the folder
2. Copy-paste `_prompts/compile-wiki.md` as your prompt (or just say "compile the wiki")
3. The LLM reads everything in `raw/`, builds out `wiki/` — articles, source summaries, index, overview, log
4. Browse the results in Obsidian — check graph view, read pages, follow links

### Adding more sources later

1. Drop new sources into `raw/`
2. Copy-paste `_prompts/update-wiki.md` (or just say "ingest the new sources")
3. The LLM finds what's new, integrates it — updates existing pages, creates new ones, updates index/overview/log

### Ingesting HelpScout tickets automatically

1. Create a HelpScout OAuth2 app in **Your Profile → My Apps → Create My App** and note the client ID and secret
2. Set credentials as environment variables (never commit secrets):
   ```bash
   export HELPSCOUT_CLIENT_ID=your_client_id
   export HELPSCOUT_CLIENT_SECRET=your_client_secret
   ```
3. Install the script dependency: `pip install requests`
4. Run the ingestion script:
   ```bash
   python scripts/ingest_helpscout.py
   ```
   Optional flags:
   ```
   --mailbox  <id>         Only fetch from a specific mailbox
   --status   closed       Filter by status (active | pending | closed | spam)
   --since    YYYY-MM-DD   Only tickets updated on or after this date
   --max      50           Maximum conversations to fetch (default: 100)
   --output   /custom/dir  Override output directory (default: raw/helpscout/)
   ```
5. Tickets are written as Markdown files in `raw/helpscout/` with the naming pattern `YYYY-MM-DD_helpscout-<id>-<slug>.md`
6. Run `_prompts/update-wiki.md` (or say "ingest the new sources") so the LLM integrates the tickets into the wiki

### Asking questions

1. Copy-paste `_prompts/qa.md` and ask your question (or just ask naturally — the schema file guides the LLM)
2. The LLM researches the wiki, writes an answer to `output/reports/`
3. If the answer is valuable, tell the LLM to file it back into the wiki as a new page

### Health checks

1. Periodically, copy-paste `_prompts/lint-wiki.md` (or say "lint the wiki")
2. The LLM scans everything, writes a report to `output/reports/lint-report.md`
3. Review the findings, tell the LLM to fix what matters

## Tips

- You don't need to use the prompt files literally — once the LLM has read the schema file, it knows the conventions. The prompts are there as references.
- Commit often with git — the wiki changes a lot per session.
- Use Obsidian's graph view to spot orphan pages and hub pages.
- If the wiki gets large, look into [qmd](https://github.com/tobi/qmd) for search.
- **Switch AI agents freely.** The wiki is just files — if you start with Claude Code and want to try Codex or another agent, just rename the schema file. Your data and all the wiki content carries over completely.
- **Your data stays yours.** Everything is local markdown and images. No data is sent to or stored by any AI provider beyond what you share in a conversation. You can zip up the whole folder and move it anywhere.
