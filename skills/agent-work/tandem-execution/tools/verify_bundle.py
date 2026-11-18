#!/usr/bin/env python3
"""Offline verification of downloaded Drive bytes; no permission, upload or dispatch claims."""
import argparse, hashlib, json, re, stat, zipfile
from pathlib import Path, PurePosixPath


def digest(data): return hashlib.sha256(data).hexdigest()


def verify(path, marker=None):
    path=Path(path)
    if marker is not None:
        if marker.get('sha256') != digest(path.read_bytes()) or marker.get('bytes') != path.stat().st_size:
            raise ValueError('Outer bundle digest or size mismatch')
        if not marker.get('drive_file_id') or not marker.get('candidate'):
            raise ValueError('Marker missing actual file or candidate identity')
    with zipfile.ZipFile(path) as z:
        entries=z.infolist(); names=[i.filename for i in entries]
        if len(names)!=len(set(names)): raise ValueError('Duplicate archive paths')
        for info in entries:
            n=info.filename; p=PurePosixPath(n)
            if not n or p.is_absolute() or '..' in p.parts or '\\' in n or ':' in n or '\x00' in n or stat.S_ISLNK(info.external_attr>>16):
                raise ValueError('Unsafe archive path: '+n)
        files={i.filename for i in entries if not i.is_dir()}
        if 'SHA256SUMS.txt' not in files: raise ValueError('No payload checksum manifest; recover/verify available native sources separately')
        checks={}
        for line in z.read('SHA256SUMS.txt').decode('utf-8').splitlines():
            if not line.strip(): continue
            m=re.fullmatch(r'([0-9a-f]{64})  (.+)',line)
            if not m or m[2] in checks: raise ValueError('Invalid/duplicate manifest entry')
            checks[m[2]]=m[1]
        if set(checks)!=files-{'SHA256SUMS.txt'}: raise ValueError('Manifest coverage mismatch')
        for name,sha in checks.items():
            if digest(z.read(name))!=sha: raise ValueError('Payload digest mismatch: '+name)
        return {'archive':path.name,'sha256':digest(path.read_bytes()),'verified_payload_files':len(checks),'result':'BYTE_VERIFIED','limit':'No Drive access, writer permission, execution or product correctness inferred.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('zip',type=Path);p.add_argument('--marker',type=Path);a=p.parse_args();print(json.dumps(verify(a.zip,json.loads(a.marker.read_text()) if a.marker else None),indent=2))
