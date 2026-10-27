from pathlib import Path
import json,hashlib
OUT=Path(__file__).resolve().parent
manifest=json.loads((OUT/'SOURCE_MANIFEST.json').read_text())
for record in manifest['files']:
 data=(OUT/'remote-source'/record['path']).read_bytes()
 blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 assert blob==record['gitBlob']
 assert len(data)==record['bytes']
 assert hashlib.sha256(data).hexdigest()==record['sha256']
print('FROZEN_REMOTE_SOURCE_PASS',len(manifest['files']))
for path in sorted(OUT.glob('file-verification-*.json')):
 assert all(row['local_remote_equal'] and row['manifest_match'] for row in json.loads(path.read_text()))
for path in sorted(OUT.glob('dependency-verification-*.json')):
 assert all(row['match'] for row in json.loads(path.read_text()))
assert all(row['match'] for row in json.loads((OUT/'staged-candidate-verification.json').read_text()))
print('CAPTURED_VERIFICATION_RECEIPTS_PASS; live-source equality was observed at original capture')
