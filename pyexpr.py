import re
from enum import Enum


class Operator(Enum):
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    EXPONENTIATION = "**"
    # MODULUS = '%'
    # FLOOR_DIVISION = '//'

    @classmethod
    def has_value(cls, val) -> bool:
        """
        Checks if val is one of the values of this enum
        """
        return val in (x.value for x in cls)


class ReplacementMap:
    """
    Class to incrementally replace regex matches with a string+count.
    Replacements are tracked in a dictionary
    """

    bracket_regex = r"\([^\(\)]+\)"

    def __init__(self, expr):
        self.expression = expr
        self.count = 0
        self.replacements = {}
        self.new_expr = self.hash_bracket_expressions(self.expression)

    def _replace_and_increment(self, matchObject: re.Match) -> str:
        self.count += 1
        replacement = f"expr{self.count}"
        self.replacements[replacement] = matchObject.group()
        return replacement

    def hash_bracket_expressions(self, expr: str) -> dict:
        """
        Recursively hash expressions between parenthesis
        so then can be referenced later when building
        the order or operations tree
        """
        new_expr = re.sub(self.bracket_regex, self._replace_and_increment, expr)
        if '(' in new_expr:
            return self.hash_bracket_expressions(new_expr)
        return new_expr



class Expression:
    def __init__(self, left, right, operator):
        self._no_funny_stuff(left, right, operator)
        self.left = left
        self.right = right
        self.operator = operator

    def _no_funny_stuff(self, left, right, operator):
        """
        Prevent malicious code execution
        """
        if any(type(x) not in [int, float] for x in [left, right]):
            raise ValueError("Operands can only be ints or floats")
        if not Operator.has_value(operator):
            raise ValueError(
                "Only basic arithmetic operators are valid: '+', '-', '*', '/', '**'"
            )

    def resolve_operand(self, operand):
        if isinstance(operand, Expression):
            return operand.calculate()
        return str(operand)

    def calculate(self):
        left = self.resolve_operand(self.left)
        right = self.resolve_operand(self.right)
        result = eval(left + self.operator + right)
        return result

    @classmethod
    def parse(self, expr: str):
        queue = []
        repls = ReplacementMap(expr)
        return repls


def main():
    test = "5+5/5+(5-5)/5"
    test2 = "5/5+(5*(5+5))"
    test3 = "(5-4)/5+(5*(5+5))"
    e = Expression(2, 5, "*")
    print(e.calculate())

    repls = Expression.parse(test3)
    print(repls.new_expr)
    print(repls.replacements)


if __name__ == "__main__":
    main()
