# Claude Code Statusline - Simple Minimal
# Installer for Windows (PowerShell)

$ErrorActionPreference = "Stop"

$ClaudeDir = "$env:USERPROFILE\.claude"
$BaseUrl = "https://raw.githubusercontent.com/2rami/claude-code-simple-statusline/main"
$Statusline = "$ClaudeDir\statusline.py"
$Hook = "$ClaudeDir\user_prompt_submit.py"
$Config = "$ClaudeDir\statusline-config.json"
$Settings = "$ClaudeDir\settings.json"

Write-Host ""
Write-Host "  Claude Code Statusline - Simple Minimal"
Write-Host "  ====================================="
Write-Host ""

# ── Find Python ─────────────────────────────────────────────────────
$PythonCmd = $null
foreach ($cmd in @("python3", "python")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3") {
            $PythonCmd = (Get-Command $cmd).Source
            break
        }
    } catch {}
}

if (-not $PythonCmd) {
    Write-Host "  [!] Python 3 not found. Install Python 3.11+ first."
    Write-Host "      https://www.python.org/downloads/"
    exit 1
}
Write-Host "  Python found: $PythonCmd"

# ── Font: D2Coding Nerd Font ────────────────────────────────────────
Write-Host "  Checking font support..."
Add-Type -AssemblyName System.Drawing
$fonts = (New-Object System.Drawing.Text.InstalledFontCollection).Families.Name
$d2Found = $fonts | Where-Object { $_ -match "D2Coding.*Nerd" }

if ($d2Found) {
    Write-Host "  D2Coding Nerd Font detected"
} else {
    Write-Host "  Installing D2Coding Nerd Font..."
    $TmpDir = Join-Path $env:TEMP "d2coding-nerd-font"
    New-Item -ItemType Directory -Path $TmpDir -Force | Out-Null

    $ZipUrl = "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/D2Coding.zip"
    $ZipPath = Join-Path $TmpDir "D2Coding.zip"

    Write-Host "  Downloading from GitHub..."
    Invoke-WebRequest -Uri $ZipUrl -OutFile $ZipPath -UseBasicParsing

    Expand-Archive -Path $ZipPath -DestinationPath $TmpDir -Force

    $FontDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
    if (-not (Test-Path $FontDir)) {
        New-Item -ItemType Directory -Path $FontDir -Force | Out-Null
    }

    $fontFiles = Get-ChildItem -Path $TmpDir -Filter "*.ttf" -Recurse
    $shell = New-Object -ComObject Shell.Application
    $fontsFolder = $shell.Namespace(0x14)
    foreach ($f in $fontFiles) {
        Copy-Item $f.FullName -Destination $FontDir -Force
        $fontsFolder.CopyHere($f.FullName, 0x14)
    }

    Remove-Item -Path $TmpDir -Recurse -Force
    Write-Host "  D2Coding Nerd Font installed"
    Write-Host ""
    Write-Host "  [!] Set D2Coding Nerd Font as your terminal font for icons to render."
    Write-Host "      Or set `"icon_set`": `"unicode`" in $Config"
    Write-Host ""
}

# ── Download files ──────────────────────────────────────────────────
if (-not (Test-Path $ClaudeDir)) {
    New-Item -ItemType Directory -Path $ClaudeDir -Force | Out-Null
}

$Configure = "$ClaudeDir\configure-statusline.py"

Write-Host "  Downloading statusline.py..."
Invoke-WebRequest -Uri "$BaseUrl/statusline.py" -OutFile $Statusline -UseBasicParsing

Write-Host "  Downloading configure-statusline.py..."
Invoke-WebRequest -Uri "$BaseUrl/configure.py" -OutFile $Configure -UseBasicParsing

Write-Host "  Downloading user_prompt_submit.py..."
Invoke-WebRequest -Uri "$BaseUrl/user_prompt_submit.py" -OutFile $Hook -UseBasicParsing

Write-Host "  Downloading config.json..."
Invoke-WebRequest -Uri "$BaseUrl/config.json" -OutFile $Config -UseBasicParsing

# ── Update settings.json (via Python for PS5.1 compat) ──────────────
$PythonPath = ($PythonCmd -replace '\\', '/')
$StatuslinePath = ($Statusline -replace '\\', '/')
$HookPath = ($Hook -replace '\\', '/')

$pyScript = @"
import json, os

path = r'$Settings'
s = {}
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        s = json.load(f)

s['statusLine'] = {
    'type': 'command',
    'command': '$PythonPath $StatuslinePath',
    'padding': 0
}

hooks = s.get('hooks', {})
ups = hooks.get('UserPromptSubmit', [])

already = False
for entry in ups:
    for h in entry.get('hooks', []):
        if 'user_prompt_submit' in h.get('command', ''):
            already = True
            break

if not already:
    ups.append({
        'matcher': '*',
        'hooks': [{'type': 'command', 'command': '$PythonPath $HookPath'}]
    })

hooks['UserPromptSubmit'] = ups
s['hooks'] = hooks

with open(path, 'w', encoding='utf-8') as f:
    json.dump(s, f, indent=2, ensure_ascii=False)
print('  Updated ' + path)
"@

& $PythonCmd -c $pyScript

# ── Set Windows Terminal font ───────────────────────────────────────
$WtSettings = @(
    "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json",
    "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe\LocalState\settings.json"
)

foreach ($wtPath in $WtSettings) {
    if (Test-Path $wtPath) {
        $wtPyScript = @"
import json

path = r'$wtPath'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = []
for line in content.split('\n'):
    stripped = line.lstrip()
    if not stripped.startswith('//'):
        lines.append(line)
clean = '\n'.join(lines)

try:
    wt = json.loads(clean)
except:
    print('  [!] Could not parse Windows Terminal settings, skipping font setup')
    exit(0)

changed = False
defaults = wt.get('profiles', {}).get('defaults', {})
font = defaults.get('font', {})
if font.get('face') != 'D2CodingLigature Nerd Font':
    font['face'] = 'D2CodingLigature Nerd Font'
    defaults['font'] = font
    wt.setdefault('profiles', {})['defaults'] = defaults
    changed = True

if changed:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(wt, f, indent=4, ensure_ascii=False)
    print('  Windows Terminal font set to D2CodingLigature Nerd Font')
else:
    print('  Windows Terminal font already set')
"@
        & $PythonCmd -c $wtPyScript
        break
    }
}

Write-Host ""
Write-Host "  Installation complete!"
Write-Host ""

# ── Launch interactive configuration ───────────────────────────────
$UvCmd = $null
try {
    $UvCmd = (Get-Command uv -ErrorAction SilentlyContinue).Source
} catch {}

if ($UvCmd) {
    Write-Host "  Launching configuration..."
    Write-Host ""
    & uv run $Configure
    Write-Host ""
    Write-Host "  Restart Claude Code to see the new statusline."
} else {
    Write-Host "  [!] 'uv' not found. Install it first:"
    Write-Host "      irm https://astral.sh/uv/install.ps1 | iex"
    Write-Host ""
    Write-Host "  Then run: uv run $Configure"
    Write-Host "  And restart Claude Code."
}
Write-Host ""
