"""Evidence-bound research synthesis. No signal generation or earnings claims."""
from __future__ import annotations
import hashlib
import json
import pathlib
from .catalog import registry
from .source import utcnow,stamp

ROOT=pathlib.Path(__file__).resolve().parents[1]
ENGINE_META=[
 {'id':'MARKET_INTEL','name':'Piyasa İstihbaratı','plain':'Kripto, funding, fiyat farkı ve veri kalitesini araştırır.','handoff':'READ_ONLY_CONTEXT'},
 {'id':'STRATEGY_DISCOVERY','name':'Strateji Laboratuvarı','plain':'Yeni stratejileri karşılaştırır; otomatik işlem açmaz.','handoff':'RESEARCH_REPORT'},
 {'id':'PERFORMANCE_RISK','name':'Performans ve Risk','plain':'Hangi fikrin ne kadar kanıtı var, maliyet ve veri boşluğu nedir?','handoff':'VALIDATION_SUMMARY'},
 {'id':'DATA_API','name':'Veri ve API Ürünleri','plain':'Ücretli veri/otomasyon hizmetine dönüşebilecek fikirleri inceler.','handoff':'NOT_APPLICABLE'},
 {'id':'REVENUE_VENTURE','name':'Gelir Girişimleri','plain':'Müşteri ve gelir ihtimali olan fikirleri değerlendirir.','handoff':'NOT_APPLICABLE'},
]


def read_config(name):return json.loads((ROOT/'config'/name).read_text(encoding='utf-8'))

def model_evidence(model,upstream):
    # A conceptual business opportunity is never upgraded just because a market scan is fresh.
    if model['id'] in {31,36,37,43,45,54,55}:
        return {'stage':'RESEARCH_ONLY','market_data':'PARTIAL_SOURCE_CONTEXT' if upstream and upstream.get('source_integrity')=='VERIFIED' else 'NOT_CONNECTED',
                'return_test':'NOT_PROVEN','revenue_test':'NO_CUSTOMER_EVIDENCE'}
    if model['engine'] in ('MARKET_INTEL','STRATEGY_DISCOVERY'):
        return {'stage':'RESEARCH_ONLY','market_data':'SOURCE_CONTEXT_ONLY' if upstream and upstream.get('source_integrity')=='VERIFIED' else 'NOT_CONNECTED',
                'return_test':'NOT_PROVEN','revenue_test':'NO_CUSTOMER_EVIDENCE'}
    return {'stage':'IDEA_ONLY','market_data':'NOT_REQUIRED_FOR_BUSINESS','return_test':'NOT_APPLICABLE','revenue_test':'NO_CUSTOMER_EVIDENCE'}


def build(upstream=None,now=None):
    now=now or utcnow(); settings=read_config('settings.json');release=read_config('release.json')
    approvals=read_config('pilot_approvals.json')
    rows=registry(); registry_status='LOCAL_VERIFIED_57_SEED'
    if upstream:
        incoming=upstream.get('catalog_names') or {}
        # Source is never executed. Detect changed names rather than silently overwriting.
        mismatch=[m['id'] for m in rows if incoming.get(m['id'])!=m['name']]
        if mismatch:registry_status='SOURCE_CATALOG_MISMATCH';
        else: registry_status='MATCHES_REMOTE_PINNED_COMMIT'
    else:mismatch=[]
    for m in rows:
        m['evidence']=model_evidence(m,upstream)
        src=(upstream or {}).get('catalog_details',{}).get(m['id']) or {}
        if m['id'] not in mismatch and src:
            m['original_catalogue']= {k:src[k] for k in ('simple','buyer','money','build','obstacle','pilot','kill','example','tag','cat','tier','capital','ops','risk','auto') if k in src}
        m['origin_verified_this_refresh']=bool(upstream) and m['id'] not in mismatch
        m['estimated_revenue_try']=None
        m['verified_revenue_try']=None
        m['profit_probability']=None
    top=sorted(rows,key=lambda m:(-m['research_priority_score'],m['id']))[:settings['top_opportunities']]
    date=stamp(now)
    source_summary={k:v for k,v in (upstream or {}).items() if k not in ('catalog_names','catalog_details','source_sha256')}
    seen={x.get('model_id') for x in approvals.get('approved_experiments',[]) if isinstance(x,dict) and x.get('approved_at_utc')}
    experiments=[x for x in approvals.get('approved_experiments',[]) if isinstance(x,dict)]
    for x in experiments:
        if x.get('model_id') not in range(1,58) or not x.get('approved_at_utc'):
            raise ValueError('An experiment is missing a valid model ID or approval timestamp')
    snapshot={
        'schema':'makine-research-report-v1','generated_at_utc':date,
        'build_id':release['build_id'],'product_version':release['product_version'],
        'product_version_approval':release['version_owner'],
        'mode':'RESEARCH_ONLY','manual_refresh':True,
        'origin_repo':'onurqlp/coin-live-pro','source_catalog_status':registry_status,
        'source_catalog_mismatches':mismatch,
        'source':source_summary if upstream else {'state':'NOT_FETCHED_YET','message':'İlk gerçek bağlantı kurulmadı. Kaynak kataloğu salt-okunur başlangıç verisidir.'},
        'engines':ENGINE_META,
        'metrics':{'catalog_models':len(rows),'research_engines':len(ENGINE_META),
                   'priority_ideas':len(top),'actual_verified_revenue_try':None,
                   'actual_revenue_status':'NO_PAYMENTS_OR_CUSTOMER_SYSTEM_CONNECTED',
                   'research_portfolio_reference_try':150000,
                   'reference_capital_not_real_deposit':True,
                   'approved_experiment_count':len(experiments),
                   'validated_profitable_models':0},
        'models':rows,'focus_ids':[m['id'] for m in top],
        'experiments':experiments,
        'research_decisions':[],
        'risk_contract':{
            'never_auto_trade':True,'never_transfer_funds':True,
            'never_write_to_coinlive_repo':True,'never_merge_coinlive_paper_balances':True,
            'existing_coinlive_signal_gate_unmodified':True,
            'signals_from_makine_are_forbidden':True,
            'source_must_have_provenance':True,
            'research_priority_is_not_win_probability':True,
            'actual_income_requires_verified_payment_records':True,
            'paper_hypothesis_is_not_actual_pnl':True},
        'manual_update_steps':['Kaynakların en son sürümünü sabitle ve veri sağlığını incele',
            '57 fikrin kanıt ve ticari durumunu karşılaştır','Onaylı deneylerin önceki kararlarını arşivle',
            'Yeni fırsat ve ürün adaylarını gerekçeleriyle güncelle',
            'COIN.LIVE için yalnız araştırma raporunu dışa aktar'],
        'next_action':'Önce ilk 6 fikrin müşteri talebini ve veri lisanslarını doğrula; COIN.LIVE motoru kendiliğinden güncellenmeyecek.',
        'warnings':['57 kavramın hiçbiri varsayılan olarak çalışan gelir makinesi değildir.',
                    'COIN.LIVE fiyat/kıvılcım verileri ALTI veya MAKİNE sanal getirisi değildir.',
                    'Kaynağın yaşı, kanıt düzeyi ve geçmiş performans ayrıdır.',
                    'MAKİNE gerçek emir, ücret tahsilatı veya harici repo yazma işlevi içermez.']}
    return snapshot


def handoff(snapshot):
    source=snapshot['source']
    integrity=source.get('source_integrity')=='VERIFIED'
    return {'schema':'makine-coinlive-research-handoff-v1',
        'generator':'MAKINE_CORE','generated_at_utc':snapshot['generated_at_utc'],
        'source_commit_sha':source.get('origin_commit_sha'),
        'source_scan_id':source.get('manifest_scan_id'),
        'source_integrity':source.get('source_integrity','UNVERIFIED'),
        'source_fresh_at_import':source.get('fresh_at_import',False),
        'can_promote_to_live_signal':False,'can_modify_live_policy':False,
        'can_execute_orders':False,'can_modify_coins_live_ledger':False,
        'new_trade_candidates':[],
        'market_context':{'status':'VERIFIED_READ_ONLY' if integrity else 'NOT_VERIFIED',
                          'radar_counts':source.get('radar_counts',{}),
                          'health':source.get('source_health_status'),
                          'import_timestamp':source.get('imported_at_utc')},
        'recommendations':[{'id':m['code'],'model_id':m['id'],'idea':m['name'],
                            'recommendation':'RESEARCH_ONLY','priority':m['tier'],
                            'not_executable':True,'alti_overlap':m['related_alti']}
                           for m in snapshot['models'] if m['related_alti']],
        'usage':'Read-only interpretation, not a trade signal, model promotion or trading authorization.'}
