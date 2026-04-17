"""
JARVIS Calendar Access — Windows stub.

Apple Calendar via AppleScript is macOS-only.
On Windows, this module returns empty data gracefully.
To add calendar support on Windows, integrate with Microsoft Graph API (Outlook)
or Google Calendar API in a future update.
"""

import logging
from datetime import datetime, timedelta

log = logging.getLogger("jarvis.calendar")

# Cache stubs
_event_cache: list[dict] = []
_cache_time: float = 0


async def refresh_cache():
    """No-op on Windows — Apple Calendar not available."""
    log.debug("Calendar refresh skipped (Windows — AppleScript not available)")


async def get_todays_events() -> list[dict]:
    """Returns empty list on Windows."""
    return []


async def get_upcoming_events(hours: int = 4) -> list[dict]:
    """Returns empty list on Windows."""
    return []


async def get_next_event() -> dict | None:
    """Returns None on Windows."""
    return None


async def get_calendar_names() -> list[str]:
    """Returns empty list on Windows."""
    return []


def format_events_for_context(events: list[dict]) -> str:
    """Format events as context for the LLM."""
    if not events:
        return "Calendar not available on Windows (Apple Calendar is macOS-only)."
    lines = []
    for evt in events:
        if evt.get("all_day"):
            entry = f"  All day — {evt['title']}"
        else:
            entry = f"  {evt['start']} — {evt['title']}"
        if evt.get("calendar"):
            entry += f" [{evt['calendar']}]"
        lines.append(entry)
    return "\n".join(lines)


def format_schedule_summary(events: list[dict]) -> str:
    """Format a brief voice-friendly summary of the schedule."""
    if not events:
        return "Calendar integration is not available on Windows, sir."

    count = len(events)
    if count == 1:
        evt = events[0]
        if evt.get("all_day"):
            return f"You have one all-day event: {evt['title']}."
        return f"You have one event: {evt['title']} at {evt['start']}."

    summaries = []
    for evt in events[:5]:
        if evt.get("all_day"):
            summaries.append(f"{evt['title']} all day")
        else:
            summaries.append(f"{evt['title']} at {evt['start']}")

    result = f"You have {count} events today. "
    result += ". ".join(summaries[:3])
    if count > 3:
        result += f". And {count - 3} more."
    return result
