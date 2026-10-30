"""Exercise the dashboard stop path with stable Windows process handles."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(os.name == "nt", "Windows process behavior only")
class DashboardStopTests(unittest.TestCase):
    def run_case(self, reused_pid: bool = False, cim_error: bool = False):
        with tempfile.TemporaryDirectory() as directory:
            pid_file = Path(directory) / "dashboard.pid"
            pid_file.write_text("17080", encoding="ascii")
            env = dict(os.environ, REUP_TEST_PID_FILE=str(pid_file),
                       REUP_TEST_UPDATER=str(ROOT / "scripts/cd/update-server.ps1"),
                       REUP_TEST_REUSED_PID="1" if reused_pid else "0",
                       REUP_TEST_CIM_ERROR="1" if cim_error else "0")
            command = r"""
$ErrorActionPreference = 'Stop'
$text = Get-Content -LiteralPath $env:REUP_TEST_UPDATER -Raw
$tokens = $null; $errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseInput($text, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw 'Updater failed to parse' }
foreach ($name in @('Get-VerifiedDashboardProcess', 'Stop-VerifiedDashboardProcess', 'Stop-OwnedDashboard')) {
    $definition = $ast.Find({ param($node)
        $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
        $node.Name -eq $name
    }, $true)
    if (-not $definition) { throw "Missing function: $name" }
    Invoke-Expression $definition.Extent.Text
}

$pidFile = $env:REUP_TEST_PID_FILE
$python = 'C:\repo\.venv\Scripts\python.exe'
$created = Get-Date '2026-10-31T01:00:00'
$script:parentCim = [pscustomobject]@{
    ProcessId = 17080
    CommandLine = 'python -u run.py'
    ExecutablePath = $python
    CreationDate = $created
}
$script:childCim = [pscustomobject]@{ProcessId = 17081; CreationDate = $created}
$script:parentHandle = [pscustomobject]@{Handle = 1; StartTime = $created; HasExited = $false}
$script:childHandle = [pscustomobject]@{Handle = 2; StartTime = $created; HasExited = $false}
if ($env:REUP_TEST_REUSED_PID -eq '1') { $script:childHandle.StartTime = $created.AddSeconds(5) }
$script:childHandle | Add-Member ScriptMethod Kill {
    $this.HasExited = $true
    $script:parentHandle.HasExited = $true
}
$script:childHandle | Add-Member ScriptMethod WaitForExit { param($timeout) return $true }
$script:parentHandle | Add-Member ScriptMethod Kill { $this.HasExited = $true }
$script:parentHandle | Add-Member ScriptMethod WaitForExit { param($timeout) return $true }
function Get-CimInstance {
    [CmdletBinding()]
    param([string]$ClassName, [string]$Filter)
    if ($env:REUP_TEST_CIM_ERROR -eq '1') { throw 'CIM unavailable' }
    if ($Filter -eq 'ProcessId=17080') { return $script:parentCim }
}
function Get-DashboardChildren {
    param([int]$ParentPid)
    return $script:childCim
}
function Get-Process {
    [CmdletBinding()]
    param([int]$Id)
    if ($Id -eq 17080) { return $script:parentHandle }
    if ($Id -eq 17081) { return $script:childHandle }
    throw 'Unexpected PID'
}
function Get-NetTCPConnection {
    [CmdletBinding()]
    param([string]$LocalAddress, [int]$LocalPort, [string]$State)
    if (-not $script:childHandle.HasExited) { return [pscustomobject]@{OwningProcess = 17081} }
}

if ($env:REUP_TEST_CIM_ERROR -eq '1') {
    try { Stop-OwnedDashboard; throw 'Expected CIM failure' }
    catch {
        if ($_.Exception.Message -notmatch 'CIM unavailable') { throw }
    }
    if ($script:childHandle.HasExited -or -not (Test-Path -LiteralPath $pidFile)) {
        throw 'CIM failure stopped dashboard or removed PID file'
    }
} elseif ($env:REUP_TEST_REUSED_PID -eq '1') {
    try { Stop-OwnedDashboard; throw 'Expected reused PID rejection' }
    catch {
        if ($_.Exception.Message -notmatch 'PID was reused') { throw }
    }
    if ($script:childHandle.HasExited -or -not (Test-Path -LiteralPath $pidFile)) {
        throw 'Reused PID was stopped or PID file removed'
    }
} else {
    Stop-OwnedDashboard
    if (-not $script:childHandle.HasExited -or -not $script:parentHandle.HasExited -or
        (Test-Path -LiteralPath $pidFile)) {
        throw 'Dashboard cleanup incomplete'
    }
}
"""
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                env=env, cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_parent_exits_after_child_is_stopped(self):
        self.run_case(reused_pid=False)

    def test_reused_child_pid_is_rejected(self):
        self.run_case(reused_pid=True)

    def test_cim_failure_stops_deployment(self):
        self.run_case(cim_error=True)
