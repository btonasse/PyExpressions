import re
from enum import Enum
from string import ascii_letters
from typing import Any, Tuple


class Operator(Enum):
    EXPONENTIATION = "^"
    MULTIPLY = "*"
    DIVIDE = "/"
    ADD = "+"
    SUBTRACT = "-"
    # MODULUS = '%'
    # FLOOR_DIVISION = '//'

    @classmethod
    def has_value(cls, val: Any) -> bool:
        """
        Checks if val is one of the values of this enum
        """
        return val in (x.value for x in cls)

    @classmethod
    def get_regex_escaped_value(cls, element) -> str:
        """
        Returned an escaped representation of the value for regex patterns
        """
        escaped = ""
        for char in element.value:
            escaped += f"\\{char}"
        return escaped


class Expression:
    def __init__(self, left, right, operator: str):
        #self._no_funny_stuff(left, right, operator)
        self.left = left
        self.right = right
        self.operator = operator.replace('^', '**')
        self._str_representation = str(left)+self.operator+str(right)

    def _no_funny_stuff(self, left, right, operator):
        """
        Prevent malicious code execution
        """
        if any(type(x) not in [int, float, Expression] for x in [left, right]):
            raise ValueError(
                "Operands can only be ints, floats, or other Expressions")
        if not Operator.has_value(operator):
            raise ValueError(
                "Only basic arithmetic operators are valid: '+', '-', '*', '/', '^'"
            )

    def resolve_operand(self, operand):
        if isinstance(operand, Expression):
            return str(operand.calculate())
        return str(operand)

    def calculate(self):
        left = self.resolve_operand(self.left)
        right = self.resolve_operand(self.right)
        result = eval(left + self.operator + right)
        print(left + self.operator + right + ' = ' + str(result))
        return result

    def __str__(self) -> str:
        return self._str_representation

    @classmethod
    def parse(cls, expr: str):
        builder = ExpressionBuilder(expr)
        expression = builder.build()
        return expression


class ExpressionBuilder:
    """
    Meta class that is not supposed to be called directly, but my the parse() method of the Expression class.
    """
    bracket_regex = re.compile(r"\([^\(\)]+\)")
    # Operators in priority ascending order
    operators = [member.value for member in reversed(list(Operator))]

    def __init__(self, expr: str):
        self.expression_str = expr

    def _test(self, matchObject: re.Match) -> str:
        match = matchObject.group()[1:-1]
        expr = self._build_expression(match)
        return str(expr.calculate())

    def _eval_brackets(self, expr: str) -> str:
        new_expr_str = re.sub(self.bracket_regex, self._test, expr)
        if '(' in new_expr_str:
            new_expr_str = self._eval_brackets(new_expr_str)
        return new_expr_str

    def _parse_terms(self, expr: str, operator: str) -> Tuple[str]:
        splitexpr = expr.rsplit(operator)
        right = splitexpr.pop()
        left = operator.join(splitexpr)
        return left, right

    def _get_lowest_priority_operator(self, expr: str) -> str:
        for operator in self.operators:
            if operator in expr:
                return operator

    def _count_operators(self, expr: str) -> bool:
        return sum((Operator.has_value(char) for char in expr))

    def _build_expression(self, expr: str) -> Expression:
        operator = self._get_lowest_priority_operator(expr)
        terms = self._parse_terms(expr, operator)
        #print(f"Expr: {expr} Operator: {operator} Terms: {terms}")
        left, right = terms[0], terms[1]
        if self._count_operators(left) > 0:
            #print(f"Left is a larger expr: {left}")
            left = self._build_expression(left)
            # print(
            #    f"out of left recursion. left = {left} type {type(left)}")
        if self._count_operators(right) > 0:
            #print(f"Right is a larger expr: {right}")
            right = self._build_expression(right)
            # print(
            #    f'out of right recursion right = {right} type {type(right)}')
        # Check if term is a letter (hashed parenthesis expression)
        if str(left) in ascii_letters:
            # print(
            #    f"Left {left} is actually {self._bracket_tree[left]}")
            left = self._build_expression(self._bracket_tree[left])
            # print(
            #    f'out of bracket left recursion. left = {left} type {type(left)}')
        if str(right) in ascii_letters:
            # print(
            #    f"Right {right} is actually {self._bracket_tree[right]}")
            right = self._build_expression(self._bracket_tree[right])
            # print(
            #    f'out of bracket right recursion right = {right} type {type(right)}')
        return Expression(left, right, operator)

    def build(self) -> Expression:
        expr_str = self._eval_brackets(self.expression_str)
        expr = self._build_expression(expr_str)
        expr._str_representation = self.expression_str
        return expr


def main():
    test = "5+5/5+(5-5)/5"
    test2 = "5/5+(5*(5+5))"
    test3 = "(5-4)/5+(5*(5+5/2))-3-2+3*5^2-1-2-3"
    demoexpr = "2*5"
    simple = Expression.parse(demoexpr)
    print(f"Demo simple expression: {simple} = {simple.calculate()}\n")

    print(test3)
    complex = Expression.parse(test3)
    print(f"Demo complex expression: {complex} = {complex.calculate()}")
    print(f"Expected result: {eval(str(complex).replace('^', '**'))}")


if __name__ == "__main__":
    main()
