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
| `2026-04-05_weekly-team-sync.md` | `raw/meetings/` |

## Subdirectory Guide

| Directory | Contents |
|-----------|----------|
| `raw/articles/` | Web-clipped articles, blog posts, tutorials |
| `raw/papers/` | Academic papers, whitepapers (PDF or markdown) |
| `raw/images/` | Diagrams, screenshots, figures referenced by articles |
| `raw/assets/` | Downloaded image attachments (via Obsidian hotkey) |
| `raw/meetings/` | Meeting notes ingested from Fellow (via `scripts/ingest_fellow.py`) |

## Ingesting meeting notes from Fellow

Run the ingest script to pull meeting notes, attendees, and action items from the Fellow API:

```bash
# 1. Install dependencies (one-time)
pip install -r scripts/requirements.txt

# 2. Set your API key
cp .env.example .env
# edit .env and set FELLOW_API_KEY=<your key>

# 3. Fetch meetings (all time)
python scripts/ingest_fellow.py

# 4. Fetch meetings in a date range
python scripts/ingest_fellow.py --since 2026-01-01 --until 2026-03-31

# 5. Preview what would be written without creating files
python scripts/ingest_fellow.py --dry-run
```

Each meeting is saved as `YYYY-MM-DD_<slug>.md` in `raw/meetings/`.  After running the script, use the `_prompts/update-wiki.md` (or `_prompts/ingest-fellow-notes.md`) prompt to integrate the new files into the wiki.
