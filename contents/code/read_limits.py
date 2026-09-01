#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Codex Limit contributors
# SPDX-License-Identifier: MIT

"""Read the newest Codex rate-limit snapshot without exposing conversation data."""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import sys
from typing import Any, Iterator


MAX_FILES = 40
CHUNK_SIZE = 64 * 1024
LIMIT_FIELDS = ("used_percent", "window_minutes", "resets_at")
CREDIT_FIELDS = ("has_credits", "unlimited", "balance")


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def reverse_lines(path: Path) -> Iterator[bytes]:
    """Yield non-empty lines from a file, newest first, in bounded memory."""
    with path.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        position = handle.tell()
        remainder = b""

        while position > 0:
            size = min(CHUNK_SIZE, position)
            position -= size
            handle.seek(position)
            block = handle.read(size) + remainder
            parts = block.split(b"\n")
            remainder = parts.pop(0)
            for line in reversed(parts):
                if line.strip():
                    yield line

        if remainder.strip():
            yield remainder


def timestamp_to_epoch(value: Any, fallback: float) -> float:
    if not isinstance(value, str):
        return fallback
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return fallback


def selected_fields(value: Any, allowed: tuple[str, ...]) -> dict[str, Any] | None:
    """Return only fields consumed by the widget UI."""
    if not isinstance(value, dict):
        return None
    return {key: value[key] for key in allowed if key in value}


def snapshot_from_event(event: Any, fallback_time: float) -> dict[str, Any] | None:
    if not isinstance(event, dict):
        return None
    if event.get("type") != "event_msg":
        return None

    payload = event.get("payload")
    if not isinstance(payload, dict) or payload.get("type") != "token_count":
        return None

    limits = payload.get("rate_limits")
    if not isinstance(limits, dict):
        info = payload.get("info")
        limits = info.get("rate_limits") if isinstance(info, dict) else None
    if not isinstance(limits, dict):
        return None

    primary = selected_fields(limits.get("primary"), LIMIT_FIELDS)
    secondary = selected_fields(limits.get("secondary"), LIMIT_FIELDS)
    if primary is None and secondary is None:
        return None

    plan_type = limits.get("plan_type")
    if not isinstance(plan_type, str):
        plan_type = None

    return {
        "ok": True,
        "updated_at": timestamp_to_epoch(event.get("timestamp"), fallback_time),
        "plan_type": plan_type,
        "primary": primary,
        "secondary": secondary,
        "credits": selected_fields(limits.get("credits"), CREDIT_FIELDS),
    }


def newest_snapshot(session_root: Path) -> dict[str, Any] | None:
    candidates: list[tuple[float, Path]] = []
    try:
        for path in session_root.rglob("*.jsonl"):
            try:
                candidates.append((path.stat().st_mtime, path))
            except OSError:
                continue
    except OSError:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    best: dict[str, Any] | None = None
    best_time = 0.0

    for modified, path in candidates[:MAX_FILES]:
        if best is not None and modified < best_time:
            break
        try:
            for raw_line in reverse_lines(path):
                try:
                    event = json.loads(raw_line)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
                snapshot = snapshot_from_event(event, modified)
                if snapshot is not None:
                    event_time = float(snapshot["updated_at"])
                    if event_time > best_time:
                        best = snapshot
                        best_time = event_time
                    break
        except OSError:
            continue

    return best


def main() -> int:
    codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
    session_root = codex_home / "sessions"

    if not session_root.is_dir():
        emit({
            "ok": False,
            "error": f"Codex session directory was not found: {session_root}",
        })
        return 1

    snapshot = newest_snapshot(session_root)
    if snapshot is None:
        emit({
            "ok": False,
            "error": "No rate-limit snapshot found. Run a Codex task, then refresh.",
        })
        return 2

    emit(snapshot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
