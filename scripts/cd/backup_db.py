"""Consistent SQLite copy for a quiesced deployment or rollback."""

import argparse
import sqlite3
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    if not args.source.is_file():
        parser.error("source database does not exist")
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(args.source) as source, sqlite3.connect(args.destination) as destination:
        source.backup(destination)


if __name__ == "__main__":
    main()
