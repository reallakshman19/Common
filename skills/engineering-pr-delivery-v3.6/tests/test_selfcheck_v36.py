"""V36-ECO-02: strict SELF-CHECK v1 whitelist parser; adversarial forms must never qualify."""
import unittest

from test_readmodel_v36 import SC_ID, comment, evidence, run, self_check

TAIL = " P1 fix · owner OTM · next run · unblocks merge · prevents task DONE yes"
ITEM_NO = "Pending: A · owner O · next n · unblocks u · prevents task DONE no"


def task(body):
    return run([comment(SC_ID, body), comment(9002, evidence())])[0]["tasks"][0]


class SelfCheckWhitelistTests(unittest.TestCase):
    def assert_not_qualified(self, bodies):
        for body in bodies:
            t = task(body)
            self.assertFalse(t["claim_qualified"], repr(body))
            unrelated = [r for r in t["reasons"] if r.startswith(("native evidence", "evidence ", "self-check candidate"))]
            self.assertEqual(unrelated, [], repr(body))

    def test_template_body_qualifies(self):
        t = task(self_check(pending="Pending: none", extra="Native report: PENDING published after this companion"))
        self.assertTrue(t["claim_qualified"], t["reasons"])
        self.assertEqual(t["self_check"]["nonconformant"], [])

    def test_ordinary_words_are_not_open_items(self):
        extra = "Tests: unittest @ abc → 23 OK; failures/skips/NOT_RUN none; no new dependencies, spend 0"
        t = task(self_check(extra=extra))
        self.assertTrue(t["claim_qualified"], t["reasons"])

    def test_non_template_pending_forms(self):
        forms = ["**Pending**:" + TAIL, "_Pending_:" + TAIL, "<b>Pending</b>:" + TAIL, "Pending item:" + TAIL,
                 "Pending (1):" + TAIL, "Pending：" + TAIL, "Pen​ding:" + TAIL, "Pend­ing:" + TAIL,
                 "Pending\\:" + TAIL, "| x | y | Pending:" + TAIL, "Pending", "1. Pending:" + TAIL,
                 "- [ ] Pending:" + TAIL, "  - Pending:  P1 fix  ·  owner OTM · next run · unblocks merge · "
                 "prevents task DONE yes", "Pending: P1 fix · owner OTM · next run · prevents task DONE yes",
                 "Pending: P1 · owner OTM · next run · unblocks x · prevents task DONE maybe", "## Pending"]
        self.assert_not_qualified([self_check(pending=f) for f in forms])

    def test_lookalikes_invisibles_and_entities(self):
        words = ["Рending:", "Pеnding:", "Peոding:", "Pénding:", "Pen‪ding:",
                 "Pen⁦ding:", "Pen͏ding:", "Pen⁢ding:", "Pen️ding:", "Penㅤding:",
                 "&#80;ending:", "Pen&shy;ding:", "Pen&#8203;ding:"]
        self.assert_not_qualified([self_check(pending=w + TAIL) for w in words])

    def test_pending_hidden_on_known_key_lines(self):
        extras = ["Basis: pending review", "Scope: approved x; Pending:" + TAIL, "Tests: 3 pass; Pending:" + TAIL,
                  "Done-when: crit 3 → MET · Pending:" + TAIL, "Native report: https://github.com/a/b/1,BLOCKED"]
        self.assert_not_qualified([self_check(extra=e) for e in extras])

    def test_prose_is_not_interpreted_by_design(self):
        """A14 'qualified' is structural; the coordinator reads prose. The basis says so."""
        for body in (self_check(extra="Tests: unittest -> 3 failed"),
                     self_check().replace("reason none", "reason gaps remain"),
                     self_check(pending=ITEM_NO + " (actually yes, blocks DONE)")):
            t = task(body)
            self.assertTrue(t["claim_qualified"], t["reasons"])
            self.assertTrue(t["qualification_basis"].startswith("STRUCTURAL"))

    def test_structural_gaps_fail_closed(self):
        bodies = [self_check(states=("MET", "NOT_APPLICABLE")), self_check(extra="Done-when: x → MET"),
                  self_check(extra="Done-when: x → MET."), self_check(extra="Scope: a\nScope: b"),
                  self_check().replace("Common#345", "Common#999", 1)]
        self.assert_not_qualified(bodies)
        t = task(self_check().replace("; candidate", "; candidate UNKNOWN; old candidate", 1))
        self.assertIn("Basis must name exactly one candidate", str(t["self_check"]["nonconformant"]))

    def test_lenient_on_case_and_trailing_whitespace(self):
        line = "Pending: P1 · owner OTM · next run · unblocks merge · prevents task DONE YES\t"
        self.assertTrue(task(self_check(pending=line))["self_check"]["pending"][0]["prevents_done"])

    def test_unparsed_done_when_never_counts_as_met(self):
        tails = ["→ PARTIAL", "→ FAILED", "→ PENDING", "→ TBD", "-> NOT_MET", "→ not met", "→ NOT MET",
                 "→ ❌ NOT_MET", "(NOT_MET)"]
        bodies = [self_check(extra="Done-when: X " + t) for t in tails]
        bodies += [self_check(extra=p + "Done-when: X → NOT_MET") for p in ("- ", "**", "> ")]
        bodies.append(self_check(extra="Done-when: a → MET Done-when: X → NOT_MET"))
        self.assert_not_qualified(bodies)

    def test_second_item_or_trailing_text_after_a_parsed_item(self):
        lines = [ITEM_NO + "; B · owner OTM · next run · unblocks merge · prevents task DONE yes",
                 ITEM_NO + "/yes", ITEM_NO + "pe"]
        self.assert_not_qualified([self_check(pending=line) for line in lines])

    def test_unknown_keys_are_non_conformant(self):
        extras = ["Blocker: P1 · prevents task DONE yes", "Open: P1", "Outstanding: Owner approval before DONE",
                  "TODO: P1 fix required before DONE", "Still open: P1 not fixed", "Pending items: none",
                  "```", "SELF-CHECK v1 · V36-341-WP1 · reallakshman19/Common#345"]
        self.assert_not_qualified([self_check(extra=e) for e in extras])

    def test_claim_must_be_single_and_exact(self):
        self.assert_not_qualified([self_check(extra="Proposed claim: BLOCKED · reason P1"),
                                   self_check().replace("DONE · reason none", "DONE but PARTIAL"),
                                   self_check(extra="Basis: second basis line")])

    def test_newer_unparseable_self_check_blocks(self):
        for header in ("**SELF-CHECK v1 · V36-341-WP1 · reallakshman19/Common#345**",
                       "﻿SELF-CHECK v1 · V36-341-WP1 · reallakshman19/Common#345",
                       "Intro\nSELF-CHECK v1 · V36-341-WP1 · reallakshman19/Common#345 (updated)"):
            newer = comment(9010, header + "\nProposed claim: BLOCKED · reason P1")
            newer["created_at"] = "2026-10-17T09:00Z"
            t = run([comment(SC_ID, self_check()), newer, comment(9002, evidence())])[0]["tasks"][0]
            self.assertFalse(t["claim_qualified"], header)
            self.assertEqual(t["unparsed_self_check_comments"], [9010])

    def test_header_must_be_first_line(self):
        t = task("Intro line\n" + self_check())
        self.assertIn("no SELF-CHECK v1 companion found", t["reasons"])

    def test_blocking_item_is_parsed_and_pooled(self):
        r = run([comment(SC_ID, self_check(pending="Pending:" + TAIL)), comment(9002, evidence())])[0]
        self.assertEqual(r["pending"][0]["prevents_done"], True)
        self.assertIn("pending item prevents DONE", r["tasks"][0]["reasons"])
        self.assertEqual(r["tasks"][0]["self_check"]["nonconformant"], [])

    def test_crlf_and_trailing_spaces_allowed(self):
        t = task(self_check(pending="Pending: none  ").replace("\n", "\r\n"))
        self.assertTrue(t["claim_qualified"], t["reasons"])


if __name__ == "__main__":
    unittest.main()
