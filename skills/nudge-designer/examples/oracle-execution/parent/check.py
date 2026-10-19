import hashlib
import importlib.util
import json
import sys
from pathlib import Path

candidate = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("candidate", candidate)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def same_scope():
    s=m.SearchSession(); old=s.begin("A","old"); new=s.begin("A","new")
    assert s.finish(new,["new", "ranked-first"]) is True
    before=s.snapshot()
    assert s.finish(old,["old"]) is False
    assert s.snapshot()==before
    assert s.fail(old,"old-error") is False
    assert s.snapshot()==before

def return_to_scope():
    s=m.SearchSession(); first=s.begin("A","one"); middle=s.begin("B","two"); last=s.begin("A","three")
    before=s.snapshot()
    assert s.finish(first,["stale-A"]) is False
    assert s.snapshot()==before
    assert s.fail(middle,"stale-B") is False
    assert s.snapshot()==before
    assert s.finish(last,["current-A"]) is True
    assert s.snapshot()["rows"]==["current-A"]

def cancelled():
    for failure in (False,True):
        s=m.SearchSession(); old=s.begin("A","one"); s.cancel(); before=s.snapshot()
        accepted=s.fail(old,"cancelled-error") if failure else s.finish(old,["cancelled"])
        assert accepted is False
        assert s.snapshot()==before
        assert s.snapshot()["rows"]==[] and not s.snapshot()["busy"] and s.snapshot()["error"] is None

def reuse():
    s=m.SearchSession(); old=s.begin("A","one");s.cancel();new=s.begin("A","two")
    before=s.snapshot();assert s.fail(old,"old") is False;assert s.snapshot()==before
    assert s.finish(new,["z", "a"]) is True
    assert s.snapshot()["rows"]==["z", "a"]
    third=s.begin("B","three");assert s.fail(third,"offline") is True
    assert s.snapshot()["error"]=="offline" and not s.snapshot()["busy"]
    fourth=s.begin("B","four");assert s.finish(fourth,["ok"]) is True
    assert s.snapshot()["error"] is None

results=[]
for f in (same_scope,return_to_scope,cancelled,reuse):
    try:f();results.append({"case":f.__name__,"result":"PASS"})
    except AssertionError:results.append({"case":f.__name__,"result":"FAIL"})
print(json.dumps({"candidate":str(candidate),"sha256":hashlib.sha256(candidate.read_bytes()).hexdigest(),"checks":results},indent=2))
sys.exit(1 if any(x["result"]!="PASS" for x in results) else 0)
