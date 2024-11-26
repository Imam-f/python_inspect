import inspect

def hello(name):
    # return
    return f"Hello, {name}!"

# Get the source code of MyClass
function_source = inspect.getsource(hello)

# Print or use the string representation of the class declaration
hello = None
print(function_source)
print(exec(function_source))
print(hello("test"))

"""
def hello(name):
    # return
    return f"Hello, {name}!"
"""