import test from 'node:test';
import assert from 'node:assert/strict';
import {validate,canonicalJSON,traceClaim,traceEvidence,traceModule,ProvenanceError} from './provenance-v1.mjs';

function fixture() {
  return {
  "schema": "relay-provenance-v1",
  "parent_issue": "reallaksh19/Common#787",
  "owner_intents": [
    {
      "id": "OI-1",
      "raw_text": "start now",
      "original_source": {
        "kind": "CHAT",
        "status": "UNKNOWN",
        "locator": null
      },
      "first_durable_mirror": "https://github.com/reallaksh19/Common/issues/787"
    }
  ],
  "claims": [
    {
      "id": "AC1",
      "intent_ids": [
        "OI-1"
      ],
      "criterion": "A different agent can trace claim source"
    }
  ],
  "responsibilities": [
    {
      "id": "R1-A",
      "claim_ids": [
        "AC1"
      ],
      "depends_on": [],
      "scope": "Pure records",
      "write_surface": [
        "skills/engineering-relay-v1/provenance-v1.mjs"
      ]
    }
  ],
  "sessions": [
    {
      "id": "S1",
      "responsibility_id": "R1-A",
      "agent_id": "AGENT-1",
      "base_sha": "957377de11843f78dd7210450c8e5a99b859eea9",
      "changed_files": [
        "skills/engineering-relay-v1/provenance-v1.mjs"
      ],
      "events": [
        {
          "kind": "OWNER_PROMPT",
          "source": {
            "kind": "CHAT",
            "status": "UNKNOWN",
            "locator": null
          },
          "summary": "start now"
        },
        {
          "kind": "CODE_CHANGE",
          "source": {
            "kind": "FILE",
            "status": "CLAIMED",
            "locator": "skills/engineering-relay-v1/provenance-v1.mjs"
          },
          "summary": "Pure module"
        }
      ]
    }
  ],
  "task_evidence": [
    {
      "id": "E1",
      "responsibility_id": "R1-A",
      "session_id": "S1",
      "kind": "START",
      "source": {
        "kind": "GITHUB_COMMENT",
        "status": "CLAIMED",
        "locator": "https://github.com/reallaksh19/Common/issues/789#issuecomment-6062540809"
      },
      "commit_sha": null
    }
  ],
  "research_findings": [
    {
      "id": "F1",
      "statement": "Prior report has errors",
      "source": {
        "kind": "GITHUB_ISSUE",
        "status": "CLAIMED",
        "locator": "https://github.com/reallaksh19/Common/issues/788"
      },
      "verification": "UNVERIFIED"
    }
  ],
  "owner_decisions": []
};
}
const clone = x => JSON.parse(JSON.stringify(x));
test('valid graph with unknown original chat source never mints authority', () => {
  const report = validate(fixture());
  assert.equal(report.valid, true);
  assert.equal(report.no_authority_asserted, true);
  assert.deepEqual(traceClaim(fixture(),'AC1'), {
    claim_id:'AC1',owner_intent_ids:['OI-1'],responsibility_ids:['R1-A'],session_ids:['S1'],evidence_ids:['E1']
  });
});
test('canonical bytes independent of property ordering', () => {
  const first = fixture(), reverse=Object.fromEntries(Object.entries(first).reverse());
  assert.equal(canonicalJSON(first),canonicalJSON(reverse));
});
test('interrupted START-only session is structurally valid, not END', () => {
  const f=fixture();
  f.sessions[0].events.push({kind:'ERROR',source:{kind:'CHAT',status:'UNKNOWN',locator:null},summary:'transport unavailable'});
  assert.equal(validate(f).valid,true);
  assert.equal(f.task_evidence[0].kind,'START');
});
const negatives = ["foreign owner source","dangling claim","duplicate global ID","wrong evidence session","unsafe write surface","malformed SHA","pretend accepted","fake status","code END missing commit","dangling decision","cycle","session to other responsibility"];
const mutations = [
 x=>x.owner_intents[0].original_source={kind:'CHAT',status:'UNKNOWN',locator:'https://fake.example'},
 x=>x.responsibilities[0].claim_ids=['AC9'],
 x=>x.claims[0].id='OI-1',
 x=>x.task_evidence[0].session_id='S99',
 x=>x.responsibilities[0].write_surface=['../secrets'],
 x=>x.sessions[0].base_sha='abc',
 x=>x.claims[0].accepted=true,
 x=>x.owner_intents[0].original_source.status='VERIFIED',
 x=>x.task_evidence[0].kind='END',
 x=>x.owner_decisions.push({id:'D1',intent_id:'OI-1',finding_ids:['F999'],disposition:'ADOPT',source:{kind:'CHAT',status:'UNKNOWN',locator:null}}),
 x=>x.responsibilities[0].depends_on=['R1-A'],
 x=>{x.responsibilities.push({id:'R2',claim_ids:['AC1'],depends_on:[],scope:'Other',write_surface:['some/file']});x.task_evidence[0].responsibility_id='R2';}
];
negatives.forEach((name,i)=>test('reject '+name,()=>{
  const f=clone(fixture());mutations[i](f);
  assert.throws(()=>validate(f),ProvenanceError);
}));
test('unadopted research remains unadopted',()=>{
  const f=fixture();f.research_findings[0].verification='SUPPORTED_CLAIM';
  assert.equal(f.owner_decisions.length,0);
  assert.equal(validate(f).no_authority_asserted,true);
});

test('canonical JSON preserves special own keys without changing the prototype',()=>{
  const payload=JSON.parse('{"__proto__":{"x":1},"constructor":{"v":2}}');
  assert.equal(canonicalJSON(payload),'{"__proto__":{"x":1},"constructor":{"v":2}}');
});
test('deep dependency chain is bounded and non-recursive',()=>{
  const f=fixture();
  for(let i=0;i<5000;i++){
    f.responsibilities.push({
      id:'CHAIN-'+i,claim_ids:['AC1'],
      depends_on:i===0?['R1-A']:['CHAIN-'+(i-1)],
      scope:'Deep chain regression',write_surface:['skills/engineering-relay-v1/README.md']
    });
  }
  assert.equal(validate(f).valid,true);
  f.responsibilities[0].depends_on=['CHAIN-4999'];
  assert.throws(()=>validate(f),ProvenanceError);
});
test('unbounded event arrays are rejected before expensive validation',()=>{
  const f=fixture();
  const original=f.sessions[0].events[0];
  f.sessions[0].events=Array.from({length:10001},()=>original);
  assert.throws(()=>validate(f),ProvenanceError);
});

test('canonicalJSON rejects cyclic objects and arrays with controlled errors',()=>{
  const node={};node.self=node;
  assert.throws(()=>canonicalJSON(node),ProvenanceError);
  const array=[];array.push(array);
  assert.throws(()=>canonicalJSON(array),ProvenanceError);
});
test('canonicalJSON rejects deep nesting before JavaScript stack overflow',()=>{
  let nested={value:'leaf'};
  for(let i=0;i<300;i++)nested={child:nested};
  assert.throws(()=>canonicalJSON(nested),ProvenanceError);
});
test('canonicalJSON never evaluates getter-based agent input',()=>{
  let invoked=false;
  const payload={};
  Object.defineProperty(payload,'secret',{enumerable:true,get(){invoked=true;return 'leak';}});
  assert.throws(()=>canonicalJSON(payload),ProvenanceError);
  assert.equal(invoked,false);
});
test('canonicalJSON handles repeated non-cyclic objects but rejects sparse arrays',()=>{
  const ref={v:1};
  assert.equal(canonicalJSON({left:ref,right:ref}),'{"left":{"v":1},"right":{"v":1}}');
  const sparse=Array(2);sparse[0]='x';
  assert.throws(()=>canonicalJSON(sparse),ProvenanceError);
});

test('canonicalJSON rejects an array accessor without evaluating it',()=>{
  let invoked=false;
  const array=[1];
  Object.defineProperty(array,'0',{enumerable:true,configurable:true,get(){invoked=true;return 5;}});
  assert.throws(()=>canonicalJSON(array),ProvenanceError);
  assert.equal(invoked,false);
});
test('canonicalJSON rejects non-finite numeric facts',()=>{
  assert.throws(()=>canonicalJSON({progress:NaN}),ProvenanceError);
  assert.throws(()=>canonicalJSON({progress:Infinity}),ProvenanceError);
});

test('reverse trace from evidence preserves verbatim Owner source but does not grant authority',()=>{
  const t=traceEvidence(fixture(),'E1');
  assert.equal(t.evidence_kind,'START');
  assert.equal(t.evidence_commit_sha,null);
  assert.equal(t.session_id,'S1');
  assert.deepEqual(t.claim_ids,['AC1']);
  assert.equal(t.owner_intents[0].raw_text,'start now');
  assert.equal(t.owner_intents[0].original_source.status,'UNKNOWN');
  assert.equal(t.owner_intents[0].original_source.locator,null);
  assert.equal(t.owner_intents[0].first_durable_mirror,
    'https://github.com/reallaksh19/Common/issues/787');
  assert.equal(t.no_authority_asserted,true);
});
test('reverse module trace returns only evidence of sessions that touched the exact file',()=>{
  const file='skills/engineering-relay-v1/provenance-v1.mjs';
  const f=fixture();
  // S2 works on different module within R1-A, with separate evidence.
  f.sessions.push({...JSON.parse(JSON.stringify(f.sessions[0])),id:'S2',
    changed_files:['skills/engineering-relay-v1/another.mjs']});
  f.task_evidence.push({...JSON.parse(JSON.stringify(f.task_evidence[0])),
    id:'E2',session_id:'S2'});
  const trace=traceModule(f,file);
  assert.deepEqual(trace.session_ids,['S1']);
  assert.deepEqual(trace.evidence_ids,['E1']);
  assert.deepEqual(trace.responsibility_ids,['R1-A']);
  assert.deepEqual(trace.claim_ids,['AC1']);
  assert.equal(trace.owner_intents[0].raw_text,'start now');
  assert.equal(trace.no_authority_asserted,true);
  const other=traceModule(f,'skills/engineering-relay-v1/another.mjs');
  assert.deepEqual(other.evidence_ids,['E2']);
});
test('unmodified module is explicitly untraced, not fabricated as accepted',()=>{
  const v=traceModule(fixture(),'skills/engineering-relay-v1/unmodified.mjs');
  assert.deepEqual(v.session_ids,[]);
  assert.deepEqual(v.evidence_ids,[]);
  assert.deepEqual(v.owner_intents,[]);
});
test('reverse trace rejects unknown evidence id and unsafe paths',()=>{
  assert.throws(()=>traceEvidence(fixture(),'E999'),ProvenanceError);
  assert.throws(()=>traceModule(fixture(),'../secrets.txt'),ProvenanceError);
});
test('two acceptance claims with same Owner intent de-duplicate exact raw Owner record',()=>{
  const f=fixture();
  f.claims.push({id:'AC2',intent_ids:['OI-1'],criterion:'Trace exact source'});
  f.responsibilities[0].claim_ids.push('AC2');
  const v=traceEvidence(f,'E1');
  assert.deepEqual(v.claim_ids,['AC1','AC2']);
  assert.equal(v.owner_intents.length,1);
  assert.equal(v.owner_intents[0].raw_text,'start now');
});
test('cross-programme sessions do not inherit evidence from a sibling responsibility',()=>{
  const f=fixture();
  const other='skills/engineering-relay-v1/sibling.mjs';
  f.responsibilities.push({id:'R1-B',claim_ids:['AC1'],depends_on:[],
    scope:'Different owner',write_surface:[other]});
  f.sessions.push({...JSON.parse(JSON.stringify(f.sessions[0])),id:'S3',
    responsibility_id:'R1-B',changed_files:[other]});
  f.task_evidence.push({...JSON.parse(JSON.stringify(f.task_evidence[0])),id:'E3',
    session_id:'S3',responsibility_id:'R1-B'});
  assert.deepEqual(traceModule(f,other).evidence_ids,['E3']);
  assert.deepEqual(traceModule(f,'skills/engineering-relay-v1/provenance-v1.mjs').evidence_ids,['E1']);
});
