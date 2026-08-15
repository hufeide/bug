import unittest
from multiply import multiply

class TestMultiply(unittest.TestCase):
    def test_multiply_positive(self):
        """两个正数相乘"""
        self.assertEqual(multiply(2, 3), 6)

    def test_multiply_negative(self):
        """两个负数相乘"""
        self.assertEqual(multiply(-1, -2), 2)

    def test_multiply_zero(self):
        """乘零"""
        self.assertEqual(multiply(5, 0), 0)
        self.assertEqual(multiply(0, 5), 0)

    def test_multiply_mixed(self):
        """正负数混合"""
        self.assertEqual(multiply(10, -3), -30)
        self.assertEqual(multiply(-10, 3), -30)

    def test_multiply_large(self):
        """大数相乘"""
        self.assertEqual(multiply(10**9, 10**9), 10**18)

    def test_multiply_type_error(self):
        """传入非数字类型应抛出 TypeError"""
        with self.assertRaises(TypeError):
            multiply("a", "a")

if __name__ == "__main__":
    unittest.main()
