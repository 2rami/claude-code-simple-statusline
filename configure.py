#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "questionary",
# ]
# ///

"""
Claude Code Statusline - Interactive Configuration

Usage:
    uv run configure.py
    python configure.py  (if questionary is installed)
"""

import json
from pathlib import Path

import questionary
from questionary import Style

# ── Style ──────────────────────────────────────────────────────────
STYLE = Style([
    ("qmark", "fg:#73daca bold"),
    ("question", "fg:#c0caf5 bold"),
    ("answer", "fg:#7aa2f7 bold"),
    ("pointer", "fg:#ff9e64 bold"),
    ("highlighted", "fg:#ff9e64 bold"),
    ("selected", "fg:#73daca"),
    ("separator", "fg:#565f89"),
    ("instruction", "fg:#565f89"),
    ("text", "fg:#c0caf5"),
])

# ── Paths ──────────────────────────────────────────────────────────
CONFIG_PATH = Path.home() / ".claude" / "statusline-config.json"
LOCAL_CONFIG = Path(__file__).parent / "config.json"

# ── Defaults ───────────────────────────────────────────────────────
DEFAULT_CONFIG = {
    "icon_set": "nerd-font",
    "icons": {
        "model": "\uf233", "git": "\ue0a0", "folder": "\uf07b", "context": "\uf0e4",
        "prompt": {
            "command": "\uf120", "question": "\uf128", "delete": "\uf1f8",
            "edit": "\uf040", "create": "\uf067", "search": "\uf002",
            "chat": "\uf075", "idle": "\uf10c",
        },
    },
    "colors": {
        "model": "#7aa2f7", "git": "#73daca", "folder": "#bb9af7",
        "context": "#ff9e64", "separator": "#565f89",
        "prompt": {
            "command": "#e0af68", "question": "#7aa2f7", "delete": "#f7768e",
            "edit": "#e0af68", "create": "#73daca", "search": "#bb9af7",
            "chat": "#c0caf5", "idle": "#565f89",
        },
    },
    "separator": "\u2502",
    "prompt_max_length": 5,
}

SEGMENT_LABELS = {
    "model": "Model (Claude model name)",
    "git": "Git Branch",
    "folder": "Project (directory name)",
    "context": "Context (window usage %)",
    "separator": "Separator (between segments)",
}

PROMPT_LABELS = {
    "command": "Command (/slash commands)",
    "question": "Question (contains ?)",
    "delete": "Delete (delete, remove, drop)",
    "edit": "Edit (fix, edit, update, refactor)",
    "create": "Create (create, add, build)",
    "search": "Search (analyze, review, search)",
    "chat": "Chat (general conversation)",
    "idle": "Idle (no prompt yet)",
}


def load_config():
    for p in [CONFIG_PATH, LOCAL_CONFIG]:
        if p.exists():
            try:
                with open(p, "r") as f:
                    return json.load(f)
            except Exception:
                pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved to {CONFIG_PATH}")


def hex_to_ansi(h):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"\033[38;2;{r};{g};{b}m"


def preview_statusline(cfg):
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    sys.path.insert(0, str(Path.home() / ".claude"))
    from statusline import ICON_PRESETS
    preset = cfg.get("icon_set", "nerd-font")
    icons = dict(ICON_PRESETS.get(preset, ICON_PRESETS["nerd-font"]))
    custom_icons = cfg.get("icons", {})
    for k in ["model", "git", "folder", "context"]:
        if k in custom_icons:
            icons[k] = custom_icons[k]
    prompt_icons = custom_icons.get("prompt", {})
    for k in prompt_icons:
        icons[k] = prompt_icons[k]

    colors = cfg.get("colors", DEFAULT_CONFIG["colors"])
    sep_char = cfg.get("separator", "\u2502")

    reset = "\033[0m"
    bold = "\033[1m"
    sep_color = hex_to_ansi(colors.get("separator", "#565f89"))
    sep = f"{sep_color}{sep_char}{reset}"

    parts = [
        f"{hex_to_ansi(colors.get('model', '#7aa2f7'))}{bold}{icons.get('model', '')} Opus 4.5{reset}",
        f"{hex_to_ansi(colors.get('git', '#73daca'))}{icons.get('git', '')} main{reset}",
        f"{hex_to_ansi(colors.get('folder', '#bb9af7'))}{icons.get('folder', '')} my-project{reset}",
        f"{hex_to_ansi(colors.get('context', '#ff9e64'))}{icons.get('context', '')} 42%{reset}",
    ]

    prompt_colors = colors.get("prompt", {})
    create_color = hex_to_ansi(prompt_colors.get("create", "#73daca"))
    create_icon = icons.get("create", "+")
    parts.append(f"{create_color}{create_icon} creat{reset}")

    print(f"\n  Preview: {f' {sep} '.join(parts)}\n")


def menu_icon_set(cfg):
    current = cfg.get("icon_set", "nerd-font")
    choices = [
        questionary.Choice(
            f"nerd-font  -  Nerd Font icons (requires patched font)",
            value="nerd-font",
        ),
        questionary.Choice(
            f"unicode    -  Basic unicode symbols (any modern font)",
            value="unicode",
        ),
        questionary.Choice(
            f"plain      -  ASCII text labels (any font)",
            value="plain",
        ),
    ]
    result = questionary.select(
        f"Icon set (current: {current})",
        choices=choices,
        default=current,
        style=STYLE,
    ).ask()
    if result is not None:
        cfg["icon_set"] = result


def menu_custom_icons(cfg):
    icons = cfg.setdefault("icons", {})
    prompt_icons = icons.setdefault("prompt", {})

    segment_choices = list(SEGMENT_LABELS.keys())
    prompt_choices = list(PROMPT_LABELS.keys())

    all_choices = [
        questionary.Choice(f"  {SEGMENT_LABELS[k]}", value=("segment", k))
        for k in segment_choices
        if k != "separator"
    ] + [
        questionary.Separator("  --- Prompt Icons ---"),
    ] + [
        questionary.Choice(f"  {PROMPT_LABELS[k]}", value=("prompt", k))
        for k in prompt_choices
    ] + [
        questionary.Separator(),
        questionary.Choice("  <- Back", value=None),
    ]

    while True:
        result = questionary.select(
            "Which icon to change?",
            choices=all_choices,
            style=STYLE,
        ).ask()

        if result is None:
            break

        group, key = result
        current = (
            icons.get(key, "") if group == "segment"
            else prompt_icons.get(key, "")
        )
        label = SEGMENT_LABELS.get(key, PROMPT_LABELS.get(key, key))

        new_val = questionary.text(
            f"  New icon for {label} (current: {current}):",
            default=current,
            style=STYLE,
        ).ask()

        if new_val is not None:
            if group == "segment":
                icons[key] = new_val
            else:
                prompt_icons[key] = new_val


def menu_colors(cfg):
    colors = cfg.setdefault("colors", dict(DEFAULT_CONFIG["colors"]))
    prompt_colors = colors.setdefault("prompt", dict(DEFAULT_CONFIG["colors"]["prompt"]))

    all_choices = [
        questionary.Choice(
            f"  {SEGMENT_LABELS[k]}  ({colors.get(k, '')})",
            value=("segment", k),
        )
        for k in SEGMENT_LABELS
    ] + [
        questionary.Separator("  --- Prompt Colors ---"),
    ] + [
        questionary.Choice(
            f"  {PROMPT_LABELS[k]}  ({prompt_colors.get(k, '')})",
            value=("prompt", k),
        )
        for k in PROMPT_LABELS
    ] + [
        questionary.Separator(),
        questionary.Choice("  <- Back", value=None),
    ]

    while True:
        result = questionary.select(
            "Which color to change? (hex format: #rrggbb)",
            choices=all_choices,
            style=STYLE,
        ).ask()

        if result is None:
            break

        group, key = result
        current = (
            colors.get(key, "#ffffff") if group == "segment"
            else prompt_colors.get(key, "#ffffff")
        )
        label = SEGMENT_LABELS.get(key, PROMPT_LABELS.get(key, key))

        sample = f"{hex_to_ansi(current)}████████\033[0m"
        new_val = questionary.text(
            f"  {label} (current: {current} {sample}):",
            default=current,
            style=STYLE,
            validate=lambda v: (
                len(v) == 7 and v.startswith("#") and all(c in "0123456789abcdefABCDEF" for c in v[1:])
            ) or "Enter a valid hex color (e.g. #7aa2f7)",
        ).ask()

        if new_val is not None:
            if group == "segment":
                colors[key] = new_val
            else:
                prompt_colors[key] = new_val

            # Rebuild choices to reflect updated color
            for i, c in enumerate(all_choices):
                if hasattr(c, "value") and c.value == (group, key):
                    new_label = (
                        f"  {label}  ({new_val})"
                    )
                    all_choices[i] = questionary.Choice(new_label, value=(group, key))
                    break


def menu_separator(cfg):
    current = cfg.get("separator", "\u2502")
    choices = [
        questionary.Choice(f"|   pipe", value="|"),
        questionary.Choice(f"\u2502   box drawing (default)", value="\u2502"),
        questionary.Choice(f"/   slash", value="/"),
        questionary.Choice(f"\u2022   bullet", value="\u2022"),
        questionary.Choice(f"    space (no separator)", value=" "),
    ]
    result = questionary.select(
        f"Separator character (current: {current})",
        choices=choices,
        style=STYLE,
    ).ask()
    if result is None:
        return

    custom = questionary.confirm(
        "  Enter a custom separator instead?",
        default=False,
        style=STYLE,
    ).ask()
    if custom:
        val = questionary.text("  Custom separator:", default=current, style=STYLE).ask()
        if val is not None:
            cfg["separator"] = val
    else:
        cfg["separator"] = result


def menu_prompt_length(cfg):
    current = cfg.get("prompt_max_length", 5)
    choices = [
        questionary.Choice(f"3   short", value=3),
        questionary.Choice(f"5   default", value=5),
        questionary.Choice(f"10  medium", value=10),
        questionary.Choice(f"20  long", value=20),
        questionary.Choice(f"0   hidden (icon only)", value=0),
    ]
    result = questionary.select(
        f"Prompt text max length (current: {current})",
        choices=choices,
        default=current if current in [3, 5, 10, 20, 0] else 5,
        style=STYLE,
    ).ask()
    if result is not None:
        cfg["prompt_max_length"] = result


def main():
    print()
    print("  Claude Code Statusline - Configuration")
    print("  =======================================")
    print()

    cfg = load_config()

    main_choices = [
        questionary.Choice("  Icon Set          Choose nerd-font / unicode / plain", value="icon_set"),
        questionary.Choice("  Custom Icons      Override individual icons", value="icons"),
        questionary.Choice("  Colors            Change segment colors", value="colors"),
        questionary.Choice("  Separator         Change the separator character", value="separator"),
        questionary.Choice("  Prompt Length     Max characters shown from prompt", value="prompt_length"),
        questionary.Separator(),
        questionary.Choice("  Preview           Show statusline preview", value="preview"),
        questionary.Choice("  Save & Exit       Save changes and quit", value="save"),
        questionary.Choice("  Exit              Quit without saving", value="quit"),
    ]

    while True:
        result = questionary.select(
            "What would you like to configure?",
            choices=main_choices,
            style=STYLE,
        ).ask()

        if result is None or result == "quit":
            print("  No changes saved.\n")
            break
        elif result == "save":
            save_config(cfg)
            try:
                preview_statusline(cfg)
            except Exception:
                pass
            break
        elif result == "icon_set":
            menu_icon_set(cfg)
        elif result == "icons":
            menu_custom_icons(cfg)
        elif result == "colors":
            menu_colors(cfg)
        elif result == "separator":
            menu_separator(cfg)
        elif result == "prompt_length":
            menu_prompt_length(cfg)
        elif result == "preview":
            try:
                preview_statusline(cfg)
            except Exception:
                print("  (Preview requires statusline.py in the same directory)\n")


if __name__ == "__main__":
    main()
