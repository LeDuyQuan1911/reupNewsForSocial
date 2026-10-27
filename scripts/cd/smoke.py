"""Start the application against disposable data, never the production DB."""

from pathlib import Path
from tempfile import TemporaryDirectory
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from app.web import create_app


with TemporaryDirectory() as temporary:
    app = create_app(Path(temporary) / "smoke.sqlite3")
    response = app.test_client().get("/")
    if response.status_code != 200:
        raise SystemExit(f"Dashboard smoke check failed: HTTP {response.status_code}")
print("Dashboard smoke check passed")
