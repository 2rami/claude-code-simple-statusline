#!/bin/bash

# Claude Code Statusline - Tokyo Night
# One-line installer

set -e

CLAUDE_DIR="$HOME/.claude"
BASE_URL="https://raw.githubusercontent.com/momeWomo/claude-code-tokyonight-statusline/main"
DEST="$CLAUDE_DIR/statusline.py"
CONFIG_DEST="$CLAUDE_DIR/statusline-config.json"
SETTINGS="$CLAUDE_DIR/settings.json"

echo ""
echo "  Claude Code Statusline - Tokyo Night"
echo "  ====================================="
echo ""

# Check for Nerd Font
echo "  Checking font support..."
if command -v fc-list &> /dev/null; then
    if fc-list | grep -qi "nerd"; then
        echo "  Nerd Font detected"
    else
        echo ""
        echo "  [!] No Nerd Font detected. Icons may not render correctly."
        echo "      Install one: brew install --cask font-jetbrains-mono-nerd-font"
        echo "      Or set \"icon_set\": \"unicode\" in $CONFIG_DEST"
        echo ""
    fi
fi

# Download files
echo "  Downloading statusline.py..."
curl -fsSL "$BASE_URL/statusline.py" -o "$DEST"
chmod +x "$DEST"
echo "  Saved to $DEST"

echo "  Downloading config.json..."
curl -fsSL "$BASE_URL/config.json" -o "$CONFIG_DEST"
echo "  Saved to $CONFIG_DEST"

# Update settings.json
if [ -f "$SETTINGS" ]; then
    if command -v python3 &> /dev/null; then
        python3 -c "
import json
with open('$SETTINGS', 'r') as f:
    s = json.load(f)
s['statusLine'] = {'type': 'command', 'command': '$DEST', 'padding': 0}
with open('$SETTINGS', 'w') as f:
    json.dump(s, f, indent=2)
print('  Updated $SETTINGS')
"
    else
        echo ""
        echo "  Add this to your $SETTINGS manually:"
        echo ""
        echo '  "statusLine": {'
        echo '    "type": "command",'
        echo "    \"command\": \"$DEST\","
        echo '    "padding": 0'
        echo '  }'
    fi
else
    mkdir -p "$CLAUDE_DIR"
    cat > "$SETTINGS" << 'EOF'
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.py",
    "padding": 0
  }
}
EOF
    echo "  Created $SETTINGS"
fi

echo ""
echo "  Done! Restart Claude Code to see the new statusline."
echo ""
