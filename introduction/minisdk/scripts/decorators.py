some_list = []

def some_decorator(function_arg):
    some_list.append(function_arg)

@some_decorator
def some_function(some_arg):
    # do something
    pass

print(some_list)

import time

def another_decorator(function_arg):
    def wrapper():
        t0 = time.time()
        print(f"About to run the function {function_arg.__name__}")
        result = function_arg()
        print(f"Function {function_arg.__name__} took {time.time()-t0:.4f} sec to run")
        return result
    return wrapper

@another_decorator
def another_function():
    return sum(x for x in range(100000))

print(another_function())