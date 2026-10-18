"""Fail-closed API scaffold; implementation follows behavioral RED."""
def validate_request(case):
    return dict(case)

def validate_reconstruction(case, record):
    return None

def profile_status(profile):
    return "UNVERIFIED"

