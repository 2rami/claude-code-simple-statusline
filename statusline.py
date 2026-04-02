#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

"""
Claude Code Statusline

A simple, minimal statusline for Claude Code with
configurable icons and intelligent prompt classification.

Wide:   Opus 4.5 |  main |  my-project |  42% |  create...
Narrow:  Opus 4.5 |  main |  my-project |  42% |  ...
"""

import json
import os
import sys
import subprocess
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BOLD = "\033[1m"
RESET = "\033[0m"

# ── Icon Presets ─────────────────────────────────────────────────────
ICON_PRESETS = {
    "nerd-font": {
        "model": "\uf233",     "git": "\ue0a0",      "folder": "\uf07b",
        "context": "\uf0e4",   "command": "\uf120",   "question": "\uf128",
        "delete": "\uf1f8",    "edit": "\uf040",      "create": "\uf067",
        "search": "\uf002",    "chat": "\uf075",      "idle": "\uf10c",
    },
    "unicode": {
        "model": ">",          "git": "*",            "folder": "~",
        "context": "%",        "command": "$",        "question": "?",
        "delete": "x",         "edit": "~",           "create": "+",
        "search": "/",         "chat": "#",           "idle": ".",
    },
    "plain": {
        "model": "[M]",        "git": "[G]",          "folder": "[D]",
        "context": "[C]",      "command": "[>]",      "question": "[?]",
        "delete": "[-]",       "edit": "[~]",         "create": "[+]",
        "search": "[/]",       "chat": "[#]",         "idle": "[.]",
    },
}

# ── Default Tokyo Night Palette ─────────────────────────────────────
DEFAULT_COLORS = {
    "model": "#7aa2f7",    "git": "#73daca",      "folder": "#bb9af7",
    "context": "#ff9e64",  "separator": "#565f89",
    "prompt": {
        "command": "#e0af68",  "question": "#7aa2f7", "delete": "#f7768e",
        "edit": "#e0af68",     "create": "#73daca",   "search": "#bb9af7",
        "chat": "#c0caf5",     "idle": "#565f89",
    },
}


def hex_to_ansi(hex_color):
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"\033[38;2;{r};{g};{b}m"


def load_config():
    config_paths = [
        Path.home() / ".claude" / "statusline-config.json",
        Path(__file__).parent / "config.json",
    ]
    for p in config_paths:
        if p.exists():
            try:
                with open(p, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
    return {}


def build_icons(cfg):
    preset_name = cfg.get("icon_set", "nerd-font")
    icons = dict(ICON_PRESETS.get(preset_name, ICON_PRESETS["nerd-font"]))

    custom = cfg.get("icons", {})
    for key in ["model", "git", "folder", "context"]:
        if key in custom:
            icons[key] = custom[key]

    prompt_custom = custom.get("prompt", {})
    for key in ["command", "question", "delete", "edit", "create", "search", "chat", "idle"]:
        if key in prompt_custom:
            icons[key] = prompt_custom[key]

    return icons


def build_colors(cfg):
    colors = {}
    custom = cfg.get("colors", {})

    for key in ["model", "git", "folder", "context", "separator"]:
        hex_val = custom.get(key, DEFAULT_COLORS.get(key))
        colors[key] = hex_to_ansi(hex_val)

    prompt_custom = custom.get("prompt", {})
    colors["prompt"] = {}
    for key in ["command", "question", "delete", "edit", "create", "search", "chat", "idle"]:
        hex_val = prompt_custom.get(key, DEFAULT_COLORS["prompt"].get(key))
        colors["prompt"][key] = hex_to_ansi(hex_val)

    return colors


def get_git_branch(cwd):
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, cwd=cwd, timeout=2
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return None


def get_last_prompt(session_id):
    prompt_file = Path.home() / ".claude" / "data" / "prompts" / f"{session_id}.json"
    if not prompt_file.exists():
        return None
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("prompt")
    except Exception:
        pass
    return None


def classify_prompt(prompt, icons, colors):
    if not prompt:
        return colors["prompt"]["idle"], icons["idle"], "..."

    if prompt.startswith('/'):
        return colors["prompt"]["command"], icons["command"], prompt

    lower = prompt.lower()

    if '?' in prompt:
        return colors["prompt"]["question"], icons["question"], prompt
    if any(w in lower for w in ['delete', 'remove', 'drop']):
        return colors["prompt"]["delete"], icons["delete"], prompt
    if any(w in lower for w in ['fix', 'edit', 'modify', 'update', 'change', 'refactor', 'improve']):
        return colors["prompt"]["edit"], icons["edit"], prompt
    if any(w in lower for w in ['create', 'write', 'add', 'implement', 'build', 'make']):
        return colors["prompt"]["create"], icons["create"], prompt
    if any(w in lower for w in ['analyze', 'check', 'review', 'explore', 'search', 'explain']):
        return colors["prompt"]["search"], icons["search"], prompt

    return colors["prompt"]["chat"], icons["chat"], prompt


def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except Exception:
        print(f"\033[38;2;247;118;142m err{RESET}")
        sys.exit(0)

    cfg = load_config()
    icons = build_icons(cfg)
    colors = build_colors(cfg)
    max_len = cfg.get("prompt_max_length", 5)
    sep_char = cfg.get("separator", "\u2502")

    try:
        model = input_data.get("model", {}).get("display_name", "Claude")
        cwd = input_data.get("cwd", os.getcwd())
        project = Path(cwd).name
        branch = get_git_branch(cwd)

        ctx = input_data.get("context_window", {})
        ctx_pct = ctx.get("used_percentage", 0) or 0

        session_id = input_data.get("session_id", "unknown")
        prompt = get_last_prompt(session_id)
        color, icon, display = classify_prompt(prompt, icons, colors)

        if display and display != "...":
            display = ' '.join(display.split())
            if len(display) > max_len:
                display = display[:max_len]

        sep = f"{colors['separator']}{sep_char}{RESET}"

        parts = [f"{colors['model']}{BOLD}{icons['model']} {model}{RESET}"]
        if branch:
            parts.append(f"{colors['git']}{icons['git']} {branch}{RESET}")
        parts.append(f"{colors['folder']}{icons['folder']} {project}{RESET}")
        parts.append(f"{colors['context']}{icons['context']} {ctx_pct:.0f}%{RESET}")
        parts.append(f"{color}{icon} {display}{RESET}")

        print(f" {sep} ".join(parts))

    except Exception as e:
        print(f"\033[38;2;247;118;142merr: {e}{RESET}")

    sys.exit(0)


if __name__ == '__main__':
    main()
