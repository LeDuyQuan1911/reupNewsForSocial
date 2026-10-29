from pathlib import Path
from threading import Thread
import time
import logging

from app.local_env import load_local_env
from app.web import create_app
from app.queue import process_due_posts
from app.automation import run_cycle


def hermes_owns_automation(path: Path) -> bool:
    return (path.parent / "hermes-automation.enabled").exists()


def run_scheduler(path: Path):
    while True:
        if hermes_owns_automation(path):
            return
        try:
            process_due_posts(path)
        except Exception:
            logging.exception("Scheduled post processing failed")
        time.sleep(30)


def run_automation(path: Path):
    while True:
        if hermes_owns_automation(path):
            return
        try:
            run_cycle(path)
        except Exception:
            logging.exception("Automatic discovery and preparation failed")
        time.sleep(30)


if __name__ == "__main__":
    load_local_env(Path(__file__).resolve().parent)
    app = create_app()
    if not hermes_owns_automation(app.config["DATABASE_PATH"]):
        Thread(target=run_scheduler, args=(app.config["DATABASE_PATH"],), daemon=True).start()
        Thread(target=run_automation, args=(app.config["DATABASE_PATH"],), daemon=True).start()
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
