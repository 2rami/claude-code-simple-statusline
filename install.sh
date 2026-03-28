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

# ── Font: D2Coding Nerd Font ────────────────────────────────────────
FONT_INSTALLED=false
if command -v fc-list &> /dev/null; then
    if fc-list | grep -qi "D2Coding.*Nerd\|D2CodingLigature.*Nerd"; then
        echo "  D2Coding Nerd Font detected"
        FONT_INSTALLED=true
    fi
fi

if [ "$FONT_INSTALLED" = false ]; then
    echo "  Installing D2Coding Nerd Font..."
    if [[ "$OSTYPE" == darwin* ]] && command -v brew &> /dev/null; then
        brew install --cask font-d2coding-nerd-font
        echo "  D2Coding Nerd Font installed via Homebrew"
    else
        FONT_DIR="$HOME/.local/share/fonts"
        mkdir -p "$FONT_DIR"
        TMP_DIR=$(mktemp -d)
        echo "  Downloading from GitHub..."
        curl -fsSL "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/D2Coding.tar.xz" -o "$TMP_DIR/D2Coding.tar.xz"
        tar -xf "$TMP_DIR/D2Coding.tar.xz" -C "$TMP_DIR"
        cp "$TMP_DIR"/*.ttf "$FONT_DIR/" 2>/dev/null || cp "$TMP_DIR"/*.otf "$FONT_DIR/" 2>/dev/null || true
        rm -rf "$TMP_DIR"
        if command -v fc-cache &> /dev/null; then
            fc-cache -fv > /dev/null 2>&1
        fi
        echo "  D2Coding Nerd Font installed to $FONT_DIR"
    fi
    echo ""
    echo "  [!] Set D2Coding Nerd Font as your terminal font for icons to render."
    echo "      Or set \"icon_set\": \"unicode\" in $CONFIG"
    echo ""
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
