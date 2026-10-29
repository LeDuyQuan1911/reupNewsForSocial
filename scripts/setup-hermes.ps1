param(
    [switch]$TestConnection
)

$ErrorActionPreference = 'Stop'

# Pin the upstream source revision tested with this project.
$hermesCommit = 'bf0203a794a07aac3ff764972ab9087baa4e4f4e'
$installerSha256 = '82781C63BEF90920CEB41A075B69FF5994D12AC1F11606D0B572573FDF515FC2'
$repoRoot = Split-Path -Parent $PSScriptRoot
& (Join-Path $PSScriptRoot 'load-env.ps1') -RepoRoot $repoRoot
$installer = Join-Path $repoRoot 'vendor\hermes-agent\scripts\install.ps1'
$hermesHome = Join-Path $env:LOCALAPPDATA 'hermes'
$sourceDir = Join-Path $hermesHome 'hermes-agent'
$hermes = Join-Path $hermesHome 'bin\hermes.exe'

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git is required to install and verify Hermes.'
}
if (-not (Test-Path -LiteralPath $installer)) {
    throw 'Vendored Hermes installer is missing. Restore vendor/hermes-agent from this repo.'
}
$actualHash = (Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash
if ($actualHash -ne $installerSha256) { throw 'Vendored Hermes installer checksum mismatch.' }

if (-not (Test-Path -LiteralPath $hermes)) {
    & $installer -Branch main -Commit $hermesCommit -Channel stable -NonInteractive
    if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw "Hermes installer failed with code $LASTEXITCODE." }
}

if (-not (Test-Path -LiteralPath $hermes) -or -not (Test-Path -LiteralPath (Join-Path $sourceDir '.git'))) {
    throw 'Hermes installation is incomplete.'
}
$installedCommit = (& git -C $sourceDir rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $installedCommit -ne $hermesCommit) {
    throw "Hermes is installed at a different revision ($installedCommit). Review it before changing the shared user installation."
}

$model = $env:REUP_LLM_MODEL
if ([string]::IsNullOrWhiteSpace($model)) {
    throw 'Set REUP_LLM_MODEL to a model ID available in 9Router, then rerun this script.'
}
$baseUrl = $env:REUP_LLM_BASE_URL
if ([string]::IsNullOrWhiteSpace($baseUrl)) { $baseUrl = 'http://127.0.0.1:20128/v1' }
if ($baseUrl -notmatch '^https?://') { throw 'REUP_LLM_BASE_URL must start with http:// or https://.' }

foreach ($setting in @(
    @('model.default', $model),
    @('model.provider', 'custom'),
    @('model.base_url', $baseUrl),
    @('model.key_env', 'REUP_LLM_API_KEY')
)) {
    & $hermes config set $setting[0] $setting[1]
    if ($LASTEXITCODE -ne 0) { throw "Hermes could not set $($setting[0])." }
}

Write-Output "Hermes $installedCommit is configured for $baseUrl ($model)."
if (-not $env:REUP_LLM_API_KEY) {
    Write-Warning 'REUP_LLM_API_KEY is not set. Set it in the User environment before running Hermes.'
}

if ($TestConnection) {
    if (-not $env:REUP_LLM_API_KEY) { throw 'REUP_LLM_API_KEY is required for -TestConnection.' }
    & $hermes -z 'Reply with exactly: OK'
    if ($LASTEXITCODE -ne 0) { throw "Hermes connection test failed with code $LASTEXITCODE." }
}
