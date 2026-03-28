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
"""

import copy
import json
import os
import sys
from pathlib import Path

import questionary
from questionary import Choice, Separator, Style

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

CONFIG_PATH = Path.home() / ".claude" / "statusline-config.json"
LOCAL_CONFIG = Path(__file__).parent / "config.json"

RESET = "\033[0m"
BOLD = "\033[1m"

# ── Icon Presets ──────────────────────────────────────────────────
ICON_PRESETS = {
    "font-awesome": {
        "label": "Font Awesome (default)",
        "requires": "nerd-font",
        "model": "\uf233", "git": "\ue0a0", "folder": "\uf07b",
        "context": "\uf0e4", "command": "\uf120", "question": "\uf128",
        "delete": "\uf1f8", "edit": "\uf040", "create": "\uf067",
        "search": "\uf002", "chat": "\uf075", "idle": "\uf10c",
    },
    "material": {
        "label": "Material Design",
        "requires": "nerd-font",
        "model": "\U000f048b", "git": "\U000f062c", "folder": "\U000f024b",
        "context": "\U000f029a", "command": "\U000f018d", "question": "\U000f02d7",
        "delete": "\U000f01b4", "edit": "\U000f03eb", "create": "\U000f0415",
        "search": "\U000f0349", "chat": "\U000f0361", "idle": "\U000f09df",
    },
    "octicons": {
        "label": "Octicons (GitHub)",
        "requires": "nerd-font",
        "model": "\uf473", "git": "\uf418", "folder": "\uf413",
        "context": "\uf463", "command": "\uf489", "question": "\uf420",
        "delete": "\uf48e", "edit": "\uf448", "create": "\uf44d",
        "search": "\uf422", "chat": "\uf41f", "idle": "\uf4aa",
    },
    "codicons": {
        "label": "Codicons (VS Code)",
        "requires": "nerd-font",
        "model": "\ueb50", "git": "\uea68", "folder": "\uea83",
        "context": "\ueacd", "command": "\uea85", "question": "\ueb32",
        "delete": "\uea81", "edit": "\uea73", "create": "\uea60",
        "search": "\uea6d", "chat": "\uea6b", "idle": "\ueb8a",
    },
    "unicode": {
        "label": "Unicode (any font)",
        "requires": None,
        "model": ">", "git": "*", "folder": "~",
        "context": "%", "command": "$", "question": "?",
        "delete": "x", "edit": "~", "create": "+",
        "search": "/", "chat": "#", "idle": ".",
    },
    "plain": {
        "label": "Plain ASCII (any font)",
        "requires": None,
        "model": "[M]", "git": "[G]", "folder": "[D]",
        "context": "[C]", "command": "[>]", "question": "[?]",
        "delete": "[-]", "edit": "[~]", "create": "[+]",
        "search": "[/]", "chat": "[#]", "idle": "[.]",
    },
}

ICON_KEYS = ["model", "git", "folder", "context", "command", "question",
             "delete", "edit", "create", "search", "chat", "idle"]

DEFAULT_COLORS = {
    "model": "#7aa2f7", "git": "#73daca", "folder": "#bb9af7",
    "context": "#ff9e64", "separator": "#565f89",
    "prompt": {
        "command": "#e0af68", "question": "#7aa2f7", "delete": "#f7768e",
        "edit": "#e0af68", "create": "#73daca", "search": "#bb9af7",
        "chat": "#c0caf5", "idle": "#565f89",
    },
}

COLOR_PRESETS = {
    "Tokyo Night": {
        "model": "#7aa2f7", "git": "#73daca", "folder": "#bb9af7",
        "context": "#ff9e64", "separator": "#565f89",
        "prompt": {
            "command": "#e0af68", "question": "#7aa2f7", "delete": "#f7768e",
            "edit": "#e0af68", "create": "#73daca", "search": "#bb9af7",
            "chat": "#c0caf5", "idle": "#565f89",
        },
    },
    "Catppuccin Mocha": {
        "model": "#89b4fa", "git": "#a6e3a1", "folder": "#cba6f7",
        "context": "#fab387", "separator": "#585b70",
        "prompt": {
            "command": "#f9e2af", "question": "#89b4fa", "delete": "#f38ba8",
            "edit": "#f9e2af", "create": "#a6e3a1", "search": "#cba6f7",
            "chat": "#cdd6f4", "idle": "#585b70",
        },
    },
    "Dracula": {
        "model": "#8be9fd", "git": "#50fa7b", "folder": "#bd93f9",
        "context": "#ffb86c", "separator": "#6272a4",
        "prompt": {
            "command": "#f1fa8c", "question": "#8be9fd", "delete": "#ff5555",
            "edit": "#f1fa8c", "create": "#50fa7b", "search": "#bd93f9",
            "chat": "#f8f8f2", "idle": "#6272a4",
        },
    },
    "Gruvbox": {
        "model": "#83a598", "git": "#b8bb26", "folder": "#d3869b",
        "context": "#fe8019", "separator": "#665c54",
        "prompt": {
            "command": "#fabd2f", "question": "#83a598", "delete": "#fb4934",
            "edit": "#fabd2f", "create": "#b8bb26", "search": "#d3869b",
            "chat": "#ebdbb2", "idle": "#665c54",
        },
    },
    "Nord": {
        "model": "#88c0d0", "git": "#a3be8c", "folder": "#b48ead",
        "context": "#d08770", "separator": "#4c566a",
        "prompt": {
            "command": "#ebcb8b", "question": "#88c0d0", "delete": "#bf616a",
            "edit": "#ebcb8b", "create": "#a3be8c", "search": "#b48ead",
            "chat": "#eceff4", "idle": "#4c566a",
        },
    },
    "Monochrome": {
        "model": "#cccccc", "git": "#aaaaaa", "folder": "#bbbbbb",
        "context": "#999999", "separator": "#555555",
        "prompt": {
            "command": "#dddddd", "question": "#cccccc", "delete": "#ff6666",
            "edit": "#dddddd", "create": "#aaaaaa", "search": "#bbbbbb",
            "chat": "#eeeeee", "idle": "#555555",
        },
    },
}

SEGMENT_KEYS = ["model", "git", "folder", "context", "separator"]
SEGMENT_LABELS = {
    "model": "Model", "git": "Git Branch", "folder": "Project",
    "context": "Context", "separator": "Separator",
}
PROMPT_KEYS = ["command", "question", "delete", "edit", "create", "search", "chat", "idle"]
PROMPT_LABELS = {
    "command": "Command", "question": "Question", "delete": "Delete",
    "edit": "Edit", "create": "Create", "search": "Search",
    "chat": "Chat", "idle": "Idle",
}

BACK = "__back__"
SAMPLE_PROMPT = "create a new component"


def hex_to_ansi(h):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"\033[38;2;{r};{g};{b}m"


def clear():
    os.system("cls" if sys.platform == "win32" else "clear")


def load_config():
    for p in [CONFIG_PATH, LOCAL_CONFIG]:
        if p.exists():
            try:
                with open(p, "r") as f:
                    return json.load(f)
            except Exception:
                pass
    return {
        "icon_set": "font-awesome",
        "colors": copy.deepcopy(DEFAULT_COLORS),
        "separator": "\u2502",
        "prompt_max_length": 5,
    }


def save_config(cfg):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = dict(cfg)
    icon_set = out.get("icon_set", "font-awesome")
    preset = ICON_PRESETS.get(icon_set, ICON_PRESETS["font-awesome"])
    if preset.get("requires") == "nerd-font":
        out["icon_set"] = "nerd-font"
    elif icon_set in ("unicode", "plain"):
        out["icon_set"] = icon_set
    out["icons"] = {k: preset[k] for k in ICON_KEYS}
    out["icons"]["prompt"] = {k: preset[k] for k in PROMPT_KEYS}
    with open(CONFIG_PATH, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)


def get_icons(cfg):
    preset_name = cfg.get("icon_set", "font-awesome")
    preset = ICON_PRESETS.get(preset_name, ICON_PRESETS["font-awesome"])
    return {k: preset[k] for k in ICON_KEYS}


def build_preview(cfg):
    icons = get_icons(cfg)
    colors = cfg.get("colors", DEFAULT_COLORS)
    sep_char = cfg.get("separator", "\u2502")
    max_len = cfg.get("prompt_max_length", 5)

    sep_color = hex_to_ansi(colors.get("separator", "#565f89"))
    sep = f" {sep_color}{sep_char}{RESET} "

    prompt_text = SAMPLE_PROMPT[:max_len] if max_len > 0 else ""
    prompt_colors = colors.get("prompt", {})
    create_color = hex_to_ansi(prompt_colors.get("create", "#73daca"))

    parts = [
        f"{hex_to_ansi(colors.get('model', '#7aa2f7'))}{BOLD}{icons['model']} Opus 4.5{RESET}",
        f"{hex_to_ansi(colors.get('git', '#73daca'))}{icons['git']} main{RESET}",
        f"{hex_to_ansi(colors.get('folder', '#bb9af7'))}{icons['folder']} my-project{RESET}",
        f"{hex_to_ansi(colors.get('context', '#ff9e64'))}{icons['context']} 42%{RESET}",
        f"{create_color}{icons['create']}{' ' + prompt_text if prompt_text else ''}{RESET}",
    ]
    return sep.join(parts)


def draw(cfg, step_num, step_name):
    clear()
    b = hex_to_ansi("#565f89")
    t = hex_to_ansi("#c0caf5")
    d = hex_to_ansi("#565f89")
    preview = build_preview(cfg)

    print()
    print(f"  {b}{BOLD}\u2501\u2501\u2501{RESET} {t}{BOLD}Claude Code Statusline{RESET} {b}{BOLD}\u2501\u2501\u2501{RESET}")
    print()
    print(f"  {preview}")
    print()
    print(f"  {b}{BOLD}\u2501\u2501\u2501{RESET} {d}[{step_num}/5] {step_name}{RESET} {b}{BOLD}\u2501\u2501\u2501{RESET}")
    print()


def ask(question, choices, **kwargs):
    result = questionary.select(
        question, choices=choices, style=STYLE, **kwargs,
    ).ask()
    if result is None:
        return BACK
    return result


def color_choice(name, palette):
    parts = []
    for key in ["model", "git", "folder", "context"]:
        parts.append((f"fg:{palette[key]}", "\u2588\u2588"))
    parts.append(("", f"  {name}"))
    return Choice(title=parts, value=name)


def icon_choice(name, preset):
    sample = f"{preset['model']} {preset['git']} {preset['folder']} {preset['context']} {preset['create']}"
    return Choice(f"{sample}  {preset['label']}", value=name)


# ── Steps ──────────────────────────────────────────────────────────

def step_icon_set(cfg):
    draw(cfg, 1, "Icon Style")
    current = cfg.get("icon_set", "font-awesome")
    choices = []
    for name, preset in ICON_PRESETS.items():
        choices.append(icon_choice(name, preset))
    choices += [
        Separator(),
        Choice("  << Back", value=BACK),
    ]
    result = ask("Icon style:", choices, default=current)
    if result == BACK:
        return "back"
    cfg["icon_set"] = result
    return "next"


def step_separator(cfg):
    draw(cfg, 2, "Separator")
    current = cfg.get("separator", "\u2502")
    seps = [
        ("\u2502", "thin line"),
        ("\u2503", "thick line"),
        ("\u2551", "double line"),
        ("\u257d", "half line"),
        ("|", "pipe"),
        ("/", "slash"),
        ("\u2022", "bullet"),
        ("\u25cf", "circle"),
        ("\u2016", "double bar"),
        ("\u00b7", "middle dot"),
        ("\u2043", "hyphen bullet"),
        (" ", "space (none)"),
    ]
    sep_values = [s[0] for s in seps]
    sep_choices = [Choice(f"{s[0]}  {s[1]}", value=s[0]) for s in seps]
    sep_choices += [
        Separator(),
        Choice("   Custom...", value="__custom__"),
        Choice("   << Back", value=BACK),
    ]
    result = ask("Separator:", sep_choices,
                 default=current if current in sep_values else "\u2502")
    if result == BACK:
        return "back"
    if result == "__custom__":
        val = questionary.text("  Enter separator:", default=current, style=STYLE).ask()
        if val is None:
            return "back"
        cfg["separator"] = val
    else:
        cfg["separator"] = result
    return "next"


def step_prompt_length(cfg):
    draw(cfg, 3, "Prompt Length")
    current = cfg.get("prompt_max_length", 5)
    result = ask("Max prompt length:", [
        Choice("0   icon only (hide text)", value=0),
        Choice("3   short", value=3),
        Choice("5   default", value=5),
        Choice("10  medium", value=10),
        Choice("20  long", value=20),
        Separator(),
        Choice("    << Back", value=BACK),
    ], default=current if current in [0, 3, 5, 10, 20] else 5)
    if result == BACK:
        return "back"
    cfg["prompt_max_length"] = result
    return "next"


def step_colors(cfg):
    draw(cfg, 4, "Color Theme")
    preset_choices = []
    for name, palette in COLOR_PRESETS.items():
        preset_choices.append(color_choice(name, palette))
    preset_choices += [
        Separator(),
        Choice("        Custom hex...", value="__custom__"),
        Choice("        << Back", value=BACK),
    ]
    result = ask("Color theme:", preset_choices)
    if result == BACK:
        return "back"
    if result == "__custom__":
        return _step_colors_custom(cfg)

    palette = COLOR_PRESETS[result]
    colors = cfg.setdefault("colors", {})
    for k in SEGMENT_KEYS:
        colors[k] = palette[k]
    colors["prompt"] = dict(palette["prompt"])
    return "next"


def _step_colors_custom(cfg):
    colors = cfg.setdefault("colors", copy.deepcopy(DEFAULT_COLORS))
    prompt_colors = colors.setdefault("prompt", dict(DEFAULT_COLORS["prompt"]))

    draw(cfg, 4, "Custom Colors - Segments")
    for key in SEGMENT_KEYS:
        current = colors.get(key, DEFAULT_COLORS.get(key, "#ffffff"))
        sample = f"{hex_to_ansi(current)}\u2588\u2588\u2588\u2588{RESET}"
        new_val = questionary.text(
            f"  {SEGMENT_LABELS[key]} ({sample} {current}):",
            default=current,
            style=STYLE,
            validate=lambda v: (
                len(v) == 7 and v.startswith("#")
                and all(c in "0123456789abcdefABCDEF" for c in v[1:])
            ) or "Use #rrggbb (e.g. #7aa2f7)",
        ).ask()
        if new_val is None:
            return "back"
        colors[key] = new_val

    draw(cfg, 4, "Custom Colors - Prompt")
    change = questionary.confirm("Change prompt intent colors too?", default=False, style=STYLE).ask()
    if change:
        for key in PROMPT_KEYS:
            current = prompt_colors.get(key, DEFAULT_COLORS["prompt"].get(key, "#ffffff"))
            sample = f"{hex_to_ansi(current)}\u2588\u2588\u2588\u2588{RESET}"
            new_val = questionary.text(
                f"  {PROMPT_LABELS[key]} ({sample} {current}):",
                default=current,
                style=STYLE,
                validate=lambda v: (
                    len(v) == 7 and v.startswith("#")
                    and all(c in "0123456789abcdefABCDEF" for c in v[1:])
                ) or "Use #rrggbb (e.g. #7aa2f7)",
            ).ask()
            if new_val is None:
                return "back"
            prompt_colors[key] = new_val
    return "next"


def step_confirm(cfg):
    draw(cfg, 5, "Confirm")
    result = ask("Save this configuration?", [
        Choice("Save and apply", value="save"),
        Choice("Reset to defaults", value="reset"),
        Separator(),
        Choice("<< Back to colors", value=BACK),
    ])
    if result == BACK:
        return "back"
    if result == "reset":
        cfg.clear()
        cfg.update({
            "icon_set": "font-awesome",
            "colors": copy.deepcopy(DEFAULT_COLORS),
            "separator": "\u2502",
            "prompt_max_length": 5,
        })
        return "back"
    save_config(cfg)
    print(f"\n  Saved to {CONFIG_PATH}")
    print("  Restart Claude Code to apply.\n")
    return "done"


def main():
    cfg = load_config()
    if cfg.get("icon_set") == "nerd-font":
        cfg["icon_set"] = "font-awesome"
    history = [copy.deepcopy(cfg)]

    steps = [step_icon_set, step_separator, step_prompt_length, step_colors, step_confirm]
    i = 0

    while i < len(steps):
        result = steps[i](cfg)

        if result == "done":
            break
        elif result == "back":
            if i > 0:
                cfg.clear()
                cfg.update(copy.deepcopy(history[max(0, i - 1)]))
                i -= 1
            continue
        else:
            history = history[:i + 1]
            history.append(copy.deepcopy(cfg))
            i += 1


if __name__ == "__main__":
    main()
