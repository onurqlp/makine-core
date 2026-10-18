"""Six-module read-only support contract; offline deterministic tests."""
import datetime as dt
import hashlib
import json
import pathlib
import tempfile
import unittest
from makine.bridge import build,pinned,persist,MODULES

NOW=dt.datetime(2026,10,18,9,tzinfo=dt.timezone.utc)
SHA="a"*40
def data(x):return json.dumps(x).encode()
def source_fixture(*,stale=False,no_alti=False,enriched=False):
    t="2026-10-17T06:00:00Z" if stale else "2026-10-18T08:59:00Z"
    radar={"scan_id":"c1","no_real_orders":True,"watch":[{"symbol":"BTCUSDT"}],"counts":{"watch":1}}
    health={"last_scan_id":"c1","status":"OK","schedule_proven":True}
    man={"scan_id":"c1","finished_at_utc":t,"publication_valid":True,"no_real_orders":True,
         "sources":{"v4-radar":{"sha256":hashlib.sha256(data(radar)).hexdigest()},
                    "health":{"sha256":hashlib.sha256(data(health)).hexdigest()}}}
    strategies=[{"id":id,"status":"WATCH_ONLY" if id=="B1" else "NOT_CONNECTED",
                "data_label":"READ_ONLY_LIVE" if id=="B1" else "NOT_CONNECTED"}
                for id,_,_ in MODULES]
    a={"generated_at_utc":t,"scan_id":"a1","scan_status":"PARTIAL_LIVE",
       "live_orders_enabled":False,"synthetic_data_in_report":False,
       "errors":[{"status":"ACCESS_BLOCKED"}],"strategies":strategies,
       "funding_records":[{"venue":"OKX","symbol":"BTCUSDT",
         "last_realized_rate_fraction":0.0001,
         "last_realized_time_utc":"2026-10-18T08:00:00Z",
         "data_label":"READ_ONLY_LIVE","rate_unit":"SIGNED_FRACTION_PER_EVENT",
         "interval_hours":8}]}
    if enriched:
        for s in strategies:
            if s['id'] in ('A3','B2'):s['data_label']='READ_ONLY_LIVE'
            if s['id']=='T0':s['data_label']='REFERENCE_ONLY'
        a['a3_basket']={
           'data_label':'READ_ONLY_LIVE','trade_ready':False,
           'aligned_closed_days':60,'source_last_closed_day_utc':'2026-10-17T00:00:00Z',
           'market':'OKX_SPOT','symbols':['BTCUSDT','ETHUSDT','SOLUSDT'],
           'observed_last_close_usdt':{'BTC':100000.,'ETH':4000.,'SOL':200.},
           'observed_return_20d_percent':{'BTC':2.,'ETH':1.,'SOL':-1.}}
        a['stablecoin']={
           'data_label':'READ_ONLY_LIVE','actionable':False,
           'eligible_for_paper_fill':False,'okx_book_age_seconds':2,
           'best_quotes':{'OKX':{'bid':1.0,'ask':1.0001},
                          'KRAKEN':{'bid':1.0002,'ask':1.0003}},
           'venues':['OKX','KRAKEN'],'routes':[{'gross_spread_bps':1.0,
                'net_spread_bps':None,'net_pnl':None}]}
        a['t0_treasury']={'source':'US_TREASURY_OFFICIAL',
           'date_utc':'2026-10-16','trade_ready':False,
           'yields_percent':{'2Y':3.5,'10Y':4.1},
           'slope_10y_minus_2y_pct_points':0.6}
    blobs={
        ("onurqlp/coin-live-pro","web/data/v4-manifest.json"):data(man),
        ("onurqlp/coin-live-pro","web/data/v4-radar.json"):data(radar),
        ("onurqlp/coin-live-pro","web/data/health.json"):data(health),
    }
    if not no_alti:blobs[("onurqlp/alti-quant-lab","site/report.json")]=data(a)
    def fetch(url):
        for repo in ("onurqlp/alti-quant-lab","onurqlp/coin-live-pro"):
            if url=="https://api.github.com/repos/"+repo+"/git/ref/heads/main":
                return data({"object":{"sha":SHA}})
            prefix="https://raw.githubusercontent.com/"+repo+"/"+SHA+"/"
            if url.startswith(prefix):
                key=(repo,url[len(prefix):])
                if key not in blobs:raise OSError("unavailable")
                return blobs[key]
        raise ValueError("unapproved url")
    return fetch

class SupportTests(unittest.TestCase):
    def test_six_only_and_funding_context(self):
        x=build(NOW,source_fixture())
        self.assertEqual([m["id"] for m in x["modules"]],["A1","A2","A3","B1","B2","T0"])
        self.assertEqual(x["observing_count"],1)
        self.assertEqual(x["modules"][3]["state"],"OBSERVING")
        self.assertEqual(x["feed"]["watched_funding_matches"],["BTCUSDT"])
        self.assertEqual(x["feed"]["trade_candidates"],[])
        self.assertFalse(x["safety"]["no_orders"] is False)
        self.assertFalse(x["feed"]["orders"])
    def test_enriched_inputs_remain_read_only(self):
        x=build(NOW,source_fixture(enriched=True))
        module={m['id']:m for m in x['modules']}
        self.assertEqual(x['observing_count'],4)
        for id in ('B2','A3','T0'):
            self.assertEqual(module[id]['state'],'OBSERVING')
            self.assertEqual(len(module[id]['observations']),1)
            self.assertFalse(module[id]['signal'])
            self.assertFalse(module[id]['executable'])
        self.assertEqual(module['A1']['state'],'BLOCKED_SOURCE')
        self.assertEqual(module['A2']['state'],'BLOCKED_SOURCE')
        self.assertEqual(module['T0']['data_scope'],'TREASURY_YIELD_REFERENCE_ONLY')
        self.assertEqual(module['B2']['observations'][0]['routes'][0]['net_pnl'],None)
        self.assertEqual(x['feed']['trade_candidates'],[])
    def test_no_fabricated_data_if_stale(self):
        x=build(NOW,source_fixture(stale=True))
        self.assertEqual(x["observing_count"],0)
        self.assertEqual(x["feed"]["status"],"NO_VERIFIED_CONTEXT")
        self.assertEqual(x["feed"]["funding_observations"],[])
    def test_unavailable_source_fail_closed(self):
        x=build(NOW,source_fixture(no_alti=True))
        self.assertEqual(x["sources"]["alti"]["state"],"UNAVAILABLE")
        self.assertEqual(x["observing_count"],0)
    def test_repo_and_path_allowlists(self):
        with self.assertRaises(ValueError):pinned("someone/other",("site/report.json",),source_fixture())
        with self.assertRaises(ValueError):pinned("onurqlp/alti-quant-lab",("../secret.json",),source_fixture())
    def test_persist_only_six_and_bounded_history(self):
        x=build(NOW,source_fixture())
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);persist(x,root);persist(x,root)
            report=json.loads((root/"site/data/support.json").read_text())
            hist=json.loads((root/"data/support-history.json").read_text())
            self.assertEqual(report["module_count"],6)
            self.assertEqual(len(hist["entries"]),1)
            self.assertFalse((root/"site/data/report.json").exists())
if __name__=="__main__":unittest.main()
