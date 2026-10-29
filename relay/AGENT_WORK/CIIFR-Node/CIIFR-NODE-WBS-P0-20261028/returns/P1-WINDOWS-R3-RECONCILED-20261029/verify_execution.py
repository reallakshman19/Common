import hashlib
import json
from pathlib import Path

root = Path(__file__).parent
payload = root / 'received/payload'
report = json.loads((payload / 'browser_qualification_report.json').read_text())
oracle = json.loads((payload / 'physical-oracle.json').read_text())
source = (payload / 'fixtures/SYNTH_V14_SOURCE.cii').read_bytes()
assert hashlib.sha256(source).hexdigest() == oracle['sha256']
lines = source.splitlines(keepends=True)
starts = []
offset = 0
for line in lines:
    starts.append(offset)
    offset += len(line)
first = next(i for i, line in enumerate(lines) if line.rstrip(b'\r\n') == b'#$ ELEMENTS') + 1
physical = []
for ordinal in (1, 2):
    fields = []
    for name, card, a, b in [('TEMPERATURE_1_STORED', 1, 41, 54), ('PRESSURE_1_STORED', 3, 2, 15), ('FLUID_DENSITY_STORED', 5, 15, 28)]:
        i = first + (ordinal-1)*15 + card
        lexeme = lines[i][a:b].decode('ascii').strip()
        fields.append(dict(identity=name, lexeme=lexeme, byteStart=starts[i]+a, byteEnd=starts[i]+b))
    assert fields == oracle['elements'][ordinal-1]['fields']
    physical.append([dict(f, storedNumber=float(f['lexeme'])) for f in fields])

assert report['candidate'] == 'd3fbd4041ef4434b4cf5b3c22459f06167be2729'
assert report['runnerRevision'] == 'R3 exact fields and ownership'
assert report['platform'] == 'win32'
assert len(report['runs']) == 2
expected_browsers = {'Microsoft Edge':'Edg/156.0.4314.42','Google Chrome':'Chrome/156.0.8078.48'}
observations = []
for run in report['runs']:
    assert run['productVersion'] == expected_browsers[run['browser']]
    assert len(run['servedSourceVerification']) == 13
    assert all(x['match'] and x['gitBlob'] == x['treeBlob'] for x in run['servedSourceVerification'])
    c = run['cases']
    assert len(c) == 6 and all(x['status'] == 'PASS' for x in c.values())
    assert c['case1_normal_demo']['proposalRows'] == 2
    assert c['case1_normal_demo']['exportEnabled'] is True
    assert c['case1_normal_demo']['target1Hash'] == '4bf7f868eda840cb45af6febfc2174a7ddfc2c21fb921be3cf411d3122bd7591'
    isolated = c['case2_property_isolation']
    assert isolated['normalStatePreserved'] and isolated['nodalStatePreserved'] and isolated['normalDecisionsMatchedCount'] == 2
    delay = c['case3_invalidation_pending_csv']
    assert all(delay[x] is True for x in ['preAppliedStateVerified','revokedOnRuleEdit','delayPendingPreconditionVerified','revokedWhilePending','clearWhilePendingSafe','eligibilityRestored'])
    process = c['case4_process_and_attachments']
    for index, key in enumerate(['forward400_500_fields','forward500_600_fields']):
        actual = process[key]
        assert actual['rawFields'] == physical[index]
        assert [actual['t1'], actual['p1'], actual['density']] == [f['storedNumber'] for f in physical[index]]
        assert actual['qual'] == 'HOLD'
    assert process['reverseOrientationRejected'] and process['node500AttachmentsVerified']
    expected_rows = {row[0].lower():row for row in oracle['node']['rows'] if row[0] != 'ELEMENT'}
    assert process['node500AttachmentRows'] == expected_rows
    challenges = c['case5_negative_zero_dormant_challenges']
    assert all(challenges['uiSearchValidation'].values()) and all(challenges['caiFileIntakeParsing'].values()) and challenges['noApplyOrExportInProperty']
    integrity = c['case6_integrity_immutability']
    assert integrity['pageErrorsCount'] == integrity['consoleErrorsCount'] == integrity['externalRequestsCount'] == 0
    assert integrity['fixturesUnchanged'] is True
    observations.append(dict(browser=run['browser'], version=run['productVersion'], cases=6, status='VERIFIED_REPORTED_EXECUTION', exactPhysicalFields=True, attachmentOwners=True, pageErrors=0, consoleErrors=0, externalPageRequests=0))

summaries = []
for name, expected in [('required-three.tap',(17,17,0)),('repair.tap',(13,13,0)),('geometry.tap',(9,9,0)),('guard-tests.tap',(23,23,0)),('vnext-all-complete.tap',(124,123,1))]:
    data = (payload / 'evidence' / name).read_bytes()
    text = data.decode('utf-16') if data.startswith(b'\xff\xfe') else data.decode('utf-8-sig')
    values = {key:int(next(line for line in text.splitlines() if line.startswith('# '+key+' ')).split()[-1]) for key in ['tests','pass','fail']}
    assert (values['tests'],values['pass'],values['fail']) == expected
    summaries.append(dict(path=name, **values, status='FAIL' if values['fail'] else 'PASS'))

result = dict(scope='Receiver reconciliation of exact committed executor evidence; no receiver Windows/browser execution and no Owner engineering acceptance', candidate=report['candidate'], sourcePhysicalOracle='Independent raw-byte recheck imports no product reader', browsers=observations, nativeSummaries=summaries, disposition='BOUNDED_WINDOWS_PUBLIC_FIXTURE_EVIDENCE_VERIFIED', original='NOT_RECEIVED / NOT_RUN')
(root / 'EXECUTION_COMPARISON.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
