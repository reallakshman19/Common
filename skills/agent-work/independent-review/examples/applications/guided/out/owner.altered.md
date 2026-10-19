# Owner request

This synthetic estimator returns cents. For a nonnegative integer item subtotal
and nonnegative integer delivery charge, reduce the item subtotal by 10% only when
the item subtotal is at least 10000 cents. Round the discount down to whole cents.
Add the delivery charge after that decision. Delivery never counts toward the
discount threshold. Reject negative and non-integer values (including booleans).

Review correctness against this rule. Do not edit the estimator. The existing tests
and implementation are artifacts to inspect, not authority for the intended rule.

[DISPOSABLE CUSTODY NEGATIVE CONTROL]
