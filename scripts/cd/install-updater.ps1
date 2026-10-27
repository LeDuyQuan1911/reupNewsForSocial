param([string]$TaskName = 'reupNewsForSocial update')

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$updater = Join-Path $PSScriptRoot 'update-server.ps1'
if (-not (Test-Path -LiteralPath $updater)) { throw 'Updater script missing.' }

# The task must use the account that owns Hermes, its User environment and local data.
$account = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$credential = Get-Credential -UserName $account -Message 'Enter this Windows account password for the scheduled deployment task'
if ($credential.UserName -ne $account) { throw 'Use the same Windows account that owns Hermes.' }
$password = $credential.GetNetworkCredential().Password
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument (
    '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "{0}" -RepoRoot "{1}"' -f $updater, $repoRoot
)
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings `
    -User $account -Password $password -Force | Out-Null
$password = $null
Write-Output "Updater task '$TaskName' installed. It checks main every five minutes under $account."
