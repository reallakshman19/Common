#!/usr/bin/env python3
"""Reviewer-only original-byte HTTP invariant for the app's actual sample URLs."""
import argparse
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
from threading import Thread
from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import urlopen

EXPECTED = {
    'S1-F05.xml': '1154c980d08344b1f803cda3bd9884b169753148b150641a745c9bfcb15de995',
    'S1-R4.xml': 'a332dd7b2551faae51de3c016941762c3b795cdf19073b373817354e309526e6',
}

def main():
    args = argparse.ArgumentParser()
    args.add_argument('app', type=Path)
    args.add_argument('artifact', type=Path)
    opt = args.parse_args()
    # Read the actual literal URL prefix used by the shipped sample-button code.
    prefixes = re.findall(r"new URL\('(\./[^']*/)'\s*\+\s*name\s*,\s*import\.meta\.url\)", opt.app.read_text())
    assert len(prefixes) == 1, 'Expected exactly one actual bundled-sample URL construction'
    handler = partial(SimpleHTTPRequestHandler, directory=str(opt.artifact))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    results = []
    try:
        app_url = f'http://127.0.0.1:{server.server_port}/prototypes/ciifr-map/app.js'
        for name, expected in EXPECTED.items():
            url = urljoin(app_url, prefixes[0] + name)
            try:
                with urlopen(url, timeout=10) as response:
                    body = response.read()
                    result = {'file': name, 'url': url, 'status': response.status,
                              'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()}
            except HTTPError as error:
                result = {'file': name, 'url': url, 'status': error.code}
            results.append(result)
        print(json.dumps({'runtime_prefix': prefixes[0], 'results': results}, indent=2))
        for result in results:
            assert result['status'] == 200, 'Runtime sample missing from Pages artifact: ' + result['file']
            assert result['sha256'] == EXPECTED[result['file']], 'Runtime sample original bytes changed'
        print('Original-hash actual sample URL / staged HTTP invariant PASS')
    finally:
        server.shutdown()
        server.server_close()

if __name__ == '__main__':
    main()
