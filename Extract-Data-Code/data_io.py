"""Load both repository data versions into a common Mongo-style structure."""

import csv
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "Data"
OUTPUT_DIR = PROJECT_ROOT / "Analysis-Log-Results"
VERSIONS = ("Version-1", "Version-2")


def _convert(value):
    if value is None or value == "":
        return None
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    try:
        return float(value) if any(c in value for c in ".eE") else int(value)
    except ValueError:
        return value


def _assign(root, column, value):
    parts = [(name, int(index) if index else None)
             for name, index in re.findall(r"([^.\[\]]+)(?:\[(\d+)\])?", column)]
    current = root
    for position, (name, index) in enumerate(parts):
        last = position == len(parts) - 1
        if index is None:
            if last:
                current[name] = value
            else:
                current = current.setdefault(name, {})
        else:
            items = current.setdefault(name, [])
            while len(items) <= index:
                items.append({})
            if last:
                items[index] = value
            else:
                current = items[index]


def load_records(path):
    """Read Version-1 JSON or Version-2 flattened CSV."""
    path = Path(path)
    if path.suffix.lower() == ".json":
        with path.open(encoding="utf-8-sig") as stream:
            return json.load(stream)
    records = []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            record = {}
            for column, raw in row.items():
                value = _convert(raw)
                if value is not None:
                    _assign(record, column, value)
            if "_id" in record and not isinstance(record["_id"], dict):
                record["_id"] = {"$oid": str(record["_id"])}
            if "eventTime" in record and not isinstance(record["eventTime"], dict):
                record["eventTime"] = {"$date": record["eventTime"]}
            records.append(record)
    return records


def source_file(version, stem):
    folder = DATA_ROOT / version
    matches = [candidate for suffix in (".json", ".csv")
               if (candidate := folder / f"{stem}{suffix}").exists()]
    if len(matches) != 1:
        raise FileNotFoundError(f"Expected exactly one {stem} source in {folder}")
    return matches[0]


def combine_frames(versioned_frames):
    import pandas as pd
    frames = []
    for version, frame in versioned_frames:
        frame = frame.copy()
        frame.insert(0, "dataVersion", version)
        frames.append(frame)
    return pd.concat(frames, ignore_index=True, sort=False)
