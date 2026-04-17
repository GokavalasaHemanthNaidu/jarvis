"""
JARVIS Mail Access — Windows stub.
Apple Mail via AppleScript is macOS-only. Returns empty data on Windows.
"""
import logging
log = logging.getLogger("jarvis.mail")

async def get_accounts(): return []
async def get_unread_count(): return {"total": 0, "accounts": {}}
async def get_recent_messages(count=10): return []
async def get_unread_messages(count=10): return []
async def get_messages_from_account(account_name, count=10): return []
async def search_mail(query, count=10): return []
async def read_message(subject_match): return None

def format_unread_summary(unread):
    return "Mail integration is not available on Windows, sir."

def format_messages_for_context(messages, label="Recent emails"):
    return "Mail integration not available on Windows (Apple Mail is macOS-only)."

def format_messages_for_voice(messages):
    return "Mail integration is not available on Windows, sir."

def _short_sender(sender):
    if "<" in sender: return sender.split("<")[0].strip().strip('"')
    if "@" in sender: return sender.split("@")[0]
    return sender
