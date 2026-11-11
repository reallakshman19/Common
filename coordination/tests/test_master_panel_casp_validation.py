"""F07-A1 contract attacks; synthetic source, no authentication/acceptance claims."""
import copy,hashlib,json,unittest
from unittest.mock import patch
from coordination.master_panel import casp_validation as cv
from coordination.master_panel.models import SourceIdentity,SourceKind

def context():
    target=dict(project_id='common',work_id='synthetic-work',lane_id='m3',assignment_id='synthetic-agent',run_id='synthetic-run',binding_id='synthetic-binding',coordinator_id='synthetic-controller',session_id='synthetic-session',chat_id=None,binding_generation=1,expected_label_sha='a'*64)
    repository=dict(id='1412133785',name='reallakshman19/Common')
    mailbox=dict(repository=repository,issue_number=375,visibility='PUBLIC')
    request=dict(protocol_version='1.0.0',message_id='00000000-0000-4000-8000-000000000001',request_id='00000000-0000-4000-8000-000000000002',kind='REQUEST',sender_id='synthetic-controller',reply_to=None,request_digest=None,created_at='2026-10-14T05:00:00Z',expires_at=None,expected_revision=1,target=target,repository=repository,mailbox=mailbox,action='DIRECTIVE',status='REQUESTED',authority_refs=['synthetic-authority-NOT-A-GRANT'],basis=dict(candidate='b'*40,sources=[],fixtures=[],profiles=[]),payload=dict(text='synthetic private prose',refs=[],decision=None),evidence=[])
    session=dict(protocol_version='1.0.0',protocol_ref=cv.PROTOCOL_REF,session_id='synthetic-session',agent_id='synthetic-agent',revision=1,lifecycle='ACTIVE',provider=dict(kind='chatgpt',instance_id='synthetic-instance',capabilities=['MANUAL_READ','MANUAL_REPLY']),bindings=[dict(target=target,repository=repository,mailbox=mailbox,mode='REPORT_ONLY',allowed_actions=['DIRECTIVE'],write_paths=[],authority_refs=['synthetic-authority-NOT-A-GRANT'])])
    reply=copy.deepcopy(request);reply.update(message_id='00000000-0000-4000-8000-000000000003',kind='RESULT',sender_id='synthetic-agent',reply_to=request['message_id'],request_digest=cv.digest(request),status='REPORTED')
    return request,reply,session

def observe(message,*,issue=375,body=None):
    text=body if body is not None else 'Synthetic report\n```casp\n'+json.dumps(message)+'\n```\n'
    source=SourceIdentity('common','1412133785','reallakshman19/Common',SourceKind.ISSUE_COMMENT,'222','2026-10-14T05:00:00Z',issue_number=issue,comment_id='222',body_sha256=hashlib.sha256(text.encode()).hexdigest())
    return text,source

class CaspValidationTests(unittest.TestCase):
    def setUp(self):self.request,self.reply,self.session=context()
    def test_registered_correlated_claim_never_authenticates_or_accepts(self):
        body,source=observe(self.reply);out=cv.inspect_comment(body,source,session=self.session,request=self.request)
        self.assertEqual(out['schema'],'VALID');self.assertEqual(out['request_correlation'],'MATCHES_SUPPLIED_REQUEST')
        for key in ['authentication','current_applicability','independent_acceptance','liveness']:self.assertEqual(out[key],'UNKNOWN')
        self.assertNotIn('synthetic private prose',json.dumps(out));self.assertNotIn('authority_refs',out);self.assertNotIn('chat_id',out)
    def test_missing_registry_request_stays_unqualified(self):
        body,source=observe(self.reply);out=cv.inspect_comment(body,source)
        self.assertEqual(out['registration'],'NOT_CONFIGURED');self.assertEqual(out['request_correlation'],'NOT_CONFIGURED')
    def test_all_reply_kinds_use_complete_wire_contract(self):
        for kind,status in [('ACK','BLOCKED'),('PLAN','PROPOSED'),('RESULT','FAILED'),('REVIEW','ACCEPTED'),('INVALIDATION','INVALIDATED')]:
            m=copy.deepcopy(self.reply);m.update(kind=kind,status=status);body,source=observe(m)
            out=cv.inspect_comment(body,source,session=self.session,request=self.request)
            self.assertEqual(out['reported_status'],status);self.assertEqual(out['independent_acceptance'],'UNKNOWN')
    def test_observed_source_and_private_mailbox_mismatch(self):
        for field in ['issue','repository','project','private']:
            m=copy.deepcopy(self.reply);issue=375
            if field=='issue':issue=374
            if field=='repository':m['repository']['id']='1363905693'
            if field=='project':m['target']['project_id']='aa3'
            if field=='private':m['mailbox']['visibility']='PRIVATE'
            body,source=observe(m,issue=issue)
            with self.assertRaises(ValueError):cv.inspect_comment(body,source)
    def test_raw_text_edit_does_not_borrow_prior_fingerprint(self):
        body,source=observe(self.reply)
        with self.assertRaisesRegex(ValueError,'fingerprint'):cv.inspect_comment(body+' ',source)
    def test_raw_newlines_and_canonical_envelope_digest_are_separate(self):
        first,source1=observe(self.reply);second=first.replace('\n','\r\n');_,source2=observe(self.reply,body=second)
        a=cv.inspect_comment(first,source1);b=cv.inspect_comment(second,source2)
        self.assertNotEqual(a['source_body_sha256'],b['source_body_sha256']);self.assertEqual(a['canonical_envelope_sha256'],b['canonical_envelope_sha256'])
    def test_wrong_supplied_request_or_descriptor_rejected(self):
        for field in ['reply_to','request_digest','request_id','target','revision','sender','action']:
            m=copy.deepcopy(self.reply)
            if field=='reply_to':m[field]='00000000-0000-4000-8000-000000000004'
            elif field=='request_digest':m[field]='c'*64
            elif field=='request_id':m[field]='00000000-0000-4000-8000-000000000005'
            elif field=='target':m['target']['binding_generation']=2
            elif field=='revision':m['expected_revision']=2
            elif field=='sender':m['sender_id']='synthetic-other-agent'
            else:m['action']='RECON_MODE'
            body,source=observe(m)
            with self.assertRaises(ValueError):cv.inspect_comment(body,source,session=self.session,request=self.request)
    def test_request_context_requires_registered_descriptor(self):
        body,source=observe(self.reply)
        with self.assertRaisesRegex(ValueError,'descriptor'):cv.inspect_comment(body,source,request=self.request)
    def test_retired_context_does_not_requalify_current_request(self):
        s=copy.deepcopy(self.session);s['lifecycle']='RETIRED';body,source=observe(self.reply)
        with self.assertRaisesRegex(ValueError,'retired'):cv.inspect_comment(body,source,session=s,request=self.request)
    def test_duplicate_and_multiple_envelopes_rejected(self):
        body,source=observe(self.reply)
        for raw in [body.replace('"protocol_version":','"protocol_version":"1.0.0","protocol_version":'),body+body]:
            _,identity=observe(self.reply,body=raw)
            with self.assertRaises(ValueError):cv.inspect_comment(raw,identity)
    def test_invalid_wire_fields_and_noncanonical_values_rejected(self):
        for field,value in [('created_at','2026-10-14T05:00:00.1Z'),('unexpected',True),('expected_revision',True),('expected_revision',1.5),('expected_revision',10**20)]:
            m=copy.deepcopy(self.reply);m[field]=value;body,source=observe(m)
            with self.assertRaises(ValueError):cv.inspect_comment(body,source)
    def test_missing_required_field_and_partial_outcome_rejected(self):
        m=copy.deepcopy(self.reply);m['evidence']=[dict(criterion='synthetic-C1',outcome='PARTIAL',basis=m['basis'],proof_ref=None)];body,source=observe(m)
        with self.assertRaisesRegex(ValueError,'outcome: enum'):cv.inspect_comment(body,source)
        m=copy.deepcopy(self.reply);del m['payload'];body,source=observe(m)
        with self.assertRaises(ValueError):cv.inspect_comment(body,source)
    def test_schema_byte_tampering_rejected_without_fallback(self):
        with patch.object(cv,'SCHEMA_SHA256',dict(cv.SCHEMA_SHA256,**{'message.schema.json':'0'*64})):
            with self.assertRaisesRegex(ValueError,'digest mismatch'):cv.validate_message(self.reply)
    def test_request_and_result_have_different_claims(self):
        body,source=observe(self.request);out=cv.inspect_comment(body,source,session=self.session)
        self.assertEqual(out['kind'],'REQUEST');self.assertEqual(out['authentication'],'UNKNOWN')

if __name__=='__main__':unittest.main()
