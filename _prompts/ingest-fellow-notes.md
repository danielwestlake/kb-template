# Ingest Fellow Meeting Notes Prompt

You are a knowledge base maintainer. New meeting notes have been ingested from Fellow into `raw/meetings/`. Your job is to integrate them into the wiki, extracting decisions, action items, recurring themes, and participant knowledge.

## Instructions

### 1. Identify new meeting files

- Read `wiki/index.md` to understand the current wiki structure
- Scan `raw/meetings/` for files that do NOT yet have a corresponding summary in `wiki/sources/`
- These are the new meetings to integrate

### 2. Read and analyse each meeting

For each new meeting file, extract:
- **Key decisions** made during the meeting
- **Action items** and who owns them
- **Topics discussed** and how they connect to existing wiki concepts
- **Attendees** and any recurring participants worth tracking
- **Open questions** or blockers raised

### 3. Update existing articles

For wiki articles related to the topics discussed:
- Add decisions and conclusions as new facts, woven into existing text naturally
- Note any contradictions or updates to earlier positions — cite both versions with sources
- Add `[[wikilinks]]` where the meeting introduces new connections between concepts
- Update the `## Sources` section to include the meeting file
- Update the `sources` count in YAML frontmatter

### 4. Create new articles

For concepts, projects, or decisions that appear in the meetings but have no wiki article yet:
- Create articles following the same style and structure as existing ones
- Add YAML frontmatter: `tags`, `date` (creation date), `sources` (count of contributing meeting files)
- Place in the appropriate `wiki/` subdirectory — create subdirectories if needed (e.g., `wiki/decisions/`, `wiki/projects/`)
- Link to and from related existing articles using `[[wikilinks]]`

### 5. Create source summaries

For each new meeting file, create `wiki/sources/<filename>.md` containing:
- Meeting title, date, and attendees summary
- One-paragraph narrative of what was discussed
- Key decisions as bullet points
- Action items as a checklist (`- [ ] item — Owner`)
- Links to concept articles it contributed to

### 6. Track action items (optional)

If this knowledge base is used for project or team tracking, consider maintaining a `wiki/action-items.md` page:
- Add new open action items from each meeting
- Mark completed items when follow-up meetings confirm completion
- Link each action item back to the meeting source

### 7. Update the index

Update `wiki/index.md` to include any new articles, maintaining the existing organisation. If a `Meetings` or `Decisions` category does not exist, create it.

### 8. Update the overview

Update `wiki/overview.md` if the meetings reveal a shift in direction, new themes, or resolved open questions. If the meetings are routine and don't change the big picture, skip this step.

### 9. Update the log

Append entries to `wiki/log.md` for each meeting ingested:

```
## [YYYY-MM-DD] ingest | Meeting: <Title>

Brief description of what was discussed, decisions made, and which wiki pages were created or updated.
```

### 10. Verify

- Confirm all new `[[wikilinks]]` resolve to existing articles
- Confirm every new meeting file has a summary in `wiki/sources/`
- Confirm all open action items are captured
- Confirm the index and log are up to date

## Guidelines

- **Preserve existing content** — do not rewrite articles not affected by the new meetings
- **Distinguish facts from discussions** — record confirmed decisions as facts; mark unresolved discussions as open questions
- **Attribute action items clearly** — always note the assigned owner and due date when available
- **Connect meetings to context** — link meeting notes to the projects, topics, and people they relate to
- **Note contradictions** — if a meeting reverses an earlier decision, document both the old and new position with citations
