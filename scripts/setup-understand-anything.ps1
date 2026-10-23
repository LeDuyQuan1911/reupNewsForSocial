param([switch]$Check)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$pluginRoot = Join-Path $repoRoot 'vendor\understand-anything\understand-anything-plugin'
$skillPath = Join-Path $pluginRoot 'skills\understand\SKILL.md'
$coreBuild = Join-Path $pluginRoot 'packages\core\dist\index.js'

if (-not (Test-Path -LiteralPath $skillPath)) {
    throw 'Vendored Understand Anything source is missing.'
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git is required.' }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw 'Node.js is required.' }
$configuredHooks = [string](git -C $repoRoot config --local --get core.hooksPath)
if ($LASTEXITCODE -notin @(0, 1)) { throw 'Cannot read local Git hook configuration.' }
if ($configuredHooks -and $configuredHooks.Trim() -ne '.githooks') {
    throw "An existing Git hooks path is configured: $configuredHooks"
}
$effectiveHooks = [string](git -C $repoRoot config --get core.hooksPath)
if ($LASTEXITCODE -notin @(0, 1)) { throw 'Cannot read effective Git hook configuration.' }
if ($effectiveHooks -and $effectiveHooks.Trim() -ne '.githooks') {
    throw "An existing effective Git hooks path is configured: $effectiveHooks"
}

if ($Check) {
    if (-not (Test-Path -LiteralPath $coreBuild)) { throw 'Core is not built yet.' }
    if ($configuredHooks.Trim() -ne '.githooks') { throw 'Post-commit hook is not enabled yet.' }
    Write-Output 'Vendored skill, core build, and post-commit hook are ready.'
    exit 0
}

if (-not (Get-Command pnpm -ErrorAction SilentlyContinue)) { throw 'pnpm is required.' }
if (-not (Test-Path -LiteralPath $coreBuild)) {
    Push-Location $pluginRoot
    try {
        pnpm install --frozen-lockfile
        if ($LASTEXITCODE -ne 0) { throw 'pnpm install failed.' }
        pnpm --filter '@understand-anything/core' build
        if ($LASTEXITCODE -ne 0) { throw 'Core build failed.' }
    } finally {
        Pop-Location
    }
}

if (-not $configuredHooks) {
    $gitDir = (git -C $repoRoot rev-parse --path-format=absolute --git-common-dir).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Cannot find Git directory.' }
    $oldHook = Join-Path $gitDir 'hooks\post-commit'
    if (Test-Path -LiteralPath $oldHook) {
        throw "An existing post-commit hook needs manual integration: $oldHook"
    }
    git -C $repoRoot config --local core.hooksPath .githooks
    if ($LASTEXITCODE -ne 0) { throw 'Cannot enable repository hooks.' }
}

Write-Output 'Vendored Understand Anything is ready; graph updates will be requested on next use.'
