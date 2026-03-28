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
import sys
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

# ── Icon Presets (duplicated to avoid import issues) ───────────────
ICON_PRESETS = {
    "nerd-font": {
        "model": "\uf233", "git": "\ue0a0", "folder": "\uf07b",
        "context": "\uf0e4", "command": "\uf120", "question": "\uf128",
        "delete": "\uf1f8", "edit": "\uf040", "create": "\uf067",
        "search": "\uf002", "chat": "\uf075", "idle": "\uf10c",
    },
    "unicode": {
        "model": ">", "git": "*", "folder": "~",
        "context": "%", "command": "$", "question": "?",
        "delete": "x", "edit": "~", "create": "+",
        "search": "/", "chat": "#", "idle": ".",
    },
    "plain": {
        "model": "[M]", "git": "[G]", "folder": "[D]",
        "context": "[C]", "command": "[>]", "question": "[?]",
        "delete": "[-]", "edit": "[~]", "create": "[+]",
        "search": "[/]", "chat": "[#]", "idle": "[.]",
    },
}

DEFAULT_COLORS = {
    "model": "#7aa2f7", "git": "#73daca", "folder": "#bb9af7",
    "context": "#ff9e64", "separator": "#565f89",
    "prompt": {
        "command": "#e0af68", "question": "#7aa2f7", "delete": "#f7768e",
        "edit": "#e0af68", "create": "#73daca", "search": "#bb9af7",
        "chat": "#c0caf5", "idle": "#565f89",
    },
}

SEGMENT_LABELS = {
    "model": "Model (모델명)",
    "git": "Git Branch (브랜치)",
    "folder": "Project (프로젝트명)",
    "context": "Context (컨텍스트 사용률)",
    "separator": "Separator (구분자)",
}

PROMPT_LABELS = {
    "command": "Command (명령어)",
    "question": "Question (질문)",
    "delete": "Delete (삭제)",
    "edit": "Edit (수정)",
    "create": "Create (생성)",
    "search": "Search (검색)",
    "chat": "Chat (대화)",
    "idle": "Idle (대기)",
}


def load_config():
    for p in [CONFIG_PATH, LOCAL_CONFIG]:
        if p.exists():
            try:
                with open(p, "r") as f:
                    return json.load(f)
            except Exception:
                pass
    return {
        "icon_set": "nerd-font",
        "icons": dict(ICON_PRESETS["nerd-font"]),
        "colors": dict(DEFAULT_COLORS),
        "separator": "\u2502",
        "prompt_max_length": 5,
    }


def save_config(cfg):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def hex_to_ansi(h):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"\033[38;2;{r};{g};{b}m"


def show_preview(cfg):
    preset = cfg.get("icon_set", "nerd-font")
    icons = dict(ICON_PRESETS.get(preset, ICON_PRESETS["nerd-font"]))
    custom_icons = cfg.get("icons", {})
    for k in ["model", "git", "folder", "context"]:
        if k in custom_icons:
            icons[k] = custom_icons[k]
    for k in custom_icons.get("prompt", {}):
        icons[k] = custom_icons["prompt"][k]

    colors = cfg.get("colors", DEFAULT_COLORS)
    sep_char = cfg.get("separator", "\u2502")
    max_len = cfg.get("prompt_max_length", 5)

    reset = "\033[0m"
    bold = "\033[1m"
    sep_color = hex_to_ansi(colors.get("separator", "#565f89"))
    sep = f" {sep_color}{sep_char}{reset} "

    prompt_text = "creat"[:max_len] if max_len > 0 else ""
    prompt_colors = colors.get("prompt", {})
    create_color = hex_to_ansi(prompt_colors.get("create", "#73daca"))

    parts = [
        f"{hex_to_ansi(colors.get('model', '#7aa2f7'))}{bold}{icons.get('model', '')} Opus 4.5{reset}",
        f"{hex_to_ansi(colors.get('git', '#73daca'))}{icons.get('git', '')} main{reset}",
        f"{hex_to_ansi(colors.get('folder', '#bb9af7'))}{icons.get('folder', '')} my-project{reset}",
        f"{hex_to_ansi(colors.get('context', '#ff9e64'))}{icons.get('context', '')} 42%{reset}",
        f"{create_color}{icons.get('create', '+')}{' ' + prompt_text if prompt_text else ''}{reset}",
    ]

    print(f"\n  {sep.join(parts)}\n")


def step_icon_set(cfg):
    print("\n  [1/5] 아이콘 세트")
    print("  Nerd Font이 설치되어 있으면 nerd-font, 아니면 unicode나 plain을 골라.")
    current = cfg.get("icon_set", "nerd-font")
    choices = [
        questionary.Choice("nerd-font   -  Nerd Font 아이콘 (패치 폰트 필요)", value="nerd-font"),
        questionary.Choice("unicode     -  기본 유니코드 기호 (아무 폰트 OK)", value="unicode"),
        questionary.Choice("plain       -  ASCII 텍스트 (아무 폰트 OK)", value="plain"),
    ]
    result = questionary.select(
        "아이콘 세트 선택:",
        choices=choices,
        default=current,
        style=STYLE,
    ).ask()
    if result is None:
        return False
    cfg["icon_set"] = result
    show_preview(cfg)
    return True


def step_separator(cfg):
    print("  [2/5] 구분자")
    current = cfg.get("separator", "\u2502")
    choices = [
        questionary.Choice("\u2502   box drawing (기본)", value="\u2502"),
        questionary.Choice("|   pipe", value="|"),
        questionary.Choice("/   slash", value="/"),
        questionary.Choice("\u2022   bullet", value="\u2022"),
        questionary.Choice("    space (구분자 없음)", value=" "),
        questionary.Choice("    직접 입력...", value="__custom__"),
    ]
    result = questionary.select(
        "구분자 선택:",
        choices=choices,
        default=current if current in ["\u2502", "|", "/", "\u2022", " "] else "\u2502",
        style=STYLE,
    ).ask()
    if result is None:
        return False
    if result == "__custom__":
        val = questionary.text("  구분자 입력:", default=current, style=STYLE).ask()
        if val is None:
            return False
        cfg["separator"] = val
    else:
        cfg["separator"] = result
    show_preview(cfg)
    return True


def step_prompt_length(cfg):
    print("  [3/5] 프롬프트 표시 길이")
    print("  상태표시줄에서 마지막 프롬프트 텍스트를 몇 글자까지 보여줄지.")
    current = cfg.get("prompt_max_length", 5)
    choices = [
        questionary.Choice("0    아이콘만 (텍스트 숨김)", value=0),
        questionary.Choice("3    짧게", value=3),
        questionary.Choice("5    기본", value=5),
        questionary.Choice("10   보통", value=10),
        questionary.Choice("20   길게", value=20),
    ]
    result = questionary.select(
        "프롬프트 최대 길이:",
        choices=choices,
        default=current if current in [0, 3, 5, 10, 20] else 5,
        style=STYLE,
    ).ask()
    if result is None:
        return False
    cfg["prompt_max_length"] = result
    show_preview(cfg)
    return True


def step_colors(cfg):
    print("  [4/5] 색상")
    colors = cfg.setdefault("colors", dict(DEFAULT_COLORS))
    prompt_colors = colors.setdefault("prompt", dict(DEFAULT_COLORS["prompt"]))

    change = questionary.confirm(
        "세그먼트 색상을 변경할래?",
        default=False,
        style=STYLE,
    ).ask()
    if change is None:
        return False
    if not change:
        show_preview(cfg)
        return True

    # Segment colors
    for key, label in SEGMENT_LABELS.items():
        current = colors.get(key, DEFAULT_COLORS.get(key, "#ffffff"))
        sample = f"{hex_to_ansi(current)}████{'\033[0m'}"
        new_val = questionary.text(
            f"  {label} ({current} {sample}):",
            default=current,
            style=STYLE,
            validate=lambda v: (
                len(v) == 7 and v.startswith("#") and all(c in "0123456789abcdefABCDEF" for c in v[1:])
            ) or "#rrggbb 형식으로 입력해 (예: #7aa2f7)",
        ).ask()
        if new_val is None:
            return False
        colors[key] = new_val

    # Prompt colors
    change_prompt = questionary.confirm(
        "프롬프트 의도별 색상도 변경할래?",
        default=False,
        style=STYLE,
    ).ask()
    if change_prompt:
        for key, label in PROMPT_LABELS.items():
            current = prompt_colors.get(key, DEFAULT_COLORS["prompt"].get(key, "#ffffff"))
            sample = f"{hex_to_ansi(current)}████{'\033[0m'}"
            new_val = questionary.text(
                f"  {label} ({current} {sample}):",
                default=current,
                style=STYLE,
                validate=lambda v: (
                    len(v) == 7 and v.startswith("#") and all(c in "0123456789abcdefABCDEF" for c in v[1:])
                ) or "#rrggbb 형식으로 입력해 (예: #7aa2f7)",
            ).ask()
            if new_val is None:
                return False
            prompt_colors[key] = new_val

    show_preview(cfg)
    return True


def step_custom_icons(cfg):
    print("  [5/5] 개별 아이콘")
    icons = cfg.setdefault("icons", {})
    prompt_icons = icons.setdefault("prompt", {})

    preset = cfg.get("icon_set", "nerd-font")
    preset_icons = ICON_PRESETS.get(preset, ICON_PRESETS["nerd-font"])

    change = questionary.confirm(
        "개별 아이콘을 변경할래? (아이콘 세트 프리셋 위에 덮어쓰기)",
        default=False,
        style=STYLE,
    ).ask()
    if change is None:
        return False
    if not change:
        return True

    # Segment icons
    for key in ["model", "git", "folder", "context"]:
        current = icons.get(key, preset_icons.get(key, ""))
        label = SEGMENT_LABELS[key]
        new_val = questionary.text(
            f"  {label} (현재: {current}):",
            default=current,
            style=STYLE,
        ).ask()
        if new_val is None:
            return False
        icons[key] = new_val

    # Prompt icons
    change_prompt = questionary.confirm(
        "프롬프트 의도별 아이콘도 변경할래?",
        default=False,
        style=STYLE,
    ).ask()
    if change_prompt:
        for key, label in PROMPT_LABELS.items():
            current = prompt_icons.get(key, preset_icons.get(key, ""))
            new_val = questionary.text(
                f"  {label} (현재: {current}):",
                default=current,
                style=STYLE,
            ).ask()
            if new_val is None:
                return False
            prompt_icons[key] = new_val

    show_preview(cfg)
    return True


def main():
    print()
    print("  Claude Code Statusline - 설정")
    print("  =============================")

    cfg = load_config()

    print("\n  현재 상태표시줄:")
    show_preview(cfg)

    steps = [step_icon_set, step_separator, step_prompt_length, step_colors, step_custom_icons]

    for step in steps:
        if not step(cfg):
            print("\n  취소됨. 변경사항이 저장되지 않았어.\n")
            sys.exit(0)

    # Final preview and save
    print("  최종 미리보기:")
    show_preview(cfg)

    confirm = questionary.confirm(
        "이대로 저장할래?",
        default=True,
        style=STYLE,
    ).ask()

    if confirm:
        save_config(cfg)
        print(f"  저장 완료! -> {CONFIG_PATH}")
        print("  Claude Code를 재시작하면 적용돼.\n")
    else:
        print("  저장하지 않았어.\n")


if __name__ == "__main__":
    main()
