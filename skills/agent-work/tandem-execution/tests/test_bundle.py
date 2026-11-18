import importlib.util, pathlib, tempfile, unittest, zipfile, warnings
P=pathlib.Path(__file__).resolve().parents[1]/'tools'/'verify_bundle.py'
s=importlib.util.spec_from_file_location('verify_bundle',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Bundle(unittest.TestCase):
    def setUp(self): self.tmp=tempfile.TemporaryDirectory();self.path=pathlib.Path(self.tmp.name)/'a.zip'
    def tearDown(self): self.tmp.cleanup()
    def make(self, content=None, manifest=None, extra=None):
        content=content or {'src/a.py':b'print(1)','test.py':b'assert True'}
        with zipfile.ZipFile(self.path,'w') as z:
            for n,b in content.items():z.writestr(n,b)
            if manifest is not False:
                z.writestr('SHA256SUMS.txt',manifest if manifest is not None else ''.join(f'{m.digest(b)}  {n}\n' for n,b in content.items()))
            if extra:
                for n,b in extra: z.writestr(n,b)
    def test_verified(self): self.make();self.assertEqual(m.verify(self.path)['verified_payload_files'],2)
    def test_missing_readme_not_blocker(self): self.make({'src/a.py':b'a'});self.assertEqual(m.verify(self.path)['result'],'BYTE_VERIFIED')
    def test_missing_manifest_reports_recovery(self):
        self.make(manifest=False)
        with self.assertRaisesRegex(ValueError,'recover/verify'):m.verify(self.path)
    def test_wrong_digest(self):
        self.make({'src/a.py':b'a'},'0'*64+'  src/a.py\n')
        with self.assertRaisesRegex(ValueError,'Payload digest mismatch'):m.verify(self.path)
    def test_extra_file(self):
        self.make(extra=[('extra.py',b'x')]);self.assertRaisesRegex(ValueError,'coverage',m.verify,self.path)
    def test_traversal(self):
        self.make({'../escape':b'a'});self.assertRaisesRegex(ValueError,'Unsafe',m.verify,self.path)
    def test_backslash(self):
        self.make({'..\\escape':b'a'});self.assertRaisesRegex(ValueError,'Unsafe',m.verify,self.path)
    def test_duplicate(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore');self.make(extra=[('test.py',b'x')])
        self.assertRaisesRegex(ValueError,'Duplicate',m.verify,self.path)
    def test_marker_matches(self):
        self.make();marker={'sha256':m.digest(self.path.read_bytes()),'bytes':self.path.stat().st_size,'drive_file_id':'synthetic-fixture-id','candidate':'c1'}
        self.assertEqual(m.verify(self.path,marker)['result'],'BYTE_VERIFIED')
    def test_wrong_marker(self):
        self.make();self.assertRaisesRegex(ValueError,'Outer bundle',m.verify,self.path,{'sha256':'0'*64,'bytes':0})
    def test_blank_identity(self):
        self.make();marker={'sha256':m.digest(self.path.read_bytes()),'bytes':self.path.stat().st_size,'candidate':'c1'}
        self.assertRaisesRegex(ValueError,'identity',m.verify,self.path,marker)
