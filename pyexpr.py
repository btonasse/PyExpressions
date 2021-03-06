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
import logging
from enum import Enum
from typing import Any, Tuple, Union

# Add a null handler to the logger in case this becomes an imported module
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Todo:
# Add proper tests


class Operator(Enum):
    """
    Enum class to facilitate the use of arithmetic operators.
    Members are ordered according to the mathematical order of operations.
    Has the following utility class methods:
        has_value(val):
            Checks if val is one of the values of this enum.
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
        self,
        left: Union[Expression, str],
        right: Union[Expression, str],
        operator: str,
        is_within_brackets: bool = False,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.no_funny_stuff(left, right, operator)
        self.left = left
        self.right = right
        # Replace standard representation of exponentiation with the python ** operator
        self.operator = operator
        self._str_representation = str(left) + operator + str(right)
        if is_within_brackets:
            self._str_representation = "(" + self._str_representation + ")"

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
        result = eval(left + self.operator.replace("^", "**") + right)
        self.logger.debug(
            "Calculating expression: %s",
            left + self.operator + right + " = " + str(result),
        )
        return result

    def __str__(self) -> str:
        return self._str_representation

    def __repr__(self) -> str:
        return f"<Expression: {self._str_representation}>"

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
    operator_regex: str = r"(?<!^)(?<!\/|\(|-)\%"
    # Get operators in ascending order of priority
    operators = [member.value for member in reversed(list(Operator))]

    def __init__(self, expr: str) -> None:
        self.expression_str = expr
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _apply_mask(match_object: re.Match) -> str:
        """
        Replaces a regex match with a string of B's of the same length.
        This method is called by _mask_brackets().
        """
        match = match_object.group()
        mask = "B" * len(match)
        return mask

    @classmethod
    def _mask_brackets(cls, expr: str) -> str:
        """
        Finds all bracket expressions in an expression string
        and replaces them with a string of B's of the same length.
        This needs to be called before calling any other methods
        that read of manipulate expression terms and operators,
        so that the operators inside the bracket expressions
        don't interfere with those methods.
        """
        new_expr_str = re.sub(cls.bracket_regex, cls._apply_mask, expr)
        if "(" in new_expr_str:
            new_expr_str = cls._mask_brackets(new_expr_str)
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
        masked_expr = cls._mask_brackets(expr)
        # Compile pattern, replacing % with the actual operator being searched
        pat = cls._compile_operator_regex(operator)
        # Get index of rightmost match
        i = list(re.finditer(pat, masked_expr))[-1].start()
        # Split string at that index, omitting the operator itself
        left, right = expr[:i], expr[i + 1 :]
        return left, right

    @classmethod
    def _get_lowest_priority_operator(cls, expr: str) -> str:
        """
        Finds the lowest priority operator present in a given expression string.
        """
        masked_expr = cls._mask_brackets(expr)
        for operator in cls.operators:
            pat = cls._compile_operator_regex(operator)
            if re.search(pat, masked_expr):
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

    def _build_expression(
        self, expr: str, is_within_brackets: bool = False
    ) -> Expression:
        """
        Recursively build the expression tree, from the lowest to the highest priority operators.
        """
        operator = self._get_lowest_priority_operator(expr)
        terms = self.parse_terms(expr, operator)
        self.logger.debug(
            "Expression: %s | Operator: '%s' | Terms: %s", expr, operator, terms
        )
        left, right = terms[0], terms[1]
        if self.count_operators(left) > 0:
            if left.startswith("(") and left.endswith(")"):
                left = self._build_expression(left[1:-1], True)
            else:
                left = self._build_expression(left)
        if self.count_operators(right) > 0:
            if right.startswith("(") and right.endswith(")"):
                right = self._build_expression(right[1:-1], True)
            else:
                right = self._build_expression(right)
        return Expression(left, right, operator, is_within_brackets)

    def build(self) -> Expression:
        """
        This is called by the parse() class method of the Expression class
        to initiate the build of the Expression instance.
        This method not only instantiates and return an Expression,
        but also populate their string representation attribute (_str_representation).
        """
        try:
            expr = self._build_expression(self.expression_str)
        except TypeError as err:
            raise ValueError(
                "Failed to build expression. Expression string might be invalid."
            ) from err
        return expr


def create_logger() -> logging.Logger:
    """
    Configure top-level logger, which is named after __name__
    and has two separate handlers:
        A console handler for warnings and above
        A file hander for debugging
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    file_handler = logging.FileHandler("pyexpr.log", "w", "utf-8")
    file_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def main() -> None:
    """
    Demo function.
    """
    logger = create_logger()

    demo = "(5-4)/5+(5*(5+5/-2))-3-2+3*5^2-1-2-3"
    logger.info("Parsing demo expression: %s", demo)
    expr = Expression.parse(demo)
    logger.info("Expression parsed. Evaluating result...")
    result = expr.calculate()
    logger.info("Result = %s", result)
    logger.info("Comparing to result of eval()...")
    eval_result = eval(demo.replace("^", "**"))
    logger.info("Eval result = %s", eval_result)
    print(f"Demo expression: {expr} = {result}")
    print(f"Expected result (using eval()): {eval_result}")


if __name__ == "__main__":
    main()
