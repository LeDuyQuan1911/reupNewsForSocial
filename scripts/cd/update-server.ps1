param(
    [string]$RepoRoot = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)),
    [switch]$CheckOnly,
    [switch]$StartOnly
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$dataDir = Join-Path $RepoRoot 'data'
$python = Join-Path $RepoRoot '.venv\Scripts\python.exe'
$hermes = Join-Path $env:LOCALAPPDATA 'hermes\bin\hermes.exe'
$jobIdFile = Join-Path $dataDir 'hermes-cron-job-id.txt'
$pauseFile = Join-Path $dataDir 'deployment-paused'
$pidFile = Join-Path $dataDir 'dashboard.pid'
$lockFile = Join-Path $dataDir 'hermes-job.lock'

function Invoke-Git([string[]]$Arguments) {
    $result = & git -C $RepoRoot @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Git failed: $($Arguments[0])" }
    return $result
}

function Get-DashboardChildren([int]$ParentPid) {
    @(Get-CimInstance Win32_Process -Filter "ParentProcessId=$ParentPid" -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -match '(^|[\\\s])run\.py(["\s]|$)' })
}

function Test-Dashboard {
    param([int]$ExpectedPid)
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        $listener = Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
        $ownedPids = @($ExpectedPid) + @(Get-DashboardChildren -ParentPid $ExpectedPid | ForEach-Object { $_.ProcessId })
        if ($listener -and $listener.OwningProcess -in $ownedPids) {
            try {
                $response = Invoke-WebRequest -Uri 'http://127.0.0.1:5000/healthz' -UseBasicParsing -TimeoutSec 3
                if ($response.StatusCode -eq 200) { return $true }
            } catch { }
        }
        Start-Sleep -Seconds 1
    }
    return $false
}

function Stop-OwnedDashboard {
    if (Test-Path -LiteralPath $pidFile) {
        $serverPid = [int](Get-Content -LiteralPath $pidFile -Raw).Trim()
        $process = Get-CimInstance Win32_Process -Filter "ProcessId=$serverPid" -ErrorAction SilentlyContinue
        if ($process) {
            if (-not $process.CommandLine -or -not $process.CommandLine.Contains('run.py') -or
                -not $process.ExecutablePath.StartsWith((Split-Path -Parent $python), [StringComparison]::OrdinalIgnoreCase)) {
                throw 'Dashboard PID does not belong to this deployment; refusing to stop it.'
            }
            $children = @(Get-DashboardChildren -ParentPid $serverPid)
            $ownedPids = @($serverPid) + @($children | ForEach-Object { $_.ProcessId })
            $listener = Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($listener -and $listener.OwningProcess -notin $ownedPids) {
                throw 'Port 5000 belongs to another process; refusing to stop it.'
            }
            foreach ($child in $children) {
                Stop-Process -Id $child.ProcessId -Force -ErrorAction SilentlyContinue
                try { Wait-Process -Id $child.ProcessId -Timeout 15 -ErrorAction SilentlyContinue } catch { }
            }
            Stop-Process -Id $serverPid -Force
            try { Wait-Process -Id $serverPid -Timeout 15 -ErrorAction SilentlyContinue } catch { }
        }
        Remove-Item -LiteralPath $pidFile -Force
    }
    $listener = Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($listener) { throw 'Port 5000 is in use by an unmanaged process; deployment stopped.' }
}

function Start-OwnedDashboard {
    $process = Start-Process -FilePath $python -ArgumentList @('-u', 'run.py') -WorkingDirectory $RepoRoot -PassThru -WindowStyle Hidden
    Set-Content -LiteralPath $pidFile -Value $process.Id -Encoding ascii
    if (-not (Test-Dashboard -ExpectedPid $process.Id)) {
        Stop-OwnedDashboard
        throw 'Dashboard health check failed.'
    }
}

if (-not (Test-Path -LiteralPath $python)) { throw 'Create .venv and install requirements on the server first.' }
if (-not (Test-Path -LiteralPath $hermes) -or -not (Test-Path -LiteralPath $jobIdFile) -or
    -not (Test-Path -LiteralPath (Join-Path $dataDir 'hermes-automation.enabled'))) {
    throw 'Hermes automation must be installed on this server before enabling CD.'
}
$origin = (Invoke-Git -Arguments @('remote', 'get-url', 'origin')) -join ''
if ($origin -notin @('https://github.com/LeDuyQuan1911/reupNewsForSocial.git',
                     'git@github.com:LeDuyQuan1911/reupNewsForSocial.git')) {
    throw 'Unexpected origin; refusing to deploy.'
}
if ((Invoke-Git -Arguments @('status', '--porcelain', '--untracked-files=normal'))) {
    throw 'Server checkout has local changes; refusing to overwrite them.'
}
Invoke-Git -Arguments @('fetch', '--no-tags', 'origin', 'main') | Out-Null
$target = (Invoke-Git -Arguments @('rev-parse', 'FETCH_HEAD')) -join ''
$current = (Invoke-Git -Arguments @('rev-parse', 'HEAD')) -join ''
if ($target -eq $current -and -not $StartOnly) { Write-Output "Already current: $current"; exit 0 }
& git -C $RepoRoot merge-base --is-ancestor $current $target
if ($LASTEXITCODE -ne 0) { throw 'Main is not a descendant of deployed code; manual review required.' }
& $python (Join-Path $PSScriptRoot 'release_gate.py') $target
if ($LASTEXITCODE -eq 1) { Write-Output 'Waiting for successful main CI.'; exit 0 }
if ($LASTEXITCODE -ne 0) { throw 'Could not verify main CI; deployment stopped.' }
if ($StartOnly) {
    if ($target -ne $current) { throw 'StartOnly requires server checkout to match current main.' }
    if (Test-Path -LiteralPath $pidFile) { throw 'Dashboard PID file already exists.' }
    $listener = Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
    if ($listener) { throw 'Port 5000 is already in use.' }
    Start-OwnedDashboard
    Write-Output "Started dashboard at $current"
    exit 0
}
if ($CheckOnly) { Write-Output "Ready to deploy $target"; exit 0 }

$deployLock = $null
$cycleLock = $null
$jobPaused = $false
$resumeAttempted = $false
$switched = $false
$pauseOwned = $false
$dashboardWasRunning = $false
$backup = Join-Path $dataDir ("backups\reup-{0}.sqlite3" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$toolsDir = Join-Path $dataDir 'deployment-tools'
$jobId = (Get-Content -LiteralPath $jobIdFile -Raw).Trim()
if ($jobId -notmatch '^[A-Za-z0-9_-]+$') { throw 'Invalid Hermes job ID.' }
try {
    $deployLock = [IO.File]::Open((Join-Path $dataDir 'deployment.lock'), 'OpenOrCreate', 'ReadWrite', 'None')
    Set-Content -LiteralPath $pauseFile -Value "Updating to $target" -Encoding ascii
    $pauseOwned = $true
    & $hermes cron pause $jobId | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Could not pause Hermes cron.' }
    $jobPaused = $true

    $deadline = (Get-Date).AddMinutes(10)
    while ((Get-Date) -lt $deadline) {
        try {
            $cycleLock = [IO.File]::Open($lockFile, 'OpenOrCreate', 'ReadWrite', 'ReadWrite')
            if ($cycleLock.Length -eq 0) { $cycleLock.WriteByte(48); $cycleLock.Flush() }
            $cycleLock.Lock(0, 1)
            break
        } catch {
            if ($cycleLock) { $cycleLock.Dispose(); $cycleLock = $null }
            Start-Sleep -Seconds 2
        }
    }
    if (-not $cycleLock) { throw 'Hermes cycle did not finish within 10 minutes.' }
    if (Test-Path -LiteralPath $pidFile) {
        $oldPid = [int](Get-Content -LiteralPath $pidFile -Raw).Trim()
        $dashboardWasRunning = [bool](Get-Process -Id $oldPid -ErrorAction SilentlyContinue)
    }
    Stop-OwnedDashboard
    $db = Join-Path $dataDir 'reup.sqlite3'
    if (-not (Test-Path -LiteralPath $db)) { throw 'Production database missing; bootstrap the server first.' }
    New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'backup_db.py') -Destination (Join-Path $toolsDir 'backup_db.py') -Force
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'smoke.py') -Destination (Join-Path $toolsDir 'smoke.py') -Force
    Copy-Item -LiteralPath (Join-Path $RepoRoot 'scripts\hermes-automation-job.py') -Destination (Join-Path $toolsDir 'old-hermes-job.py') -Force
    & $python (Join-Path $toolsDir 'backup_db.py') $db $backup
    if ($LASTEXITCODE -ne 0) { throw 'Database backup failed.' }

    $switched = $true
    Invoke-Git -Arguments @('checkout', '--detach', $target) | Out-Null
    & $python -m pip install -r (Join-Path $RepoRoot 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Dependency install failed.' }
    Push-Location $RepoRoot
    try { & $python (Join-Path $toolsDir 'smoke.py') } finally { Pop-Location }
    if ($LASTEXITCODE -ne 0) { throw 'Isolated smoke check failed.' }
    Start-OwnedDashboard
    Copy-Item -LiteralPath (Join-Path $RepoRoot 'scripts\hermes-automation-job.py') -Destination (Join-Path $env:LOCALAPPDATA 'hermes\scripts\reupnews-automation.py') -Force
    $resumeAttempted = $true
    & $hermes cron resume $jobId | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Could not resume Hermes cron.' }
    $jobPaused = $false
    Write-Output "Deployed $target; database backup: $backup"
    Remove-Item -LiteralPath $pauseFile -Force
} catch {
    $failure = $_
    if ($resumeAttempted) {
        try { & $hermes cron pause $jobId | Out-Null } catch { }
        throw "Deployment reached Hermes resume; automatic DB rollback is disabled to protect post state. Maintenance remains active. Inspect manually: $failure"
    }
    if ($switched) {
        try {
            Stop-OwnedDashboard
            Invoke-Git -Arguments @('checkout', '--detach', $current) | Out-Null
            & $python -m pip install -r (Join-Path $RepoRoot 'requirements.txt')
            if ($LASTEXITCODE -ne 0) { throw 'Rollback dependency install failed.' }
            & $python (Join-Path $toolsDir 'backup_db.py') $backup (Join-Path $dataDir 'reup.sqlite3')
            if ($LASTEXITCODE -ne 0) { throw 'Rollback database restore failed.' }
            Start-OwnedDashboard
            Copy-Item -LiteralPath (Join-Path $toolsDir 'old-hermes-job.py') -Destination (Join-Path $env:LOCALAPPDATA 'hermes\scripts\reupnews-automation.py') -Force
        } catch {
            throw "Deployment failed and rollback needs manual repair. Hermes remains paused. Failure: $failure; rollback: $_"
        }
    } elseif ($dashboardWasRunning) {
        try { Start-OwnedDashboard } catch {
            throw "Deployment stopped before checkout and dashboard did not restart. Hermes remains paused. Failure: $failure; restart: $_"
        }
    }
    if ($jobPaused) {
        & $hermes cron resume $jobId | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "Deployment failed; Hermes remains paused. Failure: $failure" }
    }
    if ($pauseOwned -and (Test-Path -LiteralPath $pauseFile)) { Remove-Item -LiteralPath $pauseFile -Force }
    throw "Deployment failed; previous version restored when possible: $failure"
} finally {
    if ($cycleLock) { $cycleLock.Unlock(0, 1); $cycleLock.Dispose() }
    if ($deployLock) { $deployLock.Dispose() }
}
