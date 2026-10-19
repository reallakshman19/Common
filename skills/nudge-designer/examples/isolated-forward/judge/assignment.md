# A-ASSESS revision 1 — local assessment brief

Purpose: assess the two generated prompts against BP-1, keeping content coverage separate from provenance, wider generator reliability and learner understanding. This is the T-ASSESS continuation of MAP-BP1-PILOT revision 1. It has no tracker alias; do not reuse MOVE-31.

One deliverable: a concise assessment.md and calculations.json within this judge/ directory. Only task inputs are this brief, ../judge-issued-inputs.sha256.json, and the four files in judge/inputs/: problems.md, blueprint.md, reference.md and setup.md. Check the listed file-byte digests against that manifest. Do not read the original generated solutions/report, Oracle records, other outputs, examples, parent check results or skill libraries. Standard local libraries are allowed. Isolation is an instruction boundary on shared storage.

Method: read the generated prompt blocks and BP-1. Independently derive signed net force and acceleration for F from its givens; derive U conversion and explanatory relation. Use Python -B with exact arithmetic where feasible, and record inputs/method/results. Assess each BP-1 required part as MET/NOT_MET/UNKNOWN with a prompt/source witness; distinguish demand coverage from numerical correctness. Compare the generated setup to the supplied reference for the claimed relationship, retaining what the setup can and cannot establish. No producer verdict is an oracle.

For part roll-up, all MET is FULFILLED; any UNKNOWN is UNKNOWN retaining known misses; otherwise some MET is PARTIAL and none MET is NOT_FULFILLED. Include a meaningful contrast or missing-part check so a correct final number alone cannot establish all demands. State a source-bound conclusion for these artifacts, not an unobserved learner or a general model/skill effect.

Preserve inputs and original artifacts. Only new judge outputs are allowed; no external action, product changes, delegation, tracker mutation or parent acceptance. Disclose relevant prior exposure and shared assumptions; a different role or fresh conversation is not formal qualification or fully independent evidence. If a file/tool/premise differs, report the affected action, observed restriction and useful remaining work.

Return the two file locators and actual file-byte hashes, coverage/witnesses, computations and limits. If no substantive defect is found, a justified empty defect set is valid; do not invent a weakness quota. Parent/Oracle will reconcile the whole pilot after your bounded assessment.
