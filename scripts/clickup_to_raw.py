#!/usr/bin/env python3
"""
ClickUp to Raw Source Importer

Reads spaces, lists, tasks, and comments from the ClickUp API and saves them
as raw markdown files in raw/articles/ ready for wiki ingestion.

Usage:
    export CLICKUP_API_TOKEN=your_token_here
    export CLICKUP_TEAM_ID=your_team_id    # optional; prompted if omitted
    python scripts/clickup_to_raw.py

Authentication:
    Create a personal API token at https://app.clickup.com/settings/apps

Output:
    raw/articles/YYYY-MM-DD_clickup-<space-slug>.md  (one file per space)
"""

import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' library not installed.")
    print("Run:  pip install -r scripts/requirements.txt")
    sys.exit(1)

BASE_URL = "https://api.clickup.com/api/v2"
# Output directory relative to this script's parent (the repo root)
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "raw" / "articles"

# Seconds to wait between API calls to stay within ClickUp rate limits
REQUEST_DELAY = 0.5


# ---------------------------------------------------------------------------
# ClickUp API client
# ---------------------------------------------------------------------------

class ClickUpClient:
    """Thin wrapper around the ClickUp v2 REST API."""

    def __init__(self, api_token: str) -> None:
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": api_token,
            "Content-Type": "application/json",
        })

    def _get(self, path: str, params: dict = None) -> dict:
        url = f"{BASE_URL}/{path.lstrip('/')}"
        response = self._session.get(url, params=params, timeout=30)
        response.raise_for_status()
        time.sleep(REQUEST_DELAY)
        return response.json()

    def get_teams(self) -> list:
        return self._get("/team").get("teams", [])

    def get_spaces(self, team_id: str) -> list:
        return self._get(f"/team/{team_id}/space", {"archived": "false"}).get("spaces", [])

    def get_folders(self, space_id: str) -> list:
        return self._get(f"/space/{space_id}/folder", {"archived": "false"}).get("folders", [])

    def get_lists_in_space(self, space_id: str) -> list:
        """Return folderless lists directly inside a space."""
        return self._get(f"/space/{space_id}/list", {"archived": "false"}).get("lists", [])

    def get_lists_in_folder(self, folder_id: str) -> list:
        return self._get(f"/folder/{folder_id}/list", {"archived": "false"}).get("lists", [])

    def get_tasks(self, list_id: str) -> list:
        """Return all tasks in a list, paginating through all pages."""
        tasks = []
        page = 0
        while True:
            data = self._get(f"/list/{list_id}/task", {
                "archived": "false",
                "page": page,
                "subtasks": "true",
            })
            batch = data.get("tasks", [])
            tasks.extend(batch)
            if not batch or data.get("last_page", False):
                break
            page += 1
        return tasks

    def get_task_comments(self, task_id: str) -> list:
        return self._get(f"/task/{task_id}/comment").get("comments", [])


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    """Convert a name to a URL/filename-safe slug (max 50 chars)."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:50]


def format_date(timestamp_ms) -> str:
    """Convert a ClickUp millisecond timestamp to YYYY-MM-DD, or empty string."""
    if not timestamp_ms:
        return ""
    try:
        ts = int(timestamp_ms) / 1000
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
    except (ValueError, OSError, OverflowError):
        return ""


def comment_text_to_str(comment_text) -> str:
    """ClickUp comment_text can be a plain string or a rich-text list of nodes."""
    if isinstance(comment_text, str):
        return comment_text
    if isinstance(comment_text, list):
        parts = []
        for item in comment_text:
            if isinstance(item, dict):
                parts.append(item.get("text", ""))
            elif isinstance(item, str):
                parts.append(item)
        return "".join(parts)
    return str(comment_text)


# ---------------------------------------------------------------------------
# Markdown renderers
# ---------------------------------------------------------------------------

def render_task(task: dict, comments: list, heading_level: int = 3) -> str:
    h = "#" * heading_level
    h_sub = "#" * (heading_level + 1)
    lines = []

    lines.append(f"{h} {task.get('name', 'Untitled Task')}")
    lines.append("")

    status = task.get("status", {})
    status_name = status.get("status", "") if isinstance(status, dict) else str(status)
    if status_name:
        lines.append(f"**Status:** {status_name}  ")

    assignees = task.get("assignees", [])
    if assignees:
        names = [a.get("username") or a.get("email", "") for a in assignees]
        lines.append(f"**Assignees:** {', '.join(n for n in names if n)}  ")

    due = format_date(task.get("due_date"))
    if due:
        lines.append(f"**Due Date:** {due}  ")

    created = format_date(task.get("date_created"))
    if created:
        lines.append(f"**Created:** {created}  ")

    url = task.get("url", "")
    if url:
        lines.append(f"**URL:** {url}  ")

    description = task.get("description", "").strip()
    if description:
        lines.append("")
        lines.append(description)

    if comments:
        lines.append("")
        lines.append(f"{h_sub} Comments")
        lines.append("")
        for comment in comments:
            user = comment.get("user", {})
            username = user.get("username") or user.get("email", "Unknown")
            comment_date = format_date(comment.get("date"))
            text = comment_text_to_str(comment.get("comment_text", "")).strip()
            if text:
                date_str = f" ({comment_date})" if comment_date else ""
                lines.append(f"- **{username}**{date_str}: {text}")

    lines.append("")
    return "\n".join(lines)


def render_list_section(list_data: dict, tasks: list, task_comments: dict) -> str:
    lines = []
    lines.append(f"## List: {list_data.get('name', 'Untitled List')}")
    lines.append("")

    if not tasks:
        lines.append("_No tasks found._")
        lines.append("")
        return "\n".join(lines)

    for task in tasks:
        task_id = task.get("id", "")
        comments = task_comments.get(task_id, [])
        lines.append(render_task(task, comments, heading_level=3))

    return "\n".join(lines)


def render_space_document(
    space,
    folders,
    folder_lists,
    space_lists,
    all_tasks,
    all_comments,
    date_str,
):
    """Render a complete markdown document for one ClickUp space."""
    space_name = space.get("name", "Untitled Space")
    space_id = space.get("id", "")

    lines = [
        "---",
        "source: clickup",
        f"space: {space_name}",
        f"space_id: {space_id}",
        f"date: {date_str}",
        "tags: [clickup, tasks]",
        "---",
        "",
        f"# {space_name} (ClickUp)",
        "",
    ]

    # Folderless lists appear first
    for lst in space_lists:
        list_id = lst.get("id", "")
        tasks = all_tasks.get(list_id, [])
        comments = all_comments.get(list_id, {})
        lines.append(render_list_section(lst, tasks, comments))

    # Folders and their lists
    for folder in folders:
        folder_name = folder.get("name", "Untitled Folder")
        folder_id = folder.get("id", "")
        lines.append(f"## Folder: {folder_name}")
        lines.append("")
        for lst in folder_lists.get(folder_id, []):
            list_id = lst.get("id", "")
            tasks = all_tasks.get(list_id, [])
            comments = all_comments.get(list_id, {})
            lines.append(render_list_section(lst, tasks, comments))

    lines += [
        "## Sources",
        "",
        f"- ClickUp Space: {space_name} (ID: {space_id})",
        f"- Exported: {date_str}",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def resolve_team_id(client):
    """Return team_id from env var or by prompting the user."""
    team_id = os.environ.get("CLICKUP_TEAM_ID", "").strip()
    if team_id:
        return team_id

    print("Fetching teams...")
    teams = client.get_teams()
    if not teams:
        print("Error: No teams found for this API token.")
        sys.exit(1)
    if len(teams) == 1:
        tid = teams[0]["id"]
        print(f"Using team: {teams[0]['name']} ({tid})")
        return tid

    print("Multiple teams found:")
    for i, t in enumerate(teams):
        print(f"  [{i}] {t['name']} ({t['id']})")
    choice = input("Enter team number [0]: ").strip() or "0"
    return teams[int(choice)]["id"]


def main():
    api_token = os.environ.get("CLICKUP_API_TOKEN", "").strip()
    if not api_token:
        print("Error: CLICKUP_API_TOKEN environment variable is not set.")
        print("Get your personal token at: https://app.clickup.com/settings/apps")
        sys.exit(1)

    client = ClickUpClient(api_token)
    date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    team_id = resolve_team_id(client)

    print(f"Fetching spaces for team {team_id}...")
    spaces = client.get_spaces(team_id)
    print(f"Found {len(spaces)} space(s).")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for space in spaces:
        space_name = space.get("name", "Untitled")
        space_id = space.get("id", "")
        print(f"\nProcessing space: {space_name} ({space_id})")

        print("  Fetching folders...")
        folders = client.get_folders(space_id)

        print("  Fetching folderless lists...")
        space_lists = client.get_lists_in_space(space_id)

        folder_lists = {}
        for folder in folders:
            fid = folder.get("id", "")
            fname = folder.get("name", "")
            print(f"  Fetching lists for folder: {fname}...")
            folder_lists[fid] = client.get_lists_in_folder(fid)

        # All lists across folders and standalone
        all_list_objects = list(space_lists)
        for lists in folder_lists.values():
            all_list_objects.extend(lists)

        all_tasks = {}
        all_comments = {}
        for lst in all_list_objects:
            list_id = lst.get("id", "")
            list_name = lst.get("name", "")
            print(f"  Fetching tasks for list: {list_name}...")
            tasks = client.get_tasks(list_id)
            all_tasks[list_id] = tasks

            list_comments = {}
            for task in tasks:
                task_id = task.get("id", "")
                comments = client.get_task_comments(task_id)
                if comments:
                    list_comments[task_id] = comments
            all_comments[list_id] = list_comments

        doc = render_space_document(
            space, folders, folder_lists, space_lists,
            all_tasks, all_comments, date_str,
        )

        slug = slugify(space_name)
        filename = f"{date_str}_clickup-{slug}.md"
        output_path = OUTPUT_DIR / filename
        output_path.write_text(doc, encoding="utf-8")
        print(f"  Saved: raw/articles/{filename}")

    print(f"\nDone! Imported {len(spaces)} space(s) to raw/articles/")
    print("Next steps:")
    print("  1. Review the files in raw/articles/")
    print("  2. Use _prompts/ingest-clickup.md to integrate them into the wiki")


if __name__ == "__main__":
    main()
