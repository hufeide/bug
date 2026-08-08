import unittest
from add import add

class TestAdd(unittest.TestCase):
    def test_add_positive(self):
        """两个正数相加"""
        self.assertEqual(add(1, 2), 3)

    def test_add_negative(self):
        """两个负数相加"""
        self.assertEqual(add(-1, -2), -3)

    def test_add_zero(self):
        """加零"""
        self.assertEqual(add(5, 0), 5)
        self.assertEqual(add(0, 5), 5)

    def test_add_mixed(self):
        """正负数混合"""
        self.assertEqual(add(10, -3), 7)
        self.assertEqual(add(-10, 3), -7)

    def test_add_large(self):
        """大数相加"""
        self.assertEqual(add(10**9, 10**9), 2 * 10**9)

    def test_add_type_error(self):
        """传入非数字类型应抛出 TypeError"""
        with self.assertRaises(TypeError):
            add("a", 1)

if __name__ == "__main__":
    unittest.main()
