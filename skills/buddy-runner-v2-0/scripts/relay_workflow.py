"""Task-scoped relay continuation, with programmatic host invocation only."""
from relay_contract import validate_request, validate_reconstruction, profile_status
from relay_evidence import digest, verify_event, verify_prior
from relay_progress import carry_forward, progress_report
from copy import deepcopy

PROTOCOL_COMMIT = "54c0f172e0ec017e338e9cc3596348a23abc1bf0"
PROTOCOL_REF = ("https://github.com/reallakshman19/Common/blob/" + PROTOCOL_COMMIT
                + "/skills/engineering-pr-delivery-v3.6/SKILL.md")


def _direction(case, record=None, *, approval=None, task=None, reader=None):
    source_reader, cached = reader, {}
    def read_once(ref):
        if ref not in cached:
            cached[ref] = deepcopy(source_reader(ref))
        return cached[ref]
    reader = read_once if callable(source_reader) else None
    report = {
        "id": case["id"], "mode": case["mode"], "continuation": case["continuation"],
        "state": "PROMPT_PREPARED", "next": "INDEPENDENT_RECONSTRUCTION",
        "semantic_assessment": "NOT_MACHINE_VERIFIED", "agent_invoked": False,
        "workflow_executed": False, "coding_authorized": False,
        "task_prompt": None, "protocol": PROTOCOL_REF,
        "profile": profile_status(case["profile"]),
    }
    if case["phase"] == "1a":
        report.update(next="G2_INDEPENDENT_RECONSTRUCTION", execution="HOLD")
        return report
    if record is None:
        return report
    validate_reconstruction(case, record)
    report["reconstruction_digest"] = digest(record)
    if report["profile"] != "CONFIGURATION_OBSERVED":
        report.update(state="PROFILE_UNQUALIFIED",
                      next="RETAIN_INVESTIGATION_CONFIGURE_PROFILE")
        return report
    if case["phase"] == "1b":
        report.update(state="RECONSTRUCTION_RECORDED", next="G1_RECONCILE_ONCE")
        return report
    if case["phase"] == "2" and not verify_prior(case, record.get("prior_1b"), reader):
        report.update(state="PRIOR_1B_UNVERIFIED", next="VERIFY_EXACT_1B_ONCE")
        return report
    if case["phase"] == "2":
        report["prior_1b_grade"] = ("SUPPLIED_UNVERIFIED" if "body_text" in record["prior_1b"]
                                    else "HOST_READBACK_REPORTED")
    report.update(state="DIRECTION_RECORDED", next="ENTER_PINNED_CODING_PROTOCOL")
    if case["continuation"] == "AWAIT_OWNER_TASK":
        if approval is None:
            report.update(state="AWAITING_RECONSTRUCTION_APPROVAL",
                          next="AWAIT_OWNER_RECONSTRUCTION_DECISION")
        elif not verify_event(case, approval, digest(record), reader):
            report.update(state="OWNER_APPROVAL_UNVERIFIED",
                          next="VERIFY_OWNER_RECONSTRUCTION_DECISION")
        elif task is None:
            report.update(state="ONBOARDED_AWAITING_TASK", next="AWAIT_OWNER_TASK")
        elif not verify_event(case, task, digest(record), reader, kind="TASK_PROMPT"):
            report.update(state="OWNER_TASK_UNVERIFIED", next="VERIFY_OWNER_TASK")
        else:
            report["task_prompt"] = reader(task["ref"])["body"]
    elif next(choice for choice in record["choices"]
              if choice["id"] == record["chosen"])["decision"] == "OWNER_DECISION_REQUIRED":
        report.update(state="OWNER_DIRECTION_DECISION_REQUIRED",
                      next="REQUEST_OWNER_DIRECTION_DECISION")
    return report


def assess(case, record=None, *, approval=None, task=None, reader=None):
    case = validate_request(case)
    report = _direction(case, record, approval=approval, task=task, reader=reader)
    report["reconstruction_status"] = ("STRUCTURALLY_RECORDED" if
        "reconstruction_digest" in report else "NOT_SUPPLIED")
    report["continuation_evidence"] = progress_report(
        case.get("progress"), owner_wait=report["next"] in {
            "AWAIT_OWNER_TASK", "AWAIT_OWNER_RECONSTRUCTION_DECISION"},
        coding_eligible=report["next"] == "ENTER_PINNED_CODING_PROTOCOL")
    dispositions = record.get("dispositions", {}) if isinstance(record, dict) else {}
    report["carry_forward"] = carry_forward(case.get("known_items", []), dispositions)
    return report


def invoke(report, assignment, *, authorize=None, executor=None, receipts=()):
    result = dict(report, state="CODING_ASSIGNMENT_PREPARED",
                  agent_invoked=False, workflow_executed=False)
    if report.get("next") != "ENTER_PINNED_CODING_PROTOCOL":
        return dict(report)
    payload = dict(assignment, protocol=PROTOCOL_REF,
                   takeover_id=report["id"],
                   reconstruction_digest=report["reconstruction_digest"])
    key = digest(payload)
    result["target"] = key
    for receipt in receipts:
        if receipt.get("target") == key:
            return dict(result, state="VERIFY_EXISTING_INVOCATION",
                        response_ref=receipt.get("response_ref"), next="RECONCILE_HOST_STATE")
    if not callable(authorize) or not callable(executor):
        return result
    if authorize(payload) is not True:
        return dict(result, state="SCOPE_NOT_AUTHORIZED")
    try:
        receipt = executor(payload)
    except Exception as error:
        return dict(result, state="INVOCATION_UNCONFIRMED",
                    error_type=type(error).__name__, next="RECONCILE_HOST_STATE")
    if not isinstance(receipt, dict) or not isinstance(receipt.get("ref"), str) or not receipt["ref"].strip():
        return dict(result, state="INVOCATION_UNCONFIRMED", next="RECONCILE_HOST_STATE")
    return dict(result, state="HOST_INVOCATION_REPORTED", agent_invoked=True,
                response_ref=receipt["ref"], receipt_grade="HOST_REPORTED_NOT_PRODUCT_PROOF")
