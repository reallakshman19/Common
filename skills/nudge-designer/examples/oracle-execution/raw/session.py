from copy import deepcopy


class SearchSession:
    def __init__(self):
        self._sequence = 0
        self._scope = None
        self._query = None
        self._busy = False
        self._rows = []
        self._error = None

    def begin(self, scope, query):
        self._sequence += 1
        self._scope = scope
        self._query = query
        self._busy = True
        self._rows = []
        self._error = None
        return {"scope": scope, "sequence": self._sequence}

    def finish(self, ticket, rows):
        if ticket["scope"] != self._scope:
            return False
        self._rows = deepcopy(rows)
        self._error = None
        self._busy = False
        return True

    def fail(self, ticket, message):
        if ticket["scope"] != self._scope:
            return False
        self._rows = []
        self._error = str(message)
        self._busy = False
        return True

    def cancel(self):
        self._rows = []
        self._error = None
        self._busy = False

    def snapshot(self):
        return deepcopy({"scope": self._scope, "query": self._query,
                         "busy": self._busy, "rows": self._rows,
                         "error": self._error})
