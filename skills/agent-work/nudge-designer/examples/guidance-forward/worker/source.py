def receive(state, source_id, request_revision, payload):
    if request_revision == state['current_revision']:
        state['result'] = {'source': state['selected_source'], 'payload': payload}
    return state
