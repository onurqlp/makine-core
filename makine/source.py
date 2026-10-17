"""Allowlisted, bounded, read-only import of Coin.Live public research outputs.
Never imports remote Python/JS into the runtime. No write to source repo.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import urllib.request
import urllib.error
from .catalog import parse_source_names,parse_source_details

OWNER='onurqlp'; REPO='coin-live-pro'
API=f'https://api.github.com/repos/{OWNER}/{REPO}'
RAW=f'https://raw.githubusercontent.com/{OWNER}/{REPO}'
NAMES=('web/fikir-laboratuvari/models.js','web/fikir-laboratuvari/arbitraj-models.js')
PUBLIC=('web/data/v4-manifest.json','web/data/health.json','web/data/v4-radar.json',
        'web/data/v4-paper.json','web/data/v4-lab.json','web/data/v4-spark-review.json')
MAX_BYTES=800000

def utcnow():return dt.datetime.now(dt.timezone.utc)
def stamp(d):return d.isoformat(timespec='seconds').replace('+00:00','Z')
def parse_time(value):
    try:
        t=dt.datetime.fromisoformat(str(value).replace('Z','+00:00'))
        return t.astimezone(dt.timezone.utc) if t.tzinfo else None
    except (TypeError,ValueError,OverflowError):return None

def read_url(url):
    if not (url.startswith(RAW+'/') or url==API+'/commits/main'):
        raise ValueError('Source outside exact approved repository')
    req=urllib.request.Request(url,headers={'Accept':'application/json','User-Agent':'MakineCoreResearch/0.1','Cache-Control':'no-cache'})
    with urllib.request.urlopen(req,timeout=20) as res:
        raw=res.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:raise ValueError('Source exceeds import size cap')
    return raw

def collect(now=None,fetch=read_url):
    now=now or utcnow();warnings=[];records={}; hashes={}
    commit=json.loads(fetch(API+'/commits/main'))
    sha=commit.get('sha')
    if not isinstance(sha,str) or len(sha)!=40 or any(c not in '0123456789abcdef' for c in sha):
        raise ValueError('No immutable source commit available')
    for path in NAMES+PUBLIC:
        raw=fetch(f'{RAW}/{sha}/{path}')
        hashes[path]=hashlib.sha256(raw).hexdigest()
        if path.endswith('.js'):
            records[path]=parse_source_details(raw.decode('utf-8'))
        else:
            records[path]=json.loads(raw.decode('utf-8'))
    source_catalog={**records[NAMES[0]],**records[NAMES[1]]}
    source_names={i:x['name'] for i,x in source_catalog.items()}
    if sorted(source_names)!=list(range(1,58)):
        raise ValueError('Remote 57-model registry is incomplete or changed')
    manifest=records['web/data/v4-manifest.json']
    health=records['web/data/health.json']
    radar=records['web/data/v4-radar.json']
    paper=records['web/data/v4-paper.json']
    lab=records['web/data/v4-lab.json']
    spark=records['web/data/v4-spark-review.json']
    manifest_ok=bool(manifest.get('publication_valid')) and bool(manifest.get('no_real_orders'))
    scan_id=manifest.get('scan_id')
    if not scan_id or any(records[p].get('scan_id')!=scan_id for p in (
         'web/data/v4-radar.json','web/data/v4-paper.json','web/data/v4-lab.json','web/data/v4-spark-review.json')):
        manifest_ok=False;warnings.append('SCAN_ID_MISMATCH')
    hash_mismatches=[]
    for p,source_key in [('web/data/v4-radar.json','v4-radar'),('web/data/v4-paper.json','v4-paper'),('web/data/v4-lab.json','v4-lab'),('web/data/v4-spark-review.json','v4-spark-review'),('web/data/health.json','health')]:
        expected=(manifest.get('sources',{}).get(source_key) or {}).get('sha256')
        if expected!=hashes[p]:hash_mismatches.append(source_key)
    if hash_mismatches:
        warnings.append('HASH_MISMATCH: '+','.join(hash_mismatches));manifest_ok=False
    time=parse_time(manifest.get('finished_at_utc'))
    age_minutes=round((now-time).total_seconds()/60,1) if time else None
    if age_minutes is None or age_minutes<-5:
        manifest_ok=False;warnings.append('SOURCE_TIME_INVALID')
    if age_minutes is not None and age_minutes>45:warnings.append('STALE_SOURCE_SNAPSHOT')
    # Date + provenance are independent of fitness-for-signal. No cross-repo promotion.
    trusted=manifest_ok and age_minutes is not None and age_minutes<=45
    return {
      'origin_repo':f'{OWNER}/{REPO}','origin_commit_sha':sha,'imported_at_utc':stamp(now),
      'manifest_scan_id':scan_id,'snapshot_finished_at_utc':manifest.get('finished_at_utc'),
      'snapshot_age_minutes_at_import':age_minutes,
      'source_integrity': 'VERIFIED' if manifest_ok else 'FAILED',
      'fresh_at_import':bool(trusted),'import_mode':'READ_ONLY_PINNED_COMMIT',
      'source_health_status':health.get('status'),'schedule_proven':health.get('schedule_proven'),
      'radar_counts':radar.get('counts') or {},
      'paper_starting_balance_usdt':paper.get('starting_balance_usdt'),
      'paper_equity_usdt':paper.get('equity_usdt'),
      'paper_realized_pnl_usdt':paper.get('realized_pnl_usdt'),
      'paper_open_positions_count':len(paper.get('open_positions') or []),
      'paper_funding_state':paper.get('funding_state'),
      'sample_status':lab.get('notes',[]),
      'spark_tickets':spark.get('total_ever_tickets'),
      'catalog_names':source_names,'catalog_details':source_catalog,'source_sha256':hashes,'warnings':warnings,
      'usable_as_trade_signal':False,'orders_enabled':False,
      'feed_summary_only':True
    }
