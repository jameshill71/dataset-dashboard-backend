#!/usr/bin/env python3
"""
File: datasets.py
Author: James C. Hill
Created: 2026-02-02
Description:
    Dataset service functions: scan the /data folder for CSV datasets and
    return metadata (name, row_count, columns).
"""
from __future__ import annotations
import csv
from pathlib import Path
from typing import Any
from datetime import datetime, timezone


def _data_dir() -> Path:
    """
    Return thr absolute path to the project's data directory.
    This is robust even if you run uvicorn from a different working directory.
    """
    # datasets.py -> services -> app -> project root
    project_root = Path(__file__).resolve().parents[2]
    return project_root / "data"


def _inspect_csv(path: Path) -> dict[str, Any]:
    """
    Inspect one CSV file and return metadata.
    Row count excludes the header row.
    """
    row_count = 0
    stat = path.stat()
    size_bytes = stat.st_size
    modified_time = datetime.fromtimestamp(
        stat.st_mtime,
        tz=timezone.utc
    ).isoformat()
    
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        header = next(reader, None)
        if header is None:
            # Empty file: no header, no rows
            return {
                "id": path.stem,
                "filename": path.name,
                "row_count": 0,
                "columns": [],
                "size_bytes": size_bytes,
                "modified_time": modified_time,
            }
        columns = [c.strip() for c in header]

        for _ in reader:
            row_count += 1

    return {
        "id": path.stem,
        "filename": path.name,
        "row_count": row_count,
        "columns": columns,
        "size_bytes": size_bytes,
        "modified_time": modified_time,
    }


def list_datasets() -> list[dict[str, Any]]:
    """
    Scan the /data directory for CSV files and return metadata for each one.
    """
    data_dir = _data_dir()

    if not data_dir.exists():
        # If data/ is missing, return empty list rather than crashing.
        return []

    datasets: list[dict[str, Any]] = []
    for csv_path in sorted(data_dir.glob("*.csv")):
        datasets.append(_inspect_csv(csv_path))

    return datasets


def readiness_check() -> dict[str, Any]:
    """
    Readiness check for the service.

    Returns a structured status payload that indicates whether the app is
    ready to serve dataset metadata.

    Checks:
      - data/ directory exists and is a directory
      - at least one *.csv exists
      - each CSV is readable and has a header row
    """
    data_dir = _data_dir()
    checks: dict[str, Any] = {
        "data_dir_exists": False,
        "data_dir_is_dir": False,
        "csv_count": 0,
        "csv_readable": 0,
        "csv_unreadable": 0,
        "errors": [],
    }

    # 1) data/ exists?
    if not data_dir.exists():
        checks["errors"].append(f"Missing data directory: {data_dir}")
        return {
            "status": "error",
            "ready": False,
            "datasets_found": 0,
            "checks": checks,
        }

    checks["data_dir_exists"] = True

    # 2) data/ is a directory?
    if not data_dir.is_dir():
        checks["errors"].append(f"data path is not a directory: {data_dir}")
        return {
            "status": "error",
            "ready": False,
            "datasets_found": 0,
            "checks": checks,
        }

    checks["data_dir_is_dir"] = True

    # 3) Find CSVs
    csv_files = sorted(data_dir.glob("*.csv"))
    checks["csv_count"] = len(csv_files)

    if not csv_files:
        checks["errors"].append("No CSV files found in data/ (expected at least one).")
        return {
            "status": "degraded",
            "ready": False,
            "datasets_found": checks["csv_count"],
            "checks": checks,
        }

    # 4) Try reading each CSV's header
    for path in csv_files:
        try:
            with path.open("r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header is None:
                    checks["csv_unreadable"] += 1
                    checks["errors"].append(f"{path.name}: empty file (no header).")
                else:
                    checks["csv_readable"] += 1
        except OSError as e:
            checks["csv_unreadable"] += 1
            checks["errors"].append(f"{path.name}: could not open/read ({e}).")

    # Ready only if every CSV is readable
    ready = checks["csv_unreadable"] == 0

    return {
        "status": "ok" if ready else "degraded",
        "ready": ready,
        "datasets_found": checks["csv_count"],
        "checks": checks,
    }
