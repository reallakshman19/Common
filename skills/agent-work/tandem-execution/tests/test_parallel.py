import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


C0 = load("parallel_c0", "examples/golden/baseline.py")
A1 = load("parallel_a1", "examples/golden/candidate_a.py")
B1 = load("parallel_b1", "examples/parallel/candidate_b1.py")
C2 = load("parallel_c2", "examples/golden/candidate_b.py")
policy = load("tandem_convergence", "tools/convergence.py")
M = {"occurrence_id": "m", "url": "same", "date": "2026-11-19", "time": "09:00"}
E = {"occurrence_id": "e", "url": "same", "date": "2026-11-19", "time": "18:00"}
MAN = {"id": "manual", "url": "manual", "title": "appointment"}


class ParallelGolden(unittest.TestCase):
    def test_c0_has_both_failures(self):
        self.assertEqual(len(C0.merge([M, E, M])), 1)
        self.assertEqual(C0.dismiss([M, E, MAN], [M, E], M), ([MAN], []))

    def test_a1_independent_merge_fix(self):
        self.assertEqual(A1.merge([M, E, M]), [M, E])
        self.assertEqual(A1.dismiss([M, E, MAN], [M, E], M), ([MAN], []))

    def test_b1_independent_dismissal_fix(self):
        self.assertEqual(len(B1.merge([M, E, M])), 1)
        self.assertEqual(B1.dismiss([M, E, MAN], [M, E], M), ([M, E, MAN], [E]))

    def test_combined_preserves_both_repairs(self):
        self.assertEqual(C2.merge([M, E, M]), A1.merge([M, E, M]))
        self.assertEqual(C2.dismiss([M, E, MAN], [M, E], M),
                         B1.dismiss([M, E, MAN], [M, E], M))

    def test_combined_boundary(self):
        suggestions = C2.merge([M, E, M])
        saved, remaining = C2.dismiss([M, E, MAN], suggestions, M)
        self.assertEqual(saved, [M, E, MAN])
        self.assertEqual(remaining, [E])
        self.assertEqual(C2.dismiss(saved, remaining, M), (saved, remaining))

    def test_b_can_reconstruct_a_fix_without_a(self):
        # Use original occurrence requirement, not A1: same semantics as C2.
        def independently_recovered_merge(events):
            return list({e["occurrence_id"]: e for e in events}.values())
        saved, remaining = B1.dismiss([M, E, MAN],
                                      independently_recovered_merge([M, E, M]), M)
        self.assertEqual((saved, remaining), ([M, E, MAN], [E]))
        r = policy.decide(policy.Observation(b_work_available=True, boundary_reached=True,
                                              done_list_supported=True))
        self.assertEqual((r["lineage"], r["outcome"]), ("FINAL_B_ONLY", "COMPLETE"))


class ParallelPolicy(unittest.TestCase):
    def case(self, **kw):
        return policy.decide(policy.Observation(**kw))

    def test_b_starts_without_a_ready(self):
        self.assertEqual(self.case()["action"], "IMPLEMENT_B")

    def test_b_continues_when_a_absent(self):
        self.assertEqual(self.case(b_work_available=True)["action"], "CONTINUE_B")

    def test_a_ready_alone_is_not_verified_bytes(self):
        self.assertEqual(self.case(a_ready=True, b_work_available=True)["action"], "CONTINUE_B")

    def test_verified_a_without_marker_can_integrate(self):
        self.assertEqual(self.case(a_bytes_verified=True, b_work_available=True)["action"],
                         "RECONCILE_AVAILABLE_A")

    def test_peer_first_still_b_implements(self):
        self.assertEqual(self.case(a_bytes_verified=True)["action"], "IMPLEMENT_B")

    def test_conflicting_shared_writer_does_not_stop_isolated_work(self):
        r = self.case(shared_writer_active=True)
        self.assertTrue(r["isolated_work"])
        self.assertFalse(r["shared_write"])

    def test_b_only_complete(self):
        r = self.case(b_work_available=True, boundary_reached=True, done_list_supported=True)
        self.assertEqual((r["action"], r["lineage"], r["outcome"]),
                         ("DELIVER_FINAL", "FINAL_B_ONLY", "COMPLETE"))

    def test_b_only_partial(self):
        r = self.case(b_work_available=True, boundary_reached=True)
        self.assertEqual((r["lineage"], r["outcome"]), ("FINAL_B_ONLY", "PARTIAL"))

    def test_combined_complete(self):
        r = self.case(a_bytes_verified=True, a_reconciled=True, b_work_available=True,
                      boundary_reached=True, done_list_supported=True)
        self.assertEqual((r["lineage"], r["outcome"]), ("FINAL_COMBINED", "COMPLETE"))

    def test_combined_partial(self):
        r = self.case(a_bytes_verified=True, a_reconciled=True, b_work_available=True,
                      boundary_reached=True)
        self.assertEqual((r["lineage"], r["outcome"]), ("FINAL_COMBINED", "PARTIAL"))

    def test_late_a_does_not_reopen_final(self):
        self.assertEqual(self.case(a_bytes_verified=True, final_published=True)["action"],
                         "KEEP_FINAL")

    def test_unverified_a_cannot_be_claimed_reconciled(self):
        with self.assertRaises(ValueError):
            self.case(a_reconciled=True)

    def test_serial_isolated_work_allowed(self):
        r = self.case(mode="SERIAL", shared_writer_active=True)
        self.assertEqual(r["action"], "IMPLEMENT_B")
        self.assertFalse(r["shared_write"])

    def test_serial_lineage_explicit(self):
        r = self.case(mode="SERIAL", a_bytes_verified=True, a_reconciled=True,
                      b_work_available=True, boundary_reached=True, done_list_supported=True)
        self.assertEqual(r["lineage"], "SERIAL_FINAL")

    def test_unknown_mode_rejected(self):
        with self.assertRaises(ValueError):
            self.case(mode="UNSELECTED")


if __name__ == "__main__":
    unittest.main()
