# Integrity / Anti-Gaming Rules

The following are prohibited unless an independently justified engineering requirement explicitly changes the acceptance basis:

- weakening tolerances because a test fails;
- replacing expected values with current implementation output;
- deleting/avoiding difficult benchmarks;
- hard-coding fixture IDs or expected answers into production;
- silencing fail-closed paths;
- changing both implementation and oracle so they agree;
- calling an implementation-coupled calculation independent;
- claiming `NOT_RUN` as `PASS`;
- classifying infrastructure no-start as product PASS/FAIL without evidence;
- broad simultaneous mechanics changes when single-factor isolation is possible;
- concealing unexplained changed files;
- promoting candidate/reference data to engineering authority without qualification.

A safety-critical false claim or fabricated repository/evidence assertion can terminate implementation authority immediately.
