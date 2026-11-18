"""Offline reference for tandem decisions, not an agent runner or authority mechanism."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Observation:
    mode: str = "PARALLEL"
    a_bytes_verified: bool = False
    a_ready: bool = False
    a_reconciled: bool = False
    a_retained: bool = False
    b_work_available: bool = False
    boundary_reached: bool = False
    budget_exhausted: bool = False
    done_list_supported: bool = False
    final_published: bool = False
    shared_writer_active: bool = False
    serial_custody_verified: bool = False


def decide(o: Observation) -> dict:
    """Describe B's next work and honest result; READY never grants permission.

    All inputs are observations within an existing authorized assignment.
    a_reconciled means actual A contribution was considered on final source,
    including explicitly rejected alternatives, not merely reading a report.
    a_retained records actual retained code or executable evidence.
    """
    if o.mode not in ("PARALLEL", "SERIAL"):
        raise ValueError("Unknown assigned mode")
    if o.a_reconciled and not o.a_bytes_verified:
        raise ValueError("Cannot reconcile unverified A bytes")
    if o.a_retained and not o.a_reconciled:
        raise ValueError("Cannot claim retained A contribution before reconciliation")
    if o.final_published:
        return {"action": "KEEP_FINAL", "isolated_work": False,
                "shared_write": False, "lineage": None, "outcome": None}
    result = {"isolated_work": True,
              "shared_write": (o.mode == "SERIAL" and o.serial_custody_verified
                               and o.a_bytes_verified and not o.shared_writer_active),
              "lineage": None, "outcome": None}
    if not o.b_work_available:
        return {**result, "action": "IMPLEMENT_B"}
    if o.a_bytes_verified and not o.a_reconciled and not o.budget_exhausted:
        return {**result, "action": "RECONCILE_AVAILABLE_A"}
    if not (o.boundary_reached or o.budget_exhausted):
        return {**result, "action": "CONTINUE_B"}
    lineage = ("SERIAL_FINAL" if o.mode == "SERIAL" else "FINAL_COMBINED") if o.a_retained else "FINAL_B_ONLY"
    return {**result, "action": "DELIVER_FINAL",
            "lineage": lineage,
            "outcome": "COMPLETE" if o.done_list_supported else "PARTIAL"}
