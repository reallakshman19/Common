from pathlib import Path
import shutil,subprocess,json
OUT=Path(__file__).resolve().parent
SRC=OUT.parent/'geo-vnext-tab-20261027'
BASE=OUT/'baseline-run'
(BASE/'tests/helpers').mkdir(parents=True,exist_ok=True)
(BASE/'docs').mkdir(exist_ok=True)
shutil.copytree(SRC/'tabs/cii-workspace/cii-fnr-vnext',BASE/'tabs/cii-workspace/cii-fnr-vnext',dirs_exist_ok=True)
shutil.copytree(SRC/'docs/tabs/cii-workspace/cii-fnr-vnext',BASE/'docs/tabs/cii-workspace/cii-fnr-vnext',dirs_exist_ok=True)
for p in ['tests/cii-fnr-vnext-branch-scope.test.mjs','tests/helpers/vnext-dom-env.mjs','docs/cii-fnr-vnext.html','package.json']:
 shutil.copyfile(SRC/p,BASE/p)
for mirror in ['', 'docs/']:
 shutil.copyfile(OUT/'base-source/app.js',BASE/(mirror+'tabs/cii-workspace/cii-fnr-vnext/ui/app.js'))
result=subprocess.run(['node','--test','tests/cii-fnr-vnext-branch-scope.test.mjs'],cwd=BASE,capture_output=True,text=True)
(OUT/'baseline-branch.log').write_text(result.stdout+result.stderr)
print('BASELINE_BRANCH_EXIT',result.returncode)
print('\n'.join((result.stdout+result.stderr).splitlines()[-30:]))
