def current_result(current_epoch, response_epoch, payload):
    return payload if current_epoch == response_epoch else None
