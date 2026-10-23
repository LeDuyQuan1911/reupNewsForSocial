from app.web import create_app
from app.queue import process_due_posts
from pathlib import Path
from threading import Thread
import time
import logging


def run_scheduler(path: Path):
    while True:
        try:
            process_due_posts(path)
        except Exception:
            logging.exception("Scheduled post processing failed")
        time.sleep(30)


if __name__ == "__main__":
    app = create_app()
    Thread(target=run_scheduler, args=(app.config["DATABASE_PATH"],), daemon=True).start()
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
