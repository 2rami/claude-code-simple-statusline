#!/usr/bin/env python3
"""
UserPromptSubmit hook
Saves per-session prompts so the statusline can display the last prompt.
"""

import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path.home() / ".claude" / "data" / "prompts"
NAMES_DIR = Path.home() / ".claude" / "data" / "session-names"


def store_prompt(session_id, prompt):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    prompt_file = DATA_DIR / f"{session_id}.json"
    with open(prompt_file, "w", encoding="utf-8") as f:
        json.dump({"prompt": prompt}, f, ensure_ascii=False)


def store_session_name(session_id, name):
    NAMES_DIR.mkdir(parents=True, exist_ok=True)
    name_file = NAMES_DIR / f"{session_id}.txt"
    with open(name_file, "w", encoding="utf-8") as f:
        f.write(name.strip())


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        session_id = input_data.get("session_id", "default")
        prompt = input_data.get("prompt", "")

        # /rename 명령 처리
        if prompt.startswith("/rename"):
            name = prompt[len("/rename"):].strip()
            if name:
                store_session_name(session_id, name)
                print(f"Session renamed to: {name}")
            else:
                print("Usage: /rename <name>")
            sys.exit(0)

        if prompt:
            store_prompt(session_id, prompt)

        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
