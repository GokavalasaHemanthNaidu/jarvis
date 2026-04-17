"""
JARVIS Notes Access — Windows stub.
Apple Notes via AppleScript is macOS-only. Returns empty data on Windows.
"""
import logging
log = logging.getLogger("jarvis.notes")

async def get_recent_notes(count=10): return []
async def read_note(title_match): return None
async def search_notes_apple(query, count=5): return []
async def create_apple_note(title, body, folder="Notes"):
    log.info(f"Note creation skipped on Windows: {title}")
    return False
async def get_note_folders(): return []
