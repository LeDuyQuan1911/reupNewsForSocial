"""Catch scripts that Windows PowerShell 5.1 cannot decode or parse."""

import os
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(os.name == "nt", "Windows PowerShell is only available on Windows")
class PowerShell5SyntaxTests(unittest.TestCase):
    def test_all_scripts_parse_in_windows_powershell(self):
        command = (
            "$files = Get-ChildItem scripts -Recurse -Filter *.ps1; "
            "$bad = @(); "
            "foreach ($file in $files) { "
            "$tokens = $null; $errors = $null; "
            "[System.Management.Automation.Language.Parser]::ParseFile("
            "$file.FullName, [ref]$tokens, [ref]$errors) | Out-Null; "
            "if ($errors.Count) { $bad += $file.FullName } "
            "}; "
            "if ($bad.Count) { $bad; exit 1 }"
        )
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
            cwd=ROOT, capture_output=True, text=True, timeout=20, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
