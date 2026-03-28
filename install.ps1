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

# ── Update settings.json ────────────────────────────────────────────
# Convert Python path to forward slashes for JSON
$PythonPath = $PythonCmd -replace '\\', '/'
$StatuslinePath = $Statusline -replace '\\', '/'
$HookPath = $Hook -replace '\\', '/'

$s = @{}
if (Test-Path $Settings) {
    $s = Get-Content $Settings -Raw | ConvertFrom-Json -AsHashtable
}

$s["statusLine"] = @{
    type    = "command"
    command = "$PythonPath $StatuslinePath"
    padding = 0
}

# Add hook
if (-not $s.ContainsKey("hooks")) {
    $s["hooks"] = @{}
}
$hooks = $s["hooks"]

$hookCmd = "$PythonPath $HookPath"
$hookEntry = @{
    matcher = "*"
    hooks   = @(@{
        type    = "command"
        command = $hookCmd
    })
}

$already = $false
if ($hooks.ContainsKey("UserPromptSubmit")) {
    foreach ($entry in $hooks["UserPromptSubmit"]) {
        foreach ($h in $entry["hooks"]) {
            if ($h["command"] -match "user_prompt_submit") {
                $already = $true
                break
            }
        }
    }
}

if (-not $already) {
    if (-not $hooks.ContainsKey("UserPromptSubmit")) {
        $hooks["UserPromptSubmit"] = @()
    }
    $hooks["UserPromptSubmit"] += $hookEntry
}

$s["hooks"] = $hooks

$s | ConvertTo-Json -Depth 10 | Set-Content $Settings -Encoding UTF8
Write-Host "  Updated $Settings"

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
