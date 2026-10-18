"""MAKİNE CORE CLI. Explicit manual refresh; no autonomous deployments or trades."""
from __future__ import annotations
import argparse
import json
import os
import pathlib
import hashlib
from .source import collect,stamp,utcnow
from .engine import build,handoff

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'site/data';DATA=ROOT/'data'

def write_json(path,doc):
    path.parent.mkdir(parents=True,exist_ok=True)
    p=path.with_suffix(path.suffix+'.tmp')
    p.write_text(json.dumps(doc,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    os.replace(p,path)

def manual_refresh(mode='online'):
    prev=None
    if (OUT/'report.json').exists():
        try:prev=json.loads((OUT/'report.json').read_text(encoding='utf-8'))
        except (OSError,ValueError):pass
    source=None;message=''
    if mode=='online':
        try:source=collect()
        except Exception as exc:
            message=f'{type(exc).__name__}: {str(exc)[:180]}'
    snap=build(source)
    automated=os.getenv('MAKINE_SCHEDULED_REFRESH')=='1'
    snap['manual_refresh']=not automated
    snap['refresh_trigger']='SCHEDULED_AUTO' if automated else 'MANUAL_CLI'
    if message:
        snap['source']={'state':'REFRESH_FAILED','message':message,
             'last_verified_source_snapshot_utc':(prev or {}).get('source',{}).get('snapshot_finished_at_utc')}
        snap['warnings'].insert(0,'Veri bağlantısı başarısız: geçmiş kaynak yeni gibi kullanılmadı.')
    write_json(OUT/'report.json',snap)
    write_json(OUT/'coinlive-handoff.json',handoff(snap))
    # Idempotent-ish manually keyed by date and snapshot digest, never postdated observations.
    index=DATA/'update-history.json'
    old=[]
    if index.exists():
        try:old=json.loads(index.read_text(encoding='utf-8'))
        except (ValueError,OSError):pass
    payload={'build_id':snap['build_id'],'time_utc':snap['generated_at_utc'],
      'source_sha':snap['source'].get('origin_commit_sha'),
      'scan_id':snap['source'].get('manifest_scan_id'),
      'state':snap['source'].get('state','VERIFIED' if snap['source'].get('source_integrity')=='VERIFIED' else 'SOURCE_NOT_VERIFIED'),
      'models':57,'published_product_version':snap['product_version'],'version_changed':False}
    payload['id']=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()[:18]
    if not any(x.get('id')==payload['id'] for x in old):old.append(payload)
    write_json(index,old[-1000:])
    write_json(OUT/'update-history.json',old[-100:][::-1])
    print(json.dumps({'created':snap['generated_at_utc'],'mode':mode,'source':snap['source'].get('state',snap['source'].get('source_integrity')),
         'models':len(snap['models']),'message':message,'no_orders':True},ensure_ascii=False))
    return 0

def main():
    p=argparse.ArgumentParser(description='MAKİNE CORE read-only research controller')
    p.add_argument('command',choices=['refresh'],help='Explicitly refresh research snapshot')
    p.add_argument('--offline',action='store_true',help='Keep 57-model catalog without contacting Coin.Live')
    opt=p.parse_args()
    return manual_refresh('offline' if opt.offline else 'online')

if __name__=='__main__':raise SystemExit(main())
