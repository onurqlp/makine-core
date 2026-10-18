"""MAKİNE · production-safe six-module COIN.LIVE support bridge.

Six independent data gates; absence of evidence never produces a signal.
Only public immutable GitHub JSON; never executes imported code or orders.
"""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
MAX_BYTES=2_000_000
SHA_PATTERN=re.compile(r"[0-9a-f]{40}")
SOURCES={"alti":"onurqlp/alti-quant-lab","coinlive":"onurqlp/coin-live-pro"}
MODULES=(
    ("A1","Hisse pairs","Hisse çifti göreli değer filtresi"),
    ("A2","ETF–ETF","ETF farkı ve endeks bağlamı filtresi"),
    ("A3","İstatistiksel sepet","Cointegration/sepet sapması filtresi"),
    ("B1","Perpetual funding","Funding gözlem ve COIN.LIVE eşleme filtresi"),
    ("B2","Stablecoin sapması","USDC/USDT çift-borsa sapma filtresi"),
    ("T0","Tahvil–repo","Tahvil/repo finansman filtresi"),
)

def now_utc():return dt.datetime.now(dt.timezone.utc)
def iso(t):return t.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")
def parse_time(value):
    if not isinstance(value,str):return None
    try:
        value=dt.datetime.fromisoformat(value.replace("Z","+00:00"))
        return value.astimezone(dt.timezone.utc) if value.tzinfo else None
    except (ValueError,OverflowError):return None
def age(value,now):
    v=parse_time(value)
    return round((now-v).total_seconds()/60,2) if v else None
def is_recent(value,now,limit):
    a=age(value,now)
    return a is not None and -5<=a<=limit

def fetch(url):
    if not (url.startswith("https://api.github.com/repos/onurqlp/") or
            url.startswith("https://raw.githubusercontent.com/onurqlp/")):
        raise ValueError("UNAPPROVED_URL")
    headers={"User-Agent":"MakineSixSupport/2.0","Accept":"application/json"}
    token=os.getenv("GITHUB_TOKEN","")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"]="Bearer "+token
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=18) as response:
        raw=response.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:raise ValueError("MAX_BYTES_EXCEEDED")
    return raw

def pinned(repo,paths,fetcher=fetch):
    if repo not in SOURCES.values():raise ValueError("REPO_DENIED")
    obj=json.loads(fetcher("https://api.github.com/repos/"+repo+"/git/ref/heads/main"))
    sha=(obj.get("object") or {}).get("sha")
    if not isinstance(sha,str) or not SHA_PATTERN.fullmatch(sha):
        raise ValueError("INVALID_IMMUTABLE_SHA")
    docs={};hashes={}
    for path in paths:
        if not re.fullmatch(r"[a-z0-9_./-]+\.json",path) or ".." in path:
            raise ValueError("PATH_DENIED")
        content=fetcher("https://raw.githubusercontent.com/"+repo+"/"+sha+"/"+path)
        if len(content)>MAX_BYTES:raise ValueError("MAX_BYTES_EXCEEDED")
        docs[path]=json.loads(content)
        hashes[path]=hashlib.sha256(content).hexdigest()
    return sha,docs,hashes

def load_coin(now,fetcher=fetch):
    paths=("web/data/v4-manifest.json","web/data/v4-radar.json","web/data/health.json")
    sha,docs,hashes=pinned(SOURCES["coinlive"],paths,fetcher)
    manifest,radar,health=[docs[p] for p in paths]
    reasons=[]
    scan=manifest.get("scan_id")
    if not scan or scan!=radar.get("scan_id"):
        reasons.append("SCAN_MISMATCH")
    if scan!=health.get("last_scan_id"):
        reasons.append("HEALTH_SCAN_LAG")
    for key,path in (("v4-radar",paths[1]),("health",paths[2])):
        expected=(manifest.get("sources",{}).get(key) or {}).get("sha256")
        if not expected or expected!=hashes[path]:reasons.append("HASH_MISMATCH_"+key)
    if (manifest.get("publication_valid") is not True or
        manifest.get("no_real_orders") is not True or radar.get("no_real_orders") is not True):
        reasons.append("SOURCE_SAFETY_UNVERIFIED")
    a=age(manifest.get("finished_at_utc"),now)
    status="FRESH" if a is not None and -5<=a<=45 else "STALE"
    if any(r.startswith(("SCAN_MISMATCH","HASH_MISMATCH","SOURCE_SAFETY_UNVERIFIED")) for r in reasons):status="INVALID"
    elif status=="FRESH" and (health.get("status")!="OK" or reasons):status="PARTIAL"
    if health.get("schedule_proven") is not True:reasons.append("CRON_NOT_PROVEN")
    watches=sorted({x["symbol"] for x in (radar.get("watch") or [])
                    if isinstance(x,dict) and isinstance(x.get("symbol"),str)})[:150]
    return {"repo":SOURCES["coinlive"],"sha":sha,"scan_id":scan,
            "observed_at_utc":manifest.get("finished_at_utc"),"age_minutes":a,
            "state":status,"health":health.get("status"),"warnings":reasons,
            "watched_symbols":watches,"counts":radar.get("counts") or {}}

def load_alti(now,fetcher=fetch):
    sha,docs,hashes=pinned(SOURCES["alti"],("site/report.json",),fetcher)
    report=docs["site/report.json"];names={m[0] for m in MODULES}
    strategies={s.get("id"):s for s in (report.get("strategies") or [])
                if isinstance(s,dict) and s.get("id") in names}
    warnings=[]
    if set(strategies)!=names:warnings.append("MODULE_REGISTRY_MISMATCH")
    if report.get("live_orders_enabled") is not False:warnings.append("LIVE_ORDERS_GUARD_UNVERIFIED")
    if report.get("synthetic_data_in_report") is True:warnings.append("SYNTHETIC_DATA")
    a=age(report.get("generated_at_utc"),now)
    state="FRESH" if a is not None and -5<=a<=120 else "STALE"
    if warnings:state="INVALID"
    elif state=="FRESH" and (report.get("errors") or report.get("scan_status")!="OK"):
        state="PARTIAL"
    funding=[]
    if state in ("FRESH","PARTIAL"):
        for f in report.get("funding_records") or []:
            if not isinstance(f,dict):continue
            rate=f.get("last_realized_rate_fraction");sym=f.get("symbol")
            if not (f.get("venue")=="OKX" and
                    f.get("data_label")=="READ_ONLY_LIVE" and
                    f.get("rate_unit")=="SIGNED_FRACTION_PER_EVENT" and
                    isinstance(sym,str) and re.fullmatch(r"[A-Z0-9]{3,24}",sym) and
                    isinstance(rate,(float,int)) and not isinstance(rate,bool) and
                    -1<=rate<=1 and is_recent(f.get("last_realized_time_utc"),now,24*60)):
                continue
            funding.append({"symbol":sym,"venue":"OKX",
                "last_realized_rate_fraction_per_event":rate,
                "last_realized_time_utc":f["last_realized_time_utc"],
                "interval_hours":f.get("interval_hours"),
                "executable":False})
    # Use only source-validated, non-executable public fields.
    # Source read-only is not evidence of borrow, settlement, fees or edge.
    public={}
    if state in ("FRESH","PARTIAL"):
        b2=report.get("stablecoin")
        if (isinstance(b2,dict) and b2.get("data_label")=="READ_ONLY_LIVE" and
            b2.get("actionable") is False and b2.get("eligible_for_paper_fill") is False and
            isinstance(b2.get("best_quotes"),dict) and len(b2["best_quotes"])>=2 and
            isinstance(b2.get("okx_book_age_seconds"),(int,float)) and
            -60<=b2["okx_book_age_seconds"]<=15):
            public["B2"]={"status":"SCREEN_ONLY","venues":b2.get("venues",[]),
                "best_quotes":b2["best_quotes"],"routes":b2.get("routes",[]),
                "asof_utc":report.get("generated_at_utc"),"actionable":False}
        a3=report.get("a3_basket")
        if (isinstance(a3,dict) and a3.get("data_label")=="READ_ONLY_LIVE" and
            a3.get("trade_ready") is False and
            isinstance(a3.get("aligned_closed_days"),int) and a3["aligned_closed_days"]>=50 and
            is_recent(a3.get("source_last_closed_day_utc"),now,7*24*60)):
            public["A3"]={"status":"INPUTS_ONLY","source":a3.get("market"),
                "symbols":a3.get("symbols",[]),
                "latest_close_usdt":a3.get("observed_last_close_usdt",{}),
                "return_20d_percent":a3.get("observed_return_20d_percent",{}),
                "aligned_closed_days":a3["aligned_closed_days"],
                "asof_utc":a3["source_last_closed_day_utc"],"actionable":False}
        t0=report.get("t0_treasury")
        if (isinstance(t0,dict) and t0.get("source")=="US_TREASURY_OFFICIAL" and
            t0.get("trade_ready") is False and
            isinstance(t0.get("date_utc"),str) and
            is_recent(t0.get("date_utc")+"T00:00:00Z",now,10*24*60) and
            isinstance(t0.get("yields_percent"),dict) and
            isinstance(t0["yields_percent"].get("10Y"),(int,float))):
            public["T0"]={"status":"REFERENCE_ONLY",
                "date_utc":t0["date_utc"],"yields_percent":t0["yields_percent"],
                "slope_10y_minus_2y_pct_points":t0.get("slope_10y_minus_2y_pct_points"),
                "actionable":False}
    return {"repo":SOURCES["alti"],"sha":sha,"scan_id":report.get("scan_id"),
        "observed_at_utc":report.get("generated_at_utc"),"age_minutes":a,
        "state":state,"scan_status":report.get("scan_status"),
        "provider_error_count":len(report.get("errors") or []),
        "strategies":strategies,"funding":funding[:20],
        "public_inputs":public,
        "warnings":warnings,"sha256":hashes["site/report.json"]}

def unavailable(repo,e):
    return {"repo":repo,"sha":None,"scan_id":None,"observed_at_utc":None,
            "age_minutes":None,"state":"UNAVAILABLE",
            "warnings":["READ_FAILED_"+type(e).__name__]}

def build(now=None,fetcher=fetch):
    now=now or now_utc()
    try:coin=load_coin(now,fetcher)
    except (OSError,ValueError,KeyError,TypeError,TimeoutError) as e:coin=unavailable(SOURCES["coinlive"],e)
    try:alti=load_alti(now,fetcher)
    except (OSError,ValueError,KeyError,TypeError,TimeoutError) as e:alti=unavailable(SOURCES["alti"],e)
    items=[];seen=set()
    strategy_rows=alti.get("strategies") or {}
    watchers=set(coin.get("watched_symbols") or [])
    for id_,title,mission in MODULES:
        s=strategy_rows.get(id_) or {}
        valid=(alti.get("state") in ("FRESH","PARTIAL") and
               s.get("data_label")=="READ_ONLY_LIVE")
        inputs=(alti.get("public_inputs") or {}).get(id_)
        observations=alti.get("funding",[]) if id_=="B1" and valid else []
        if id_!="B1" and isinstance(inputs,dict) and not inputs.get("actionable"):
            observations=[inputs]
        state="OBSERVING" if observations else "BLOCKED_SOURCE"
        matches=sorted({f["symbol"] for f in observations if "symbol" in f and f["symbol"] in watchers})
        item={"id":id_,"name":title,"purpose":mission,"state":state,
              "strategy_state":s.get("status","UNAVAILABLE"),
              "data_label":s.get("data_label","NOT_CONNECTED"),
              "blocker":None if state=="OBSERVING" else
                        str(s.get("reason") or "Gerçek ve uygun kaynak henüz doğrulanmadı")[:200],
              "observations":observations,"coinlive_watch_matches":matches,
              "data_scope":("TREASURY_YIELD_REFERENCE_ONLY" if id_=="T0" and observations else
                            "DAILY_SPOT_INPUTS_ONLY" if id_=="A3" and observations else
                            "CROSS_VENUE_BOOK_SCREEN_ONLY" if id_=="B2" and observations else
                            "REALIZED_FUNDING_ONLY" if id_=="B1" and observations else
                            "NOT_CONNECTED"),
              "signal":False,"executable":False,"source_repo_write":False}
        items.append(item);seen.add(id_)
    assert seen=={x[0] for x in MODULES}
    observing=sum(x["state"]=="OBSERVING" for x in items)
    nowstr=iso(now)
    context_ok=coin.get("state") in ("FRESH","PARTIAL")
    alti_ok=alti.get("state") in ("FRESH","PARTIAL")
    feed={"schema":"makine-coinlive-support-feed-v2",
        "generated_at_utc":nowstr,"source":"onurqlp/makine-core",
        "coinlive_sha":coin.get("sha"),"coinlive_scan_id":coin.get("scan_id"),
        "alti_sha":alti.get("sha"),"alti_scan_id":alti.get("scan_id"),
        "status":"LIMITED_READ_ONLY_CONTEXT" if context_ok and alti_ok and observing else "NO_VERIFIED_CONTEXT",
        "funding_observations":items[3]["observations"] if context_ok and alti_ok else [],
        "watched_funding_matches":items[3]["coinlive_watch_matches"] if context_ok and alti_ok else [],
        "trade_candidates":[],"change_signals":False,"orders":False,
        "change_paper_ledger":False,"requires_explicit_coinlive_integration":True}
    return {"schema":"makine-six-support-v2","generated_at_utc":nowstr,
        "mission":"COINLIVE_INDEPENDENT_SUPPORT","retired_idea_count":57,
        "ideas_in_active_service":0,"module_count":6,"observing_count":observing,
        "state":"PARTIAL" if any(x["state"]!="OBSERVING" for x in items) else "READY",
        "sources":{"alti":{k:v for k,v in alti.items() if k not in ("strategies","funding")},
                   "coinlive":{k:v for k,v in coin.items() if k!="watched_symbols"}},
        "modules":items,"feed":feed,"safety":{"no_orders":True,"no_paper_fills":True,
        "no_source_repo_writes":True,"no_external_strategy_updates":True,
        "no_virtual_portfolio_merger":True,"no_automated_signals":True},
        "runtime":{"event":os.getenv("GITHUB_EVENT_NAME","LOCAL"),
                   "mode":"SCHEDULED_READ_ONLY","ai_agent":False}}

def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+".tmp")
    temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    os.replace(temp,path)

def v5_compatibility(result):
    """Adapt the SIX modules to the fixed legacy URI hard-coded in V5 preview.

    This is an API compatibility facade, NOT restoration of the retired
    57 model catalog or research workflow.
    """
    coin=result["sources"]["coinlive"]
    clean=coin.get("state") in ("FRESH","PARTIAL")
    fresh=coin.get("age_minutes")
    generated=result["generated_at_utc"]
    return {
        "schema":"makine-coinlive-research-handoff-v1",
        "generator":"MAKINE_CORE",
        "generated_at_utc":generated,
        "source_commit_sha":coin.get("sha"),
        "source_scan_id":coin.get("scan_id"),
        "source_integrity":"VERIFIED" if clean else "UNVERIFIED",
        "source_fresh_at_import":bool(clean and isinstance(fresh,(int,float)) and -5<=fresh<=45),
        "can_promote_to_live_signal":False,
        "can_modify_live_policy":False,
        "can_execute_orders":False,
        "can_modify_coins_live_ledger":False,
        "new_trade_candidates":[],
        "market_context":{
            "status": "SIX_MODULE_LIMITED_CONTEXT" if result["feed"]["status"]=="LIMITED_READ_ONLY_CONTEXT" else "NO_VERIFIED_CONTEXT",
            "radar_counts":coin.get("counts",{}),
            "health":coin.get("health"),
            "import_timestamp":generated,
            "alti_source_state":result["sources"]["alti"]["state"],
            "funding_watch_matches":result["feed"]["watched_funding_matches"],
            "modules_observing":result["observing_count"],
            "module_ids":[x["id"] for x in result["modules"]],
        },
        "recommendations":[{
            "id":"SUPPORT-"+m["id"],"module_id":m["id"],
            "title":m["name"],
            "state":m["state"],
            "recommendation":"OBSERVATION_ONLY" if m["state"]=="OBSERVING" else "SOURCE_NOT_READY",
            "not_executable":True,
            "alti_overlap":m["id"],
        } for m in result["modules"]],
        "usage":"V5 compatibility endpoint for six independent support modules. No retired revenue ideas, trading signals, model promotion, or orders."
    }

def persist(result,root=ROOT):
    write(root/"site/data/support.json",result)
    write(root/"site/data/coinlive-support.json",result["feed"])
    write(root/"site/data/coinlive-handoff.json",v5_compatibility(result))
    path=root/"data/support-history.json"
    try:previous=json.loads(path.read_text("utf-8")).get("entries",[])
    except (ValueError,OSError):previous=[]
    item={"generated_at_utc":result["generated_at_utc"],
          "event":result["runtime"]["event"],"state":result["state"],
          "alti":result["sources"]["alti"]["state"],
          "coinlive":result["sources"]["coinlive"]["state"],
          "observing_count":result["observing_count"]}
    entries=[x for x in previous if x.get("generated_at_utc","")[:16]!=item["generated_at_utc"][:16]]
    entries.append(item);write(path,{"schema":"makine-six-history-v2","entries":entries[-672:]})

def main():
    result=build();persist(result)
    print(json.dumps({"modules":6,"observing":result["observing_count"],
                      "alti":result["sources"]["alti"]["state"],
                      "coinlive":result["sources"]["coinlive"]["state"],
                      "orders":False},ensure_ascii=False))
if __name__=="__main__":main()
