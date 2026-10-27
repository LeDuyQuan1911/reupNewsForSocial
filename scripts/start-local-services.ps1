$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot

foreach ($name in @(
    'REUP_LLM_BASE_URL', 'REUP_LLM_MODEL', 'REUP_LLM_VISION_MODEL', 'REUP_LLM_IMAGE_MODEL', 'REUP_LLM_API_KEY',
    'REUP_AUTO_ENABLED', 'REUP_FACEBOOK_PAGE_ID', 'REUP_FACEBOOK_PAGE_NAME', 'REUP_FACEBOOK_PAGE_NAME_ID', 'REUP_FACEBOOK_PAGE_TOKEN',
    'REUP_FACEBOOK_AUTH_MODE', 'REUP_FACEBOOK_SYSTEM_USER_TOKEN',
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

if (Test-Path -LiteralPath (Join-Path $root 'data\hermes-automation.enabled')) {
    $hermes = Join-Path $env:LOCALAPPDATA 'hermes\bin\hermes.exe'
    if (-not (Test-Path -LiteralPath $hermes)) {
        throw 'Hermes CLI chưa được cài trên máy này.'
    }
    $routerReady = $false
    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        try {
            Invoke-WebRequest -Uri 'http://127.0.0.1:20128/login' -UseBasicParsing -TimeoutSec 2 | Out-Null
            $routerReady = $true
            break
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    if (-not $routerReady) {
        throw '9Router chưa sẵn sàng; chưa khởi động Hermes để tránh xử lý bài khi model không khả dụng.'
    }
    & $hermes gateway ensure --timeout 60 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw 'Không khởi động được Hermes gateway.'
    }
}

$dashboard = Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
if (-not $dashboard) {
    $python = (Get-Command python -ErrorAction Stop).Source
    Start-Process -FilePath $python -ArgumentList @('-u', 'run.py') -WorkingDirectory $root -WindowStyle Hidden
}
