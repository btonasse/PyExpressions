"""
Try to generate random expressions to solve the following puzzle:
Given a list of digits 5, 5, 5, 5, 5, use basic arithmetic operators (parenthesis allowed) to form the numbers 1 to 15
"""

import random
from pyexpr import Operator

def generate_expression(numbers: list) -> str:
    operators = [x.value for x in Operator]
    expr = ''
    open_brackets = 0
    for i, number in enumerate(numbers):
        expr += random.choices([str(number), '('], [0.7, 0.3])[0]
        if expr[-1] == '(':
            open_brackets += 1
            expr += str(number)
        if open_brackets and expr[-2] != '(' and random.random() > 0.5:
            expr += ')'
            open_brackets -= 1
        if i+1 < len(numbers):
            expr += random.choice(operators)
    while open_brackets:
        expr += ')'
        open_brackets -= 1
    return expr

def test_expressions(numbers: list, goal: int) -> str:
    for i in range(1000):
        expr = generate_expression(numbers)
        print(expr)
        try:
            result = eval(expr)
        except OverflowError:
            result = 'OVERFLOW'
        except ZeroDivisionError:
            result = "ZERO DIVISION"
        print(f"Attempt {i}: {expr} = {result}")
        if result == goal:
            print(f"{expr} = {goal}!")
            return expr
    print("No expression found.")

def main():
    test = '5+5/5+(5-5)/5'

    numbers = [5,5,5,5,5]
    goal = 9

    expr = test_expressions(numbers, goal)
    


if __name__ == '__main__':
    main()
