# PyExpressions

Emulate the `eval()` function, but only for representing and evaluating complex arithmetic expressions via a tree of `Expression` objects (i.e. preventing the execution of arbitrary code).

This module contains three classes:

### `Operator`:

Enum class to facilitate the use of arithmetic operators

### `Expression`:

Represents a simple expression (`left` operand + `operator` + `right` operand). Operands must be string representations of floats/ints or other `Expression` instances. Use the class method `parse()` to parse a string representation of an expression. To evaluate the expression, call the method `calculate()`.

### `ExpressionBuilder`:

Class that is used to build a tree of `Expression`s that represent complex arithmetic expressions. Should not be instantiated directly.