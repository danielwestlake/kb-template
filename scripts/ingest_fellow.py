#!/usr/bin/env python3
"""
Ingest meeting notes from the Fellow API into raw/meetings/.

For each meeting retrieved, a markdown file is written to raw/meetings/ using
the naming convention: YYYY-MM-DD_<slug>.md

Each file contains:
  - Meeting title, date, and duration
  - Attendee list
  - Agenda / meeting notes
  - Action items

Usage
-----
    python scripts/ingest_fellow.py [--since YYYY-MM-DD] [--until YYYY-MM-DD]

Environment variables
---------------------
FELLOW_API_KEY   Your Fellow API key (required).  Copy from
                 Fellow → Settings → Integrations → API.
FELLOW_API_URL   Base URL for the Fellow API (optional).
                 Defaults to https://api.fellow.app/v2

See .env.example for a ready-to-copy template.
"""

import argparse
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit(
        "Missing dependency: run  pip install -r scripts/requirements.txt  first."
    )

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional; rely on shell environment

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FELLOW_API_KEY = os.environ.get("FELLOW_API_KEY", "")
FELLOW_API_URL = os.environ.get("FELLOW_API_URL", "https://api.fellow.app/v2").rstrip("/")

RAW_MEETINGS_DIR = Path(__file__).parent.parent / "raw" / "meetings"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _session() -> requests.Session:
    """Return an authenticated requests Session."""
    if not FELLOW_API_KEY:
        sys.exit(
            "FELLOW_API_KEY environment variable is not set.\n"
            "Copy .env.example to .env and fill in your API key."
        )
    s = requests.Session()
    s.headers.update(
        {
            "Authorization": f"Bearer {FELLOW_API_KEY}",
            "Accept": "application/json",
        }
    )
    return s


def _slugify(text: str, max_words: int = 5) -> str:
    """Convert a title into a lowercase hyphen-separated slug (3-5 words)."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    words = text.split()[:max_words]
    return "-".join(words) if words else "meeting"


def _format_date(value: str | None) -> str:
    """Return an ISO date string (YYYY-MM-DD) from an ISO 8601 value, or empty string."""
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.date().isoformat()
    except ValueError:
        return value[:10]


# ---------------------------------------------------------------------------
# Fellow API calls
# ---------------------------------------------------------------------------


def fetch_meetings(
    session: requests.Session,
    since: date | None,
    until: date | None,
) -> list[dict]:
    """Fetch all meetings in the given date range, handling pagination."""
    params: dict = {}
    if since:
        params["start_date"] = since.isoformat()
    if until:
        params["end_date"] = until.isoformat()

    meetings: list[dict] = []
    url = f"{FELLOW_API_URL}/meetings"

    while url:
        resp = session.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        # Support both list and paginated envelope responses
        if isinstance(data, list):
            meetings.extend(data)
            break
        else:
            meetings.extend(data.get("data", data.get("meetings", [])))
            # Common pagination patterns: next_page_url / next / links.next
            url = (
                data.get("next_page_url")
                or data.get("next")
                or (data.get("links") or {}).get("next")
            )
        params = {}  # params are encoded in the pagination URL already

    return meetings


def fetch_meeting_detail(session: requests.Session, meeting_id: str) -> dict:
    """Fetch full detail for a single meeting (notes, attendees, action items)."""
    resp = session.get(f"{FELLOW_API_URL}/meetings/{meeting_id}")
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def _render_attendees(attendees: list[dict]) -> str:
    lines = []
    for a in attendees:
        name = a.get("name") or a.get("display_name") or a.get("email") or "Unknown"
        email = a.get("email", "")
        entry = f"- {name}"
        if email and email != name:
            entry += f" <{email}>"
        lines.append(entry)
    return "\n".join(lines) if lines else "_No attendees recorded._"


def _render_notes(notes) -> str:
    """Render agenda / meeting notes.

    Notes can arrive as a plain string, a list of section dicts, or None.
    """
    if not notes:
        return "_No notes recorded._"
    if isinstance(notes, str):
        return notes.strip() or "_No notes recorded._"
    if isinstance(notes, list):
        sections = []
        for item in notes:
            if isinstance(item, str):
                sections.append(item.strip())
            elif isinstance(item, dict):
                heading = item.get("title") or item.get("heading") or ""
                body = item.get("body") or item.get("content") or item.get("notes") or ""
                if heading:
                    sections.append(f"### {heading}\n\n{body}".strip())
                elif body:
                    sections.append(str(body).strip())
        return "\n\n".join(s for s in sections if s) or "_No notes recorded._"
    return str(notes).strip() or "_No notes recorded._"


def _render_action_items(items: list[dict]) -> str:
    if not items:
        return "_No action items recorded._"
    lines = []
    for item in items:
        title = item.get("title") or item.get("description") or item.get("text") or "Untitled action"
        assignee = item.get("assignee") or {}
        assignee_name = (
            assignee.get("name") or assignee.get("display_name") or assignee.get("email")
            if isinstance(assignee, dict)
            else str(assignee)
        )
        due = _format_date(item.get("due_date") or item.get("due"))
        done = item.get("completed") or item.get("done") or False

        checkbox = "- [x]" if done else "- [ ]"
        parts = [f"{checkbox} {title}"]
        if assignee_name:
            parts.append(f"  - **Assignee:** {assignee_name}")
        if due:
            parts.append(f"  - **Due:** {due}")
        lines.append("\n".join(parts))
    return "\n".join(lines)


def render_meeting_markdown(detail: dict) -> str:
    """Convert a Fellow meeting detail dict into a markdown document."""
    title = detail.get("title") or detail.get("name") or "Untitled Meeting"
    meeting_date = _format_date(
        detail.get("start_date_time")
        or detail.get("start_time")
        or detail.get("date")
        or detail.get("created_at")
    )
    duration_min = detail.get("duration") or detail.get("duration_minutes") or ""
    duration_str = f"{duration_min} min" if duration_min else ""

    attendees = detail.get("attendees") or detail.get("participants") or []
    notes = detail.get("notes") or detail.get("agenda") or detail.get("meeting_notes") or []
    action_items = (
        detail.get("action_items")
        or detail.get("tasks")
        or detail.get("follow_up_items")
        or []
    )

    lines = [
        f"# {title}",
        "",
        "## Metadata",
        "",
        f"- **Date:** {meeting_date or 'Unknown'}",
    ]
    if duration_str:
        lines.append(f"- **Duration:** {duration_str}")
    meeting_id = detail.get("id") or detail.get("meeting_id") or ""
    if meeting_id:
        lines.append(f"- **Fellow ID:** {meeting_id}")
    lines += [
        "",
        "## Attendees",
        "",
        _render_attendees(attendees),
        "",
        "## Meeting Notes",
        "",
        _render_notes(notes),
        "",
        "## Action Items",
        "",
        _render_action_items(action_items),
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# File output
# ---------------------------------------------------------------------------


def meeting_filename(detail: dict) -> str:
    """Return the YYYY-MM-DD_slug.md filename for a meeting."""
    raw_date = (
        detail.get("start_date_time")
        or detail.get("start_time")
        or detail.get("date")
        or detail.get("created_at")
    )
    file_date = _format_date(raw_date) or date.today().isoformat()
    title = detail.get("title") or detail.get("name") or "meeting"
    slug = _slugify(title)
    return f"{file_date}_{slug}.md"


def write_meeting_file(detail: dict, output_dir: Path, overwrite: bool = False) -> Path:
    """Write the meeting markdown to output_dir and return the path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = meeting_filename(detail)
    filepath = output_dir / filename

    if filepath.exists() and not overwrite:
        print(f"  [skip] {filename} already exists (use --overwrite to replace)")
        return filepath

    action = "overwrite" if filepath.exists() else "write"
    content = render_meeting_markdown(detail)
    filepath.write_text(content, encoding="utf-8")
    print(f"  [{action}] {filename}")
    return filepath


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch Fellow meeting notes and write them to raw/meetings/."
    )
    parser.add_argument(
        "--since",
        metavar="YYYY-MM-DD",
        help="Only fetch meetings on or after this date (inclusive).",
    )
    parser.add_argument(
        "--until",
        metavar="YYYY-MM-DD",
        help="Only fetch meetings on or before this date (inclusive).",
    )
    parser.add_argument(
        "--output-dir",
        metavar="PATH",
        default=str(RAW_MEETINGS_DIR),
        help=f"Directory to write meeting files into (default: {RAW_MEETINGS_DIR}).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files. By default existing files are skipped.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written without creating any files.",
    )
    return parser.parse_args()


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        sys.exit(f"Invalid date format '{value}' — expected YYYY-MM-DD.")


def main() -> None:
    args = parse_args()
    since = _parse_date(args.since)
    until = _parse_date(args.until)
    output_dir = Path(args.output_dir)

    session = _session()

    print(f"Fetching meetings from Fellow API ({FELLOW_API_URL}) …")
    meetings = fetch_meetings(session, since, until)
    print(f"Found {len(meetings)} meeting(s).")

    if not meetings:
        return

    written = 0
    for m in meetings:
        meeting_id = m.get("id") or m.get("meeting_id")
        if not meeting_id:
            print("  [warn] Meeting entry has no id — skipping.")
            continue

        print(f"  Fetching detail for meeting {meeting_id} …")
        try:
            detail = fetch_meeting_detail(session, str(meeting_id))
        except requests.HTTPError as exc:
            print(f"  [error] Could not fetch meeting {meeting_id}: {exc}")
            continue

        if args.dry_run:
            filename = meeting_filename(detail)
            print(f"  [dry-run] would write {output_dir / filename}")
            continue

        write_meeting_file(detail, output_dir, overwrite=args.overwrite)
        written += 1

    if not args.dry_run:
        print(f"\nDone. {written} file(s) written to {output_dir}/")
        print("Next step: run the update-wiki prompt to integrate the new meeting notes.")


if __name__ == "__main__":
    main()
