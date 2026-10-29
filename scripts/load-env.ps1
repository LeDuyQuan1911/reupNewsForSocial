# Load local configuration for the current process. Never print its values.
param([string]$RepoRoot = (Split-Path -Parent $PSScriptRoot))

foreach ($name in [Environment]::GetEnvironmentVariables('User').Keys) {
    if ($name -cmatch '^REUP_[A-Z0-9_]+$') {
        $value = [Environment]::GetEnvironmentVariable($name, 'User')
        if ($value) { [Environment]::SetEnvironmentVariable($name, $value, 'Process') }
    }
}

$envFile = Join-Path $RepoRoot '.env'
if (-not (Test-Path -LiteralPath $envFile -PathType Leaf)) { return }
$lineNumber = 0
foreach ($rawLine in [IO.File]::ReadAllLines($envFile, [Text.UTF8Encoding]::new($false))) {
    $lineNumber++
    $line = $rawLine.Trim().TrimStart([char]0xFEFF)
    if (-not $line -or $line.StartsWith('#')) { continue }
    if ($line -cnotmatch '^(REUP_[A-Z0-9_]+)\s*=(.*)$') {
        throw "Invalid .env line ${lineNumber}: expected REUP_NAME=VALUE"
    }
    $name = $Matches[1]
    $value = $Matches[2].Trim()
    if ($value.Length -ge 2 -and (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'")))) {
        $value = $value.Substring(1, $value.Length - 2)
    }
    [Environment]::SetEnvironmentVariable($name, $value, 'Process')
}
