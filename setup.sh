#!/bin/bash

# Claude Code Setup - Harness Engineering Edition
# 개별 설치:  curl -fsSL .../setup.sh | bash -s -- <component>
# 전체 설치:  curl -fsSL .../setup.sh | bash -s -- all
#
# 사용 가능한 컴포넌트:
#   node, claude, statusline, mcp, commands, settings, claudemd, cheatsheet, all

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

CLAUDE_DIR="$HOME/.claude"
BASE_URL="https://raw.githubusercontent.com/2rami/claude-code-simple-statusline/main"

ok()    { echo -e "  ${GREEN}+${NC} $1"; }
skip()  { echo -e "  ${YELLOW}-${NC} $1 ${DIM}(이미 설치됨)${NC}"; }
info()  { echo -e "  ${DIM}  $1${NC}"; }
header(){ echo -e "\n  ${BLUE}${BOLD}$1${NC}"; }

# ════════════════════════════════════════════════════
# 1. Node.js
# ════════════════════════════════════════════════════
setup_node() {
    header "Node.js"
    if command -v node &> /dev/null; then
        skip "Node.js $(node -v)"
    else
        if [[ "$OSTYPE" == darwin* ]] && command -v brew &> /dev/null; then
            brew install node
        else
            info "fnm으로 설치 중..."
            curl -fsSL https://fnm.vercel.app/install | bash -s -- --skip-shell
            export PATH="$HOME/.local/share/fnm:$PATH"
            eval "$(fnm env)"
            fnm install --lts
        fi
        ok "Node.js $(node -v)"
    fi
}

# ════════════════════════════════════════════════════
# 2. Claude Code
# ════════════════════════════════════════════════════
setup_claude() {
    header "Claude Code"
    if command -v claude &> /dev/null; then
        skip "Claude Code"
    else
        npm install -g @anthropic-ai/claude-code
        ok "Claude Code 설치됨"
    fi
}

# ════════════════════════════════════════════════════
# 3. Status Line
# ════════════════════════════════════════════════════
setup_statusline() {
    header "Status Line"
    mkdir -p "$CLAUDE_DIR"

    # 폰트
    FONT_INSTALLED=false
    if command -v fc-list &> /dev/null; then
        fc-list | grep -qi "D2Coding.*Nerd\|D2CodingLigature.*Nerd" && FONT_INSTALLED=true
    fi
    if [ "$FONT_INSTALLED" = false ]; then
        if [[ "$OSTYPE" == darwin* ]] && command -v brew &> /dev/null; then
            brew install --cask font-d2coding-nerd-font 2>/dev/null || true
            ok "D2Coding Nerd Font"
        else
            FONT_DIR="$HOME/.local/share/fonts"
            mkdir -p "$FONT_DIR"
            TMP_DIR=$(mktemp -d)
            curl -fsSL "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/D2Coding.tar.xz" \
                -o "$TMP_DIR/D2Coding.tar.xz" 2>/dev/null
            tar -xf "$TMP_DIR/D2Coding.tar.xz" -C "$TMP_DIR"
            cp "$TMP_DIR"/*.ttf "$FONT_DIR/" 2>/dev/null || true
            rm -rf "$TMP_DIR"
            command -v fc-cache &> /dev/null && fc-cache -fv > /dev/null 2>&1
            ok "D2Coding Nerd Font"
        fi
    else
        skip "D2Coding Nerd Font"
    fi

    # 파일 다운로드
    curl -fsSL "$BASE_URL/statusline.py" -o "$CLAUDE_DIR/statusline.py"
    curl -fsSL "$BASE_URL/user_prompt_submit.py" -o "$CLAUDE_DIR/user_prompt_submit.py"
    curl -fsSL "$BASE_URL/configure.py" -o "$CLAUDE_DIR/configure-statusline.py"
    curl -fsSL "$BASE_URL/config.json" -o "$CLAUDE_DIR/statusline-config.json"
    chmod +x "$CLAUDE_DIR/statusline.py" "$CLAUDE_DIR/user_prompt_submit.py" "$CLAUDE_DIR/configure-statusline.py"

    # settings.json에 statusline + hook 등록
    PYTHON_CMD=""
    command -v python3 &> /dev/null && PYTHON_CMD="python3" || \
        { command -v python &> /dev/null && PYTHON_CMD="python"; }

    if [ -n "$PYTHON_CMD" ]; then
        $PYTHON_CMD << 'PYEOF'
import json, os

claude_dir = os.path.expanduser("~/.claude")
path = os.path.join(claude_dir, "settings.json")

s = {}
if os.path.exists(path):
    with open(path, "r") as f:
        s = json.load(f)

s["statusLine"] = {
    "type": "command",
    "command": os.path.join(claude_dir, "statusline.py"),
    "padding": 0,
}

hooks = s.get("hooks", {})
ups = hooks.get("UserPromptSubmit", [])
exists = any(
    "user_prompt_submit" in h.get("command", "")
    for e in ups for h in e.get("hooks", [])
)
if not exists:
    ups.append({
        "matcher": "*",
        "hooks": [{"type": "command",
                    "command": "python3 " + os.path.join(claude_dir, "user_prompt_submit.py")}]
    })
hooks["UserPromptSubmit"] = ups
s["hooks"] = hooks

with open(path, "w") as f:
    json.dump(s, f, indent=2)
PYEOF
    fi
    ok "상태표시줄"
}

# ════════════════════════════════════════════════════
# 4. MCP Servers
# ════════════════════════════════════════════════════
setup_mcp() {
    header "MCP Servers"
    info "context7 — 라이브러리/프레임워크 최신 문서 자동 조회"
    info "exa — Claude Code 안에서 웹 검색"

    # context7
    if claude mcp list 2>/dev/null | grep -q "context7"; then
        skip "context7"
    else
        claude mcp add context7 -s user -- npx -y @upstash/context7-mcp@latest 2>/dev/null
        ok "context7"
    fi

    # exa
    if claude mcp list 2>/dev/null | grep -q "^exa:"; then
        skip "exa"
    else
        EXA_KEY=""
        echo -ne "  Exa API key ${DIM}(exa.ai에서 무료 발급 — Enter로 건너뛰기)${NC}: "
        read -r EXA_KEY < /dev/tty 2>/dev/null || EXA_KEY=""
        if [ -n "$EXA_KEY" ]; then
            claude mcp add exa -s user -e "EXA_API_KEY=$EXA_KEY" -- npx -y exa-mcp-server 2>/dev/null
            ok "exa"
        else
            info "Exa 건너뜀 — 나중에: claude mcp add exa -s user -e EXA_API_KEY=키 -- npx -y exa-mcp-server"
        fi
    fi
}

# ════════════════════════════════════════════════════
# 5. Skills (Plugins)
# ════════════════════════════════════════════════════
setup_skills() {
    header "Skills (Plugins)"
    mkdir -p "$CLAUDE_DIR"

    PYTHON_CMD=""
    command -v python3 &> /dev/null && PYTHON_CMD="python3" || \
        { command -v python &> /dev/null && PYTHON_CMD="python"; }

    if [ -n "$PYTHON_CMD" ]; then
        $PYTHON_CMD << 'PYEOF'
import json, os

claude_dir = os.path.expanduser("~/.claude")
path = os.path.join(claude_dir, "settings.json")

s = {}
if os.path.exists(path):
    with open(path, "r") as f:
        s = json.load(f)

plugins = s.get("enabledPlugins", {})
for p in [
    "context7@claude-plugins-official",
    "frontend-design@claude-plugins-official",
    "chrome-devtools-mcp@claude-plugins-official",
    "claude-md-management@claude-plugins-official",
]:
    plugins[p] = True
s["enabledPlugins"] = plugins

with open(path, "w") as f:
    json.dump(s, f, indent=2)
PYEOF
        ok "context7, frontend-design, chrome-devtools, claude-md-management"
    else
        echo -e "  ${YELLOW}!${NC} Python 없음 — settings.json 수동 설정 필요"
    fi
}

# ════════════════════════════════════════════════════
# 6. Custom Commands
# ════════════════════════════════════════════════════
setup_commands() {
    header "Custom Commands"
    CMDS_DIR="$CLAUDE_DIR/commands"
    mkdir -p "$CMDS_DIR"
    for cmd in architect debug review; do
        curl -fsSL "$BASE_URL/commands/$cmd.md" -o "$CMDS_DIR/$cmd.md" 2>/dev/null
    done
    ok "/architect  /debug  /review"
}

# ════════════════════════════════════════════════════
# 7. Settings
# ════════════════════════════════════════════════════
setup_settings() {
    header "Settings"
    mkdir -p "$CLAUDE_DIR"

    PYTHON_CMD=""
    command -v python3 &> /dev/null && PYTHON_CMD="python3" || \
        { command -v python &> /dev/null && PYTHON_CMD="python"; }

    if [ -n "$PYTHON_CMD" ]; then
        $PYTHON_CMD << 'PYEOF'
import json, os

claude_dir = os.path.expanduser("~/.claude")
path = os.path.join(claude_dir, "settings.json")

s = {}
if os.path.exists(path):
    with open(path, "r") as f:
        s = json.load(f)

env = s.get("env", {})
env["CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"] = "1"
env["CLAUDE_CODE_NO_FLICKER"] = "1"
s["env"] = env
s["skipDangerousModePermissionPrompt"] = True

with open(path, "w") as f:
    json.dump(s, f, indent=2)
PYEOF
        ok "권한 바이패스 + 팀 모드 + 노플리커"
    else
        echo -e "  ${YELLOW}!${NC} Python 없음 — settings.json 수동 설정 필요"
    fi
}

# ════════════════════════════════════════════════════
# 8. CLAUDE.md
# ════════════════════════════════════════════════════
setup_claudemd() {
    header "CLAUDE.md"
    mkdir -p "$CLAUDE_DIR"
    CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
    if [ -f "$CLAUDE_MD" ]; then
        info "기존 파일 백업: ~/.claude/CLAUDE.md.bak"
        cp "$CLAUDE_MD" "$CLAUDE_MD.bak"
    fi
    curl -fsSL "$BASE_URL/templates/CLAUDE.md" -o "$CLAUDE_MD" 2>/dev/null
    ok "CLAUDE.md 적용됨"
}

# ════════════════════════════════════════════════════
# 9. Cheatsheet
# ════════════════════════════════════════════════════
setup_cheatsheet() {
    cat << 'CHEAT'

  Cheatsheet
  ──────────────────────────────────────

  모드
    /fast             빠른 출력 (같은 모델)
    ultrathink        프롬프트에 추가하면 깊은 추론
    Shift+Tab         플랜 모드 토글

  커스텀 명령어
    /architect        시스템 아키텍처 설계
    /debug            체계적 디버깅
    /review           코드 리뷰

  단축키
    Esc               현재 작업 취소
    Ctrl+C            생성 중단
    Tab               파일 경로 자동완성

  MCP
    context7          라이브러리 최신 문서 자동 조회
    exa               Claude Code 안에서 웹 검색

  ──────────────────────────────────────

CHEAT
}

# ════════════════════════════════════════════════════
# 전체 설치
# ════════════════════════════════════════════════════
setup_all() {
    setup_node
    setup_claude
    setup_statusline
    setup_mcp
    setup_skills
    setup_commands
    setup_settings
    setup_claudemd
    setup_cheatsheet
    echo -e "\n  ${GREEN}${BOLD}설치 완료.${NC} ${BOLD}claude${NC} 로 시작하세요.\n"
}

# ════════════════════════════════════════════════════
# 메인
# ════════════════════════════════════════════════════
CMD="${1:-help}"

case "$CMD" in
    node)       setup_node ;;
    claude)     setup_claude ;;
    statusline) setup_statusline ;;
    mcp)        setup_mcp ;;
    skills)     setup_skills ;;
    commands)   setup_commands ;;
    settings)   setup_settings ;;
    claudemd)   setup_claudemd ;;
    cheatsheet) setup_cheatsheet ;;
    all)        setup_all ;;
    *)
        echo ""
        echo -e "  ${BOLD}Claude Code Setup${NC} ${DIM}— 하네스 엔지니어링 에디션${NC}"
        echo ""
        echo -e "  ${BOLD}사용법${NC}"
        echo -e "    curl -fsSL .../setup.sh | bash -s -- <component>"
        echo ""
        echo -e "  ${BOLD}컴포넌트${NC}"
        echo -e "    ${GREEN}all${NC}          전체 설치"
        echo -e "    ${GREEN}node${NC}         Node.js"
        echo -e "    ${GREEN}claude${NC}       Claude Code CLI"
        echo -e "    ${GREEN}statusline${NC}   상태표시줄 + Nerd Font"
        echo -e "    ${GREEN}mcp${NC}          MCP 서버 (context7, exa)"
        echo -e "    ${GREEN}skills${NC}       플러그인 (context7, frontend-design, chrome-devtools 등)"
        echo -e "    ${GREEN}commands${NC}     커스텀 명령어 (/architect, /debug, /review)"
        echo -e "    ${GREEN}settings${NC}     권한 바이패스 + 팀 모드 + 노플리커"
        echo -e "    ${GREEN}claudemd${NC}     CLAUDE.md 코딩 규칙 (기존 파일 덮어쓰기)"
        echo -e "    ${GREEN}cheatsheet${NC}   빠른 참조"
        echo ""
        echo -e "  ${BOLD}예시${NC}"
        echo -e "    curl -fsSL .../setup.sh | bash -s -- all"
        echo -e "    curl -fsSL .../setup.sh | bash -s -- statusline"
        echo -e "    curl -fsSL .../setup.sh | bash -s -- mcp"
        echo ""
        ;;
esac
