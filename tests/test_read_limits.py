# SPDX-FileCopyrightText: 2026 Codex Limit contributors
# SPDX-License-Identifier: MIT

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


MODULE_PATH = Path(__file__).parents[1] / "contents" / "code" / "read_limits.py"
SPEC = importlib.util.spec_from_file_location("read_limits", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
read_limits = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(read_limits)


def event(timestamp: str, used: float) -> dict:
    return {
        "timestamp": timestamp,
        "type": "event_msg",
        "payload": {
            "type": "token_count",
            "rate_limits": {
                "limit_id": "codex",
                "plan_type": "plus",
                "primary": {
                    "used_percent": used,
                    "window_minutes": 300,
                    "resets_at": 2_000_000_000,
                    "unexpected_private_field": "must not leave the helper",
                },
                "secondary": {
                    "used_percent": used + 10,
                    "window_minutes": 10080,
                    "resets_at": 2_000_100_000,
                },
            },
        },
    }


class ReadLimitsTest(unittest.TestCase):
    def test_reverse_lines_handles_file_without_final_newline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            path.write_bytes(b"first\nsecond\nthird")
            self.assertEqual(list(read_limits.reverse_lines(path)), [b"third", b"second", b"first"])

    def test_newest_snapshot_uses_latest_limit_event(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            older = root / "2026" / "08" / "older.jsonl"
            newer = root / "2026" / "09" / "newer.jsonl"
            older.parent.mkdir(parents=True)
            newer.parent.mkdir(parents=True)

            older.write_text(json.dumps(event("2026-08-31T12:00:00Z", 20)) + "\n", encoding="utf-8")
            newer.write_text(
                "not json\n"
                + json.dumps(event("2026-09-01T12:00:00Z", 40))
                + "\n"
                + json.dumps({"type": "event_msg", "payload": {"type": "other"}})
                + "\n",
                encoding="utf-8",
            )
            os.utime(older, (1_788_177_600, 1_788_177_600))
            os.utime(newer, (1_788_264_000, 1_788_264_000))

            snapshot = read_limits.newest_snapshot(root)
            self.assertIsNotNone(snapshot)
            assert snapshot is not None
            self.assertEqual(snapshot["primary"]["used_percent"], 40)
            self.assertEqual(snapshot["secondary"]["window_minutes"], 10080)
            self.assertEqual(snapshot["plan_type"], "plus")
            self.assertNotIn("limit_id", snapshot)
            self.assertNotIn("unexpected_private_field", snapshot["primary"])

    def test_ignores_non_object_json_events(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "events.jsonl"
            path.write_text(
                json.dumps(event("2026-09-01T12:00:00Z", 30))
                + "\n"
                + "[]\n"
                + '"private text"\n',
                encoding="utf-8",
            )

            snapshot = read_limits.newest_snapshot(root)
            self.assertIsNotNone(snapshot)
            assert snapshot is not None
            self.assertEqual(snapshot["primary"]["used_percent"], 30)

    def test_account_result_includes_allowlisted_gpt_reserve_limit(self) -> None:
        result = {
            "rateLimits": {
                "planType": "plus",
                "primary": {
                    "usedPercent": 7,
                    "windowDurationMins": 300,
                    "resetsAt": 2_000_000_000,
                },
                "secondary": {
                    "usedPercent": 29,
                    "windowDurationMins": 10080,
                    "resetsAt": 2_000_100_000,
                },
            },
            "rateLimitsByLimitId": {
                "codex": {
                    "planType": "plus",
                    "primary": {
                        "usedPercent": 7,
                        "windowDurationMins": 300,
                        "resetsAt": 2_000_000_000,
                    },
                    "secondary": {
                        "usedPercent": 29,
                        "windowDurationMins": 10080,
                        "resetsAt": 2_000_100_000,
                    },
                },
                "base_model_inference": {
                    "limitId": "base_model_inference",
                    "limitName": "gpt-reserve",
                    "primary": {
                        "usedPercent": 0,
                        "windowDurationMins": 10080,
                        "resetsAt": 2_000_200_000,
                        "unexpected_private_field": "must not leave the helper",
                    },
                },
            },
        }

        snapshot = read_limits.snapshot_from_account_result(result, fetched_at=123.0)

        self.assertIsNotNone(snapshot)
        assert snapshot is not None
        self.assertEqual(snapshot["updated_at"], 123.0)
        self.assertEqual(snapshot["plan_type"], "plus")
        self.assertEqual(snapshot["primary"]["used_percent"], 7)
        self.assertEqual(snapshot["secondary"]["used_percent"], 29)
        self.assertEqual(snapshot["reserve"]["used_percent"], 0)
        self.assertEqual(snapshot["reserve"]["window_minutes"], 10080)
        self.assertNotIn("limitName", snapshot["reserve"])
        self.assertNotIn("unexpected_private_field", snapshot["reserve"])

    def test_app_server_reader_accepts_jsonl_response(self) -> None:
        response = {
            "id": 1,
            "result": {
                "rateLimits": {
                    "primary": {"usedPercent": 7, "windowDurationMins": 300},
                    "secondary": {"usedPercent": 29, "windowDurationMins": 10080},
                },
                "rateLimitsByLimitId": {
                    "base_model_inference": {
                        "limitName": "gpt-reserve",
                        "primary": {"usedPercent": 0, "windowDurationMins": 10080},
                    },
                },
            },
        }

        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "fake-codex"
            executable.write_text(
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                "response = " + repr(response) + "\n"
                "for line in sys.stdin:\n"
                "    request = json.loads(line)\n"
                "    if request.get('id') == 1:\n"
                "        print(json.dumps(response), flush=True)\n"
                "        break\n",
                encoding="utf-8",
            )
            executable.chmod(0o700)

            with mock.patch.object(read_limits, "codex_executable", return_value=str(executable)):
                snapshot = read_limits.app_server_snapshot(Path(directory))

        self.assertIsNotNone(snapshot)
        assert snapshot is not None
        self.assertEqual(snapshot["primary"]["used_percent"], 7)
        self.assertEqual(snapshot["reserve"]["used_percent"], 0)


if __name__ == "__main__":
    unittest.main()
