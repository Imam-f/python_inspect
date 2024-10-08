def inspect_function(func):
    print(f"Function Name: {func.__name__}")
    print(f"Qualified Name: {func.__qualname__}\n")
    
    # Docstring
    print("Docstring:")
    print(f"  {func.__doc__}\n" if func.__doc__ else "  No docstring available.\n")
    
    # Code object
    print("Code Object:")
    print(f"  Argument Count: {func.__code__.co_argcount}")
    print(f"  Positional Arguments: {func.__code__.co_varnames[:func.__code__.co_argcount]}")
    print(f"  Keyword-only Arguments Count: {func.__code__.co_kwonlyargcount}")
    print(f"  Local Variables: {func.__code__.co_varnames}")
    print(f"  Constants: {func.__code__.co_consts}")
    print(f"  Free Variables: {func.__code__.co_freevars}\n")
    
    # Defaults
    print("Defaults:")
    print(f"  Positional Defaults: {func.__defaults__}")
    print(f"  Keyword-only Defaults: {func.__kwdefaults__}\n")
    
    # Annotations
    print("Annotations:")
    if func.__annotations__:
        for key, value in func.__annotations__.items():
            print(f"  {key}: {value}")
    else:
        print("  No annotations.")
    print()
    
    # Closure
    print("Closure:")
    if func.__closure__:
        for i, cell in enumerate(func.__closure__):
            print(f"  Free variable {i}: {cell.cell_contents}")
    else:
        print("  No closure (not a closure or no free variables).\n")
    
    # Globals
    print("Globals:")
    if func.__globals__:
        print(f"  Accessible globals count: {len(func.__globals__)}")
    print()

# Example usage with a closure
def outer(x):
    y = 10
    def inner(z):
        return x + y + z
    return inner

# Get the closure
closure_func = outer(5)
inspect_function(closure_func)

"""
Function Name: inner
Qualified Name: outer.<locals>.inner

Docstring:
  No docstring available.

Code Object:
  Argument Count: 1
  Positional Arguments: ('z',)
  Keyword-only Arguments Count: 0
  Local Variables: ('z',)
  Constants: (None,)
  Free Variables: ('x', 'y')

Defaults:
  Positional Defaults: None
  Keyword-only Defaults: None

Annotations:
  No annotations.

Closure:
  Free variable 0: 5
  Free variable 1: 10
Globals:
  Accessible globals count: 12
"""