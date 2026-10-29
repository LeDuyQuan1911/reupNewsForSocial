param(
    [string]$Prompt
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
& (Join-Path $PSScriptRoot 'load-env.ps1') -RepoRoot $repoRoot
$hermes = Join-Path $env:LOCALAPPDATA 'hermes\bin\hermes.exe'

if (-not (Test-Path -LiteralPath $hermes)) {
    throw 'Hermes chưa được cài. Chạy scripts/setup-hermes.ps1 trước.'
}

if (-not $env:REUP_LLM_API_KEY) {
    throw 'Thiếu REUP_LLM_API_KEY trong .env hoặc biến môi trường User.'
}

if ($Prompt) {
    & $hermes --in $repoRoot -z $Prompt
} else {
    & $hermes --in $repoRoot
}

if ($LASTEXITCODE -ne 0) { throw "Hermes kết thúc với mã lỗi $LASTEXITCODE." }
