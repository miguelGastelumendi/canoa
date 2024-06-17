<!--
   /* cSpell:locale en
   /* cSpell:ignore isinstance
-->

# Python Common Exceptions
>   _Annotated by Miguel Gastelumendi with the help of Gemini_
>   Last update 2024-06-17


### Common Exceptions
- `SyntaxError`: Raised when there's an error in the syntax of your code (e.g., missing colon, mismatched parentheses).
- `NameError`: Occurs when you reference a variable that hasn't been defined yet.
- `TypeError`: Thrown when an operation or function is attempted with the wrong type of arguments. This is the most likely candidate for unexpected parameter types.
- `ValueError`: Raised when an operation or function receives an argument that has the correct type but an inappropriate value (e.g., dividing by zero, converting a non-numeric string to an integer).
- `IndexError`: Indicates an attempt to access an element of a sequence (like a list or string) using an invalid index (out of bounds).
- `KeyError`: Occurs when you try to access a key that doesn't exist in a dictionary.
- `AttributeError`: Raised when you try to access an attribute (like a variable) of an object that doesn't exist.

### File-Related Exceptions

- `IOError` (deprecated in Python 3): A general base class for input/output (I/O) exceptions. In Python 3, specific exceptions like `FileNotFoundError` and `PermissionError` are used.
- `FileNotFoundError`: Thrown when a file you're trying to open doesn't exist.
- `PermissionError`: Occurs when you lack the necessary permissions to perform an operation on a file (e.g., reading from a read-only file).

### Import-Related Exceptions

- `ImportError`: Raised when you try to import a module that doesn't exist or can't be found.
- `ModuleNotFoundError`: (Python 3) A more specific exception for modules not being found.

### Iteration-Related Exceptions

- `StopIteration`: Indicates that the iteration has reached the end.

### Assertion Errors

- `AssertionError`: Used to raise an error when an assertion fails (a statement you expect to be true is found to be false).

### System-Related Exceptions

- `SystemExit`: Raised to exit the Python interpreter.

### Custom Exceptions

You can also define your own custom exceptions to handle specific error conditions in your code. This helps improve code readability and maintainability.

## Example for Unexpected Parameter Type

```python
def add(x, y):
  """Adds two numbers."""
  if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
    raise TypeError("add() only accepts numbers")
  return x + y

# Valid usage
result = add(3, 5)
print(result)  # Output: 8

# Unexpected parameter type
try:
  result = add("hello", 2)
except TypeError as e:
  print(e)  # Output: add() only accepts numbers
```

`eof`

