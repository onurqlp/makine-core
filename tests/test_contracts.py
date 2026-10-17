"""Critical evidence, data and no-trading contracts; no network calls."""
import copy
import datetime as dt
import hashlib
import json
import unittest
from makine.catalog import registry,parse_source_details
from makine.engine import build,handoff
from makine.source import collect,RAW,API

class ContractTests(unittest.TestCase):
    def test_exact_57_no_duplicates(self):
        rows=registry()
        self.assertEqual(len(rows),57)
        self.assertEqual([x['id'] for x in rows],list(range(1,58)))
        self.assertEqual(len({x['name'] for x in rows}),57)
        self.assertEqual(len([x for x in rows if x.get('related_alti')]),6)
        self.assertTrue(all(x['validated_revenue_try'] is None for x in rows))

    def test_parser_extracts_js_and_json_without_execution(self):
        js='''window.MODELS=[{id:1,name:"Deneme",money:"Net ödeme",pilot:"Pilot",risk:5}, {"id":31,"name":"Fonlama", "buyer":"Kendi sermayemiz"}]; throw Error('NEVER EXECUTE');'''
        result=parse_source_details(js)
        self.assertEqual(result[1]['money'],'Net ödeme')
        self.assertEqual(result[1]['risk'],5)
        self.assertEqual(result[31]['buyer'],'Kendi sermayemiz')

    def test_no_earnings_guessed(self):
        r=build()
        self.assertEqual(r['product_version'],'UNASSIGNED')
        self.assertIsNone(r['metrics']['actual_verified_revenue_try'])
        self.assertEqual(r['metrics']['validated_profitable_models'],0)
        self.assertEqual(len(r['models']),57)
        self.assertEqual(len(r['focus_ids']),6)
        self.assertTrue(all(m['estimated_revenue_try'] is None for m in r['models']))

    def test_research_handoff_is_never_a_signal(self):
        h=handoff(build())
        self.assertFalse(h['can_promote_to_live_signal'])
        self.assertFalse(h['can_execute_orders'])
        self.assertFalse(h['can_modify_live_policy'])
        self.assertFalse(h['can_modify_coins_live_ledger'])
        self.assertEqual(h['new_trade_candidates'],[])

    def fixture(self):
        now=dt.datetime(2026,10,17,12,0,tzinfo=dt.timezone.utc)
        sha='a'*40
        src={}
        def payload(doc):return json.dumps(doc,ensure_ascii=False).encode()
        for p in ('web/fikir-laboratuvari/models.js','web/fikir-laboratuvari/arbitraj-models.js'):
            s=registry()[:30] if p.endswith('/models.js') else registry()[30:]
            src[p]=('window.MODELS=['+','.join('{id:'+str(x['id'])+',name:'+json.dumps(x['name'],ensure_ascii=False)+'}' for x in s)+'];').encode()
        fixed='2026-10-17T11:59:30Z';scan='source-scan-001'
        src['web/data/health.json']=payload({'status':'HEALTHY','schedule_proven':False,'updated_at':fixed})
        src['web/data/v4-radar.json']=payload({'scan_id':scan,'counts':{'watch':5},'updated_at':fixed})
        src['web/data/v4-paper.json']=payload({'scan_id':scan,'starting_balance_usdt':10000,'equity_usdt':10000,'realized_pnl_usdt':0,'open_positions':[],'funding_state':'UNKNOWN_NOT_MODELED'})
        src['web/data/v4-lab.json']=payload({'scan_id':scan,'notes':['Insufficient sample']})
        src['web/data/v4-spark-review.json']=payload({'scan_id':scan,'total_ever_tickets':20})
        sources={}
        for p,sourcekey in [('web/data/health.json','health'),('web/data/v4-radar.json','v4-radar'),('web/data/v4-paper.json','v4-paper'),('web/data/v4-lab.json','v4-lab'),('web/data/v4-spark-review.json','v4-spark-review')]:
            sources[sourcekey]={'sha256':hashlib.sha256(src[p]).hexdigest()}
        src['web/data/v4-manifest.json']=payload({'publication_valid':True,'no_real_orders':True,'scan_id':scan,'finished_at_utc':fixed,'sources':sources})
        def fetch(url):
            if url==API+'/commits/main':return payload({'sha':sha})
            prefix=f'{RAW}/{sha}/'
            if not url.startswith(prefix):raise AssertionError('Not pinned to source commit')
            return src[url[len(prefix):]]
        return now,fetch,src

    def test_remote_snapshot_pin_hash_and_scan(self):
        now,fetch,_=self.fixture()
        x=collect(now=now,fetch=fetch)
        self.assertEqual(x['origin_commit_sha'],'a'*40)
        self.assertEqual(x['source_integrity'],'VERIFIED')
        self.assertTrue(x['fresh_at_import'])
        self.assertEqual(len(x['catalog_names']),57)
        self.assertFalse(x['usable_as_trade_signal'])

    def test_remote_digest_mismatch_blocks_source(self):
        now,fetch,source=self.fixture()
        previous=fetch
        def corrupted(url):
            data=previous(url)
            if url.endswith('/web/data/v4-radar.json'):
                return data.replace(b'"watch": 5',b'"watch": 6')
            return data
        x=collect(now=now,fetch=corrupted)
        self.assertEqual(x['source_integrity'],'FAILED')
        self.assertFalse(x['fresh_at_import'])
        self.assertTrue(any('HASH_MISMATCH' in w for w in x['warnings']))

    def test_old_snapshot_not_current(self):
        now,fetch,_=self.fixture()
        x=collect(now=now+dt.timedelta(days=1),fetch=fetch)
        self.assertEqual(x['source_integrity'],'VERIFIED')
        self.assertFalse(x['fresh_at_import'])
        self.assertIn('STALE_SOURCE_SNAPSHOT',x['warnings'])

if __name__=='__main__':unittest.main()
