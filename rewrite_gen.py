import ast
import inspect
import textwrap
from typing import Any, Dict, List, Optional, Tuple
import json
import pickle


def code_transform_generator(func):
    """
    Transform a generator function by analyzing its source code
    and creating a state machine that can be serialized at yield boundaries.
    """
    
    # Get and clean the source code
    source = inspect.getsource(func)
    source = textwrap.dedent(source)
    
    # Parse the AST
    tree = ast.parse(source)
    func_node = tree.body[0]
    
    # Extract parameter names
    param_names = [arg.arg for arg in func_node.args.args]
    
    # Find local variables and yield statements
    local_vars = set(param_names)  # Parameters are local vars
    yield_locations = []
    
    class CodeAnalyzer(ast.NodeVisitor):
        def __init__(self):
            self.in_function = False
            self.statement_index = 0
            
        def visit_FunctionDef(self, node):
            if node.name == func.__name__:
                self.in_function = True
                self.analyze_body(node.body)
                self.in_function = False
        
        def analyze_body(self, body):
            for i, stmt in enumerate(body):
                self.statement_index = i
                self.visit(stmt)
        
        def visit_Assign(self, node):
            if self.in_function:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        local_vars.add(target.id)
            self.generic_visit(node)
        
        def visit_AugAssign(self, node):
            if self.in_function and isinstance(node.target, ast.Name):
                local_vars.add(node.target.id)
            self.generic_visit(node)
        
        def visit_For(self, node):
            if self.in_function and isinstance(node.target, ast.Name):
                local_vars.add(node.target.id)
            self.generic_visit(node)
        
        def visit_Yield(self, node):
            if self.in_function:
                yield_locations.append(self.statement_index)
            self.generic_visit(node)
    
    analyzer = CodeAnalyzer()
    analyzer.visit(tree)
    
    # Convert function body to source code segments
    func_body = func_node.body
    segments = []
    
    # Simple approach: convert each statement to string
    for i, stmt in enumerate(func_body):
        code = ast.unparse(stmt)
        segments.append((i, code, any(isinstance(n, ast.Yield) for n in ast.walk(stmt))))
    
    # Create the state machine class
    class GeneratorStateMachine:
        def __init__(self, *args, **kwargs):
            # Store arguments
            self._args = args
            self._kwargs = kwargs
            
            # Initialize state
            self._state = 0
            self._exhausted = False
            self._current_value = None
            self._yield_count = 0
            
            # Initialize local variables
            for var in local_vars:
                setattr(self, var, None)
            
            # Bind parameters
            for i, param in enumerate(param_names):
                if i < len(args):
                    setattr(self, param, args[i])
            
            for key, value in kwargs.items():
                if key in param_names:
                    setattr(self, key, value)
        
        def __iter__(self):
            return self
        
        def __next__(self):
            if self._exhausted:
                raise StopIteration
            
            # Execute statements until we hit a yield or exhaust
            while self._state < len(segments):
                stmt_index, code, has_yield = segments[self._state]
                
                try:
                    if has_yield:
                        # Execute and capture yield value
                        result = self._execute_with_yield(code)
                        self._state += 1
                        self._yield_count += 1
                        if result is not None:
                            self._current_value = result
                            return result
                    else:
                        # Execute without yield
                        self._execute_statement(code)
                        self._state += 1
                except StopIteration:
                    self._exhausted = True
                    raise
            
            # If we get here, we've exhausted all statements
            self._exhausted = True
            raise StopIteration
        
        def _execute_statement(self, code):
            """Execute a non-yielding statement"""
            # Create execution context with local variables
            local_context = {var: getattr(self, var) for var in local_vars}
            
            try:
                exec(code, globals(), local_context)
                
                # Update instance variables from execution context
                for var in local_vars:
                    if var in local_context:
                        setattr(self, var, local_context[var])
                        
            except Exception as e:
                # Handle control flow statements that might cause issues
                if "break" in str(e) or "continue" in str(e):
                    # These need special handling in state machines
                    pass
                else:
                    raise
        
        def _execute_with_yield(self, code):
            """Execute a statement containing yield and return the yielded value"""
            local_context = {var: getattr(self, var) for var in local_vars}
            
            # For yield statements, we need to capture the yielded value
            # This is a simplified approach - in practice, you'd need more sophisticated parsing
            
            if 'yield' in code and not ('while' in code or 'for' in code or 'if' in code):
                # Simple yield statement
                yield_expr = code.strip()
                if yield_expr.startswith('yield '):
                    expr = yield_expr[6:].strip()  # Remove 'yield '
                    try:
                        result = eval(expr, globals(), local_context)
                        # Update instance variables
                        for var in local_vars:
                            if var in local_context:
                                setattr(self, var, local_context[var])
                        return result
                    except:
                        return None
            else:
                # Complex statement with yield - need to handle control flow
                # This is where it gets tricky - we'd need to parse the control structure
                # For now, fall back to the original generator approach
                return self._fallback_execution(code)
        
        def _fallback_execution(self, code):
            """Fallback for complex yield statements"""
            # Create a temporary generator to execute this part
            temp_func_code = f"""
def temp_gen():
    {chr(10).join(f'    {var} = {repr(getattr(self, var))}' for var in local_vars)}
    {code}
"""
            
            try:
                exec(temp_func_code, globals())
                temp_gen = globals()['temp_gen']()
                result = next(temp_gen)
                
                # This is incomplete - we'd need to capture state changes
                return result
            except:
                return None
        
        def get_state(self):
            """Get serializable state"""
            state = {
                'args': self._args,
                'kwargs': self._kwargs,
                'state': self._state,
                'exhausted': self._exhausted,
                'current_value': self._current_value,
                'yield_count': self._yield_count,
            }
            
            # Add local variables
            for var in local_vars:
                state[f'var_{var}'] = getattr(self, var)
            
            return state
        
        def set_state(self, state_dict):
            """Restore from serializable state"""
            self._args = state_dict['args']
            self._kwargs = state_dict['kwargs']
            self._state = state_dict['state']
            self._exhausted = state_dict['exhausted']
            self._current_value = state_dict['current_value']
            self._yield_count = state_dict['yield_count']
            
            # Restore local variables
            for var in local_vars:
                key = f'var_{var}'
                if key in state_dict:
                    setattr(self, var, state_dict[key])
        
        def to_json(self):
            return json.dumps(self.get_state(), default=str)
        
        def from_json(self, json_str):
            self.set_state(json.loads(json_str))
        
        def to_pickle(self):
            return pickle.dumps(self.get_state())
        
        def from_pickle(self, pickle_bytes):
            self.set_state(pickle.loads(pickle_bytes))
        
        def __repr__(self):
            return f"<{func.__name__}StateMachine state={self._state} yields={self._yield_count}>"
    
    # Store reference to original function and metadata
    GeneratorStateMachine._original_func = func
    GeneratorStateMachine._segments = segments
    GeneratorStateMachine._local_vars = local_vars
    GeneratorStateMachine.__name__ = f"{func.__name__}StateMachine"
    
    return GeneratorStateMachine


# Simpler, more practical approach using bytecode stepping
def practical_serializable_generator(func):
    """
    A more practical approach that creates serializable checkpoints
    by tracking generator state and recreating execution context.
    """
    
    class PracticalStateMachine:
        def __init__(self, *args, **kwargs):
            self.func = func
            self.args = args
            self.kwargs = kwargs
            self.values_yielded = []  # Track all yielded values
            self.step_count = 0
            self.exhausted = False
            self.generator = None
            self._reset()
        
        def _reset(self):
            """Create fresh generator"""
            self.generator = self.func(*self.args, **self.kwargs)
        
        def __iter__(self):
            return self
        
        def __next__(self):
            if self.exhausted:
                raise StopIteration
            
            try:
                value = next(self.generator)
                self.values_yielded.append(value)
                self.step_count += 1
                return value
            except StopIteration:
                self.exhausted = True
                raise
        
        def get_state(self):
            """Get state that allows reconstruction"""
            return {
                'func_name': self.func.__name__,
                'args': self.args,
                'kwargs': self.kwargs,
                'step_count': self.step_count,
                'values_yielded': self.values_yielded,
                'exhausted': self.exhausted
            }
        
        def set_state(self, state_dict):
            """Restore state by replaying execution"""
            self.args = state_dict['args']
            self.kwargs = state_dict['kwargs']
            self.step_count = state_dict['step_count']
            self.values_yielded = state_dict['values_yielded']
            self.exhausted = state_dict['exhausted']
            
            if not self.exhausted and self.step_count > 0:
                # Recreate generator and advance to correct position
                self._reset()
                for _ in range(self.step_count):
                    try:
                        next(self.generator)
                    except StopIteration:
                        self.exhausted = True
                        break
        
        def to_json(self):
            return json.dumps(self.get_state(), default=str)
        
        def from_json(self, json_str):
            self.set_state(json.loads(json_str))
        
        def clone_at_state(self):
            """Create a copy at current state"""
            new_instance = PracticalStateMachine(*self.args, **self.kwargs)
            new_instance.set_state(self.get_state())
            return new_instance
    
    return PracticalStateMachine


# Examples
@code_transform_generator
def countdown(n):
    while n > 0:
        yield n
        n -= 1

@practical_serializable_generator
def fibonacci(count):
    a, b = 0, 1
    for i in range(count):
        yield a
        a, b = b, a + b

@practical_serializable_generator
def complex_generator(data):
    total = 0
    for i, item in enumerate(data):
        total += item
        if i % 2 == 0:
            yield f"Even index {i}: sum={total}"
        else:
            yield f"Odd index {i}: sum={total}"


# Demo
if __name__ == "__main__":
    print("=== Code Transform Generator ===")
    
    try:
        counter = countdown(5)
        print("Local vars detected:", counter._local_vars)
        print("Segments:", len(counter._segments))
        
        print("Values:", next(counter), next(counter))
        
        # Serialize
        state_json = counter.to_json()
        print("State serialized")
        
        # Restore
        counter2 = countdown(10)
        counter2.from_json(state_json)
        print("Restored values:", next(counter2), next(counter2))
        
    except Exception as e:
        print(f"Code transform error: {e}")
        print("The code transform approach needs more work for complex control flow")
    
    print("\n=== Practical Serializable Generator ===")
    
    fib = fibonacci(8)
    values = [next(fib), next(fib), next(fib)]
    print("Fibonacci:", values)
    
    # Clone at current state
    fib_clone = fib.clone_at_state()
    
    print("Original continues:", next(fib))
    print("Clone continues:", next(fib_clone))
    
    # Test complex generator
    complex_gen = complex_generator([1, 2, 3, 4, 5])
    print("\nComplex generator:")
    for _ in range(3):
        print(next(complex_gen))
    
    # Serialize and restore
    state = complex_gen.get_state()
    complex_gen2 = complex_generator([])  # Will be overridden
    complex_gen2.set_state(state)
    print("Restored complex:", next(complex_gen2))