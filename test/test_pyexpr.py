"""
Unit tests for pyexpr.py
"""

import unittest
import pyexpr as pe

class TestExpression(unittest.TestCase):
    def setUp(self) -> None:
        self.expressions = (
            ('5-4', '5', '4', '-'),
            ('2.4*-45', '2.4', '-45', '*'),
            ('0.45/2', '0.45', '2', '/'),
            ('3+98', '3', '98', '+'),
            ('-2^-3', '-2', '-3', '^'),
            ('-2+2.2', -2, 2.2, '+')
        )

    def test_parse_simple_operations(self):
        for expression in self.expressions:
            expr = pe.Expression(expression[1], expression[2], expression[3])
            self.assertEqual(str(expr), expression[0])
            self.assertEqual(expr.left, expression[1])
            self.assertEqual(expr.right, expression[2])
            self.assertEqual(expr.operator, expression[3])

    def test_parse_bracket_expression(self):
        expression = ('(-5-4)', '-5', '4', '-')
        expr = pe.Expression(expression[1], expression[2], expression[3], True)
        self.assertEqual(str(expr), expression[0])
        self.assertEqual(expr.left, expression[1])
        self.assertEqual(expr.right, expression[2])
        self.assertEqual(expr.operator, expression[3])

        expr = pe.Expression(expression[1], expression[2], expression[3])
        self.assertNotEqual(str(expr), expression[0])

    def test_parse_invalid_string(self):
        terms = ('a', '5', '-')
        with self.assertRaises(ValueError):
            pe.Expression(terms[0], terms[1], terms[2])

    def test_evaluation(self):
        for expression in self.expressions:
            expr = pe.Expression(expression[1], expression[2], expression[3])
            self.assertEqual(expr.calculate(), eval(expression[0].replace('^', '**')), f"Expression: {expression[0]}")
        expression = ('(-5-4)', '-5', '4', '-')
        expr = pe.Expression(expression[1], expression[2], expression[3], True)
        self.assertEqual(expr.calculate(), eval(expression[0]), f"Expression: {expression[0]}")

    def test_equality(self):
        self.assertEqual(pe.Expression(5, 4, '+'), pe.Expression(3.0, '3', '*'))
        self.assertNotEqual(pe.Expression(5, 3, '+'), pe.Expression(3.0, '3', '*'))



class TestExpressionBuilder(unittest.TestCase):
    def setUp(self) -> None:
        self.expression = {
            "string": "(5-4)/5+(5*(5+5/-2))-3-2+3*5^2-1-2-3",
            "result": 76.7
        }

if __name__ == '__main__':
    unittest.main()
