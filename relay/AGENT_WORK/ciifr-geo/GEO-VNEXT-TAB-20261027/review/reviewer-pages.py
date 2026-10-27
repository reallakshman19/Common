from pathlib import Path
import subprocess,re,json,hashlib
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from threading import Thread
from urllib.request import urlopen
from urllib.parse import urljoin,urlparse
OUT=Path(__file__).resolve().parent;ROOT=OUT.parent/'geo-vnext-tab-20261027'
STAGE=OUT/'staged'/'XML_Compare_Utilities';STAGE.mkdir(parents=True,exist_ok=True)
workflow=(ROOT/'.github/workflows/deploy.yml').read_text();excludes=re.findall(r"--exclude='([^']+)'",workflow)
subprocess.run(['rsync','-a',*['--exclude='+x for x in excludes],str(ROOT)+'/',str(STAGE)+'/'],check=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(STAGE.parent)));Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/XML_Compare_Utilities/'
try:
 def fetch(url):
  with urlopen(url,timeout=5) as response:
   assert response.status==200;return response.read(),response.headers['Content-Type']
 outer=(STAGE/'tabs/cii-workspace/cii-workspace-find-replace-ui.js').read_text();assert "'../../docs/cii-fnr-vnext.html'" in outer
 host=urljoin(base,'docs/cii-fnr-vnext.html');html=fetch(host)[0].decode();assert 'data-tab="CIIFR_GEO"' in html
 target=urljoin(host,'../prototypes/ciifr-map/index.html');geo=fetch(target)[0].decode()
 assert 'id="tab-A"' in geo and 'id="tab-B"' in geo and 'id="tab-C"' in geo
 imports=json.loads(re.search(r'<script type="importmap">(.*?)</script>',geo).group(1))['imports']
 assert imports['three']==imports['https://esm.sh/three@0.160.0/build/three.module.js']
 queue=[];visited={}
 for page,markup in [(host,html),(target,geo)]:queue.extend(urljoin(page,p) for p in re.findall(r'(?:src|href)=["\']([^"\']+\.(?:js|css))["\']',markup))
 queue.extend(urljoin(target,p) for p in imports.values())
 while queue:
  url=queue.pop()
  if url in visited:continue
  assert url.startswith(base),url
  data,mime=fetch(url);assert ('javascript' in mime if url.endswith('.js') else 'css' in mime),mime
  visited[url.removeprefix(base)]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
  text=data.decode()
  deps=re.findall(r"(?:from\s*|import\s*)['\"]([^'\"]+\.js)['\"]",text)
  deps+=re.findall(r"new URL\(\s*['\"]([^'\"]+\.js)['\"]\s*,\s*import.meta.url",text)
  queue.extend(urljoin(url,p) for p in deps)
 for required in ['prototypes/ciifr-map/resolution-worker.js','workbench3d/viewer/scene-derivation-worker.js','prototypes/ciifr-map/vendor/three-0.160.0/three.module.min.js','docs/tabs/cii-workspace/cii-fnr-vnext/ui/geo-tab.js']:assert required in visited,required
 manifest=json.loads((STAGE/'prototypes/ciifr-map/samples/manifest.json').read_text());samples={}
 for name,expected in manifest['files'].items():
  data=fetch(urljoin(target,'samples/'+name))[0];actual=hashlib.sha256(data).hexdigest();assert len(data)==expected['bytes'] and actual==expected['sha256'];samples[name]=actual
 try:fetch(urljoin(base,'docs/prototypes/ciifr-map/index.html'));raise AssertionError('wrong route unexpectedly succeeds')
 except Exception as error:
  assert getattr(error,'code',None)==404,str(error)
 result={'status':'PASS','observation':'STAGED_HTTP_NOT_BROWSER','prefix':'/XML_Compare_Utilities/','assets':visited,'samples':samples,'wrong_docs_route':404,'workers_and_importmap_vendor_present':True}
 (OUT/'reviewer-pages.json').write_text(json.dumps(result,indent=2)+'\n');print('REVIEWER_STAGED_HTTP_PASS',len(visited),'assets;2 workers;local importmap vendor;sample hashes;wrong route404;browser NOT_RUN')
finally:server.shutdown();server.server_close()
