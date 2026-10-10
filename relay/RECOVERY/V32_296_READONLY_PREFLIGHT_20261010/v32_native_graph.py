"""Source-pinned native V3.2 graph structure validation — READ ONLY.

Load the repository's existing frozen V3.2 DELP graph validator from its
exact neighbouring source path. This helper never computes a projection,
ledger, eligible E, status/title, custody or programme write. A syntactically
valid graph is not a released Owner graph and does not authenticate its digest.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Mapping


_NATIVE_GRAPH_SOURCE = (
    Path(__file__).resolve().parents[3] /
    "skills" / "engineering-pr-delivery-v3.2" / "scripts" /
    "delp_projection_v32.py"
)


class NativeGraphBoundaryError(ValueError):
    pass


def inspect_native_graph_structure(
    graph: Mapping[str, Any],
    *,
    expected_repository: str,
    expected_leaf: str,
    expected_pr: int,
) -> dict[str, Any]:
    """Validate exact V3.2 graph grammar + expected leaf/PR binding.

    Does *not* authenticate Owner release or an accepted root. The caller
    separately pins raw graph bytes and checks source drift.
    """
    try:
        spec = importlib.util.spec_from_file_location("_v32_preflight_native_graph", _NATIVE_GRAPH_SOURCE)
        if spec is None or spec.loader is None:
            raise NativeGraphBoundaryError("NATIVE_GRAPH_MODULE_UNAVAILABLE")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        indexed = module.validate_graph(graph)
        # Also enforce the real native live repository gate; this does not
        # imply a valid graph was ever released or authorized by its Owner.
        module.require_repository_match(graph, expected_repository, live=True)
    except NativeGraphBoundaryError:
        raise
    except (ValueError, TypeError, AttributeError, RuntimeError) as exc:
        raise NativeGraphBoundaryError("NATIVE_V32_GRAPH_CONTRACT_INVALID") from exc
    nodes = indexed.get("nodes") or {}
    leaf = nodes.get(expected_leaf)
    if not isinstance(leaf, Mapping) or leaf.get("kind") != "LEAF":
        raise NativeGraphBoundaryError("PROVIDER_GRAPH_LEAF_NOT_BOUND")
    bound_pr = leaf.get("primary_pr")
    try:
        if bound_pr is None or module.ref_number(bound_pr) != expected_pr:
            raise NativeGraphBoundaryError("PROVIDER_GRAPH_PR_NOT_BOUND")
        # An explicitly repository-qualified PR reference cannot silently
        # redirect to another repository that shares the same number.
        repo_part, _ = module.parse_ref(bound_pr)
        if repo_part is not None and repo_part.lower() not in (
            expected_repository.lower(), expected_repository.rsplit("/", 1)[-1].lower()
        ):
            raise NativeGraphBoundaryError("PROVIDER_GRAPH_PR_FOREIGN_REPOSITORY")
    except NativeGraphBoundaryError:
        raise
    except (ValueError, TypeError) as exc:
        raise NativeGraphBoundaryError("PROVIDER_GRAPH_PR_NOT_BOUND") from exc
    return {
        "native_contract": "STRUCTURALLY_VALID_UNRELEASED",
        "graph_digest": indexed.get("digest"),
        "leaf_ref": leaf["ref"],
        "declared_unit_count": len(leaf["units"]),
        "declared_gate_count": len(leaf["delivery_gates"]),
    }
