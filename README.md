<div align="center">

**English** | **[한국어](README.ko.md)**

# Claude Code Statusline

A simple, minimal statusline for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude_Code-statusline-purple.svg)](https://docs.anthropic.com/en/docs/claude-code)

![statusline-preview](./assets/preview.png)

<!-- Replace with a GIF for better engagement: -->
<!-- ![demo](./assets/demo.gif) -->

</div>

## Features

| Segment | Info | Color |
|---------|------|-------|
| Model | Current Claude model name | `#7aa2f7` Blue |
| Git Branch | Active branch from `git` | `#73daca` Green |
| Project | Working directory name | `#bb9af7` Purple |
| Context | Context window usage % | `#ff9e64` Orange |
| Prompt | Last prompt with intent icon | Varies |

### Prompt Classification

The statusline automatically classifies your last prompt and shows a matching icon:

| Intent | Icon | Color | Keywords |
|--------|------|-------|----------|
| Command | `` | Yellow | `/slash` commands |
| Question | `` | Blue | Contains `?` |
| Delete | `` | Red | delete, remove, drop |
| Edit | `` | Yellow | fix, edit, update, refactor |
| Create | `` | Green | create, add, build, implement |
| Search | `` | Purple | analyze, review, search, explain |
| Chat | `` | White | General conversation |
| Idle | `` | Dim | No prompt yet |

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python package runner)
- A terminal font that supports the icon set you choose (see [Font Setup](#font-setup))

## Font Setup

The default icon set uses **Nerd Font** glyphs. Your terminal font must be a Nerd Font patched variant for icons to render correctly.

### Recommended Fonts

| Font | Download |
|------|----------|
| **JetBrainsMono Nerd Font** | [nerdfonts.com](https://www.nerdfonts.com/font-downloads) |
| **FiraCode Nerd Font** | [nerdfonts.com](https://www.nerdfonts.com/font-downloads) |
| **Hack Nerd Font** | [nerdfonts.com](https://www.nerdfonts.com/font-downloads) |
| **MesloLGS Nerd Font** | [nerdfonts.com](https://www.nerdfonts.com/font-downloads) |

### Install via Homebrew (macOS)

```bash
brew install --cask font-jetbrains-mono-nerd-font
```

### After Installing

Set the Nerd Font as your terminal's font:

- **iTerm2**: Preferences > Profiles > Text > Font
- **Terminal.app**: Preferences > Profiles > Font
- **Alacritty**: `font.normal.family` in `alacritty.toml`
- **Warp**: Settings > Appearance > Font
- **VS Code Terminal**: `terminal.integrated.fontFamily` in settings

> Don't want to install a Nerd Font? Switch to `"icon_set": "unicode"` or `"plain"` in the config. See [Icon Sets](#icon-sets).

## Install

**One-line install:**

```bash
curl -fsSL https://raw.githubusercontent.com/2rami/claude-code-simple-statusline/main/install.sh | bash
```

**Manual install:**

1. Copy files to `~/.claude/`:

```bash
cp statusline.py ~/.claude/statusline.py
cp config.json ~/.claude/statusline-config.json
chmod +x ~/.claude/statusline.py
```

2. Add to your `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.py",
    "padding": 0
  }
}
```

3. Restart Claude Code.

## Configuration

All customization is done through `config.json`. The script looks for config in this order:

1. `~/.claude/statusline-config.json`
2. `config.json` next to the script

### Icon Sets

Switch between icon sets with `icon_set`:

```json
{
  "icon_set": "nerd-font"
}
```

| Set | Requirement | Example |
|-----|-------------|---------|
| `nerd-font` | Nerd Font installed | ` Opus 4.5 \|  main \|  my-project` |
| `unicode` | Any modern font | `> Opus 4.5 \| * main \| ~ my-project` |
| `plain` | Any font | `[M] Opus 4.5 \| [G] main \| [D] my-project` |

### Custom Icons Per Segment

Override individual icons regardless of the preset:

```json
{
  "icon_set": "nerd-font",
  "icons": {
    "model": "\uf233",
    "git": "\ue0a0",
    "folder": "\uf07b",
    "context": "\uf0e4",
    "prompt": {
      "command": "\uf120",
      "question": "\uf128",
      "delete": "\uf1f8",
      "edit": "\uf040",
      "create": "\uf067",
      "search": "\uf002",
      "chat": "\uf075",
      "idle": "\uf10c"
    }
  }
}
```

### Custom Colors

Override any color with hex values:

```json
{
  "colors": {
    "model": "#7aa2f7",
    "git": "#73daca",
    "folder": "#bb9af7",
    "context": "#ff9e64",
    "separator": "#565f89",
    "prompt": {
      "command": "#e0af68",
      "question": "#7aa2f7",
      "delete": "#f7768e",
      "edit": "#e0af68",
      "create": "#73daca",
      "search": "#bb9af7",
      "chat": "#c0caf5",
      "idle": "#565f89"
    }
  }
}
```

### Other Options

| Key | Default | Description |
|-----|---------|-------------|
| `separator` | `\|` | Character between segments |
| `prompt_max_length` | `5` | Max characters shown from prompt text |

## How It Works

Claude Code's `statusLine` setting supports `"type": "command"`, which pipes a JSON object to stdin containing:

```json
{
  "model": { "display_name": "Opus 4.5" },
  "cwd": "/path/to/project",
  "session_id": "abc123",
  "context_window": { "used_percentage": 42 }
}
```

The script parses this, fetches git info and the last prompt, then outputs a styled string with ANSI escape codes.

## License

[MIT](LICENSE)
