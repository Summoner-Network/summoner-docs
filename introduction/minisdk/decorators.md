# Python decorators

Python provides a powerful tool called a **decorator**, which allows you to modify or wrap the behavior of functions or methods. Decorators are applied using the `@` symbol, placed just above a function definition, like this:

```python
@some_decorator
def some_function(some_arg):
    # do something
    pass
```

Although this syntax might seem mysterious at first, all it really does is pass the function `some_function` as an argument to `some_decorator`. The result of that call replaces the original function.

In other words, the above is equivalent to:

```python
def some_function(some_arg):
    # do something
    pass

some_function = some_decorator(some_function)
```

## Example 1: Storing Functions in a List

Let's define a simple decorator that stores decorated functions in a list:

```python
some_list = []

def some_decorator(function_arg):
    some_list.append(function_arg)
    return function_arg
```

Now, if you apply `@some_decorator` to a function:

```python
@some_decorator
def some_function():
    pass
```

The function `some_function` will be added to `some_list`:

```python
print(some_list)
```

Output:

```
[<function some_function at 0x...>]
```

## Example 2: Measuring Execution Time

Decorators are often used to modify the behavior of a function. Here's an example that prints timing information each time the function is called:

```python
import time

def another_decorator(function_arg):
    def wrapper():
        t0 = time.time()
        print(f"About to run the function {function_arg.__name__}")
        result = function_arg()
        print(f"Function {function_arg.__name__} took {time.time() - t0:.4f} sec to run")
        return result
    return wrapper
```

Using this decorator:

```python
@another_decorator
def another_function():
    return sum(x for x in range(100000))

print(another_function())
```

Output:

```
About to run the function another_function
Function another_function took 0.0025 sec to run
4999950000
```

This pattern is widely used in logging, access control, caching, and performance monitoring.

The code used in this tutorial is available [in this script](scripts/decorators.py).

<p align="center">
  <a href="../mini_sdk.md">&laquo; Previous: The Mini SDK Concept</a> &nbsp;&nbsp;&nbsp;|
  </a>
</p>