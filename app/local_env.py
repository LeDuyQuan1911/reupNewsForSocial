"""Load repository-local REUP settings without an extra runtime dependency."""

import os
from pathlib import Path
import re


def load_local_env(root: Path) -> bool:
    """Load .env into this process; explicit file values override inherited settings."""
    path = root / ".env"
    if not path.is_file():
        return False
    for number, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Invalid .env line {number}: expected KEY=VALUE")
        name, value = line.split("=", 1)
        name = name.strip()
        if not re.fullmatch(r"REUP_[A-Z0-9_]+", name):
            raise ValueError(f"Invalid .env variable name on line {number}")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ[name] = value
    return True
