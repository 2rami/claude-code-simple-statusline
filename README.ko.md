<div align="center">

**[English](README.md)** | **Korean**

# Claude Code Statusline

[Claude Code](https://docs.anthropic.com/en/docs/claude-code)를 위한 심플하고 미니멀한 상태표시줄.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude_Code-statusline-purple.svg)](https://docs.anthropic.com/en/docs/claude-code)

![statusline-preview](./assets/preview.png)
![statusline-preview2](./assets/preview2.png)

**macOS/Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/2rami/claude-code-simple-statusline/main/install.sh | bash
```

**Windows PowerShell:**
```powershell
irm https://raw.githubusercontent.com/2rami/claude-code-simple-statusline/main/install.ps1 | iex
```

</div>

---

## 풀 셋업 (하네스 엔지니어링 에디션)

한 번에 전부 설치하거나, 필요한 것만 골라서:

**전부 설치:**
```bash
curl -fsSL https://raw.githubusercontent.com/2rami/claude-code-simple-statusline/main/setup.sh | bash -s -- all
```

**개별 설치:**

> URL 먼저 저장 — `S="https://raw.githubusercontent.com/2rami/claude-code-simple-statusline/main/setup.sh"`

**1. Node.js** — 없으면 brew (macOS) 또는 fnm (Linux)으로 자동 설치
```bash
curl -fsSL $S | bash -s -- node
```

**2. Claude Code** — `npm i -g @anthropic-ai/claude-code`로 CLI 전역 설치
```bash
curl -fsSL $S | bash -s -- claude
```

**3. 상태표시줄** — D2Coding Nerd Font + 프롬프트 분류 아이콘 + 훅 설정
```bash
curl -fsSL $S | bash -s -- statusline
```

**4. MCP 서버** — context7 (라이브러리 문서 자동 조회) + exa (웹 검색, API 키 선택)
```bash
curl -fsSL $S | bash -s -- mcp
```

**5. 스킬 (플러그인)** — settings.json에 플러그인 활성화: context7, frontend-design, chrome-devtools, claude-md-management
```bash
curl -fsSL $S | bash -s -- skills
```

**6. 커스텀 명령어** — `/architect` (시스템 설계), `/debug` (체계적 디버깅), `/review` (코드 리뷰)
```bash
curl -fsSL $S | bash -s -- commands
```

**7. 설정** — settings.json 구성: 권한 바이패스 (`skipDangerousModePermissionPrompt`), 팀 모드 (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`), 노플리커 렌더링 (`CLAUDE_CODE_NO_FLICKER`)
```bash
curl -fsSL $S | bash -s -- settings
```

**8. CLAUDE.md** — `~/.claude/CLAUDE.md`에 코딩 규칙 적용 (기존 파일은 `.bak`으로 백업)
```bash
curl -fsSL $S | bash -s -- claudemd
```

**9. 치트시트** — `/fast`, `ultrathink`, 단축키, MCP 서버 빠른 참조 출력
```bash
curl -fsSL $S | bash -s -- cheatsheet
```

---

## 기능

| 세그먼트 | 정보 | 색상 |
|----------|------|------|
| Model | 현재 Claude 모델 이름 | `#7aa2f7` 파랑 |
| Git Branch | `git`에서 가져온 현재 브랜치 | `#73daca` 초록 |
| Project | 작업 디렉토리 이름 | `#bb9af7` 보라 |
| Context | 컨텍스트 윈도우 사용률 % | `#ff9e64` 주황 |
| Prompt | 마지막 프롬프트와 의도 아이콘 | 다양함 |

### 프롬프트 분류

상태표시줄이 마지막 프롬프트를 자동으로 분류해서 맞는 아이콘을 표시해줘:

| 의도 | 아이콘 | 색상 | 키워드 |
|------|--------|------|--------|
| 명령 | `` | 노랑 | `/slash` 명령어 |
| 질문 | `` | 파랑 | `?` 포함 |
| 삭제 | `` | 빨강 | delete, remove, drop |
| 수정 | `` | 노랑 | fix, edit, update, refactor |
| 생성 | `` | 초록 | create, add, build, implement |
| 검색 | `` | 보라 | analyze, review, search, explain |
| 대화 | `` | 흰색 | 일반 대화 |
| 대기 | `` | 어두움 | 아직 프롬프트 없음 |

## 요구사항

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Python 3.11+
- 선택한 아이콘 세트를 지원하는 터미널 폰트 ([폰트 설정](#폰트-설정) 참고)

## 폰트 설정

기본 아이콘 세트는 **Nerd Font** 글리프를 사용해. 이 프로젝트는 **D2Coding Nerd Font**을 사용해 — 한글 지원, 리거처, Nerd Font 아이콘이 다 포함된 모노스페이스 폰트야.

설치 스크립트가 자동으로 폰트를 다운로드해서 설치해줘. 수동으로 설치하려면:

<details>
<summary><b>macOS (Homebrew)</b></summary>

```bash
brew install --cask font-d2coding-nerd-font
```
</details>

<details>
<summary><b>Windows</b></summary>

[Nerd Fonts GitHub](https://github.com/ryanoasis/nerd-fonts/releases/latest/download/D2Coding.zip)에서 다운로드 후 `.ttf` 파일을 설치.
</details>

<details>
<summary><b>Linux</b></summary>

```bash
curl -fsSL https://github.com/ryanoasis/nerd-fonts/releases/latest/download/D2Coding.tar.xz -o /tmp/D2Coding.tar.xz
mkdir -p ~/.local/share/fonts
tar -xf /tmp/D2Coding.tar.xz -C ~/.local/share/fonts
fc-cache -fv
```
</details>

### 터미널 폰트 설정

설치 후 터미널에서 **D2Coding Nerd Font**를 기본 폰트로 설정해:

| 터미널 | 설정 위치 |
|--------|----------|
| **iTerm2** | Preferences > Profiles > Text > Font |
| **Terminal.app** | Preferences > Profiles > Font |
| **Windows Terminal** | 설정 > 프로필 > 모양 > 글꼴 |
| **VS Code** | 설정에서 `terminal.integrated.fontFamily` |
| **Alacritty** | `alacritty.toml`에서 `font.normal.family` |
| **Warp** | Settings > Appearance > Font |

> Nerd Font 설치하기 싫으면? 설정에서 `"icon_set": "unicode"` 또는 `"plain"`으로 바꾸면 돼. [아이콘 세트](#아이콘-세트) 참고.

## 설치

### macOS / Linux

**한 줄 설치:**

```bash
curl -fsSL https://raw.githubusercontent.com/2rami/claude-code-simple-statusline/main/install.sh | bash
```

**수동 설치:**

1. 파일들을 `~/.claude/`에 복사:

```bash
cp statusline.py ~/.claude/statusline.py
cp configure.py ~/.claude/configure-statusline.py
cp user_prompt_submit.py ~/.claude/user_prompt_submit.py
cp config.json ~/.claude/statusline-config.json
chmod +x ~/.claude/statusline.py ~/.claude/configure-statusline.py ~/.claude/user_prompt_submit.py
```

2. `~/.claude/settings.json`에 추가:

```json
{
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
}
```

3. Claude Code 재시작.

### Windows

**한 줄 설치 (PowerShell):**

```powershell
irm https://raw.githubusercontent.com/2rami/claude-code-simple-statusline/main/install.ps1 | iex
```

**수동 설치:**

1. 파일들을 `%USERPROFILE%\.claude\`에 복사:

```powershell
Copy-Item statusline.py $env:USERPROFILE\.claude\statusline.py
Copy-Item configure.py $env:USERPROFILE\.claude\configure-statusline.py
Copy-Item user_prompt_submit.py $env:USERPROFILE\.claude\user_prompt_submit.py
Copy-Item config.json $env:USERPROFILE\.claude\statusline-config.json
```

2. `%USERPROFILE%\.claude\settings.json`에 추가:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python C:/Users/YOU/.claude/statusline.py",
    "padding": 0
  },
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "python C:/Users/YOU/.claude/user_prompt_submit.py"
      }]
    }]
  }
}
```

> `C:/Users/YOU` 부분을 본인 경로로 바꿔야 해.

3. Claude Code 재시작.

## 설정

### 인터랙티브 CLI (추천)

방향키로 선택하면서 설정할 수 있는 CLI 도구:

```bash
uv run ~/.claude/configure-statusline.py
```

아이콘 세트, 색상, 구분자, 프롬프트 길이, 개별 아이콘까지 전부 터미널에서 파일 수정 없이 설정 가능해.

### 수동 설정

모든 커스터마이징은 `config.json`에서 해. 스크립트가 설정 파일을 찾는 순서:

1. `~/.claude/statusline-config.json`
2. 스크립트 옆의 `config.json`

### 아이콘 세트

`icon_set`으로 아이콘 세트 변경:

```json
{
  "icon_set": "nerd-font"
}
```

| 세트 | 필요사항 | 예시 |
|------|----------|------|
| `nerd-font` | Nerd Font 설치됨 | ` Opus 4.5 \|  main \|  my-project` |
| `unicode` | 아무 모던 폰트 | `> Opus 4.5 \| * main \| ~ my-project` |
| `plain` | 아무 폰트 | `[M] Opus 4.5 \| [G] main \| [D] my-project` |

### 세그먼트별 커스텀 아이콘

프리셋과 관계없이 개별 아이콘 오버라이드:

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

### 커스텀 색상

hex 값으로 색상 오버라이드:

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

### 기타 옵션

| 키 | 기본값 | 설명 |
|----|--------|------|
| `separator` | `\|` | 세그먼트 사이 구분 문자 |
| `prompt_max_length` | `5` | 프롬프트 텍스트에서 보여줄 최대 글자 수 |

## 작동 원리

Claude Code의 `statusLine` 설정은 `"type": "command"`를 지원하는데, stdin으로 아래 같은 JSON 객체를 파이프해줘:

```json
{
  "model": { "display_name": "Opus 4.5" },
  "cwd": "/path/to/project",
  "session_id": "abc123",
  "context_window": { "used_percentage": 42 }
}
```

스크립트가 이걸 파싱하고, git 정보와 마지막 프롬프트(`UserPromptSubmit` 훅이 저장한 것)를 가져온 다음, ANSI 이스케이프 코드로 스타일링된 문자열을 출력해.

## 라이선스

[MIT](LICENSE)
