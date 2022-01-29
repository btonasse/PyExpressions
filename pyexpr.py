"""
Emulate the eval() function, but only for representing
and evaluating complex arithmetic expressions via a tree of Expression objects
(i.e. preventing the execution of arbitrary code)

This module contains three classes:

Operator:
    Enum class to facilitate the use of arithmetic operators
Expression:
    Represents a simple expression (left operand + operator + right operand).
    Operands must be string representations of floats/ints or other Expressions.
    Use the class method parse() to parse a string representation of an expression.
    To evaluate the expression, call the method calculate()
ExpressionBuilder:
    Class that is used to build a tree of Expressions
    that represent complex arithmetic expressions. Should not be instantiated directly.
"""

from __future__ import annotations
import re
from enum import Enum
from typing import Any, Tuple, Union

# Todo:
# Add proper logging
# Add proper tests
# Move parenthesis logic to parse_terms
# so brackets can also be represented as persistent expressions in the expression tree


class Operator(Enum):
    """
    Enum class to facilitate the use of arithmetic operators.
    Members are ordered according to the mathematical order of operations.
    Has the following utility class methods:
        has_value(val):
            Checks if val is one of the values of this enum.
        get_regex_escaped_value(element):
            Returns an escaped representation of the member's value (to be used in regex patterns).
    """

    EXPONENTIATION = "^"
    MULTIPLY = "*"
    DIVIDE = "/"
    SUBTRACT = "-"
    ADD = "+"

    # MODULUS = '%'
    # FLOOR_DIVISION = '//'

    @classmethod
    def has_value(cls, val: Any) -> bool:
        """
        Checks if val is one of the values of this enum
        """
        return val in (x.value for x in cls)


class Expression:
    """
    Represents a simple expression (left operand + operator + right operand).
    Operands must be string representations of floats/ints or other Expressions.
    Use the class method parse() to parse a string representation of an expression.
    To evaluate the expression, call the method calculate()
    """

    def __init__(
        self, left: Union[Expression, str], right: Union[Expression, str], operator: str
    ) -> None:
        self.no_funny_stuff(left, right, operator)
        self.left = left
        self.right = right
        # Replace standard representation of exponentiation with the python ** operator
        self.operator = operator.replace("^", "**")
        self._str_representation = str(left) + self.operator + str(right)

    @staticmethod
    def no_funny_stuff(
        left: Union[Expression, str], right: Union[Expression, str], operator: str
    ) -> None:
        """
        Prevent malicious code execution by checking the following:
            1) Operands must be string representations of floats/ints or other Expressions.
            2) Operator must be a member of the Operator class
        """
        for term in [left, right]:
            try:
                float(term)
            except (ValueError, TypeError) as err:
                if not isinstance(term, Expression):
                    raise ValueError(
                        "Operands can only be ints, floats, number strings or other Expressions"
                    ) from err

        if not Operator.has_value(operator):
            raise ValueError(
                "Only basic arithmetic operators are valid: '+', '-', '*', '/', '^'"
            )

    @staticmethod
    def resolve_operand(operand: Union[Expression, str]) -> str:
        """
        Determine the nature of an operand.
        If operando is a string, return it. If it's an Expression,
        evaluate it and return the result as a string.
        """
        if isinstance(operand, Expression):
            return str(operand.calculate())
        return str(operand)

    def calculate(self) -> Union[int, float]:
        """
        Evaluate expression.
        """
        left = self.resolve_operand(self.left)
        right = self.resolve_operand(self.right)
        result = eval(left + self.operator + right)
        # print(left + self.operator + right + ' = ' + str(result))
        return result

    def __str__(self) -> str:
        return self._str_representation

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Expression):
            return self.calculate() == other.calculate()
        return self.calculate() == other

    @classmethod
    def parse(cls, expr: str) -> Expression:
        """
        Class method used to return an instance of this class
        by parsing a string representation of an expression.
        This is done via the ExpressionBuilder metaclass.
        """
        builder = ExpressionBuilder(expr)
        expression = builder.build()
        return expression


class ExpressionBuilder:
    """
    Metaclass that is used to build a tree of Expressions
    to represent complex arithmetic expressions. Should not be instantiated directly.
    """

    bracket_regex: re.Pattern = re.compile(r"\([^\(\)]+\)")
    # Regex to find an operator (replace % with the operator to be searched)
    # The negative lookbehind is there to prevent false matches when dealing with negative numbers
    operator_regex: str = r".(?<!\/|\(|-)(\%)"
    # Get operators in ascending order of priority
    operators = [member.value for member in reversed(list(Operator))]

    def __init__(self, expr: str) -> None:
        self.expression_str = expr

    def _evaluate_match(self, match_object: re.Match) -> str:
        """
        Evaluates the result of a simple expression inside brackets.
        This is called by _eval_brackets() and accepts a match object
        containing the expression to be evaluated.
        """
        match = match_object.group()[1:-1]
        expr = self._build_expression(match)
        return str(expr.calculate())

    def _eval_brackets(self, expr: str) -> str:
        """
        Use regex to locate expressions inside brackets in order to evaluate them
        by calling _evaluate_match(). The expression is then replaced by the result.
        The regex pattern does not match bracket expressions that contain other bracket expressions.
        This function is therefore called recursively if brackets are still found after evaluation.
        """
        new_expr_str = re.sub(self.bracket_regex, self._evaluate_match, expr)
        if "(" in new_expr_str:
            new_expr_str = self._eval_brackets(new_expr_str)
        return new_expr_str

    @classmethod
    def _compile_operator_regex(cls, operator: str) -> re.Pattern:
        """
        Compile a re.Pattern to find operators in an expression string
        by replacing the placeholder '%' with the given operator in self.operator_regex
        """
        return re.compile(cls.operator_regex.replace("%", operator))

    @classmethod
    def parse_terms(cls, expr: str, operator: str) -> Tuple[str]:
        """
        Splits a string representation of an expression at the rightmost given operator.
        This method assumes the operator exists in the string
        (i.e. it should be called after _get_lowest_priority_operator())
        """
        # Compile pattern, replacing % with the actual operator being searched
        pat = cls._compile_operator_regex(operator)
        # Get index of rightmost match
        i = list(re.finditer(pat, expr))[-1].start() + 1
        # Split string at that index, omitting the operator itself
        left, right = expr[:i], expr[i + 1 :]
        return left, right

    @classmethod
    def _get_lowest_priority_operator(cls, expr: str) -> str:
        """
        Finds the lowest priority operator present in a given expression string.
        """
        for operator in cls.operators:
            pat = cls._compile_operator_regex(operator)
            if re.search(pat, expr):
                return operator

    @classmethod
    def count_operators(cls, expr: str) -> int:
        """
        Count how many arithmetic operators are present in a given expression string.
        This is used to determine whether the given expression is ready to be turned
        into an instance of the Expression class, since this class is supposed to represent
        a single operation (e.g. 5+4, but not 5+4-2).
        """
        count = 0
        for operator in cls.operators:
            pat = cls._compile_operator_regex(operator)
            matches = re.findall(pat, expr)
            if matches:
                count += len(matches)
        return count
    
    def _build_expression(self, expr: str) -> Expression:
        """
        Recursively build the expression tree, from the lowest to the highest priority operators.
        Currently expressions inside brackets are evaluated first and replaced by their result,
        but in the future the code will be refactored to represent them also as a child Expression
        built by this method.
        """
        operator = self._get_lowest_priority_operator(expr)
        terms = self.parse_terms(expr, operator)
        # print(f"Expr: {expr} Operator: {operator} Terms: {terms}")
        left, right = terms[0], terms[1]
        if self.count_operators(left) > 0:
            # print(f"Left is a larger expr: {left}")
            left = self._build_expression(left)
            # print(
            #    f"out of left recursion. left = {left} type {type(left)}")
        if self.count_operators(right) > 0:
            # print(f"Right is a larger expr: {right}")
            right = self._build_expression(right)
            # print(
            #    f'out of right recursion right = {right} type {type(right)}')
        return Expression(left, right, operator)

    def build(self) -> Expression:
        """
        This is called by the parse() class method of the Expression class
        to initiate the build of the Expression instance.
        This method not only instantiates and return an Expression,
        but also populate their string representation attribute (_str_representation).
        """
        expr_str = self._eval_brackets(self.expression_str)
        # print(f"String after brackets evaluated: {expr_str}")
        expr = self._build_expression(expr_str)
        expr._str_representation = self.expression_str
        return expr


def main() -> None:
    """
    Demo function.
    """
    # test = "5+5/5+(5-5)/5"
    # test2 = "5/5+(5*(5+5))"
    test3 = "(5-4)/5+(5*(5+5/-2))-3-2+3*5^2-1-2-3"

    expr = Expression.parse(test3)
    print(f"Demo complex expression: {expr} = {expr.calculate()}")
    print(f"Expected result (using eval()): {eval(str(expr).replace('^', '**'))}")


if __name__ == "__main__":
    main()
