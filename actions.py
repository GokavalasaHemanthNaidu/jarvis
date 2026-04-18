"""
JARVIS Action Executor — Windows-native system actions.

Execute actions IMMEDIATELY, before generating any LLM response.
Each function returns {"success": bool, "confirmation": str}.
"""

import asyncio
import logging
import os
import re
import subprocess
import time
import webbrowser
from pathlib import Path
from urllib.parse import quote

log = logging.getLogger("jarvis.actions")

DESKTOP_PATH = Path.home() / "Desktop"


async def open_terminal(command: str = "") -> dict:
    """Open Windows Terminal (or PowerShell) and optionally run a command."""
    try:
        if command:
            # Try Windows Terminal first, fall back to PowerShell
            try:
                proc = await asyncio.create_subprocess_exec(
                    "wt", "-w", "0", "new-tab", "powershell", "-NoExit", "-Command", command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await asyncio.wait_for(proc.communicate(), timeout=5)
                success = proc.returncode == 0
            except FileNotFoundError:
                # Fall back to PowerShell directly
                subprocess.Popen(
                    ["powershell", "-NoExit", "-Command", command],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
                success = True
        else:
            try:
                proc = await asyncio.create_subprocess_exec(
                    "wt",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await asyncio.wait_for(proc.communicate(), timeout=5)
                success = proc.returncode == 0
            except FileNotFoundError:
                subprocess.Popen(
                    ["powershell"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
                success = True

        return {
            "success": success,
            "confirmation": "Terminal is open, sir." if success else "I had trouble opening Terminal, sir.",
        }
    except Exception as e:
        log.error(f"open_terminal failed: {e}")
        return {"success": False, "confirmation": "I had trouble opening Terminal, sir."}


async def open_browser(url: str, browser: str = "chrome") -> dict:
    """Open URL in the default browser (or Chrome/Firefox if available)."""
    try:
        if browser.lower() == "firefox":
            try:
                subprocess.Popen(["firefox", url])
                app_name = "Firefox"
                success = True
            except FileNotFoundError:
                webbrowser.open(url)
                app_name = "your browser"
                success = True
        else:
            # Try Chrome explicitly, fall back to default browser
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
            chrome_found = False
            for chrome_path in chrome_paths:
                if Path(chrome_path).exists():
                    subprocess.Popen([chrome_path, url])
                    chrome_found = True
                    break
            if not chrome_found:
                webbrowser.open(url)
            app_name = "Chrome" if chrome_found else "your browser"
            success = True

        return {
            "success": success,
            "confirmation": f"Pulled that up in {app_name}, sir.",
        }
    except Exception as e:
        log.error(f"open_browser failed: {e}")
        return {"success": False, "confirmation": "Browser ran into a problem, sir."}


# Keep backward compat
async def open_chrome(url: str) -> dict:
    return await open_browser(url, "chrome")


async def open_claude_in_project(project_dir: str, prompt: str) -> dict:
    """Open a new PowerShell window, cd to project dir, run Claude Code."""
    # Write prompt to CLAUDE.md — claude reads this automatically
    claude_md = Path(project_dir) / "CLAUDE.md"
    claude_md.write_text(
        f"# Task\n\n{prompt}\n\nBuild this completely. If web app, make index.html work standalone.\n"
    )

    try:
        command = f"cd '{project_dir}'; claude --dangerously-skip-permissions"
        try:
            subprocess.Popen(
                ["wt", "-w", "0", "new-tab", "powershell", "-NoExit", "-Command", command],
            )
        except FileNotFoundError:
            subprocess.Popen(
                ["powershell", "-NoExit", "-Command", command],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        return {
            "success": True,
            "confirmation": "Claude Code is running in a new terminal, sir. You can watch the progress.",
        }
    except Exception as e:
        log.error(f"open_claude_in_project failed: {e}")
        return {"success": False, "confirmation": "Had trouble spawning Claude Code, sir."}


async def prompt_existing_terminal(project_name: str, prompt: str) -> dict:
    """On Windows, we open a new terminal for the project (no keystroke injection)."""
    # Windows doesn't support AppleScript keystroke injection — open fresh terminal
    project_dir = str(DESKTOP_PATH / project_name)
    if Path(project_dir).exists():
        return await open_claude_in_project(project_dir, prompt)
    else:
        return {
            "success": False,
            "confirmation": f"Couldn't find project {project_name} on Desktop, sir.",
        }


async def get_chrome_tab_info() -> dict:
    """On Windows, we can't read Chrome tabs without extensions — return empty."""
    return {}


async def monitor_build(project_dir: str, ws=None, synthesize_fn=None) -> None:
    """Monitor a Claude Code build for completion. Notify via WebSocket when done."""
    import base64

    output_file = Path(project_dir) / ".jarvis_output.txt"
    start = time.time()
    timeout = 600  # 10 minutes

    while time.time() - start < timeout:
        await asyncio.sleep(5)
        if output_file.exists():
            content = output_file.read_text()
            if "--- JARVIS TASK COMPLETE ---" in content:
                log.info(f"Build complete in {project_dir}")
                if ws and synthesize_fn:
                    try:
                        msg = "The build is complete, sir."
                        audio_bytes = await synthesize_fn(msg)
                        if audio_bytes:
                            encoded = base64.b64encode(audio_bytes).decode()
                            await ws.send_json({"type": "status", "state": "speaking"})
                            await ws.send_json({"type": "audio", "data": encoded, "text": msg})
                            await ws.send_json({"type": "status", "state": "idle"})
                    except Exception as e:
                        log.warning(f"Build notification failed: {e}")
                return

    log.warning(f"Build timed out in {project_dir}")


async def execute_action(intent: dict, projects: list = None) -> dict:
    """Route a classified intent to the right action function.

    Args:
        intent: {"action": str, "target": str} from classify_intent()
        projects: list of known project dicts for resolving working dirs

    Returns: {"success": bool, "confirmation": str, "project_dir": str | None}
    """
    action = intent.get("action", "chat")
    target = intent.get("target", "")

    if action == "open_terminal":
        result = await open_terminal("claude --dangerously-skip-permissions")
        result["project_dir"] = None
        return result

    elif action == "browse":
        if target.startswith("http://") or target.startswith("https://"):
            url = target
        else:
            url = f"https://www.google.com/search?q={quote(target)}"

        # Detect which browser user wants
        target_lower = target.lower()
        if "firefox" in target_lower:
            browser = "firefox"
        else:
            browser = "chrome"

        result = await open_browser(url, browser)
        result["project_dir"] = None
        return result

    elif action == "build":
        # Create project folder on Desktop, spawn Claude Code
        project_name = _generate_project_name(target)
        project_dir = str(DESKTOP_PATH / project_name)
        os.makedirs(project_dir, exist_ok=True)
        result = await open_claude_in_project(project_dir, target)
        result["project_dir"] = project_dir
        return result

    elif action == "open_app":
        from computer_use import open_app as _open_app
        res = await _open_app(target)
        return {"success": True, "confirmation": res, "project_dir": None}

    elif action == "type":
        from computer_use import type_text
        res = await type_text(target)
        return {"success": True, "confirmation": res, "project_dir": None}

    elif action == "press":
        from computer_use import press_key
        res = await press_key(target)
        return {"success": True, "confirmation": res, "project_dir": None}

    elif action == "shortcut":
        from computer_use import shortcut
        keys = target.split("+")
        res = await shortcut(keys)
        return {"success": True, "confirmation": res, "project_dir": None}

    else:
        return {"success": False, "confirmation": "", "project_dir": None}


def _generate_project_name(prompt: str) -> str:
    """Generate a kebab-case project folder name from the prompt."""
    # First: check for a quoted name like "tiktok-analytics-dashboard"
    quoted = re.search(r'"([^"]+)"', prompt)
    if quoted:
        name = quoted.group(1).strip()
        name = re.sub(r"[^a-zA-Z0-9\s-]", "", name).strip()
        if name:
            return re.sub(r"[\s]+", "-", name.lower())

    # Second: check for "called X" or "named X" pattern
    called = re.search(r'(?:called|named)\s+(\S+(?:[-_]\S+)*)', prompt, re.IGNORECASE)
    if called:
        name = re.sub(r"[^a-zA-Z0-9-]", "", called.group(1))
        if len(name) > 3:
            return name.lower()

    # Fallback: extract meaningful words
    words = re.sub(r"[^a-zA-Z0-9\s]", "", prompt.lower()).split()
    skip = {"a", "the", "an", "me", "build", "create", "make", "for", "with", "and",
            "to", "of", "i", "want", "need", "new", "project", "directory", "called",
            "on", "desktop", "that", "application", "app", "full", "stack", "simple",
            "web", "page", "site", "named"}
    meaningful = [w for w in words if w not in skip and len(w) > 2][:4]
    return "-".join(meaningful) if meaningful else "jarvis-project"
