from django.test import TestCase
from utils.calculator import add, subtract, multiply, divide


class TestCalculator(TestCase):
    """Test cases untuk fungsi calculator."""

    # ===== Test Addition =====
    def test_add_positive_numbers(self):
        """Test penjumlahan bilangan positif."""
        self.assertEqual(add(2, 3), 5)

    def test_add_negative_numbers(self):
        """Test penjumlahan bilangan negatif."""
        self.assertEqual(add(-1, -1), -2)

    def test_add_mixed_numbers(self):
        """Test penjumlahan bilangan positif dan negatif."""
        self.assertEqual(add(-1, 1), 0)

    # ===== Test Subtraction =====
    def test_subtract_positive_numbers(self):
        """Test pengurangan bilangan positif."""
        self.assertEqual(subtract(5, 3), 2)

    def test_subtract_negative_result(self):
        """Test pengurangan dengan hasil negatif."""
        self.assertEqual(subtract(3, 5), -2)

    # ===== Test Multiplication =====
    def test_multiply_positive_numbers(self):
        """Test perkalian bilangan positif."""
        self.assertEqual(multiply(3, 4), 12)

    def test_multiply_by_zero(self):
        """Test perkalian dengan nol."""
        self.assertEqual(multiply(5, 0), 0)

    # ===== Test Division =====
    def test_divide_positive_numbers(self):
        """Test pembagian bilangan positif."""
        self.assertEqual(divide(10, 2), 5)

    def test_divide_returns_float(self):
        """Test pembagian menghasilkan float."""
        self.assertEqual(divide(7, 2), 3.5)

    def test_divide_by_zero_raises_error(self):
        """Test pembagian dengan nol melempar ValueError."""
        with self.assertRaises(ValueError) as context:
            divide(10, 0)
        self.assertEqual(
            str(context.exception),
            "Tidak bisa membagi dengan nol!"
        )

    # ===== Edge Cases =====
    def test_add_zero(self):
        """Test penjumlahan dengan nol."""
        self.assertEqual(add(5, 0), 5)
        self.assertEqual(add(0, 0), 0)

    def test_subtract_same_number(self):
        """Test pengurangan bilangan dengan dirinya sendiri."""
        self.assertEqual(subtract(5, 5), 0)

    def test_multiply_negative_numbers(self):
        """Test perkalian dengan bilangan negatif."""
        self.assertEqual(multiply(-3, -4), 12)
        self.assertEqual(multiply(-3, 4), -12)

    def test_divide_negative_numbers(self):
        """Test pembagian dengan bilangan negatif."""
        self.assertEqual(divide(-10, 2), -5)
        self.assertEqual(divide(-10, -2), 5)

    def test_divide_fraction_result(self):
        """Test pembagian yang menghasilkan hasil pecahan."""
        self.assertAlmostEqual(divide(1, 3), 0.3333333, places=5)

    def test_add_floats(self):
        """Test penjumlahan dengan bilangan float."""
        self.assertAlmostEqual(add(1.5, 2.5), 4.0)

    def test_subtract_floats(self):
        """Test pengurangan dengan bilangan float."""
        self.assertAlmostEqual(subtract(5.5, 2.5), 3.0)

    def test_multiply_floats(self):
        """Test perkalian dengan bilangan float."""
        self.assertAlmostEqual(multiply(2.5, 4.0), 10.0)

    def test_divide_floats(self):
        """Test pembagian dengan bilangan float."""
        self.assertAlmostEqual(divide(5.0, 2.0), 2.5)