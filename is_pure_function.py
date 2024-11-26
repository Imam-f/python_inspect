import inspect
import dis
import builtins

def is_pure_function(func, _analyzed_funcs=None):
    """
    Check if a function is pure by analyzing bytecode, closure variables, and recursively checking function calls.
    
    Args:
        func (callable): Function to check for purity
        _analyzed_funcs (set, optional): Internal set to track already analyzed functions and prevent infinite recursion
    
    Returns:
        bool: True if function appears to be pure, False otherwise
    """
    # Initialize set of analyzed functions to prevent infinite recursion
    if _analyzed_funcs is None:
        _analyzed_funcs = set()
    
    # Prevent analyzing the same function multiple times
    if func in _analyzed_funcs:
        return True
    _analyzed_funcs.add(func)
    
    # Check closure variables
    closure_vars = inspect.getclosurevars(func)
    
    # Check if any non-read-only closure variables exist
    for var, value in closure_vars.nonlocals.items():
        if not isinstance(value, (int, float, str, tuple, frozenset, bytes, type(None))):
            return False
    
    for var, value in closure_vars.globals.items():
        # Allow only immutable globals and builtins
        if not (isinstance(value, (int, float, str, tuple, frozenset, bytes, type(None))) or 
                hasattr(builtins, var)):
            return False
    
    # Analyze bytecode
    code = dis.Bytecode(func)
    
    # Tracks function calls to recursively check
    function_calls = []
    
    impure_ops = {
        'STORE_DEREF',   # Modifying closure variable
        'STORE_GLOBAL',  # Modifying global variable
    }
    
    for instr in code:
        # Track function calls for recursive purity check
        if instr.opname == 'CALL_FUNCTION':
            # Try to get the function being called
            try:
                # This is a simplified approach and might not work for all cases
                frame = inspect.currentframe()
                function_calls.append(frame.f_locals.get(instr.argval))
            except Exception:
                # If we can't determine the function, assume it might not be pure
                return False
        
        # Check for impure operations
        if instr.opname in impure_ops:
            return False
    
    # Recursively check purity of called functions
    for called_func in function_calls:
        if called_func and callable(called_func):
            try:
                if not is_pure_function(called_func, _analyzed_funcs):
                    return False
            except Exception:
                return False
    
    return True
    # Verify consistent output
    # try:
    #     inputs = [1, 'test', (1, 2), None]
    #     results = [func(*[input]) for input in inputs]
    #     return len(set(map(str, results))) == 1
    # except Exception:
    #     return False

# Example usage
def pure_math_func(x):
    return x * 2

def impure_func():
    global x
    x += 1
    return x

def pure_complex_func(x):
    def helper(y):
        return y * 2
    return helper(x) + len(str(x))

def create_pure_closure():
    x = 10  # Immutable value in closure
    def pure_func(y):
        return y + x
    return pure_func

def create_impure_closure():
    x = [1, 2, 3]  # Mutable list in closure
    def impure_func(y):
        x.append(y)  # Modifies closure variable
        return y
    return impure_func

# Demonstration
print("pure_math_func:", is_pure_function(pure_math_func))  # Should be True
print("impure_func:", is_pure_function(impure_func))  # Should be False
print("pure_complex_func:", is_pure_function(pure_complex_func))  # Should be True
print("create_pure_closure():", is_pure_function(create_pure_closure()))  # Should be True
print("create_impure_closure():", is_pure_function(create_impure_closure()))  # Should be False