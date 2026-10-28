import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from provider_mutation import (
    canonical_provider_key,
    derive_provider_action,
    validate_provider_mutation,
)


DIGEST = "d" * 64


def identity(resource_kind="ISSUE"):
    value = {
        "programme_or_parent_id": "COMMON-PROD-CONTROL-V1",
        "prd_id": "PRD-527-P1-R3A",
        "resource_kind": resource_kind,
        "mutation_slot": "MATERIAL_RESPONSIBILITY",
        "canonical_key": "",
    }
    value["canonical_key"] = canonical_provider_key(value)
    return value


def transaction(
    mutation_class="CREATE_ONCE",
    operation="CREATE_ISSUE",
    resource_kind="ISSUE",
):
    ident = identity(resource_kind)
    return {
        "schema_version": "PROVIDER_MUTATION_V1",
        "authority": "PROVIDER_MUTATION_TRANSACTION",
        "identity": ident,
        "mutation": {
            "class": mutation_class,
            "operation": operation,
            "payload_digest": DIGEST,
            "attempted": False,
            "attempt_id": None,
            "provider_id": None,
        },
        "lookup": {
            "performed": False,
            "matches": [],
        },
        "readback": {
            "performed": False,
            "found": False,
            "provider_id": None,
            "canonical_key": None,
            "payload_digest": None,
        },
        "next_action": {
            "type": "LOOKUP",
            "reason_code": "LOOKUP_REQUIRED",
        },
    }


def set_derived(value):
    value["next_action"] = derive_provider_action(value)
    return value


class ProviderMutationTests(unittest.TestCase):
    def test_canonical_key_is_stable_machine_identity(self):
        first = identity()
        second = copy.deepcopy(first)
        self.assertEqual(first["canonical_key"], canonical_provider_key(second))
        self.assertTrue(first["canonical_key"].startswith("pm:v1:"))

    def test_title_or_chat_state_cannot_be_identity_input(self):
        value = transaction()
        value["title"] = "same looking issue"
        errors = validate_provider_mutation(value)
        self.assertTrue(any("Additional properties are not allowed" in error for error in errors), errors)

    def test_stored_key_must_match_machine_identity(self):
        value = transaction()
        value["identity"]["canonical_key"] = "pm:v1:" + "0" * 64
        errors = validate_provider_mutation(value)
        self.assertTrue(any("machine-derived provider key" in error for error in errors), errors)

    def test_lookup_is_mandatory_first_action(self):
        value = transaction()
        self.assertEqual(derive_provider_action(value)["type"], "LOOKUP")
        self.assertEqual(validate_provider_mutation(value), [])

    def test_create_once_zero_matches_allows_one_mutation(self):
        value = transaction()
        value["lookup"]["performed"] = True
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "CREATE_ONCE")
        self.assertEqual(validate_provider_mutation(value), [])

    def test_create_once_one_match_reuses_without_mutation(self):
        value = transaction()
        key = value["identity"]["canonical_key"]
        value["lookup"] = {
            "performed": True,
            "matches": [{"provider_id": "issue://546", "canonical_key": key}],
        }
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "READBACK_EXISTING")
        self.assertEqual(validate_provider_mutation(value), [])

    def test_multiple_matches_fail_closed(self):
        value = transaction()
        key = value["identity"]["canonical_key"]
        value["lookup"] = {
            "performed": True,
            "matches": [
                {"provider_id": "issue://1", "canonical_key": key},
                {"provider_id": "issue://2", "canonical_key": key},
            ],
        }
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "RECONCILE_DUPLICATES")
        self.assertEqual(validate_provider_mutation(value), [])

    def test_lost_create_response_retry_never_creates_twice(self):
        value = transaction()
        value["lookup"]["performed"] = True
        value["mutation"].update({
            "attempted": True,
            "attempt_id": "provider-request://1",
        })
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "READBACK_AFTER_MUTATION")
        self.assertEqual(validate_provider_mutation(value), [])

    def test_mutate_existing_zero_matches_fails_closed(self):
        value = transaction(
            "MUTATE_EXISTING_ONCE",
            "UPDATE_ISSUE",
            "ISSUE",
        )
        value["lookup"]["performed"] = True
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "RECONCILE_MISSING_TARGET")
        self.assertEqual(validate_provider_mutation(value), [])

    def test_mutate_existing_one_match_allows_one_mutation(self):
        value = transaction(
            "MUTATE_EXISTING_ONCE",
            "UPDATE_ISSUE",
            "ISSUE",
        )
        key = value["identity"]["canonical_key"]
        value["lookup"] = {
            "performed": True,
            "matches": [{"provider_id": "issue://546", "canonical_key": key}],
        }
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "MUTATE_ONCE")
        self.assertEqual(validate_provider_mutation(value), [])

    def test_lost_update_response_retry_never_mutates_twice(self):
        value = transaction(
            "MUTATE_EXISTING_ONCE",
            "UPDATE_ISSUE",
            "ISSUE",
        )
        key = value["identity"]["canonical_key"]
        value["lookup"] = {
            "performed": True,
            "matches": [{"provider_id": "issue://546", "canonical_key": key}],
        }
        value["mutation"].update({
            "attempted": True,
            "attempt_id": "provider-request://2",
            "provider_id": "issue://546",
        })
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "READBACK_AFTER_MUTATION")
        self.assertEqual(validate_provider_mutation(value), [])

    def test_matching_readback_completes(self):
        value = transaction()
        key = value["identity"]["canonical_key"]
        value["lookup"]["performed"] = True
        value["mutation"].update({
            "attempted": True,
            "attempt_id": "provider-request://1",
        })
        value["readback"] = {
            "performed": True,
            "found": True,
            "provider_id": "issue://546",
            "canonical_key": key,
            "payload_digest": DIGEST,
        }
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "COMPLETE")
        self.assertEqual(validate_provider_mutation(value), [])

    def test_not_found_readback_after_attempt_fails_closed(self):
        value = transaction()
        value["lookup"]["performed"] = True
        value["mutation"].update({
            "attempted": True,
            "attempt_id": "provider-request://1",
        })
        value["readback"]["performed"] = True
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "RECONCILE_MISSING_TARGET")
        self.assertEqual(validate_provider_mutation(value), [])

    def test_payload_mismatch_reconciles(self):
        value = transaction()
        key = value["identity"]["canonical_key"]
        value["lookup"]["performed"] = True
        value["readback"] = {
            "performed": True,
            "found": True,
            "provider_id": "issue://546",
            "canonical_key": key,
            "payload_digest": "e" * 64,
        }
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "RECONCILE_MISMATCH")
        self.assertEqual(validate_provider_mutation(value), [])

    def test_provider_id_mismatch_reconciles(self):
        value = transaction(
            "MUTATE_EXISTING_ONCE",
            "UPDATE_ISSUE",
            "ISSUE",
        )
        key = value["identity"]["canonical_key"]
        value["lookup"] = {
            "performed": True,
            "matches": [{"provider_id": "issue://546", "canonical_key": key}],
        }
        value["readback"] = {
            "performed": True,
            "found": True,
            "provider_id": "issue://999",
            "canonical_key": key,
            "payload_digest": DIGEST,
        }
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "RECONCILE_MISMATCH")

    def test_operation_resource_kind_must_match(self):
        value = transaction(
            "CREATE_ONCE",
            "CREATE_PULL_REQUEST",
            "ISSUE",
        )
        set_derived(value)
        errors = validate_provider_mutation(value)
        self.assertTrue(any("requires resource_kind PULL_REQUEST" in error for error in errors), errors)

    def test_merge_is_one_shot_mutation_of_existing_pull_request(self):
        value = transaction(
            "MUTATE_EXISTING_ONCE",
            "MERGE_PULL_REQUEST",
            "PULL_REQUEST",
        )
        key = value["identity"]["canonical_key"]
        value["lookup"] = {
            "performed": True,
            "matches": [{"provider_id": "pr://547", "canonical_key": key}],
        }
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "MUTATE_ONCE")
        self.assertEqual(validate_provider_mutation(value), [])

    def test_merge_cannot_target_synthetic_merge_resource(self):
        value = transaction(
            "MUTATE_EXISTING_ONCE",
            "MERGE_PULL_REQUEST",
            "MERGE",
        )
        set_derived(value)
        errors = validate_provider_mutation(value)
        self.assertTrue(errors)

    def test_operation_mutation_class_must_match(self):
        value = transaction(
            "CREATE_ONCE",
            "UPDATE_REF",
            "REF",
        )
        set_derived(value)
        errors = validate_provider_mutation(value)
        self.assertTrue(any("requires mutation class MUTATE_EXISTING_ONCE" in error for error in errors), errors)

    def test_attempt_before_lookup_is_invalid(self):
        value = transaction()
        value["mutation"].update({
            "attempted": True,
            "attempt_id": "provider-request://1",
        })
        set_derived(value)
        errors = validate_provider_mutation(value)
        self.assertTrue(any("before lookup" in error for error in errors), errors)

    def test_create_attempt_with_existing_match_is_invalid(self):
        value = transaction()
        key = value["identity"]["canonical_key"]
        value["lookup"] = {
            "performed": True,
            "matches": [{"provider_id": "issue://546", "canonical_key": key}],
        }
        value["mutation"].update({
            "attempted": True,
            "attempt_id": "provider-request://1",
        })
        set_derived(value)
        errors = validate_provider_mutation(value)
        self.assertTrue(any("cannot be attempted when lookup found" in error for error in errors), errors)

    def test_stored_next_action_must_equal_derived(self):
        value = transaction()
        value["next_action"] = {
            "type": "CREATE_ONCE",
            "reason_code": "CREATE_ALLOWED",
        }
        errors = validate_provider_mutation(value)
        self.assertTrue(any("exactly equal" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
