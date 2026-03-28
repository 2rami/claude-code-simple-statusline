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

# ── Font check ──────────────────────────────────────────────────────
Write-Host "  Checking font support..."
$fonts = (New-Object System.Drawing.Text.InstalledFontCollection).Families.Name
$nerdFound = $fonts | Where-Object { $_ -match "Nerd" }
if ($nerdFound) {
    Write-Host "  Nerd Font detected"
} else {
    Write-Host ""
    Write-Host "  [!] No Nerd Font detected. Icons may not render correctly."
    Write-Host "      Install: winget install JetBrainsMono.NerdFont"
    Write-Host "      Or:      choco install nerd-fonts-jetbrains-mono"
    Write-Host "      Or set `"icon_set`": `"unicode`" in $Config"
    Write-Host ""
}

# ── Download files ──────────────────────────────────────────────────
if (-not (Test-Path $ClaudeDir)) {
    New-Item -ItemType Directory -Path $ClaudeDir -Force | Out-Null
}

Write-Host "  Downloading statusline.py..."
Invoke-WebRequest -Uri "$BaseUrl/statusline.py" -OutFile $Statusline -UseBasicParsing

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
Write-Host "  Done! Restart Claude Code to see the new statusline."
Write-Host ""
