"""Read the selected coding protocol from immutable Git objects; no provider writes."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from relay_workflow import PROTOCOL_COMMIT, PROTOCOL_REF

PREFIX = "skills/engineering-pr-delivery-v3.6/"
FILES = ("scripts/lifecycle_v36.py", "scripts/decompose_v36.py",
         "SKILL.md", "MODE_STANDALONE.md", "CODING_PRACTICES_ADDENDUM.md")

PROBE = """
import json, sys
sys.path.insert(0, sys.argv[1])
from lifecycle_v36 import load_label, require_explicit_lab
from decompose_v36 import load_plan, is_task_issue
label = load_label(sys.argv[2])
if label.get('mode') != 'standalone':
    raise ValueError('explicit standalone mode required')
plan = load_plan(sys.argv[3], label)
require_explicit_lab(label, plan['parent'], sys.argv[6] or None)
tasks = [t for t in plan['tasks'] if t['task_id'] == sys.argv[4]]
child = json.loads(sys.argv[5])
if len(tasks) != 1 or not is_task_issue(child, tasks[0], plan['parent']):
    raise ValueError('selected task must bind the real child')
number = child.get('number')
if type(number) is not int or number < 1:
    raise ValueError('positive child number required')
print(json.dumps({'parent': plan['parent'], 'task': tasks[0],
                  'child': plan['parent'].split('#')[0] + '#' + str(number),
                  'plan_version': plan['plan_version']}))
"""


def git_blob(checkout, path):
    result = subprocess.run(["git", "-C", str(checkout), "show",
                             PROTOCOL_COMMIT + ":" + PREFIX + path],
                            text=True, capture_output=True, check=False)
    if result.returncode:
        raise ValueError("pinned protocol Git objects unavailable: " + path)
    return result.stdout


def preflight(checkout, label, plan, task_id, child, *, lab=None):
    """Validate supplied local binding; host still verifies provider facts and permission."""
    documents = {name: git_blob(checkout, name) for name in FILES}
    with tempfile.TemporaryDirectory(prefix="br20-native-") as temporary:
        scripts = Path(temporary)
        for name in FILES[:2]:
            (scripts / Path(name).name).write_text(documents[name], encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-I", "-c", PROBE, str(scripts),
             str(Path(label).resolve()), str(Path(plan).resolve()), task_id,
             json.dumps(child), lab or ""], capture_output=True, text=True, check=False)
    if result.returncode:
        raise ValueError("native binding refused: " + result.stderr.splitlines()[-1])
    binding = json.loads(result.stdout)
    return dict(binding, protocol=PROTOCOL_REF, protocol_commit=PROTOCOL_COMMIT,
                loaded_from="PINNED_GIT_OBJECTS", binding_valid=True,
                coding_authorized=False, provider_verified=False,
                grade="LOCAL_NATIVE_VALIDATION_NOT_OWNER_APPROVAL",
                skill_text=documents["SKILL.md"],
                source_digests={name: hashlib.sha256(body.encode("utf-8")).hexdigest()
                                for name, body in documents.items()})
