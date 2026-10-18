def receive(state, request_revision, payload):
    state["result"] = payload
    return state
