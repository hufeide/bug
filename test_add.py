import unittest
from add import add

class TestAdd(unittest.TestCase):
    def test_add_positive(self):
        """test positive numbers"""
        self.assertEqual(add(1, 2), 3)

    def test_add_negative(self):
        """test negative numbers"""
        self.assertEqual(add(-1, -2), -3)

    def test_add_zero(self):
        """test with zero"""
        self.assertEqual(add(5, 0), 5)
        self.assertEqual(add(0, 5), 5)

    def test_add_mixed(self):
        """test mixed signs"""
        self.assertEqual(add(10, -3), 7)
        self.assertEqual(add(-10, 3), -7)

    def test_add_large(self):
        """test large numbers"""
        self.assertEqual(add(10**9, 10**9), 2 * 10**9)

    def test_add_type_error(self):
        """test type error on invalid input"""
        with self.assertRaises(TypeError):
            add("a", 1)

if __name__ == "__main__":
    unittest.main()
