"""Offline gates for the six-module support-only production contract."""
import datetime as dt
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from makine.bridge import SPECS,build,pinned,persist,modules
from makine.tasks import make_board,notify

NOW=dt.datetime(2026,10,18,8,30,tzinfo=dt.timezone.utc)
SHA="a"*40
def j(x):return json.dumps(x,ensure_ascii=False).encode()

def sample(*,alti_old=False,coin_old=False,provider_error=True):
    coin_time="2026-10-18T04:00:00Z" if coin_old else "2026-10-18T08:25:00Z"
    radar={"scan_id":"coin-id-1","no_real_orders":True,"counts":{"watch":2},
        "watch":[{"symbol":"BTCUSDT"},{"symbol":"SOLUSDT"}]}
    health={"status":"DEGRADED_SCHEDULE_GAP","last_scan_id":"coin-id-1",
        "updated_at":coin_time,"schedule_proven":True}
    manifest={"scan_id":"coin-id-1","finished_at_utc":coin_time,
       "publication_valid":True,"no_real_orders":True,
       "sources":{"v4-radar":{"sha256":hashlib.sha256(j(radar)).hexdigest()},
                  "health":{"sha256":hashlib.sha256(j(health)).hexdigest()}}}
    strategies=[{"id":code,"status":"WATCH_ONLY" if code=="B1" else "NOT_CONNECTED",
                 "data_label":"READ_ONLY_LIVE" if code=="B1" else "NOT_CONNECTED",
                 "reason":"No verified required source"} for code,*_ in SPECS]
    alti={"generated_at_utc":"2026-10-18T04:00:00Z" if alti_old else "2026-10-18T08:24:00Z",
          "scan_id":"alti-id","scan_status":"PARTIAL_LIVE","live_orders_enabled":False,
          "synthetic_data_in_report":False,"strategies":strategies,
          "errors":[{"status":"ACCESS_BLOCKED"}] if provider_error else [],
          "funding_records":[{"venue":"OKX","symbol":"BTCUSDT","rate_unit":"SIGNED_FRACTION_PER_EVENT",
            "data_label":"READ_ONLY_LIVE","last_realized_rate_fraction":0.0001,
            "last_realized_time_utc":"2026-10-18T08:00:00Z","interval_hours":8}]}
    rows={
       ("onurqlp/coin-live-pro","web/data/v4-manifest.json"):j(manifest),
       ("onurqlp/coin-live-pro","web/data/v4-radar.json"):j(radar),
       ("onurqlp/coin-live-pro","web/data/health.json"):j(health),
       ("onurqlp/alti-quant-lab","site/report.json"):j(alti),
    }
    def fake(url):
        for repo in ["onurqlp/coin-live-pro","onurqlp/alti-quant-lab"]:
            if url=="https://api.github.com/repos/"+repo+"/git/ref/heads/main":
                return j({"object":{"sha":SHA}})
            prefix="https://raw.githubusercontent.com/"+repo+"/"+SHA+"/"
            if url.startswith(prefix):
                return rows[(repo,url[len(prefix):])]
        raise AssertionError("Unexpected URL: "+url)
    return fake

class BridgeTests(unittest.TestCase):
    def test_six_modules_only_one_with_available_market_context(self):
        r=build(NOW,sample())
        self.assertEqual(r["schema"],"makine-coinlive-support-v2")
        self.assertEqual(r["module_count"],6)
        self.assertEqual([m["id"] for m in r["modules"]],[x[0] for x in SPECS])
        self.assertEqual(r["modules_observing"],1)
        self.assertEqual([x["symbol"] for x in r["coinlive_feed"]["funding_event_context"]],["BTCUSDT"])
        self.assertIn("BTCUSDT",r["coinlive_feed"]["matching_watch_symbols"])
        self.assertEqual(r["coinlive_feed"]["trade_candidates"],[])
        self.assertFalse(r["coinlive_feed"]["can_change_signal_policy"])
        self.assertFalse(r["safety"]["allow_orders"])
        self.assertEqual(r["business_models"],0)
        self.assertEqual(r["sources"]["coinlive"]["state"],"PARTIAL")
    def test_stale_coin_prevents_context_export(self):
        r=build(NOW,sample(coin_old=True))
        self.assertEqual(r["sources"]["coinlive"]["state"],"STALE")
        self.assertEqual(r["coinlive_feed"]["status"],"NO_VERIFIED_HANDOFF")
        self.assertEqual(r["coinlive_feed"]["funding_event_context"],[])
    def test_stale_alti_never_exports_old_funding(self):
        r=build(NOW,sample(alti_old=True))
        self.assertEqual(r["sources"]["alti"]["state"],"STALE")
        self.assertEqual(r["modules_observing"],0)
        self.assertEqual(r["coinlive_feed"]["funding_event_context"],[])
    def test_rejects_other_repo_and_invalid_paths(self):
        with self.assertRaises(ValueError):
            pinned("unknown/repo",("site/report.json",),sample())
        with self.assertRaises(ValueError):
            pinned("onurqlp/alti-quant-lab",("../secret.json",),sample())
    def test_provider_block_is_visible_and_not_execution_auth(self):
        r=build(NOW,sample(provider_error=True))
        self.assertEqual(r["sources"]["alti"]["provider_error_count"],1)
        self.assertTrue(all(m["trade_signal"] is False for m in r["modules"]))
    def test_fails_closed_per_source(self):
        r=build(NOW,lambda url: (_ for _ in ()).throw(OSError("simulated down")))
        self.assertEqual(r["modules_observing"],0)
        self.assertEqual(r["coinlive_feed"]["status"],"NO_VERIFIED_HANDOFF")
        self.assertTrue(all(x["state"]=="BLOCKED_SOURCE" for x in r["modules"]))
    def test_atomic_output_and_history(self):
        r=build(NOW,sample())
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);persist(r,p);persist(r,p)
            self.assertEqual(json.loads((p/"site/data/support.json").read_text())["module_count"],6)
            self.assertEqual(len(json.loads((p/"data/support-history.json").read_text())["entries"]),1)
    def test_task_notification_deduplication(self):
        report=build(NOW,sample())
        board=make_board(report)
        self.assertEqual(len(board["open_tasks"]),6)
        calls=[]
        def fake_send(payload):
            calls.append(payload)
            return {"id":100}
        posted=notify(board,"test",sender=fake_send)
        self.assertEqual(posted["notification"]["state"],"POSTED")
        again=notify(make_board(report,posted),"test",sender=fake_send)
        self.assertEqual(again["notification"]["state"],"UNCHANGED")
        self.assertEqual(len(calls),1)
        self.assertFalse(any("COIN.LIVE" in str(x.get("can_place_orders")) for x in report["modules"]))
    def test_task_notification_missing_token_no_false_claim(self):
        r=build(NOW,sample())
        b=notify(make_board(r),"")
        self.assertEqual(b["notification"]["state"],"TOKEN_OR_SCOPE_MISSING")
        self.assertTrue(b["notification_required"])
if __name__=="__main__":unittest.main()
