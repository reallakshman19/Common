from pathlib import Path
import hashlib,json
out=Path(__file__).resolve().parent
data=json.loads((out/'addendum-live-receipt.json').read_text())
assert data['commit']['sha']=='7d7d100c51a4ccebc2b9ba877ebb6e337e1a591a'
assert data['commit']['tree']['sha']=='812395ee191b653764a7c8577b1ef5ce9db8a3e2'
assert data['commit']['parents'][0]['sha']=='1f4fb608ccdbeb53adae230ac45877d94a16c113'
assert len(data['compare']['files'])==2
assert {x['filename'] for x in data['compare']['files']}=={'agents/PR191_workreport.md','prototypes/ciifr-map/index.html'}
for record in json.loads((out/'addendum-verification.json').read_text())['files']:
 b=(out/'final-source'/record['path']).read_bytes()
 assert hashlib.sha256(b).hexdigest()==record['sha256']
 assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==record['git_blob']
old=(out/'staged/XML_Compare_Utilities/prototypes/ciifr-map/index.html').read_bytes()
new=(out/'final-source/prototypes/ciifr-map/index.html').read_bytes()
assert old.replace(b'VNext integration pending',b'independent CIIFR_GEO tab in VNext')==new
original=(out/'REPORT.md').read_text()
assert hashlib.sha256(original.encode()).hexdigest()=='a9d0cfb38ea2087bb07e3eca78669f2ec3655d8917addb75f4c440bde4e6049c'
assert original in data['comment']['body']
print('AFFECTED_DELTA_PASS; exact single banner phrase; report custody retained; browser NOT_RUN')
