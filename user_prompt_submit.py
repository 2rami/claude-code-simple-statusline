#!/usr/bin/env python3
"""
UserPromptSubmit hook
Saves per-session prompts so the statusline can display the last prompt.
"""

import json
import sys
from pathlib import Path

try:
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

DATA_DIR = Path.home() / ".claude" / "data" / "prompts"


def store_prompt(session_id, prompt):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    prompt_file = DATA_DIR / f"{session_id}.json"
    with open(prompt_file, "w", encoding="utf-8") as f:
        json.dump({"prompt": prompt}, f, ensure_ascii=False)


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        session_id = input_data.get("session_id", "default")
        prompt = input_data.get("prompt", "")

        if prompt:
            store_prompt(session_id, prompt)

        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
