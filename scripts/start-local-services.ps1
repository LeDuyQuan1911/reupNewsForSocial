$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot

foreach ($name in @(
    'REUP_LLM_BASE_URL', 'REUP_LLM_MODEL', 'REUP_LLM_VISION_MODEL', 'REUP_LLM_API_KEY',
    'REUP_AUTO_ENABLED', 'REUP_FACEBOOK_PAGE_ID', 'REUP_FACEBOOK_PAGE_TOKEN',
    'REUP_META_GRAPH_VERSION', 'REUP_SECRET_KEY'
)) {
    $value = [Environment]::GetEnvironmentVariable($name, 'User')
    if ($value) {
        [Environment]::SetEnvironmentVariable($name, $value, 'Process')
    }
}

$router = Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 20128 -State Listen -ErrorAction SilentlyContinue
if (-not $router) {
    $routerCommand = Join-Path $env:APPDATA 'npm\9router.cmd'
    if (-not (Test-Path -LiteralPath $routerCommand)) {
        throw '9Router CLI is not installed in global npm.'
    }
    Start-Process -FilePath $routerCommand -ArgumentList @(
        '--host', '127.0.0.1', '--port', '20128', '--no-browser', '--skip-update'
    ) -WindowStyle Hidden
}

$dashboard = Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
if (-not $dashboard) {
    $python = (Get-Command python -ErrorAction Stop).Source
    Start-Process -FilePath $python -ArgumentList @('-u', 'run.py') -WorkingDirectory $root -WindowStyle Hidden
}
