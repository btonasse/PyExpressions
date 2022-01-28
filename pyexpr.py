import re
from string import ascii_letters
from enum import Enum
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
            raise ValueError("Operands can only be ints, floats, or other Expressions")
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
        #print(left + self.operator + right + ' = ' + str(result))
        return result

    def __str__(self) -> str:
        return self._str_representation

    """
    @classmethod
    def parse(cls, expr: str):
        treeobj = ExpressionTree(expr)
        expression = treeobj.build_expression()
        expression._str_representation = expr
        return expression
    """

    @classmethod
    def parse(cls, expr: str):
        builder = ExpressionBuilder(expr)
        expression = builder.build()
        return expression

class ExpressionBuilder:
    """
    Meta class that is not supposed to be called directly, but my the parse() method of the Expression class.
    """
    bracket_regex = r"\([^\(\)]+\)"
    #operation_regex = r"(?=(\d+\.?\d*%\d+\.?\d*))"  # Replace % with the actual escaped operand
    operators = [member.value for member in reversed(list(Operator))] # Operators is priority ascending order
    def __init__(self, expr: str):
        self._count = -1
        self._bracket_tree = {}
        self.expression_str = expr
        self._expr_hashed_brackets = self._hash_brackets(self.expression_str)
        print(self._expr_hashed_brackets, self._bracket_tree)

    def _replace_and_increment(self, matchObject: re.Match) -> str:
        self._count += 1
        replacement = ascii_letters[self._count]
        new_expr = matchObject.group().replace('(', '').replace(')', '')
        self._bracket_tree[replacement] = new_expr
        return replacement

    def _hash_brackets(self, expr: str) -> str:
        """
        Recursively hash expressions between parenthesis
        so then can be referenced later when building
        the order or operations tree
        """
        new_expr = re.sub(self.bracket_regex, self._replace_and_increment, expr)
        # print(self._tree)
        # print(new_expr)
        if "(" in new_expr:
            return self._hash_brackets(new_expr)
        return new_expr

    def _parse_terms(self, expr: str, operator: str) -> Tuple[str]:
        splitexpr = expr.rsplit(operator)
        if splitexpr[0] == expr: # No more operations found for given operator
            return None
        right = splitexpr.pop()
        left = operator.join(splitexpr)
        return left, right
    
    def _build_expression(self, expr: str) -> Expression:
        for operator in self.operators:
            terms = self._parse_terms(expr, operator)
            #print(f"Expr: {expr} Operator: {operator} Terms: {terms}")
            if not terms:
                continue
            print(f"Expr: {expr} Operator: {operator} Terms: {terms}")
            left, right = terms[0], terms[1]
            if sum((Operator.has_value(char) for char in left)) > 1:
                print(f"Left is a larger expr: {left}")
                left = self._build_expression(left)
                print(f"out of left recursion. left = {left} type {type(left)}")
            if sum((Operator.has_value(char) for char in right)) > 1:
                print(f"Right is a larger expr: {right}")
                right = self._build_expression(right)
                print(f'out of right recursion right = {right} type {type(right)}')
            if sum((Operator.has_value(char) for char in expr)) == 1: # Base case: only one operation left in expression
                # Check if term is a letter (hashed parenthesis expression)
                if left in ascii_letters:
                    print(f"Left {left} is actually {self._bracket_tree[left]}")
                    left = self._build_expression(self._bracket_tree[left])
                    print(f'out of bracket left recursion. left = {left} type {type(left)}')
                if right in ascii_letters:
                    print(f"Right {right} is actually {self._bracket_tree[right]}")
                    right = self._build_expression(self._bracket_tree[right])
                    print(f'out of bracket right recursion right = {right} type {type(right)}')
                return Expression(left, right, operator)
    
    def build(self) -> Expression:
        expr = self._build_expression(self._expr_hashed_brackets)
        expr._str_representation = self.expression_str
        return expr

class ExpressionTree:
    """
    Class to incrementally replace regex matches with a string+count.
    Replacements are tracked in a dictionary
    """

    bracket_regex = r"\([^\(\)]+\)"
    operation_regex = r"(?:(?:\d+\.?\d*)|\w)%(?:(?:\d+\.?\d*)|\w)"  # Replace % with the actual escaped operand

    def __init__(self, expr: str):
        self.expression_str = expr
        self._count = -1
        self._tree = {}
        self._root = self._hash_brackets(self.expression_str)
        for element in Operator:
            self._root = self._hash_operations(self._root, element)
        self._hash_operations_in_brackets()
        print(self._tree)

    def _replace_and_increment(self, matchObject: re.Match) -> str:
        self._count += 1
        replacement = ascii_letters[self._count]
        new_expr = matchObject.group()
        self._tree[replacement] = new_expr
        return replacement

    def _hash_brackets(self, expr: str) -> str:
        """
        Recursively hash expressions between parenthesis
        so then can be referenced later when building
        the order or operations tree
        """
        new_expr = re.sub(self.bracket_regex, self._replace_and_increment, expr)
        # print(self._tree)
        # print(new_expr)
        if "(" in new_expr:
            return self._hash_brackets(new_expr)
        return new_expr

    def _hash_operations(self, expr: str, operator: Operator) -> str:
        operator_str = operator.value
        regex = self.operation_regex.replace(
            "%", Operator.get_regex_escaped_value(operator)
        )
        new_expr = re.sub(regex, self._replace_and_increment, expr)
        # print(self._tree)
        # print(new_expr)
        if operator_str in new_expr:
            return self._hash_operations(new_expr, operator)
        return new_expr

    def _hash_operations_in_brackets(self) -> None:
        for k, v in dict(self._tree).items():
            if "(" in v:
                for element in Operator:
                    if sum((Operator.has_value(char) for char in self._tree[k])) > 1:
                        self._tree[k] = self._hash_operations(v, element)
                self._tree[k] = self._tree[k].replace("(", "").replace(")", "") # Remove unnecessary brackets from expression

    def build_expression(self) -> Expression:
        root_expr = self._tree[self._root]
        expr = self._build_node(root_expr)
        return expr

    def _parse_terms(self, expr: str) -> Tuple[str]:
        operator = re.search(r"\W", expr)[0]
        operands = expr.split(operator)
        return operands[0], operands[1], operator

    def _build_node(self, root_expr: str) -> Expression:
        left, right, operator = self._parse_terms(root_expr)
        try:
            if int(left) == float(left):
                left = int(left)
            else:
                left = float(left)
        except ValueError:
            left = self._build_node(self._tree[left])
        try:
            if int(right) == float(right):
                right = int(right)
            else:
                right = float(right)
        except ValueError:
            right = self._build_node(self._tree[right])
        return Expression(left, right, operator)


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
