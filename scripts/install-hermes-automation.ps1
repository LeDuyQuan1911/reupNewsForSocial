$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$hermes = Join-Path $env:LOCALAPPDATA 'hermes\bin\hermes.exe'
$hermesScripts = Join-Path $env:LOCALAPPDATA 'hermes\scripts'
$jobScript = Join-Path $hermesScripts 'reupnews-automation.py'
$rootPointer = Join-Path $hermesScripts 'reupnews-root.txt'
$dataDir = Join-Path $repoRoot 'data'
$jobIdFile = Join-Path $dataDir 'hermes-cron-job-id.txt'
$ownerMarker = Join-Path $dataDir 'hermes-automation.enabled'

if (-not (Test-Path -LiteralPath $hermes)) {
    throw 'Hermes chưa được cài. Chạy scripts/setup-hermes.ps1 trước.'
}
$python = Join-Path $repoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    $python = (Get-Command python -ErrorAction Stop).Source
}
New-Item -ItemType Directory -Path $hermesScripts -Force | Out-Null
New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'hermes-automation-job.py') -Destination $jobScript -Force
Set-Content -LiteralPath $rootPointer -Value $repoRoot -Encoding utf8
& $python $jobScript --check
if ($LASTEXITCODE -ne 0) { throw 'Hermes automation job không qua kiểm tra cục bộ.' }

# Keep the Hermes gateway alive after the next Windows login as well.
& $hermes gateway install --if-missing --start-on-login --no-start-now
if ($LASTEXITCODE -ne 0) { throw 'Không cài được Hermes gateway tự khởi động.' }
& $hermes cron status
if ($LASTEXITCODE -ne 0) { throw 'Hermes cron chưa sẵn sàng.' }

$jobId = ''
if (Test-Path -LiteralPath $jobIdFile) {
    $jobId = (Get-Content -LiteralPath $jobIdFile -Raw).Trim()
}
if ($jobId) {
    & $hermes cron pause $jobId
    if ($LASTEXITCODE -ne 0) { throw 'Không tạm dừng được job Hermes hiện có.' }
    & $hermes cron edit $jobId --schedule '1m' --script 'reupnews-automation.py' --no-agent --workdir $repoRoot --interpreter $python --deliver local --failure-deliver local
    if ($LASTEXITCODE -ne 0) { throw 'Không cập nhật được job Hermes.' }
} else {
    $created = & $hermes cron create '1m' --name 'reupNewsForSocial automation' --script 'reupnews-automation.py' --no-agent --workdir $repoRoot --interpreter $python --deliver local --failure-deliver local --paused
    if ($LASTEXITCODE -ne 0) { throw 'Không tạo được job Hermes.' }
    $match = [regex]::Match(($created -join "`n"), 'Created job:\s*([A-Za-z0-9_-]+)')
    if (-not $match.Success) { throw 'Hermes đã tạo job nhưng không trả ID; kiểm tra hermes cron list --all.' }
    $jobId = $match.Groups[1].Value
    Set-Content -LiteralPath $jobIdFile -Value $jobId -Encoding ascii
}

Set-Content -LiteralPath $ownerMarker -Value 'Hermes cron owns automatic preparation and due Page posts.' -Encoding ascii
& $hermes cron resume $jobId
if ($LASTEXITCODE -ne 0) {
    Remove-Item -LiteralPath $ownerMarker -ErrorAction SilentlyContinue
    throw 'Không bật được job Hermes; dashboard vẫn giữ bộ chạy lịch cũ.'
}
Write-Output "Hermes đang điều phối tự động cho repo này (job $jobId)."
Write-Output 'Dashboard đang mở cần khởi động lại một lần để chỉ phục vụ giao diện.'
