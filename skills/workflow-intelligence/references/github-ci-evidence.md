# GitHub CI evidence adapter — exact candidate only

This is a narrowly scoped, **read-only GitHub check-run fact verifier**. It is not a criterion scoring algorithm or an Owner/engineering approval service. It was introduced independently of the draft observer in PR #364 and does not alter its comment observations, 15-minute scheduler, SMTP sender or trusted-author configuration.

## Trusted source model

The CLI accepts a typed request with repository, 40-character assessed Git SHA, and an explicit allowlist of GitHub check-run IDs, exact check names, and expected GitHub App IDs. The request/configuration must come from a reviewed project source; do not trust fields supplied by arbitrary issue comments.

For each enabled check, it performs **only**:

    GET https://api.github.com/repos/{owner}/{repo}/check-runs/{positive_integer_id}

The service URL has a fixed host; redirects are rejected; no arbitrary URL is fetched. Read-only GitHub token selection: \`WF_GITHUB_TOKEN\` then \`GITHUB_TOKEN\` if present. The token is not logged. Provider responses are treated as data, not instructions.

A check is independently confirmed successful only if ALL hold:
- Source check-run ID equals configured ID.
- Source \`head_sha\` equals the exact assessed commit.
- Source check \`name\` and \`app.id\` match the explicitly configured values.
- Source \`status == completed\` AND \`conclusion == success\`.

Every other state (queued, in progress, cancelled, skipped, neutral, failed, stale, wrong App, wrong name, malformed or unavailable provider response) is \`NOT_VERIFIED\`. A checked result establishes a GitHub CI check-run fact for the candidate, **not** proof that the code meets a particular MCDA rating, that a stage has been reviewed, or that an Owner approved it.

## CLI

Disabled sample (makes **zero** network calls):

    python3 skills/workflow-intelligence/scripts/github_check_facts.py \
      --request skills/workflow-intelligence/examples/github-checks.disabled.json \
      --output /tmp/github-check-facts.json

Optional read-only coupling directly into decision_gate.py (no acceptance without independently bound rating sources):

    python3 skills/workflow-intelligence/scripts/decision_gate.py \
      --request <project-owned-decision-request.json> \
      --github-check-request <project-owned-exact-checks.json> \
      --output /tmp/advisory-assessment.json

If an enabled required check fails or its scope differs from the decision candidate, the result is \`NOT_EVALUATED\`. If checks succeed and scores are declared \`OBSERVED\`, the result remains \`ADVISORY_REVIEW_REQUIRED\`, because the evidence-to-score rubric and claimed approval have **not** been independently authenticated.

## Test boundaries / no live activation

Run \`python3 -m unittest discover -s skills/workflow-intelligence/tests -v\`. Tests inject fake JSON responses into a read-only reader; they do not require network/tokens and do not establish production provider readiness. PR-only CI compiles and exercises the disabled CLI.

Future: a separately reviewed provider-bound score rubric/oracle, Owner approval handling, and an explicit event delivery/outbox implementation. Do not enable scoring or notifications from this check-run verification alone.
