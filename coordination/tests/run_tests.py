#!/usr/bin/env python3
"""
Dedicated Test Runner for Coordination Control Tower v3 (WP0 & P0)
Executes all identity contract, adversarial scenario, and security tests.
"""

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent.parent.resolve()

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(HERE.parent) not in sys.path:
    sys.path.insert(0, str(HERE.parent))


def main():
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(HERE), pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if not result.wasSuccessful():
        print(f"\n[FAIL] Test suite failed: {len(result.failures)} failures, {len(result.errors)} errors.")
        sys.exit(1)
    else:
        print(f"\n[SUCCESS] All {result.testsRun} tests passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
