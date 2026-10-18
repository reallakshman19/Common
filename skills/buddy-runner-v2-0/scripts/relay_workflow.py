"""Fail-closed API scaffold; never invokes an agent."""
def assess(case, record, *, approval=None, task=None, reader=None):
    return {"state": "NOT_IMPLEMENTED", "next": "NOT_IMPLEMENTED",
            "semantic_assessment": "NOT_MACHINE_VERIFIED", "agent_invoked": False,
            "coding_authorized": False, "task_prompt": None}

def invoke(report, assignment, *, authorize=None, executor=None):
    return {"state": "CODING_ASSIGNMENT_PREPARED", "agent_invoked": False,
            "workflow_executed": False, "response_ref": None}

