# Prediction recorded before execution

The unchanged source checks only `request_revision == current_revision`. It does
not check `source_id`, and it labels every accepted payload with the selected
source. Therefore:

| Fresh-state order | Predicted intermediate results |
| --- | --- |
| A12, B12 | A12 is incorrectly published as source B; B12 then replaces it correctly. |
| B12, A12 | B12 publishes correctly; A12 then incorrectly replaces it while labeled source B. |
| B11, B12 | B11 is rejected because revision 11 is stale; B12 then publishes correctly. |

The required contrast is that both source and revision must match, while valid
B12 must still publish. These predictions concern only the supplied synthetic
function and inputs. Production behavior and integration are unknown.
