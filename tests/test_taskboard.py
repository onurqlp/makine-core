"""Offline contract tests: issue dedupe, no cross-repo mutation, and no trades."""
import copy
import datetime as dt
import unittest
from makine.taskboard import build_board, post_update, _comment, POST_URL

T = dt.datetime(2026, 10, 18, 8, 0, tzinfo=dt.timezone.utc)


def snap(alti="STALE", coin="FRESH", warnings=None):
    return {
        "generated_at_utc": "2026-10-18T08:00:00Z",
        "sources": {
            "coinlive": {"repo": "onurqlp/coin-live-pro", "state": coin,
                         "observed_at_utc": "2026-10-18T07:59:00Z",
                         "scan_id": "a", "warnings": []},
            "alti": {"repo": "onurqlp/alti-quant-lab", "state": alti,
                     "observed_at_utc": "2026-10-18T03:21:03Z",
                     "scan_id": "b",
                     "warnings": warnings if warnings is not None else ["PARTIAL_PROVIDER_ACCESS"]},
        },
    }


class TaskBoardTests(unittest.TestCase):
    def test_open_alerts_are_scoped_and_reproducible(self):
        b = build_board(snap(), now=T)
        self.assertEqual(b["status"], "ATTENTION_REQUIRED")
        self.assertEqual([x["id"] for x in b["active"]],
                         ["ALTI_PROVIDER_ACCESS", "ALTI_SOURCE_FRESHNESS"])
        self.assertTrue(all(x["approval_required"] and not x["autonomous_code_execution"]
                            for x in b["active"]))
        self.assertFalse(b["automation"]["cross_repository_writes"])

    def test_one_comment_only_per_status_signature(self):
        calls = []
        def sender(doc):
            calls.append(doc)
            return {"id": 123}
        a = post_update(build_board(snap(), now=T), "dummy", sender=sender)
        self.assertEqual(a["issue_delivery"]["state"], "POSTED")
        self.assertIn("MAKINE-READONLY-COORDINATION", calls[0]["body"])
        later = T + dt.timedelta(hours=1)
        b = build_board(snap(), a, now=later)
        post_update(b, "dummy", sender=sender)
        self.assertEqual(len(calls), 1)
        self.assertEqual(b["issue_delivery"]["state"], "UNCHANGED")
        self.assertEqual(b["active"][0]["first_seen_utc"], a["active"][0]["first_seen_utc"])

    def test_resolved_only_after_new_verified_source(self):
        before = post_update(build_board(snap(), now=T), "dummy",
                             sender=lambda p: {"id": 1})
        after = build_board(snap(alti="FRESH", warnings=[]), before,
                            now=T + dt.timedelta(hours=1))
        self.assertEqual(after["status"], "CLEAR")
        self.assertEqual(len(after["transition"]["resolved"]), 2)
        self.assertTrue(after["notification_required"])

    def test_fails_closed_and_retries_when_token_absent(self):
        a = build_board(snap(), now=T)
        b = post_update(a, "")
        self.assertEqual(b["issue_delivery"]["state"], "TOKEN_UNAVAILABLE")
        self.assertIsNone(b["last_notified_signature"])
        next_a = build_board(snap(), b, now=T + dt.timedelta(hours=1))
        self.assertTrue(next_a["notification_required"])

    def test_sender_failure_does_not_silently_mark_delivered(self):
        def fail(p):
            raise OSError("simulated API error")
        b = post_update(build_board(snap(), now=T), "dummy", sender=fail)
        self.assertEqual(b["issue_delivery"]["state"], "FAILED_RETRY_NEXT_RUN")
        self.assertIsNone(b["last_notified_signature"])

    def test_cross_repository_api_absent(self):
        self.assertEqual(POST_URL,
                         "https://api.github.com/repos/onurqlp/makine-core/issues/1/comments")
        b = build_board(snap(coin="UNAVAILABLE"), now=T)
        self.assertIn("COIN_SOURCE_FRESHNESS", [x["id"] for x in b["active"]])
        self.assertNotIn("github_token", repr(b).lower())

if __name__ == "__main__":
    unittest.main()
