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
        if operator not in ['+', '-', '*', '/', '**']:
            raise ValueError(
                "Only basic arithmetic operators are valid: '+', '-', '*', '/', '**'")

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
    def parse_expression(self, expr: str):
        pass


def main():
    e = Expression(2, 5, '*')
    print(e.calculate())


if __name__ == '__main__':
    main()
