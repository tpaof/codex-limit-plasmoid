#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Codex Limit contributors
# SPDX-License-Identifier: MIT

"""Read sanitized Codex rate-limit snapshots for the Plasma widget."""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import select
import shutil
import subprocess
import sys
import time
from typing import Any, Iterator


MAX_FILES = 40
CHUNK_SIZE = 64 * 1024
APP_SERVER_TIMEOUT = 12.0
APP_SERVER_MAX_OUTPUT = 1024 * 1024
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


def numeric(value: Any) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value


def normalize_window(value: Any) -> dict[str, Any] | None:
    """Normalize app-server camelCase or session snake_case window fields."""
    if not isinstance(value, dict):
        return None

    used_percent = numeric(value.get("usedPercent", value.get("used_percent")))
    if used_percent is None:
        return None

    result: dict[str, Any] = {"used_percent": used_percent}
    window_minutes = numeric(value.get("windowDurationMins", value.get("window_minutes")))
    resets_at = numeric(value.get("resetsAt", value.get("resets_at")))
    if window_minutes is not None:
        result["window_minutes"] = window_minutes
    if resets_at is not None:
        result["resets_at"] = resets_at
    return result


def normalize_credits(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    mapping = {
        "has_credits": value.get("hasCredits", value.get("has_credits")),
        "unlimited": value.get("unlimited"),
        "balance": value.get("balance"),
    }
    return {key: mapping[key] for key in CREDIT_FIELDS if mapping[key] is not None}


def weekly_window(snapshot: Any) -> dict[str, Any] | None:
    if not isinstance(snapshot, dict):
        return None
    primary = normalize_window(snapshot.get("primary"))
    secondary = normalize_window(snapshot.get("secondary"))
    for window in (primary, secondary):
        if window and numeric(window.get("window_minutes")) == 10080:
            return window
    return primary or secondary


def snapshot_from_account_result(result: Any, fetched_at: float | None = None) -> dict[str, Any] | None:
    """Convert account/rateLimits/read output to the widget's allowlisted schema."""
    if not isinstance(result, dict):
        return None

    buckets = result.get("rateLimitsByLimitId")
    if not isinstance(buckets, dict):
        buckets = {}

    main_bucket = buckets.get("codex")
    if not isinstance(main_bucket, dict):
        main_bucket = result.get("rateLimits")
    if not isinstance(main_bucket, dict):
        return None

    primary = normalize_window(main_bucket.get("primary"))
    secondary = normalize_window(main_bucket.get("secondary"))
    if primary is None and secondary is None:
        return None

    reserve = None
    for bucket_id, bucket in buckets.items():
        if not isinstance(bucket, dict):
            continue
        limit_name = bucket.get("limitName")
        normalized_name = limit_name.casefold() if isinstance(limit_name, str) else ""
        if normalized_name == "gpt-reserve" or bucket_id == "base_model_inference":
            reserve = weekly_window(bucket)
            break

    plan_type = main_bucket.get("planType")
    if not isinstance(plan_type, str):
        plan_type = ""

    return {
        "ok": True,
        "updated_at": fetched_at if fetched_at is not None else time.time(),
        "plan_type": plan_type,
        "primary": primary,
        "secondary": secondary,
        "reserve": reserve,
        "credits": normalize_credits(main_bucket.get("credits")),
    }


def codex_executable(codex_home: Path) -> str | None:
    override = os.environ.get("CODEX_BINARY")
    path_executable = shutil.which("codex")
    candidates = [
        Path(override).expanduser() if override else None,
        Path(path_executable) if path_executable else None,
        codex_home / "packages" / "standalone" / "current" / "bin" / "codex",
        Path("~/.local/bin/codex").expanduser(),
    ]
    for candidate in candidates:
        if candidate and candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def app_server_snapshot(codex_home: Path) -> dict[str, Any] | None:
    """Fetch the multi-bucket account snapshot through the local Codex binary."""
    executable = codex_executable(codex_home)
    if executable is None:
        return None

    try:
        process = subprocess.Popen(
            [executable, "app-server", "--stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0,
        )
    except OSError:
        return None

    try:
        if process.stdin is None or process.stdout is None:
            return None

        messages = (
            {
                "method": "initialize",
                "id": 0,
                "params": {
                    "clientInfo": {
                        "name": "codex_limit_widget",
                        "title": "Codex Limit Widget",
                        "version": "1.1.0",
                    }
                },
            },
            {"method": "initialized", "params": {}},
            {"method": "account/rateLimits/read", "id": 1},
        )
        for message in messages:
            encoded = json.dumps(message, separators=(",", ":")).encode("utf-8") + b"\n"
            process.stdin.write(encoded)
        process.stdin.flush()

        deadline = time.monotonic() + APP_SERVER_TIMEOUT
        pending = b""
        while time.monotonic() < deadline:
            while b"\n" in pending:
                line, pending = pending.split(b"\n", 1)
                if not line.strip():
                    continue
                try:
                    message = json.loads(line)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
                if not isinstance(message, dict) or message.get("id") != 1:
                    continue
                if "error" in message:
                    return None
                return snapshot_from_account_result(message.get("result"))

            if process.poll() is not None:
                return None
            remaining = max(0.0, deadline - time.monotonic())
            ready, _, _ = select.select([process.stdout], [], [], remaining)
            if not ready:
                return None
            chunk = os.read(process.stdout.fileno(), CHUNK_SIZE)
            if not chunk:
                return None
            pending += chunk
            if len(pending) > APP_SERVER_MAX_OUTPUT:
                return None
        return None
    except (OSError, BrokenPipeError, ValueError):
        return None
    finally:
        if process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=2)
            except (OSError, subprocess.TimeoutExpired):
                try:
                    process.kill()
                    process.wait(timeout=2)
                except (OSError, subprocess.TimeoutExpired):
                    pass
        for stream in (process.stdin, process.stdout):
            if stream is not None:
                try:
                    stream.close()
                except OSError:
                    pass


def snapshot_from_event(event: Any, fallback_time: float) -> dict[str, Any] | None:
    if not isinstance(event, dict) or event.get("type") != "event_msg":
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

    primary = normalize_window(limits.get("primary"))
    secondary = normalize_window(limits.get("secondary"))
    if primary is None and secondary is None:
        return None

    plan_type = limits.get("plan_type")
    if not isinstance(plan_type, str):
        plan_type = ""

    return {
        "ok": True,
        "updated_at": timestamp_to_epoch(event.get("timestamp"), fallback_time),
        "plan_type": plan_type,
        "primary": primary,
        "secondary": secondary,
        "reserve": None,
        "credits": normalize_credits(limits.get("credits")),
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

    snapshot = app_server_snapshot(codex_home)
    if snapshot is None:
        session_root = codex_home / "sessions"
        if session_root.is_dir():
            snapshot = newest_snapshot(session_root)

    if snapshot is None:
        emit({
            "ok": False,
            "error": "No Codex rate-limit snapshot was available. Run a Codex task, then refresh.",
        })
        return 2

    emit(snapshot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
