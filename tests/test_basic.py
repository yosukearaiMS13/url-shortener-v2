"""Basic test to verify test infrastructure."""

import unittest


class TestBasic(unittest.TestCase):
    """Basic test case to ensure test infrastructure works."""

    def test_basic(self):
        """Basic test that always passes."""
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
