#!/bin/bash

# Claude Code Statusline - Simple Minimal
# Installer for macOS / Linux

set -e

CLAUDE_DIR="$HOME/.claude"
BASE_URL="https://raw.githubusercontent.com/2rami/claude-code-simple-statusline/main"
STATUSLINE="$CLAUDE_DIR/statusline.py"
HOOK="$CLAUDE_DIR/user_prompt_submit.py"
CONFIG="$CLAUDE_DIR/statusline-config.json"
SETTINGS="$CLAUDE_DIR/settings.json"

echo ""
echo "  Claude Code Statusline - Simple Minimal"
echo "  ====================================="
echo ""

# ── Font check ──────────────────────────────────────────────────────
echo "  Checking font support..."
if command -v fc-list &> /dev/null; then
    if fc-list | grep -qi "nerd"; then
        echo "  Nerd Font detected"
    else
        echo ""
        echo "  [!] No Nerd Font detected. Icons may not render correctly."
        if [[ "$OSTYPE" == darwin* ]]; then
            echo "      Install: brew install --cask font-jetbrains-mono-nerd-font"
        else
            echo "      Install: https://www.nerdfonts.com/font-downloads"
        fi
        echo "      Or set \"icon_set\": \"unicode\" in $CONFIG"
        echo ""
    fi
fi

# ── Download files ──────────────────────────────────────────────────
mkdir -p "$CLAUDE_DIR"

echo "  Downloading statusline.py..."
curl -fsSL "$BASE_URL/statusline.py" -o "$STATUSLINE"
chmod +x "$STATUSLINE"

echo "  Downloading user_prompt_submit.py..."
curl -fsSL "$BASE_URL/user_prompt_submit.py" -o "$HOOK"
chmod +x "$HOOK"

echo "  Downloading config.json..."
curl -fsSL "$BASE_URL/config.json" -o "$CONFIG"

# ── Update settings.json ────────────────────────────────────────────
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

if [ -n "$PYTHON_CMD" ]; then
    $PYTHON_CMD -c "
import json, os

path = '$SETTINGS'
s = {}
if os.path.exists(path):
    with open(path, 'r') as f:
        s = json.load(f)

s['statusLine'] = {
    'type': 'command',
    'command': '$STATUSLINE',
    'padding': 0
}

hooks = s.get('hooks', {})
ups = hooks.get('UserPromptSubmit', [])

hook_entry = {
    'matcher': '*',
    'hooks': [{
        'type': 'command',
        'command': '$PYTHON_CMD $HOOK'
    }]
}

already = False
for entry in ups:
    for h in entry.get('hooks', []):
        if 'user_prompt_submit' in h.get('command', ''):
            already = True
            break

if not already:
    ups.append(hook_entry)

hooks['UserPromptSubmit'] = ups
s['hooks'] = hooks

with open(path, 'w') as f:
    json.dump(s, f, indent=2)
print('  Updated $SETTINGS')
"
else
    echo ""
    echo "  [!] Python not found. Add this to $SETTINGS manually:"
    echo ""
    cat << 'MANUAL'
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.py",
    "padding": 0
  },
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/user_prompt_submit.py"
      }]
    }]
  }
MANUAL
fi

echo ""
echo "  Done! Restart Claude Code to see the new statusline."
echo ""
