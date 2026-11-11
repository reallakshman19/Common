# CI Investigation Report: Hosted Run 38267158083

> **Investigation Target:** Hosted GitHub Actions run for PR #355  
> **Run ID:** [38267158083](https://github.com/reallakshman19/Common/actions/runs/38267158083)  
> **Commit SHA:** `ef2bbf7b0594461bb9457e8879aafed96f58c6a8`  
> **Branch:** `proposal/v36-stress-plan-01`  
> **Pull Request:** [reallakshman19/Common#355](https://github.com/reallakshman19/Common/pull/355)  
> **Date:** October 12, 2026  

---

## 1. Summary of Results Across PR Workflows

| Workflow / Job | Status | Duration | Assessment |
| :--- | :---: | :---: | :--- |
| `engineering-pr-delivery-v3.2` | **SUCCESS** | 1m 35s | Passing |
| `DELP-projection` | **SUCCESS** | 1m 20s | Passing |
| `Local-v1.1-integration` | **SUCCESS** | 1m 25s | Passing |
| `engineering-pr-delivery-v3.1` (`validate-v3-1-foundation`) | **FAILED** | 1m 23s | **7 Failures (1 failure, 6 errors)** |

---

## 2. Root Cause Analysis of `validate-v3-1-foundation` Failure

### 2.1 Why the Workflow Ran
The job `.github/workflows/engineering-pr-delivery-v3.1.yml` contains a path relevance check intended to evaluate whether a PR affects legacy v3.1 scope:

```bash
relevant=false
while IFS= read -r path; do
  case "$path" in
    skills/engineering-pr-delivery-v3.1/*|skills/two-pass-prompt-generator/*|relay/*|.github/workflows/engineering-pr-delivery-v3.1.yml)
      relevant=true
      break
      ;;
  esac
done < "$changed_paths"
```

Because PR #355 introduces proposal sticky label `relay/AIM/V36-STRESS.yaml`, it matched the glob `relay/*`. The workflow concluded `relevant=true` and executed the legacy test suite `skills/engineering-pr-delivery-v3.1/tests/test_ci_terminal_checks.py`.

### 2.2 Detailed Breakdown of the Seven Failures

The test suite executed 274 tests, producing **failures=1, errors=6** in `skills/engineering-pr-delivery-v3.1/tests/test_ci_terminal_checks.py`:

```python
WORKFLOWS = {
    "engineering-pr-delivery-v2.5.yml": (
        "skills/engineering-pr-delivery-v2.5/*",
        "skills/three-pass-prompt-generator/*",
    ),
    "engineering-pr-delivery-v3.yml": (
        V3_SKILL_PATTERN,
    ),
    "engineering-pr-delivery-v3.1.yml": (
        "skills/engineering-pr-delivery-v3.1/*",
        "skills/two-pass-prompt-generator/*",
        "relay/*",
    ),
}
```

1. **Error 1 (`test_relay_workflows_remain_valid_yaml` - `v2.5`):**
   `FileNotFoundError: [Errno 2] No such file or directory: '.github/workflows/engineering-pr-delivery-v2.5.yml'`
   *Root Cause:* The legacy `v2.5` workflow was retired/deleted in earlier repository refactorings, but the v3.1 test table still mandates its presence on disk.
2. **Error 2 (`test_relay_workflows_remain_valid_yaml` - `v3`):**
   `FileNotFoundError: [Errno 2] No such file or directory: '.github/workflows/engineering-pr-delivery-v3.yml'`
   *Root Cause:* The legacy `v3` workflow was retired/deleted, but the v3.1 test table still expects it.
3. **Error 3 (`test_relay_required_checks_always_instantiate_on_pull_requests` - `v2.5`):**
   `FileNotFoundError: [Errno 2] No such file or directory: '.github/workflows/engineering-pr-delivery-v2.5.yml'`
4. **Error 4 (`test_relay_required_checks_always_instantiate_on_pull_requests` - `v3`):**
   `FileNotFoundError: [Errno 2] No such file or directory: '.github/workflows/engineering-pr-delivery-v3.yml'`
5. **Failure 5 (`test_relay_required_checks_always_instantiate_on_pull_requests` - `v3.1`):**
   `AssertionError: 'git diff --name-only --no-renames "$BASE_SHA" "$HEAD_SHA"' not found in ...`
   *Root Cause:* Commit `a123b2d` on `Common/main` modernized `.github/workflows/engineering-pr-delivery-v3.1.yml` to compute relevance against `git merge-base "$BASE_SHA" "$HEAD_SHA"` rather than directly diffing the moving base tip. However, `test_ci_terminal_checks.py` line 51 retained an exact string assertion expecting the older `$BASE_SHA` diff line.
6. **Error 6 (`test_relay_required_checks_keep_real_validation_path_gated_inside_job` - `v2.5`):**
   `FileNotFoundError: [Errno 2] No such file or directory: '.github/workflows/engineering-pr-delivery-v2.5.yml'`
7. **Error 7 (`test_relay_required_checks_keep_real_validation_path_gated_inside_job` - `v3`):**
   `FileNotFoundError: [Errno 2] No such file or directory: '.github/workflows/engineering-pr-delivery-v3.yml'`

---

## 3. Policy & Remediation Status

* **No Suppression:** In accordance with the Owner instructions, this failure is recorded as an authentic historical fact of the existing repository state.
* **Separation of Concerns:** The failure resides entirely within the legacy v3.1 test assertions and retired v2.5/v3 workflow files.
* **Impact on V3.6:** v3.6 has zero runtime dependency on v3.1 or its retired workflows. However, until the legacy v3.1 relevance filter is path-scoped to exclude modern v3.6 labels under `relay/AIM/` or until the legacy tests are aligned, PRs touching `relay/*` will trigger this check.
