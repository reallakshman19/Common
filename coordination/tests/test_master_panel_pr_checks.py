"""F01 source-qualified negative/positive fixtures; no live/provider acceptance."""
import copy
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import HTTPServer

from coordination.master_panel.github_source import ProviderError
from coordination.master_panel.pr_checks import PullCheckIntake
from coordination.master_panel.read_api import MasterPanelHandler,MasterReadService
from coordination.master_panel.storage import SourceStore
from coordination.tests.test_master_panel_read_api import source

REPO='reallakshman19/Common';RID='1412133785'
A='a'*40;B='b'*40;STAMP='2026-10-14T01:00:00Z'


def check(ident=200,status='queued',conclusion=None,head=A):
    return {'id':ident,'name':'same check name','head_sha':head,'status':status,
            'conclusion':conclusion,'started_at':None if status=='queued' else STAMP,
            'completed_at':STAMP if status=='completed' else None,
            'check_suite':{'id':99},'html_url':f'https://github.com/{REPO}/actions/runs/99/job/{ident}',
            'output':{'summary':'PRIVATE OUTPUT DO NOT EXPOSE'},
            'details_url':'https://private.example/secret'}


class FakeChecks:
    def __init__(self,runs=None):
        self.runs=runs if runs is not None else [check()]
        self.calls=[];self.pr_reads=0;self.move=False;self.head=A
        self.fail=None;self.page_overrides={};self.pr_id=9000
        self.private=False;self.repo_id=int(RID)
    def get_json(self,path,query=None):
        self.calls.append((path,query))
        if self.fail:raise ProviderError(*self.fail)
        if path==f'repos/{REPO}':
            return {'id':self.repo_id,'full_name':REPO,'private':self.private}
        if path==f'repos/{REPO}/pulls/377':
            self.pr_reads+=1
            return {'id':self.pr_id,'number':377,'state':'open','draft':True,
                    'created_at':STAMP,'updated_at':STAMP,'merged_at':None,
                    'head':{'sha':B if self.move and self.pr_reads>=2 else self.head},
                    'base':{'sha':B,'repo':{'id':int(RID),'full_name':REPO}},
                    'html_url':f'https://github.com/{REPO}/pull/377',
                    'body':'PRIVATE PR BODY DO NOT EXPOSE'}
        if path.endswith('/check-runs'):
            self.last_filter=query['filter']
            page=query['page']
            if page in self.page_overrides:return copy.deepcopy(self.page_overrides[page])
            return {'total_count':len(self.runs),'check_runs':copy.deepcopy(self.runs[(page-1)*100:page*100])}
        raise AssertionError('Unexpected provider request '+path)


class PullCheckSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=str(Path(self.temp.name)/'source.sqlite')
        self.store=SourceStore(self.path);self.reader=FakeChecks()
        self.intake=PullCheckIntake(self.store,self.reader);self.api=MasterReadService(self.path)
    def tearDown(self):
        self.store.close();self.temp.cleanup()
    def run_scan(self,budget=20):
        return self.intake.run('common',377,budget)

    def test_queued_check_has_no_invented_clocks_or_acceptance(self):
        result=self.run_scan();self.assertTrue(result['complete'])
        row=next(x for x in self.api.pr_checks('common',377)['items'] if x['source']['kind']=='CHECK_RUN')
        self.assertIsNone(row['provider']['started_at']);self.assertIsNone(row['provider']['completed_at'])
        self.assertEqual(row['provider']['status'],'queued')
        self.assertEqual(row['independent_acceptance'],'UNKNOWN')
        self.assertEqual(self.reader.last_filter,'all')

    def test_missing_family_is_unknown_and_read_does_not_initialize_tables(self):
        with tempfile.TemporaryDirectory() as temp:
            path=str(Path(temp)/'old.sqlite');writer=SourceStore(path)
            try:
                view=MasterReadService(path).pr_checks('common',377)
                self.assertEqual(view['state'],'UNKNOWN');self.assertIsNone(view['total_count'])
                self.assertEqual(view['source_family'],'PR_CHECK_COLLECTION')
                self.assertFalse(writer.conn.execute("SELECT 1 FROM sqlite_master WHERE name='pr_check_scans'").fetchone())
                with self.assertRaises(LookupError):MasterReadService(path).pr_checks('common',377,cursor='old-cursor')
            finally:writer.close()

    def test_skipped_success_and_same_name_distinct_ids_stay_distinct(self):
        self.reader.runs=[check(200,'completed','success'),check(201,'completed','skipped')]
        self.run_scan()
        rows=[x for x in self.api.pr_checks('common',377)['items'] if x['source']['kind']=='CHECK_RUN']
        self.assertEqual(len(rows),2)
        self.assertEqual({x['provider']['conclusion'] for x in rows},{'success','skipped'})
        self.assertTrue(all(x['independent_acceptance']=='UNKNOWN' for x in rows))

    def test_aba_replay_durable_versions(self):
        self.run_scan();self.run_scan()
        self.reader.runs=[check(200,'in_progress')];self.run_scan()
        self.reader.runs=[check()];self.run_scan()
        self.store.close();self.store=SourceStore(self.path);self.intake=PullCheckIntake(self.store,self.reader)
        rows=self.store.conn.execute("SELECT revision_id FROM pr_check_versions WHERE kind='CHECK_RUN' ORDER BY version").fetchall()
        self.assertEqual(len(rows),3);self.assertEqual(rows[0][0],rows[2][0]);self.assertNotEqual(rows[0][0],rows[1][0])

    def test_more_than100_partial_restart_then_complete(self):
        self.reader.runs=[check(200+i) for i in range(101)]
        first=self.run_scan(3)
        self.assertFalse(first['complete']);self.assertEqual(first['requests'],3);self.assertEqual(first['cursor_page'],2)
        self.store.close();self.store=SourceStore(self.path);self.intake=PullCheckIntake(self.store,self.reader)
        self.assertTrue(self.run_scan()['complete'])
        rows=self.api.pr_checks('common',377,200)['items']
        self.assertEqual(sum(x['source']['kind']=='CHECK_RUN' for x in rows),101)

    def test_pr_head_moving_during_scan_is_unknown(self):
        self.reader.move=True
        result=self.run_scan()
        self.assertEqual(result['error_kind'],'HEAD_MOVED');self.assertFalse(result['complete'])
        rows=self.api.pr_checks('common',377)['items']
        self.assertTrue(all(x['provider_head_relation']=='UNKNOWN' and x['source_freshness']=='UNKNOWN' for x in rows))

    def test_wrong_head_and_nonobject_and_duplicate_are_typed_failures(self):
        cases=[{'total_count':1,'check_runs':[check(head=B)]},
               {'total_count':1,'check_runs':[None]},
               {'total_count':2,'check_runs':[check(),check()]},
               {'total_count':True,'check_runs':[]}]
        for value in cases:
            with self.subTest(value=value):
                self.reader.page_overrides={1:value}
                result=self.run_scan()
                self.assertEqual(result['state'],'UNAVAILABLE');self.assertEqual(result['error_kind'],'SOURCE_CONFLICT')

    def test_wrong_repository_or_private_source_is_not_read(self):
        for prop,value in [('repo_id',123),('private',True)]:
            with self.subTest(prop=prop):
                setattr(self.reader,prop,value)
                result=self.run_scan()
                self.assertEqual(result['error_kind'],'SOURCE_CONFLICT')
                setattr(self.reader,prop,int(RID) if prop=='repo_id' else False)

    def test_same_check_identity_cannot_be_transferred_to_new_head(self):
        self.run_scan();self.reader.head=B;self.reader.runs=[check(head=B)]
        self.assertEqual(self.run_scan()['error_kind'],'SOURCE_CONFLICT')

    def test_family_cannot_refresh_or_tombstone_issue_scan(self):
        self.store.observe(source('1001','PRIVATE LEGACY BODY'),'old-scan')
        self.store.save_scan(project_id='common',repo_id=RID,scan_id='old-scan',
                             issue_page=1,issue_index=0,comment_page=1,status='PARTIAL')
        before=self.store.scan('common')
        self.run_scan()
        self.assertEqual(self.store.scan('common'),before)
        self.assertEqual(self.store.objects('common')[0]['deleted'],0)
        self.assertEqual(next(x for x in self.api.sources()['sources'] if x['project_id']=='common')['state'],'PARTIAL')

    def test_same_numbers_across_registered_repositories_do_not_collide(self):
        self.run_scan()
        class AA3(FakeChecks):
            def get_json(self,path,query=None):
                data=super().get_json(path.replace('reallakshman19/AA3',REPO),query)
                data=copy.deepcopy(data)
                if path=='repos/reallakshman19/AA3':
                    data.update(id=1363905693,full_name='reallakshman19/AA3')
                elif '/pulls/' in path:
                    data['base']['repo'].update(id=1363905693,full_name='reallakshman19/AA3')
                    data['html_url']=data['html_url'].replace(REPO,'reallakshman19/AA3')
                elif path.endswith('/check-runs'):
                    for value in data['check_runs']:
                        value['html_url']=value['html_url'].replace(REPO,'reallakshman19/AA3')
                return data
        self.assertTrue(PullCheckIntake(self.store,AA3()).run('aa3',377)['complete'])
        common=self.api.pr_checks('common',377)['items'];aa3=self.api.pr_checks('aa3',377)['items']
        self.assertEqual({x['source']['entity_id'] for x in common},{x['source']['entity_id'] for x in aa3})
        self.assertTrue(all(x['source']['repo_id']=='1412133785' for x in common))
        self.assertTrue(all(x['source']['repo_id']=='1363905693' for x in aa3))

    def test_changed_pr_identity_same_number_is_a_conflict(self):
        self.run_scan();self.reader.pr_id=9001
        self.assertEqual(self.run_scan()['error_kind'],'SOURCE_CONFLICT')

    def test_failure_retains_last_good_without_false_freshness(self):
        self.run_scan()
        for code,state in [(401,'FORBIDDEN'),(403,'FORBIDDEN'),(429,'RATE_LIMITED'),(503,'UNAVAILABLE')]:
            with self.subTest(code=code):
                self.reader.fail=(code,'PRIVATE SERVER PROSE')
                self.assertEqual(self.run_scan()['state'],state)
                view=self.api.pr_checks('common',377)
                self.assertTrue(view['items']);self.assertEqual(view['freshness'],'UNKNOWN')
                self.assertTrue(all(x['source_freshness']=='UNKNOWN' for x in view['items']))

    def test_total_drift_keeps_unqualified_objects_and_no_deletion(self):
        self.run_scan();self.reader.runs=[]
        self.reader.page_overrides={1:{'total_count':2,'check_runs':[check()]}}
        self.assertEqual(self.run_scan()['error_kind'],'PAGE_DRIFT')
        self.assertTrue(all(x['presence']=='UNQUALIFIED_LAST_GOOD' for x in self.api.pr_checks('common',377)['items']))

    def test_deleted_or_unseen_provider_row_is_not_asserted_absent(self):
        self.run_scan();self.reader.runs=[]
        self.assertTrue(self.run_scan()['complete'])
        row=next(x for x in self.api.pr_checks('common',377)['items'] if x['source']['kind']=='CHECK_RUN')
        self.assertEqual(row['presence'],'UNQUALIFIED_LAST_GOOD')
        self.assertFalse(self.api.pr_checks('common',377)['absence_verified'])

    def test_generation_cursor_bound_to_collection_and_revision(self):
        self.reader.runs=[check(200),check(201)];self.run_scan()
        first=self.api.pr_checks('common',377,1);cursor=first['next_cursor']
        second=self.api.pr_checks('common',377,1,cursor)
        self.assertNotEqual(first['items'][0]['source']['entity_id'],second['items'][0]['source']['entity_id'])
        with self.assertRaises(LookupError):self.api.pr_checks('common',378,1,cursor)
        self.reader.runs=[check(200,'completed','failure'),check(201)];self.run_scan()
        with self.assertRaises(LookupError):self.api.pr_checks('common',377,1,cursor)

    def test_safe_projection_suppresses_output_body_and_private_links(self):
        self.run_scan();encoded=json.dumps(self.api.pr_checks('common',377))
        for secret in ['PRIVATE OUTPUT','PRIVATE PR BODY','private.example','details_url','summary']:
            self.assertNotIn(secret,encoded)

    def test_loopback_route_read_only_bounded_and_origin_guarded(self):
        self.run_scan()
        service=self.api
        class Handler(MasterPanelHandler):pass
        Handler.service=service
        server=HTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        url=f'http://127.0.0.1:{server.server_port}/api/master/v1/pr-checks?project_id=common&pr_number=377'
        try:
            with urllib.request.urlopen(url) as response:
                self.assertEqual(json.load(response)['source_family'],'PR_CHECK_COLLECTION')
            for suffix in ['&limit=999','&private_key=SECRET']:
                with self.assertRaises(urllib.error.HTTPError) as error:urllib.request.urlopen(url+suffix)
                self.assertEqual(error.exception.code,400)
            req=urllib.request.Request(url,headers={'Origin':'https://foreign.example'})
            with self.assertRaises(urllib.error.HTTPError) as error:urllib.request.urlopen(req)
            self.assertEqual(error.exception.code,403)
            req=urllib.request.Request(url,data=b'{}',method='POST')
            with self.assertRaises(urllib.error.HTTPError) as error:urllib.request.urlopen(req)
            self.assertNotEqual(error.exception.code,200)
        finally:
            server.shutdown();server.server_close();thread.join()


if __name__=='__main__':unittest.main()

