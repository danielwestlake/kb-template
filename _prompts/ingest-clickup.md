# ClickUp Ingest Prompt

After running the ClickUp importer script (`scripts/clickup_to_raw.py`), use this
prompt to integrate the imported data into the knowledge base wiki.

## Steps

1. **Find new ClickUp files** — scan `raw/articles/` for files matching
   `YYYY-MM-DD_clickup-*.md`. Compare against `wiki/index.md` to identify
   which files have not yet been ingested.

2. **Read and analyse each new file** — for each ClickUp source:
   - Identify the space name, lists, task statuses, assignees, and due dates
   - Note recurring themes, blockers, priorities, and decisions in comments
   - Identify key people (frequent assignees) and projects (spaces/lists)

3. **Create a source summary** — write `wiki/sources/YYYY-MM-DD_clickup-<slug>.md`
   following the standard wiki page format (YAML frontmatter, wikilinks, sources
   section).

4. **Update or create concept pages** — based on the data:
   - **Project status page** — current state of each list/space
   - **Team workload page** — tasks per assignee, workload balance
   - **Blockers and risks** — tasks overdue, unassigned, or stalled
   - **Decisions log** — comments that represent decisions or key context
   - Create new pages for recurring themes not yet in the wiki

5. **Update `wiki/index.md`** — add all new pages with one-line summaries and
   metadata. Keep categories consistent with existing entries.

6. **Update `wiki/overview.md`** — if the ClickUp data shifts the big picture
   (new projects, major completions, team changes), update the narrative.

7. **Append to `wiki/log.md`** — use the format:
   ```
   ## [YYYY-MM-DD] ingest | ClickUp: <Space Name>
   ```

## Tips for ClickUp data

- **Task comments often carry the real context** — decisions, blockers, and
  rationale are frequently in comments, not in task descriptions.
- **Status names vary** by workspace. Normalise to Open / In Progress / Done
  equivalents when writing wiki pages so cross-space comparisons are readable.
- **Due dates signal priorities** — tasks with past due dates in Open status
  are worth flagging on a blockers/risks page.
- **Frequent assignees** may warrant their own wiki pages as key stakeholders.
- **Space = project boundary** — consider one wiki project page per ClickUp space.
