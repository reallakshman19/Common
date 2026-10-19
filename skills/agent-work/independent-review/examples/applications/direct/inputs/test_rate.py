import unittest

from rate import estimate


class ExistingChecks(unittest.TestCase):
    def test_large(self):
        self.assertEqual(estimate(20000, 500), 18500)

    def test_small(self):
        self.assertEqual(estimate(4000, 500), 4500)

    def test_invalid(self):
        for value in (-1, 0.5, True):
            with self.assertRaises(ValueError):
                estimate(value, 0)
