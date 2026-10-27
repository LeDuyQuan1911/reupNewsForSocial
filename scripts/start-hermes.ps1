param(
    [string]$Prompt
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$hermes = Join-Path $env:LOCALAPPDATA 'hermes\bin\hermes.exe'

if (-not (Test-Path -LiteralPath $hermes)) {
    throw 'Hermes chưa được cài. Chạy scripts/setup-hermes.ps1 trước.'
}

foreach ($name in @('REUP_LLM_BASE_URL', 'REUP_LLM_MODEL', 'REUP_LLM_API_KEY')) {
    if (-not [Environment]::GetEnvironmentVariable($name, 'Process')) {
        $value = [Environment]::GetEnvironmentVariable($name, 'User')
        if ($value) { [Environment]::SetEnvironmentVariable($name, $value, 'Process') }
    }
}

if (-not $env:REUP_LLM_API_KEY) {
    throw 'REUP_LLM_API_KEY chưa có trong biến môi trường User.'
}

if ($Prompt) {
    & $hermes --in $repoRoot -z $Prompt
} else {
    & $hermes --in $repoRoot
}

if ($LASTEXITCODE -ne 0) { throw "Hermes kết thúc với mã lỗi $LASTEXITCODE." }
