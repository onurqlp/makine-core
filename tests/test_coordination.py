"""Offline tests for scheduled MAKİNE coordination; no API calls or trading."""
import datetime as dt
import hashlib
import json
import pathlib
import tempfile
import unittest

from makine.coordinator import build_snapshot, persist, read_pinned, REPOS

NOW = dt.datetime(2026, 10, 18, 7, 30, tzinfo=dt.timezone.utc)
SHA = "a" * 40

def j(doc):
    return json.dumps(doc, ensure_ascii=False).encode("utf-8")


def sources(coin_time="2026-10-18T07:29:00Z", alti_time="2026-10-18T07:20:00Z",
            missing_alti=False, blocked=False):
    radar = {"scan_id": "scan1", "counts": {"watch": 8}}
    paper = {"scan_id": "scan1", "open_positions": []}
    man = {
        "scan_id": "scan1", "finished_at_utc": coin_time,
        "publication_valid": True, "no_real_orders": True,
        "sources": {
            "v4-radar": {"sha256": hashlib.sha256(j(radar)).hexdigest()},
            "v4-paper": {"sha256": hashlib.sha256(j(paper)).hexdigest()},
        },
    }
    health = {"updated_at": coin_time, "status": "OK",
              "schedule_proven": True, "observed_real_scheduled_runs": 2}
    a = {"generated_at_utc": alti_time, "scan_id": "alti-01",
         "scan_status": "COMPLETED", "live_orders_enabled": False,
         "synthetic_data_in_report": False, "errors": [],
         "provider_health": ([{"status": "ACCESS_BLOCKED"}] if blocked else []),
         "strategies": [{"id": x, "status": "WATCH_ONLY", "data_label": "READ_ONLY_LIVE"}
                        for x in ("A1", "A2", "A3", "B1", "B2", "T0")]}
    payloads = {
        ("onurqlp/coin-live-pro", "web/data/v4-manifest.json"): j(man),
        ("onurqlp/coin-live-pro", "web/data/health.json"): j(health),
        ("onurqlp/coin-live-pro", "web/data/v4-radar.json"): j(radar),
        ("onurqlp/coin-live-pro", "web/data/v4-paper.json"): j(paper),
    }
    if not missing_alti:
        payloads[("onurqlp/alti-quant-lab", "site/report.json")] = j(a)

    def fetch(url):
        for r in [x["repo"] for x in REPOS.values()]:
            if url == "https://api.github.com/repos/" + r + "/git/ref/heads/main":
                return j({"object": {"sha": SHA}})
            prefix = "https://raw.githubusercontent.com/" + r + "/" + SHA + "/"
            if url.startswith(prefix):
                path = url[len(prefix):]
                key = (r, path)
                if key not in payloads:
                    raise OSError("offline fixture source absent")
                return payloads[key]
        raise AssertionError("Unapproved access: " + url)

    return fetch


class CoordinationTests(unittest.TestCase):
    def test_fresh_sources_and_six_mappings(self):
        report = build_snapshot(NOW, sources())
        self.assertEqual(report["system_state"], "FRESH")
        self.assertEqual(report["sources"]["coinlive"]["state"], "FRESH")
        self.assertEqual(report["sources"]["alti"]["state"], "FRESH")
        self.assertEqual(len(report["overlaps"]), 6)
        self.assertEqual(report["sources"]["coinlive"]["commit_sha"], SHA)
        self.assertEqual(report["agent_runtime"]["state"], "NOT_CONNECTED")
        self.assertFalse(report["controls"]["promote_live_signals"])
        self.assertFalse(report["controls"]["place_real_orders"])
        self.assertIsNone(report["controls"]["verified_revenue_try"])

    def test_stale_data_is_not_called_fresh(self):
        report = build_snapshot(NOW, sources(coin_time="2026-10-18T05:20:00Z"))
        self.assertEqual(report["system_state"], "ATTENTION_REQUIRED")
        self.assertEqual(report["sources"]["coinlive"]["state"], "STALE")
        self.assertEqual(report["sources"]["alti"]["state"], "FRESH")

    def test_unavailable_source_fail_closed(self):
        report = build_snapshot(NOW, sources(missing_alti=True))
        self.assertEqual(report["sources"]["alti"]["state"], "UNAVAILABLE")
        self.assertEqual(report["system_state"], "ATTENTION_REQUIRED")
        self.assertTrue(all(x["handoff_status"] == "RESEARCH_ONLY"
                            for x in report["overlaps"]))

    def test_partial_data_stays_partial(self):
        report = build_snapshot(NOW, sources(blocked=True))
        self.assertEqual(report["sources"]["alti"]["state"], "PARTIAL")
        self.assertIn("PARTIAL_PROVIDER_ACCESS", report["sources"]["alti"]["warnings"])

    def test_prohibits_unapproved_repo_or_file(self):
        with self.assertRaises(ValueError):
            read_pinned("other/project", ("site/report.json",), sources())
        with self.assertRaises(ValueError):
            read_pinned("onurqlp/alti-quant-lab", ("../secrets.json",), sources())

    def test_history_deduplicates_hour_and_keeps_only_its_own_files(self):
        report = build_snapshot(NOW, sources())
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            out = root / "site" / "data" / "coordination.json"
            hist = root / "data" / "coordination-history.json"
            persist(report, out, hist)
            persist(report, out, hist)
            self.assertEqual(json.loads(hist.read_text())["entries"][0]["hour_utc"],
                             "2026-10-18T07")
            self.assertEqual(len(json.loads(hist.read_text())["entries"]), 1)
            self.assertEqual(json.loads(out.read_text())["schema"], "makine-coordination-v1")


if __name__ == "__main__":
    unittest.main()
