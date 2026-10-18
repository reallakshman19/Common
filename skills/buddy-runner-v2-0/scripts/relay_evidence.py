"""Read-only host evidence boundary. Host classification is a trust boundary."""
import hashlib
import json
import re
from urllib.parse import unquote, urlsplit


def digest(value):
    body = value if isinstance(value, str) else json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


def guard_url(case, ref):
    if not isinstance(ref, str):
        raise ValueError("source reference must be text")
    url = urlsplit(ref)
    if url.scheme != "https" or url.username or url.password or url.port:
        raise ValueError("source URL must be credential-free HTTPS")
    path = unquote(url.path)
    if "%" in path or "\\" in path or any(x in {".", ".."} for x in path.split("/")):
        raise ValueError("ambiguous source path")
    parts = path.strip("/").split("/")
    if url.netloc == "github.com" and len(parts) >= 4:
        owner, repo, resource = parts[:3]
    elif url.netloc == "api.github.com" and len(parts) >= 5 and parts[0] == "repos":
        owner, repo, resource = parts[1:4]
    else:
        raise ValueError("unsupported source host/path")
    if repo.casefold() == "coordinatorlandingpage":
        raise ValueError("standalone isolation forbids coordination repository reads")
    if resource not in {"issues", "pull", "pulls", "blob", "tree", "commits", "contents", "git"}:
        raise ValueError("unsupported repository resource")
    if (owner + "/" + repo).casefold() != case["repository"].casefold():
        raise ValueError("source outside selected project repository")
    return ref


def collect(case, reader):
    refs = list(dict.fromkeys(case["assignment"]["inputs"]))
    if len(refs) > 30:
        raise ValueError("source batch exceeds 30 explicit references")
    for ref in refs:
        guard_url(case, ref)
    results = []
    for ref in refs:
        item = reader(ref)
        if not isinstance(item, dict) or not isinstance(item.get("body"), str):
            raise ValueError("host reader must return exact text body")
        if item.get("ref", ref) != ref:
            raise ValueError("host returned a different source")
        results.append({"ref": ref, "digest": digest(item["body"]),
                        "revision": item.get("revision", "UNKNOWN"),
                        "body": item["body"], "grade": "HOST_FETCHED_NOT_OWNER_APPROVAL",
                        "permission_to_write": False})
    return results


def verify_event(case, event, subject, reader, *, kind="RECONSTRUCTION_APPROVAL"):
    if not isinstance(event, dict) or not callable(reader) or event.get("subject") != subject:
        return False
    try:
        ref = guard_url(case, event["ref"])
        base, _, fragment = ref.partition("#")
        if base != case["issue"] or (fragment and not re.fullmatch(r"issuecomment-[1-9][0-9]*", fragment)):
            return False
        item = reader(ref)
        return bool(
            isinstance(item, dict) and isinstance(item.get("body"), str)
            and item.get("ref", ref) == ref
            and digest(item["body"]) == event.get("digest")
            and item.get("author") == case["owner"]
            and item.get("owner_instruction") is True
            and kind in item.get("instruction_kinds", [])
        )
    except (ValueError, KeyError, TypeError):
        return False


def verify_prior(case, event, reader):
    if not isinstance(event, dict):
        return False
    try:
        if "body_text" in event:
            body = event["body_text"]
            if not isinstance(event.get("supplied_ref"), str) or not event["supplied_ref"].strip():
                return False
        elif callable(reader):
            guard_url(case, event["ref"])
            if event["ref"].partition("#")[0] != case["issue"]:
                return False
            item = reader(event["ref"])
            if not isinstance(item, dict) or item.get("actor") != case["incoming"]:
                return False
            body = item["body"]
        else:
            return False
        if not isinstance(body, str) or digest(body) != event["digest"]:
            return False
        from relay_contract import validate_reconstruction
        prior = json.loads(body)
        incoming_case = dict(case, actor=case["incoming"], phase="1b")
        validate_reconstruction(incoming_case, prior)
        return True
    except (ValueError, KeyError, TypeError):
        return False
