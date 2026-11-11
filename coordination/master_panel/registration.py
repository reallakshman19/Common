"""Private controller-recorded descriptor contexts; not authentication/authority.

Standalone B1 only: no scanner, HTTP, worker, command or live-import integration.
Proof fields assert the controller's inspected existing records. This module
cannot establish human intent, provider identity, acceptance or writer custody.
"""
from __future__ import annotations
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from . import casp_validation as cv
from .github_source import ALLOWLIST
from .storage import SourceConflict

ID = re.compile(r'[A-Za-z0-9_.:-]{1,128}\Z')
HEX = re.compile(r'[0-9a-f]{64}\Z')

def sha(raw): return hashlib.sha256(raw.encode('utf-8')).hexdigest()

def safe_id(value):
    if not isinstance(value,str) or not ID.fullmatch(value): raise ValueError('safe record identity required')
    return value

def proof_for(proof, raw_hash, controller=None):
    keys={'controller_id','source_ref','source_sha256','descriptor_sha256','owner_authorized','verified'}
    if not isinstance(proof,dict) or set(proof)!=keys: raise ValueError('explicit inspected controller proof required')
    safe_id(proof['controller_id'])
    if controller is not None and proof['controller_id']!=controller: raise ValueError('controller mismatch')
    if proof['owner_authorized'] is not True or proof['verified'] is not True: raise ValueError('existing mapping proof required')
    if not isinstance(proof['source_ref'],str) or not proof['source_ref'].strip() or len(proof['source_ref'].encode())>2048: raise ValueError('bounded proof provenance required')
    if not isinstance(proof['source_sha256'],str) or not HEX.fullmatch(proof['source_sha256']): raise ValueError('exact proof digest required')
    if proof['descriptor_sha256']!=raw_hash: raise ValueError('descriptor proof mismatch')
    return cv.canonical(proof).decode()

class RegistrationStore:
    def __init__(self,path,*,read_only=False):
        if type(read_only) is not bool: raise ValueError('read_only must be boolean')
        self.path=str(path);self.read_only=read_only
        if read_only:
            p=Path(path)
            if not p.is_file(): raise FileNotFoundError('registration database unavailable')
            with p.open('rb') as f: header=f.read(20)
            if header[:16]==b'SQLite format 3\x00' and header[18:20]==b'\x02\x02': raise ValueError('read-only registry needs qualified rollback journal')
            uri=p.resolve().as_uri()+'?mode=ro';self.conn=sqlite3.connect(uri,uri=True,timeout=10)
            self.conn.execute('PRAGMA query_only=ON')
            self.conn.execute('SELECT sequence FROM registration_events LIMIT 0')
        else:
            self.conn=sqlite3.connect(path,timeout=10)
            self.conn.executescript('''
              CREATE TABLE IF NOT EXISTS registration_snapshots(
                snapshot_id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL,
                raw_sha256 TEXT NOT NULL, canonical_sha256 TEXT NOT NULL,
                session_id TEXT NOT NULL, revision INTEGER NOT NULL,
                descriptor_raw TEXT NOT NULL, proof_raw TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS registration_bindings(
                snapshot_id TEXT NOT NULL, binding_id TEXT NOT NULL,
                project_id TEXT NOT NULL, repo_id TEXT NOT NULL, assignment_id TEXT NOT NULL,
                binding_json TEXT NOT NULL, PRIMARY KEY(snapshot_id,binding_id));
              CREATE TABLE IF NOT EXISTS registration_events(
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL, fingerprint TEXT NOT NULL,
                project_id TEXT NOT NULL, repo_id TEXT NOT NULL, assignment_id TEXT NOT NULL,
                snapshot_id TEXT NOT NULL, binding_id TEXT NOT NULL,
                action TEXT NOT NULL, previous_event TEXT, proof_raw TEXT NOT NULL);
              CREATE INDEX IF NOT EXISTS registration_slot
                ON registration_events(project_id,repo_id,assignment_id,sequence);
            ''')
            for table in ('registration_snapshots','registration_bindings','registration_events'):
                for op in ('UPDATE','DELETE'):
                    self.conn.execute(f"CREATE TRIGGER IF NOT EXISTS {table}_no_{op.lower()} BEFORE {op} ON {table} BEGIN SELECT RAISE(ABORT,'registration history immutable'); END")
            self.conn.commit()
        self.conn.row_factory=sqlite3.Row

    def close(self): self.conn.close()
    def __enter__(self): return self
    def __exit__(self,*args): self.close()

    @contextmanager
    def _write(self):
        if self.read_only: raise ValueError('read-only registration store')
        self.conn.execute('BEGIN IMMEDIATE')
        try: yield;self.conn.commit()
        except BaseException: self.conn.rollback();raise

    @contextmanager
    def _read(self):
        own=not self.conn.in_transaction
        if own:self.conn.execute('BEGIN')
        try:
            yield
            if own:self.conn.commit()
        except BaseException:
            if own:self.conn.rollback()
            raise

    def record_snapshot(self,snapshot_id,descriptor_raw,proof):
        safe_id(snapshot_id)
        if not isinstance(descriptor_raw,str) or len(descriptor_raw.encode('utf-8'))>65536: raise ValueError('bounded exact descriptor required')
        session=cv.loads(descriptor_raw);cv.validate_session(session)
        if session['protocol_ref']!=cv.PROTOCOL_REF: raise ValueError('unqualified protocol pin')
        raw_hash=sha(descriptor_raw);canonical_hash=cv.digest(session)
        proof_raw=proof_for(proof,raw_hash)
        seen=set()
        for b in session['bindings']:
            t=b['target'];reg=ALLOWLIST.get(t['project_id'])
            if not reg or b['repository']!={'id':reg.repo_id,'name':reg.repo_full_name} or b['mailbox']['repository']!=b['repository']: raise ValueError('unregistered project/repository/mailbox')
            if t['coordinator_id']!=proof['controller_id']: raise ValueError('controller mismatch')
            slot=(t['project_id'],b['repository']['id'],t['assignment_id'])
            if slot in seen: raise ValueError('ambiguous assignment binding')
            seen.add(slot)
        fingerprint=cv.digest({'raw_sha256':raw_hash,'proof':proof})
        with self._write():
            old=self.conn.execute('SELECT * FROM registration_snapshots WHERE snapshot_id=?',(snapshot_id,)).fetchone()
            if old:
                if old['fingerprint']!=fingerprint: raise SourceConflict('snapshot identity conflict')
                return {'snapshot_id':snapshot_id,'replay':True,'raw_sha256':raw_hash}
            prior=self.conn.execute('SELECT canonical_sha256 FROM registration_snapshots WHERE session_id=? AND revision=?',(session['session_id'],session['revision'])).fetchall()
            if any(r['canonical_sha256']!=canonical_hash for r in prior): raise SourceConflict('descriptor revision conflict')
            self.conn.execute('INSERT INTO registration_snapshots VALUES (?,?,?,?,?,?,?,?)',(snapshot_id,fingerprint,raw_hash,canonical_hash,session['session_id'],session['revision'],descriptor_raw,proof_raw))
            for b in session['bindings']:
                t=b['target'];self.conn.execute('INSERT INTO registration_bindings VALUES (?,?,?,?,?,?)',(snapshot_id,t['binding_id'],t['project_id'],b['repository']['id'],t['assignment_id'],cv.canonical(b).decode()))
        return {'snapshot_id':snapshot_id,'replay':False,'raw_sha256':raw_hash}

    def _binding(self,snapshot_id,binding_id):
        row=self.conn.execute('''SELECT b.*,s.descriptor_raw,s.raw_sha256,s.revision FROM registration_bindings b
              JOIN registration_snapshots s USING(snapshot_id) WHERE snapshot_id=? AND binding_id=?''',(snapshot_id,binding_id)).fetchone()
        if row is None: raise ValueError('unknown recorded binding')
        return row,json.loads(row['binding_json']),cv.loads(row['descriptor_raw'])

    def select_current(self,event_id,snapshot_id,binding_id,proof,*,expected_previous=None,action='SET'):
        safe_id(event_id);safe_id(snapshot_id);safe_id(binding_id)
        if expected_previous is not None: safe_id(expected_previous)
        if action not in ('SET','RETIRE'): raise ValueError('explicit pointer action required')
        with self._write():
            row,b,session=self._binding(snapshot_id,binding_id);t=b['target']
            proof_raw=proof_for(proof,row['raw_sha256'],t['coordinator_id'])
            if (action=='RETIRE')!=(session['lifecycle']=='RETIRED'): raise ValueError('pointer/lifecycle mismatch')
            fingerprint=cv.digest({'snapshot_id':snapshot_id,'binding_id':binding_id,'action':action,'previous_event':expected_previous,'proof':proof})
            old=self.conn.execute('SELECT * FROM registration_events WHERE event_id=?',(event_id,)).fetchone()
            if old:
                if old['fingerprint']!=fingerprint: raise SourceConflict('pointer event conflict')
                return {'event_id':event_id,'replay':True,'sequence':old['sequence']}
            slot=(row['project_id'],row['repo_id'],row['assignment_id'])
            current=self.conn.execute('SELECT * FROM registration_events WHERE project_id=? AND repo_id=? AND assignment_id=? ORDER BY sequence DESC LIMIT 1',slot).fetchone()
            if (current['event_id'] if current else None)!=expected_previous: raise SourceConflict('stale current pointer')
            if current:
                before,old_b,old_s=self._binding(current['snapshot_id'],current['binding_id']);old_t=old_b['target']
                if t['binding_generation']<old_t['binding_generation']: raise SourceConflict('historical generation cannot become current')
                new_identity=(t['binding_id'],t['session_id'],t['chat_id'],session['provider']['kind'],session['provider']['instance_id'])
                old_identity=(old_t['binding_id'],old_t['session_id'],old_t['chat_id'],old_s['provider']['kind'],old_s['provider']['instance_id'])
                if new_identity!=old_identity and t['binding_generation']<=old_t['binding_generation']: raise SourceConflict('rebind needs newer generation')
                if t['binding_id']==old_t['binding_id'] and row['revision']<before['revision']: raise SourceConflict('historical revision cannot become current')
                if current['action']=='RETIRE' and action=='SET' and t['binding_generation']<=old_t['binding_generation']: raise SourceConflict('retired generation cannot resurrect')
            cur=self.conn.execute('INSERT INTO registration_events(event_id,fingerprint,project_id,repo_id,assignment_id,snapshot_id,binding_id,action,previous_event,proof_raw) VALUES (?,?,?,?,?,?,?,?,?,?)',(event_id,fingerprint,*slot,snapshot_id,binding_id,action,expected_previous,proof_raw))
            return {'event_id':event_id,'replay':False,'sequence':cur.lastrowid}

    def public_current(self,project_id):
        if project_id not in ALLOWLIST: raise ValueError('unregistered project')
        with self._read():
            rows=self.conn.execute('''SELECT e.* FROM registration_events e WHERE project_id=? AND sequence=(SELECT MAX(p.sequence) FROM registration_events p WHERE p.project_id=e.project_id AND p.repo_id=e.repo_id AND p.assignment_id=e.assignment_id) ORDER BY assignment_id''',(project_id,)).fetchall()
            out=[]
            for e in rows:
                row,b,s=self._binding(e['snapshot_id'],e['binding_id']);t=b['target']
                out.append(dict(project_id=e['project_id'],repo_id=e['repo_id'],assignment_id=e['assignment_id'],binding_id=e['binding_id'],binding_generation=t['binding_generation'],work_id=t['work_id'],lane_id=t['lane_id'],run_id=t['run_id'],session_id=s['session_id'],descriptor_revision=s['revision'],descriptor_raw_sha256=row['raw_sha256'],provider_kind=s['provider']['kind'],lifecycle=s['lifecycle'],pointer_event=e['event_id'],registration='CONTROLLER_RECORDED_CONTEXT',authentication='UNKNOWN',independent_acceptance='UNKNOWN',liveness='UNKNOWN',dispatch_authority='NOT_GRANTED'))
            return out

    def generation(self):
        with self._read():
            snapshots=self.conn.execute('SELECT snapshot_id,fingerprint FROM registration_snapshots ORDER BY snapshot_id').fetchall()
            events=self.conn.execute('SELECT sequence,event_id,fingerprint FROM registration_events ORDER BY sequence').fetchall()
            return cv.digest({'snapshots':[dict(r) for r in snapshots],'events':[dict(r) for r in events]})
