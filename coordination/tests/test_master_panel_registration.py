"""Synthetic isolated B1 checks, not live admission or acceptance."""
import copy,hashlib,json,tempfile,unittest
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import threading
from pathlib import Path
from coordination.master_panel import casp_validation as cv
from coordination.master_panel.registration import RegistrationStore
from coordination.tests.test_master_panel_casp_validation import context

class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'registry.sqlite';self.store=RegistrationStore(self.path)
        self.request,self.reply,self.session=context();self.raw=json.dumps(self.session)
        self.proof=self.proof_for(self.raw)
    def tearDown(self):self.store.close();self.tmp.cleanup()
    def proof_for(self,raw):
        return dict(controller_id='synthetic-controller',source_ref='PRIVATE_CHAT_TOKEN_PROOF_CANARY',source_sha256='a'*64,descriptor_sha256=hashlib.sha256(raw.encode()).hexdigest(),owner_authorized=True,verified=True)
    def record(self,s=None,identifier='S1'):
        raw=json.dumps(s or self.session);p=self.proof_for(raw);self.store.record_snapshot(identifier,raw,p);return p
    def first(self):
        self.record();return self.store.select_current('E1','S1','synthetic-binding',self.proof)
    def successor(self,generation=2):
        s=copy.deepcopy(self.session);s['session_id']='synthetic-successor';s['provider']['instance_id']='synthetic-successor-instance';t=s['bindings'][0]['target'];t.update(session_id=s['session_id'],binding_id='successor-binding',binding_generation=generation);return s
    def test_snapshot_does_not_select_or_authenticate(self):
        self.record();self.assertEqual(self.store.public_current('common'),[])
        self.first();r=self.store.public_current('common')[0]
        for key in ('authentication','independent_acceptance','liveness'):self.assertEqual(r[key],'UNKNOWN')
        self.assertEqual(r['dispatch_authority'],'NOT_GRANTED')
    def test_public_projection_omits_private_proof_route_payload(self):
        s=copy.deepcopy(self.session);s['bindings'][0]['authority_refs']=['PRIVATE_SOURCE_CANARY'];s['provider']['instance_id']='private-instance-canary';p=self.record(s)
        self.store.select_current('E1','S1','synthetic-binding',p)
        rows=self.store.public_current('common');out=json.dumps(rows)
        for value in ('PRIVATE_SOURCE_CANARY','private-instance-canary','PRIVATE_CHAT_TOKEN_PROOF_CANARY'):self.assertNotIn(value,out)
        for row in rows:
            for key in ('descriptor_raw','proof_raw','chat_id','authority_refs','instance_id'):self.assertNotIn(key,row)
    def test_unverified_unknown_or_mismatched_proof_is_rejected(self):
        for change in ({'verified':False},{'owner_authorized':False},{'source_ref':''},{'source_sha256':'bad'},{'descriptor_sha256':'b'*64},{'controller_id':'wrong'},{'unknown':True}):
            with self.subTest(change=change),self.assertRaises(ValueError):self.store.record_snapshot('BAD',self.raw,{**self.proof,**change})
        self.assertEqual(self.store.conn.execute('SELECT count(*) FROM registration_snapshots').fetchone()[0],0)
    def test_missing_proof_fields_rejected(self):
        for key in self.proof:
            p={k:v for k,v in self.proof.items() if k!=key}
            with self.subTest(key=key),self.assertRaises(ValueError):self.store.record_snapshot('BAD',self.raw,p)
    def test_schema_pin_project_repo_mailbox_and_session_identity_rejected(self):
        for field in ('pin','project','repo','mailbox','session','revision'):
            s=copy.deepcopy(self.session)
            if field=='pin':s['protocol_ref']=s['protocol_ref'].replace('d9180904','11111111')
            if field=='project':s['bindings'][0]['target']['project_id']='unknown'
            if field=='repo':s['bindings'][0]['repository']['id']='1363905693'
            if field=='mailbox':s['bindings'][0]['mailbox']['repository']={'id':'1','name':'other/Repo'}
            if field=='session':s['bindings'][0]['target']['session_id']='other'
            if field=='revision':s['revision']=True
            with self.subTest(field=field),self.assertRaises(ValueError):self.record(s)
    def test_duplicate_assignment_binding_rejects_whole_snapshot(self):
        s=copy.deepcopy(self.session);b=copy.deepcopy(s['bindings'][0]);b['target']['binding_id']='second';s['bindings'].append(b)
        with self.assertRaises(ValueError):self.record(s)
        self.assertEqual(self.store.conn.execute('SELECT count(*) FROM registration_bindings').fetchone()[0],0)
    def test_same_snapshot_id_changed_raw_or_proof_conflicts(self):
        self.record()
        for raw,p in ((self.raw+' ',self.proof_for(self.raw+' ')),(self.raw,{**self.proof,'source_ref':'changed'})):
            with self.assertRaises(ValueError):self.store.record_snapshot('S1',raw,p)
        self.assertEqual(self.store.conn.execute('SELECT count(*) FROM registration_snapshots').fetchone()[0],1)
    def test_same_session_revision_changed_semantics_conflicts(self):
        self.record();s=copy.deepcopy(self.session);s['lifecycle']='HOLD'
        with self.assertRaises(ValueError):self.record(s,'S2')
    def test_exact_replay_after_restart_changes_no_generation(self):
        self.first();before=self.store.generation();self.store.close();self.store=RegistrationStore(self.path)
        self.assertTrue(self.store.record_snapshot('S1',self.raw,self.proof)['replay'])
        self.assertTrue(self.store.select_current('E1','S1','synthetic-binding',self.proof)['replay'])
        self.assertEqual(before,self.store.generation())
    def test_pointer_replay_cannot_resurrect_old_binding(self):
        self.first();p=self.record(self.successor(),'S2');self.store.select_current('E2','S2','successor-binding',p,expected_previous='E1')
        self.store.select_current('E1','S1','synthetic-binding',self.proof)
        self.assertEqual(self.store.public_current('common')[0]['binding_id'],'successor-binding')
    def test_stale_pointer_fence_and_changed_event_rejected(self):
        self.first();p=self.record(self.successor(),'S2');before=self.store.generation()
        with self.assertRaises(ValueError):self.store.select_current('E2','S2','successor-binding',p)
        with self.assertRaises(ValueError):self.store.select_current('E1','S2','successor-binding',p,expected_previous='E1')
        self.assertEqual(before,self.store.generation())
    def test_rebind_requires_new_generation_even_when_binding_id_reused(self):
        self.first();s=self.successor(1);s['bindings'][0]['target']['binding_id']='synthetic-binding';p=self.record(s,'S2')
        with self.assertRaises(ValueError):self.store.select_current('E2','S2','synthetic-binding',p,expected_previous='E1')
    def test_old_generation_and_revision_cannot_become_current(self):
        self.first();p=self.record(self.successor(),'S2');self.store.select_current('E2','S2','successor-binding',p,expected_previous='E1')
        with self.assertRaises(ValueError):self.store.select_current('E3','S1','synthetic-binding',self.proof,expected_previous='E2')
    def test_retirement_is_explicit_and_preserves_history(self):
        self.first();s=copy.deepcopy(self.session);s.update(lifecycle='RETIRED',revision=2);p=self.record(s,'S2')
        with self.assertRaises(ValueError):self.store.select_current('E2','S2','synthetic-binding',p,expected_previous='E1')
        self.store.select_current('E2','S2','synthetic-binding',p,expected_previous='E1',action='RETIRE')
        self.assertEqual(self.store.public_current('common')[0]['lifecycle'],'RETIRED')
        self.assertEqual(self.store.conn.execute('SELECT count(*) FROM registration_events').fetchone()[0],2)
    def test_retired_generation_cannot_resurrect_under_new_revision(self):
        self.first();s=copy.deepcopy(self.session);s.update(lifecycle='RETIRED',revision=2);p=self.record(s,'S2');self.store.select_current('E2','S2','synthetic-binding',p,expected_previous='E1',action='RETIRE')
        s.update(lifecycle='ACTIVE',revision=3);p=self.record(s,'S3')
        with self.assertRaises(ValueError):self.store.select_current('E3','S3','synthetic-binding',p,expected_previous='E2')
    def test_other_binding_or_pointer_proof_cannot_be_guessed(self):
        self.record()
        for binding,p in (('unknown',self.proof),('synthetic-binding',{**self.proof,'verified':False})):
            with self.assertRaises(ValueError):self.store.select_current('E1','S1',binding,p)
        self.assertEqual(self.store.public_current('common'),[])
    def test_pointer_transaction_failure_is_atomic(self):
        self.record();self.store.conn.execute("CREATE TRIGGER synthetic_failure BEFORE INSERT ON registration_events BEGIN SELECT RAISE(ABORT,'synthetic failure'); END");self.store.conn.commit()
        with self.assertRaises(Exception):self.store.select_current('E1','S1','synthetic-binding',self.proof)
        self.assertEqual(self.store.public_current('common'),[])
        self.assertEqual(self.store.conn.execute('SELECT count(*) FROM registration_events').fetchone()[0],0)
    def test_history_cannot_be_updated_or_deleted(self):
        self.first()
        for table in ('registration_snapshots','registration_bindings','registration_events'):
            for op in (f'DELETE FROM {table}',f'UPDATE {table} SET '+('snapshot_id=snapshot_id' if table!='registration_events' else 'event_id=event_id')):
                with self.subTest(op=op),self.assertRaises(Exception):self.store.conn.execute(op)
                self.store.conn.rollback()
    def test_read_only_projection_writes_nothing_and_cannot_import(self):
        self.first();before=self.path.read_bytes();files=set(Path(self.tmp.name).iterdir())
        with RegistrationStore(self.path,read_only=True) as reader:
            self.assertEqual(reader.public_current('common'),self.store.public_current('common'))
            reader.generation()
            with self.assertRaises(ValueError):reader.record_snapshot('S2',self.raw,self.proof)
        self.assertEqual(self.path.read_bytes(),before);self.assertEqual(set(Path(self.tmp.name).iterdir()),files)
    def test_unknown_project_is_not_invented(self):
        with self.assertRaises(ValueError):self.store.public_current('new-project')
    def test_registry_tables_have_no_report_acceptance_or_send_interface(self):
        self.first();out=self.store.public_current('common')[0]
        self.assertEqual(out['registration'],'CONTROLLER_RECORDED_CONTEXT')
        self.assertFalse(hasattr(self.store,'send'));self.assertFalse(hasattr(self.store,'accept'))
        self.assertNotIn('reported_status',out);self.assertNotIn('evidence',out)

    def test_two_writers_with_same_pointer_expectation_have_one_winner(self):
        self.first();sessions=[self.successor(),self.successor()]
        sessions[1]['session_id']='second-successor';sessions[1]['bindings'][0]['target']['session_id']='second-successor';sessions[1]['bindings'][0]['target']['binding_id']='second-binding'
        proofs=[self.record(s,f'S{i+2}') for i,s in enumerate(sessions)];barrier=threading.Barrier(2)
        def attempt(i):
            with RegistrationStore(self.path) as writer:
                barrier.wait(timeout=5)
                try:
                    writer.select_current(f'E{i+2}',f'S{i+2}',sessions[i]['bindings'][0]['target']['binding_id'],proofs[i],expected_previous='E1');return 'SELECTED'
                except ValueError:return 'STALE_EXPECTATION'
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(attempt,range(2)))
        self.assertCountEqual(results,['SELECTED','STALE_EXPECTATION'])
        self.assertEqual(self.store.conn.execute('SELECT count(*) FROM registration_events').fetchone()[0],2)

    def test_generation_read_keeps_one_snapshot_during_concurrent_pointer_update(self):
        self.first();p=self.record(self.successor(),'S2');self.store.conn.execute('PRAGMA journal_mode=WAL');before=self.store.generation()
        writer=RegistrationStore(self.path);changed=[]
        def interleave(cursor,row):
            value=sqlite3.Row(cursor,row)
            if 'snapshot_id' in value.keys() and 'fingerprint' in value.keys() and not changed:
                changed.append(True);writer.select_current('E2','S2','successor-binding',p,expected_previous='E1')
            return value
        self.store.conn.row_factory=interleave
        try:self.assertEqual(self.store.generation(),before)
        finally:self.store.conn.row_factory=sqlite3.Row;writer.close()
        self.assertEqual(changed,[True]);self.assertNotEqual(self.store.generation(),before)

if __name__=='__main__':unittest.main()
