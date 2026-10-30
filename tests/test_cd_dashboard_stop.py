"""Exercise the Windows venv launcher exiting when its child is stopped."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(os.name == "nt", "Windows process behavior only")
class DashboardStopTests(unittest.TestCase):
    def test_parent_exits_after_child_is_stopped(self):
        with tempfile.TemporaryDirectory() as directory:
            pid_file = Path(directory) / "dashboard.pid"
            pid_file.write_text("17080", encoding="ascii")
            env = dict(os.environ, REUP_TEST_PID_FILE=str(pid_file),
                       REUP_TEST_UPDATER=str(ROOT / "scripts/cd/update-server.ps1"))
            command = r"""
$ErrorActionPreference = 'Stop'
$text = Get-Content -LiteralPath $env:REUP_TEST_UPDATER -Raw
$tokens = $null; $errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseInput($text, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw 'Updater failed to parse' }
$definition = $ast.Find({ param($node)
    $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
    $node.Name -eq 'Stop-OwnedDashboard'
}, $true)
if (-not $definition) { throw 'Stop-OwnedDashboard missing' }
Invoke-Expression $definition.Extent.Text

$pidFile = $env:REUP_TEST_PID_FILE
$python = 'C:\repo\.venv\Scripts\python.exe'
$script:parentAlive = $true
$script:childAlive = $true
$script:parentStopped = $false
$script:parent = [pscustomobject]@{
    CommandLine = 'python -u run.py'
    ExecutablePath = $python
    CreationDate = '20261031010000.000000+420'
}
function Get-CimInstance {
    [CmdletBinding()]
    param([string]$ClassName, [string]$Filter)
    if ($script:parentAlive -and $Filter -eq 'ProcessId=17080') { return $script:parent }
}
function Get-DashboardChildren {
    param([int]$ParentPid)
    if ($script:childAlive) { return [pscustomobject]@{ProcessId = 17081} }
}
function Get-NetTCPConnection {
    [CmdletBinding()]
    param([string]$LocalAddress, [int]$LocalPort, [string]$State)
    if ($script:childAlive) { return [pscustomobject]@{OwningProcess = 17081} }
}
function Stop-Process {
    [CmdletBinding()]
    param([int]$Id, [switch]$Force)
    if ($Id -eq 17081) {
        $script:childAlive = $false
        $script:parentAlive = $false
    } elseif ($Id -eq 17080) {
        $script:parentStopped = $true
        throw 'Already exited'
    } else { throw 'Unexpected PID' }
}
function Wait-Process {
    [CmdletBinding()]
    param([int]$Id, [int]$Timeout)
}
Stop-OwnedDashboard
if ($script:parentStopped -or $script:childAlive -or (Test-Path -LiteralPath $pidFile)) {
    throw 'Dashboard cleanup incomplete'
}
"""
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                env=env, cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
