import logging
import asyncio
import time
import pyautogui

log = logging.getLogger("jarvis.computer_use")

# Set pyautogui failsafe to True (moving mouse to corner aborts)
pyautogui.FAILSAFE = True
# Small pause after every action
pyautogui.PAUSE = 0.5

async def open_app(app_name: str) -> str:
    """Opens an application using the Windows Start menu search."""
    try:
        log.info(f"Opening app: {app_name}")
        pyautogui.press('win')
        await asyncio.sleep(0.5)
        pyautogui.write(app_name, interval=0.05)
        await asyncio.sleep(0.5)
        pyautogui.press('enter')
        return f"Opened {app_name}"
    except Exception as e:
        log.error(f"Failed to open app {app_name}: {e}")
        return f"Failed to open {app_name}: {e}"

async def type_text(text: str, hit_enter: bool = True) -> str:
    """Types text at the current cursor location."""
    try:
        log.info(f"Typing text: {text[:20]}...")
        pyautogui.write(text, interval=0.02)
        if hit_enter:
            pyautogui.press('enter')
        return f"Typed text: {text}"
    except Exception as e:
        log.error(f"Failed to type text: {e}")
        return f"Failed to type text: {e}"

async def press_key(key: str) -> str:
    """Presses a specific key (e.g., 'enter', 'tab', 'esc', 'win')."""
    try:
        log.info(f"Pressing key: {key}")
        pyautogui.press(key)
        return f"Pressed {key}"
    except Exception as e:
        log.error(f"Failed to press key {key}: {e}")
        return f"Failed to press {key}: {e}"

async def shortcut(keys: list[str]) -> str:
    """Executes a keyboard shortcut (e.g., ['ctrl', 'c'])."""
    try:
        log.info(f"Executing shortcut: {'+'.join(keys)}")
        pyautogui.hotkey(*keys)
        return f"Executed shortcut: {'+'.join(keys)}"
    except Exception as e:
        return f"Failed shortcut: {e}"
