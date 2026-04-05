#!/usr/bin/env python3
"""
HelpScout ticket ingestion script.

Fetches conversations from the HelpScout Mailbox API and writes each one as
a Markdown file in raw/helpscout/, following the kb-template naming convention:

    YYYY-MM-DD_helpscout-<id>-<slug>.md

Usage
-----
Set credentials via environment variables (recommended):

    export HELPSCOUT_CLIENT_ID=your_client_id
    export HELPSCOUT_CLIENT_SECRET=your_client_secret

Or pass them as CLI arguments:

    python scripts/ingest_helpscout.py --client-id <id> --client-secret <secret>

Optional filters:

    --mailbox   Mailbox ID to fetch from (omit to fetch from all mailboxes)
    --status    Conversation status: active | pending | closed | spam (default: all)
    --since     Only fetch conversations updated after this date (YYYY-MM-DD)
    --max       Maximum number of conversations to fetch (default: 100)
    --output    Output directory (default: raw/helpscout relative to repo root)

Requirements
------------
    pip install requests
"""

import argparse
import os
import re
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit(
        "Error: 'requests' is not installed. Run: pip install requests"
    )

# ---------------------------------------------------------------------------
# HelpScout API helpers
# ---------------------------------------------------------------------------

HELPSCOUT_API_BASE = "https://api.helpscout.net/v2"
HELPSCOUT_TOKEN_URL = f"{HELPSCOUT_API_BASE}/tokens"


def get_access_token(client_id: str, client_secret: str) -> str:
    """Obtain an OAuth2 access token using client credentials."""
    resp = requests.post(
        HELPSCOUT_TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=30,
    )
    if not resp.ok:
        sys.exit(
            f"Authentication failed ({resp.status_code}): {resp.text}"
        )
    return resp.json()["access_token"]


def api_get(token: str, path: str, params: dict | None = None) -> dict:
    """Make an authenticated GET request to the HelpScout API."""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{HELPSCOUT_API_BASE}{path}",
        headers=headers,
        params=params or {},
        timeout=30,
    )
    if not resp.ok:
        sys.exit(
            f"API request failed [{path}] ({resp.status_code}): {resp.text}"
        )
    return resp.json()


def fetch_conversations(
    token: str,
    mailbox_id: str | None = None,
    status: str | None = None,
    since: str | None = None,
    max_count: int = 100,
) -> list[dict]:
    """Return a list of conversation objects from the API."""
    params: dict = {"pageSize": min(max_count, 50)}
    if mailbox_id:
        params["mailboxId"] = mailbox_id
    if status:
        params["status"] = status
    if since:
        # API expects ISO-8601 date-time
        params["modifiedSince"] = f"{since}T00:00:00Z"

    conversations: list[dict] = []
    page = 1

    while len(conversations) < max_count:
        params["page"] = page
        data = api_get(token, "/conversations", params)
        page_items = data.get("_embedded", {}).get("conversations", [])
        if not page_items:
            break
        conversations.extend(page_items)
        # Check pagination
        total_pages = data.get("page", {}).get("totalPages", 1)
        if page >= total_pages:
            break
        page += 1

    return conversations[:max_count]


def fetch_threads(token: str, conversation_id: int) -> list[dict]:
    """Return all threads for a given conversation."""
    data = api_get(token, f"/conversations/{conversation_id}/threads")
    return data.get("_embedded", {}).get("threads", [])


# ---------------------------------------------------------------------------
# Markdown formatting
# ---------------------------------------------------------------------------

def slugify(text: str, max_words: int = 5) -> str:
    """Convert text to a lowercase hyphenated slug (max_words words)."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    words = text.split()[:max_words]
    return "-".join(words) or "ticket"


def format_datetime(iso: str | None) -> str:
    """Return a human-readable date-time string from an ISO-8601 value."""
    if not iso:
        return "unknown"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        return iso


def customer_display(customer: dict) -> str:
    """Return a 'Name <email>' string for a customer object."""
    first = customer.get("first", "")
    last = customer.get("last", "")
    email = customer.get("email", "")
    name = f"{first} {last}".strip()
    if name and email:
        return f"{name} <{email}>"
    return name or email or "unknown"


def thread_author(thread: dict) -> str:
    """Return a display string for the thread author."""
    created_by = thread.get("createdBy", {})
    author_type = created_by.get("type", "")
    if author_type == "customer":
        return f"Customer ({customer_display(created_by)})"
    name = f"{created_by.get('first', '')} {created_by.get('last', '')}".strip()
    return f"Support Agent ({name})" if name else "Support Agent"


def strip_html(html: str) -> str:
    """Very light HTML tag removal — preserves text content."""
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<p[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def conversation_to_markdown(conv: dict, threads: list[dict]) -> str:
    """Render a HelpScout conversation and its threads as Markdown."""
    conv_id = conv.get("id", "unknown")
    subject = conv.get("subject", "(no subject)")
    status = conv.get("status", "unknown")
    created_at = conv.get("createdAt", "")
    updated_at = conv.get("updatedAt", "")
    tags = [t.get("name", "") for t in conv.get("tags", [])]
    mailbox_name = conv.get("mailbox", {}).get("name", "")
    customer_obj = conv.get("primaryCustomer", {})
    customer = customer_display(customer_obj)

    # --- YAML frontmatter ---
    tag_list = ", ".join(tags) if tags else ""
    frontmatter_lines = [
        "---",
        "source: helpscout",
        f"ticket_id: {conv_id}",
    ]
    if mailbox_name:
        frontmatter_lines.append(f"mailbox: {mailbox_name}")
    frontmatter_lines += [
        f'subject: "{subject}"',
        f"customer: {customer}",
        f"status: {status}",
        f"created_at: {format_datetime(created_at)}",
        f"updated_at: {format_datetime(updated_at)}",
    ]
    if tag_list:
        frontmatter_lines.append(f"tags: [{tag_list}]")
    frontmatter_lines.append("---")

    # --- Header ---
    header = textwrap.dedent(f"""\
        # {subject}

        **Ticket ID:** {conv_id}  
        **Status:** {status}  
        **Customer:** {customer}  
        **Created:** {format_datetime(created_at)}  
        **Updated:** {format_datetime(updated_at)}  
    """)
    if mailbox_name:
        header += f"**Mailbox:** {mailbox_name}  \n"
    if tags:
        header += f"**Tags:** {', '.join(tags)}  \n"

    # --- Threads ---
    thread_sections: list[str] = ["---", "", "## Conversation"]
    for thread in threads:
        thread_type = thread.get("type", "")
        # Skip internal line items (status changes, assignments, etc.)
        if thread_type == "lineitem":
            continue
        created = format_datetime(thread.get("createdAt", ""))
        author = thread_author(thread)
        body_html = thread.get("body", "")
        body = strip_html(body_html) if body_html else "_no content_"
        thread_sections.append(f"\n### {author} — {created}\n")
        thread_sections.append(body)

    return (
        "\n".join(frontmatter_lines)
        + "\n\n"
        + header
        + "\n"
        + "\n".join(thread_sections)
        + "\n"
    )


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def output_filename(conv: dict) -> str:
    """Return the raw/ filename for a conversation."""
    created_at = conv.get("createdAt", "")
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        date_prefix = dt.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        date_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    conv_id = conv.get("id", "unknown")
    subject = conv.get("subject", "ticket")
    slug = slugify(subject)
    return f"{date_prefix}_helpscout-{conv_id}-{slug}.md"


def resolve_output_dir(output_arg: str | None) -> Path:
    """Return the resolved output directory path."""
    if output_arg:
        return Path(output_arg).expanduser().resolve()
    # Default: raw/helpscout relative to the repo root (two levels up from
    # scripts/) when the script is invoked from anywhere inside the repo.
    script_dir = Path(__file__).resolve().parent
    return script_dir.parent / "raw" / "helpscout"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest HelpScout tickets as Markdown into raw/helpscout/",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--client-id",
        default=os.environ.get("HELPSCOUT_CLIENT_ID"),
        help="HelpScout OAuth2 client ID (or set HELPSCOUT_CLIENT_ID env var)",
    )
    parser.add_argument(
        "--client-secret",
        default=os.environ.get("HELPSCOUT_CLIENT_SECRET"),
        help="HelpScout OAuth2 client secret (or set HELPSCOUT_CLIENT_SECRET env var)",
    )
    parser.add_argument(
        "--mailbox",
        default=None,
        help="Mailbox ID to fetch from (omit for all mailboxes)",
    )
    parser.add_argument(
        "--status",
        default=None,
        choices=["active", "pending", "closed", "spam"],
        help="Filter by conversation status",
    )
    parser.add_argument(
        "--since",
        default=None,
        metavar="YYYY-MM-DD",
        help="Only fetch conversations updated on or after this date",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=100,
        metavar="N",
        help="Maximum number of conversations to fetch (default: 100)",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="DIR",
        help="Output directory (default: raw/helpscout/)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.client_id or not args.client_secret:
        sys.exit(
            "Error: HelpScout credentials are required.\n"
            "Set HELPSCOUT_CLIENT_ID and HELPSCOUT_CLIENT_SECRET environment "
            "variables, or pass --client-id and --client-secret."
        )

    output_dir = resolve_output_dir(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Authenticating with HelpScout API...")
    token = get_access_token(args.client_id, args.client_secret)

    print(
        f"Fetching up to {args.max} conversations"
        + (f" from mailbox {args.mailbox}" if args.mailbox else "")
        + (f" with status '{args.status}'" if args.status else "")
        + (f" updated since {args.since}" if args.since else "")
        + "..."
    )
    conversations = fetch_conversations(
        token,
        mailbox_id=args.mailbox,
        status=args.status,
        since=args.since,
        max_count=args.max,
    )
    print(f"Found {len(conversations)} conversation(s).")

    written = 0
    skipped = 0
    for conv in conversations:
        filename = output_filename(conv)
        dest = output_dir / filename
        if dest.exists():
            print(f"  [skip] {filename} (already exists)")
            skipped += 1
            continue

        conv_id = conv.get("id")
        threads = fetch_threads(token, conv_id)
        markdown = conversation_to_markdown(conv, threads)

        dest.write_text(markdown, encoding="utf-8")
        print(f"  [write] {filename}")
        written += 1

    print(
        f"\nDone. {written} file(s) written, {skipped} skipped. "
        f"Output: {output_dir}"
    )


if __name__ == "__main__":
    main()
