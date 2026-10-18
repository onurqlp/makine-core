"""MAKİNE · six-module ALTI → COIN.LIVE support service.

All six module gates execute; they do not fake missing upstream data.
Read-only immutable GitHub inputs. Output never authorizes signals or orders.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
MAX_BYTES=2_000_000
SOURCES={"alti":"onurqlp/alti-quant-lab","coinlive":"onurqlp/coin-live-pro"}
SPECS=(
 ("A1","Hisse pairs","Hisse göreli değer stres filtresi","Lisanslı ve düzeltilmiş hisse çiftleri doğrulanmadı"),
 ("A2","ETF–ETF","ETF risk aktarım filtresi","Endeks/NAV/kur ve ETF fiyatları doğrulanmadı"),
 ("A3","İstatistiksel sepet","Sepet ayrışma kontrolü","Formation/OOS ve cointegration kanıtı yok"),
 ("B1","Perpetual funding","Funding gözlem köprüsü","İkinci doğrulanmış borsa ve işlem erişimi yok"),
 ("B2","Stablecoin sapması","USDT/USDC sapma kontrolü","Çift borsa fiyat kotasyonu doğrulanmadı"),
 ("T0","Tahvil–repo","Finansman koşulları kontrolü","ISIN ve repo veri erişimi doğrulanmadı"),
)
STAMP=lambda d:d.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")
def now_utc():return dt.datetime.now(dt.timezone.utc)
def parsed(v):
    if not isinstance(v,str):return None
    try:
        d=dt.datetime.fromisoformat(v.replace("Z","+00:00"))
        return d.astimezone(dt.timezone.utc) if d.tzinfo else None
    except (TypeError,ValueError,OverflowError):return None
def age_minutes(v,now):
    d=parsed(v)
    return round((now-d).total_seconds()/60,2) if d else None
def freshness(v,now,max_minutes):
    age=age_minutes(v,now)
    if age is None or age < -5:return "INVALID_TIME",age
    return ("STALE" if age>max_minutes else "FRESH"),age

def fetch(url):
    allowed=("https://api.github.com/repos/onurqlp/",
             "https://raw.githubusercontent.com/onurqlp/")
    if not url.startswith(allowed):raise ValueError("SOURCE_NOT_ALLOWED")
    req=urllib.request.Request(url,headers={"User-Agent":"MakineSixSupport/1.0","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=18) as r:raw=r.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:raise ValueError("SOURCE_TOO_LARGE")
    return raw

def pinned(repo,paths,fetcher=fetch):
    if repo not in SOURCES.values():raise ValueError("REPO_NOT_ALLOWED")
    ref=json.loads(fetcher("https://api.github.com/repos/"+repo+"/git/ref/heads/main"))
    sha=(ref.get("object") or {}).get("sha")
    if not isinstance(sha,str) or not re.fullmatch("[a-f0-9]{40}",sha):
        raise ValueError("MISSING_IMMUTABLE_SHA")
    out={};hashes={}
    for path in paths:
        if not re.fullmatch(r"[a-z0-9_./-]+\.json",path) or ".." in path:
            raise ValueError("PATH_NOT_ALLOWED")
        blob=fetcher("https://raw.githubusercontent.com/"+repo+"/"+sha+"/"+path)
        if len(blob)>MAX_BYTES:raise ValueError("SOURCE_TOO_LARGE")
        out[path]=json.loads(blob)
        hashes[path]=hashlib.sha256(blob).hexdigest()
    return sha,out,hashes

def coin_input(now,fetcher=fetch):
    repo=SOURCES["coinlive"]
    paths=("web/data/v4-manifest.json","web/data/v4-radar.json","web/data/health.json")
    sha,docs,h=pinned(repo,paths,fetcher)
    m,r,health=(docs[x] for x in paths)
    reasons=[]
    scan=m.get("scan_id")
    if not isinstance(scan,str) or not scan or r.get("scan_id")!=scan:reasons.append("SCAN_ID_MISMATCH")
    for path,key in ((paths[1],"v4-radar"),(paths[2],"health")):
        expected=(m.get("sources",{}).get(key) or {}).get("sha256")
        if not expected or expected!=h[path]:reasons.append("HASH_MISMATCH_"+key.upper())
    if m.get("publication_valid") is not True or m.get("no_real_orders") is not True or r.get("no_real_orders") is not True:
        reasons.append("UNVERIFIED_MANIFEST_SAFETY")
    fresh,age=freshness(m.get("finished_at_utc"),now,45)
    healthy=health.get("status")=="OK"
    # The health payload is manifest-hash-pinned, but its last_scan_id can
    # refer to a different scheduler slot than the publication manifest.
    # Flag that discrepancy separately; it is not a radar integrity failure.
    health_differs=health.get("last_scan_id")!=scan
    if health_differs:reasons.append("HEALTH_SCAN_REFERENCE_DIFFERS")
    st=fresh
    if any(x.startswith("HASH_MISMATCH") or x in ("SCAN_ID_MISMATCH","UNVERIFIED_MANIFEST_SAFETY") for x in reasons):
        st="INVALID"
    elif fresh=="FRESH" and (not healthy or health_differs):st="PARTIAL"
    if health.get("schedule_proven") is not True:reasons.append("SCHEDULE_NOT_PROVEN")
    return {"repo":repo,"source_sha":sha,"scan_id":scan,"observed_at_utc":m.get("finished_at_utc"),
            "age_minutes":age,"state":st,"health_status":health.get("status"),
            "schedule_proven":health.get("schedule_proven") is True,
            "counts":{k:v for k,v in (r.get("counts") or {}).items() if isinstance(v,int)},
            "watch_symbols":sorted({x.get("symbol") for x in r.get("watch",[])
                                     if isinstance(x,dict) and isinstance(x.get("symbol"),str)})[:150],
            "warnings":reasons,"verified_market_context":st in ("FRESH","PARTIAL")}

def alti_input(now,fetcher=fetch):
    repo=SOURCES["alti"];sha,docs,h=pinned(repo,("site/report.json",),fetcher)
    p=docs["site/report.json"]
    reasons=[]
    strategies={x.get("id"):x for x in p.get("strategies",[]) if isinstance(x,dict) and x.get("id") in [a[0] for a in SPECS]}
    if set(strategies)!={x[0] for x in SPECS}:reasons.append("SIX_MODULES_MISSING")
    if p.get("live_orders_enabled") is not False:reasons.append("ORDER_GUARD_NOT_VERIFIED")
    if p.get("synthetic_data_in_report") is True:reasons.append("SYNTHETIC_INPUT")
    fresh,age=freshness(p.get("generated_at_utc"),now,120)
    status=fresh
    if reasons:status="INVALID"
    elif fresh=="FRESH" and (p.get("errors") or p.get("scan_status")!="OK"):
        status="PARTIAL"
    rec=[]
    if status in ("FRESH","PARTIAL"):
        for f in p.get("funding_records",[]):
            if not isinstance(f,dict):continue
            if (f.get("venue")!="OKX" or f.get("rate_unit")!="SIGNED_FRACTION_PER_EVENT"
                or f.get("data_label")!="READ_ONLY_LIVE"):continue
            sym=f.get("symbol");rate=f.get("last_realized_rate_fraction")
            fstate,fage=freshness(f.get("last_realized_time_utc"),now,24*60)
            if not re.fullmatch(r"[A-Z0-9]{2,24}",str(sym)) or not isinstance(rate,(int,float)) or isinstance(rate,bool) or not -1<=rate<=1 or fstate!="FRESH":continue
            rec.append({"symbol":sym,"venue":"OKX","last_realized_fraction_per_event":rate,
                        "last_realized_time_utc":f["last_realized_time_utc"],
                        "interval_hours":f.get("interval_hours"),
                        "event_age_minutes":fage,"trade_ready":False})
    return {"repo":repo,"source_sha":sha,"scan_id":p.get("scan_id"),
            "observed_at_utc":p.get("generated_at_utc"),"age_minutes":age,"state":status,
            "scan_status":p.get("scan_status"),"strategy_data":strategies,
            "funding":rec[:20],"warnings":reasons,
            "provider_error_count":len(p.get("errors") or []),
            "source_hash":h["site/report.json"]}

def absent(repo,exc):
    return {"repo":repo,"source_sha":None,"scan_id":None,"observed_at_utc":None,
            "age_minutes":None,"state":"UNAVAILABLE","warnings":["FETCH_"+type(exc).__name__]}

def modules(alti,coin,now):
    result=[];strategies=alti.get("strategy_data") or {}
    for code,title,service,why in SPECS:
        s=strategies.get(code) or {}
        inputs_valid=(alti.get("state") in ("FRESH","PARTIAL") and s.get("data_label")=="READ_ONLY_LIVE")
        records=[]
        if code=="B1" and inputs_valid:records=alti.get("funding",[])
        operational="OBSERVING" if code=="B1" and records else "BLOCKED_SOURCE"
        coin_watch=set(coin.get("watch_symbols") or [])
        matches=sorted({f["symbol"] for f in records if f["symbol"] in coin_watch})
        result.append({
            "id":code,"name":title,"coinlive_support":service,"state":operational,
            "source_strategy_status":s.get("status","UNAVAILABLE"),
            "data_label":s.get("data_label","NOT_CONNECTED"),
            "blocker":None if operational=="OBSERVING" else (s.get("reason") or why)[:220],
            "funding_observations":records if code=="B1" else [],
            "coinlive_watch_symbol_matches":matches if code=="B1" else [],
            "calculated_at_utc":STAMP(now),"cross_venue_spread_verified":False,
            "verified_execution_edge":False,"trade_signal":False,"can_modify_coinlive":False,
        })
    return result

def build(now=None,fetcher=fetch):
    now=now or now_utc()
    try:c=coin_input(now,fetcher)
    except (OSError,ValueError,KeyError,TypeError,TimeoutError) as exc:c=absent(SOURCES["coinlive"],exc)
    try:a=alti_input(now,fetcher)
    except (OSError,ValueError,KeyError,TypeError,TimeoutError) as exc:a=absent(SOURCES["alti"],exc)
    six=modules(a,c,now)
    active=sum(x["state"]=="OBSERVING" for x in six)
    system="DEGRADED" if any(x["state"] not in ("FRESH","PARTIAL") for x in (a,c)) or active<6 else "HEALTHY"
    report={
        "schema":"makine-coinlive-support-v2","generated_at_utc":STAMP(now),
        "mission":"INDEPENDENT_COINLIVE_SUPPORT","business_models":0,"research_laboratory":False,
        "system_state":system,"sources":{"alti":{k:v for k,v in a.items() if k not in ("strategy_data","funding")},
                                         "coinlive":{k:v for k,v in c.items() if k!="watch_symbols"}},
        "modules":six,"module_count":6,"modules_observing":active,
        "coinlive_feed":{"schema":"coinlive-external-context-v1",
             "source":"MAKINE","generated_at_utc":STAMP(now),
             "coinlive_scan_id":c.get("scan_id"),"coinlive_source_sha":c.get("source_sha"),
             "alti_scan_id":a.get("scan_id"),"alti_source_sha":a.get("source_sha"),
             "status":"LIMITED_CONTEXT" if active and c.get("verified_market_context") else "NO_VERIFIED_HANDOFF",
             "funding_event_context":next((x["funding_observations"] for x in six if x["id"]=="B1"),[])
                 if c.get("verified_market_context") else [],
             "matching_watch_symbols":next((x["coinlive_watch_symbol_matches"] for x in six if x["id"]=="B1"),[])
                 if c.get("verified_market_context") else [],
             "trade_candidates":[],"can_change_signal_policy":False,"can_place_orders":False,
             "can_change_paper_ledger":False,"machine_readable_context_only":True},
        "safety":{"allow_source_repo_writes":False,"allow_orders":False,"allow_paper_fills":False,
                  "automatic_trade_signal":False,"allow_model_promotion":False,
                  "combine_virtual_portfolios":False,
                  "verified_income":None,"verified_profit":None},
        "runtime":{"mode":"UNATTENDED_RULE_BASED","external_coding_agents_running":False,
                   "ai_api_required":False,"trigger":os.getenv("GITHUB_EVENT_NAME","LOCAL")},
    }
    return report

def save_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+".tmp")
    temp.write_text(json.dumps(obj,ensure_ascii=False,allow_nan=False,indent=2)+"\n",encoding="utf-8")
    os.replace(temp,path)

def persist(report,root=ROOT):
    save_json(root/"site/data/support.json",report)
    save_json(root/"site/data/coinlive-support.json",report["coinlive_feed"])
    history=root/"data/support-history.json"
    try:rows=json.loads(history.read_text("utf-8"))["entries"]
    except (ValueError,OSError,KeyError,TypeError):rows=[]
    entry={"at_utc":report["generated_at_utc"],"run_trigger":report["runtime"]["trigger"],
           "state":report["system_state"],
           "alti":report["sources"]["alti"]["state"],"coinlive":report["sources"]["coinlive"]["state"],
           "observing":[m["id"] for m in report["modules"] if m["state"]=="OBSERVING"],
           "coin_scan":report["sources"]["coinlive"].get("scan_id"),
           "alti_scan":report["sources"]["alti"].get("scan_id")}
    key=entry["at_utc"][:16]
    rows=[r for r in rows if str(r.get("at_utc",""))[:16]!=key]
    rows.append(entry)
    save_json(history,{"schema":"makine-six-support-history-v2","entries":rows[-672:]})
def main():
    r=build();persist(r)
    print(json.dumps({"state":r["system_state"],"modules":6,"observing":r["modules_observing"],
                      "handoff":r["coinlive_feed"]["status"],"no_orders":True},ensure_ascii=False))
if __name__=="__main__":main()
