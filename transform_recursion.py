import ast
import inspect
import textwrap
import types

class TailRecursionTransformer(ast.NodeTransformer):
    """
    This AST transformer can handle *either* a top-level 'if' statement
    OR a top-level 'match' statement with exactly one tail call case.
    
    Pattern handled (conceptually):
    
    def func(...):
        if <condition>:
            return <base_expr>
        return func(<updated_args>)

    OR

    def func(...):
        match <expr>:
            case <pattern1>:
                return <base_expr1>
            ...
            case _:
                return func(<updated_args>)
    """

    def __init__(self, func_name):
        super().__init__()
        self.func_name = func_name

    def visit_FunctionDef(self, node):
        if node.name != self.func_name:
            return node  # Only transform the targeted function

        # Try transforming an if-based tail recursion first
        new_body = self._maybe_transform_if_tail_recursion(node)
        if new_body is not None:
            node.body = new_body
            return node

        # Otherwise, try transforming a match-based tail recursion
        new_body = self._maybe_transform_match_tail_recursion(node)
        if new_body is not None:
            node.body = new_body
            return node

        return node  # No transformation applied

    def _maybe_transform_if_tail_recursion(self, funcdef_node):
        """
        Look for a 2-statement function body:
           if <cond>:
               return <base_expr>
           return func(<updated_args>)
        Rewrite it into a `while True:` loop.
        """
        if len(funcdef_node.body) != 2:
            return None
        
        if_stmt = funcdef_node.body[0]
        return_stmt = funcdef_node.body[1]

        # Check for the pattern: top-level if + tail-call return
        if not (isinstance(if_stmt, ast.If) and isinstance(return_stmt, ast.Return)):
            return None

        # The if-stmt body must be a single return
        if len(if_stmt.body) != 1 or not isinstance(if_stmt.body[0], ast.Return):
            return None
        if if_stmt.orelse:
            # We only handle if with no else / elif
            return None

        # The second statement must be a tail call: return <func>(...)
        if not isinstance(return_stmt.value, ast.Call):
            return None
        call_node = return_stmt.value
        if not (isinstance(call_node.func, ast.Name) and call_node.func.id == self.func_name):
            return None

        # Everything checks out; build the loop
        condition_check = ast.If(
            test=if_stmt.test,
            body=[if_stmt.body[0]],  # The 'return base_expr'
            orelse=[]
        )

        assignment = self._make_assignment_from_call(funcdef_node, call_node)
        if assignment is None:
            return None

        while_node = ast.While(
            test=ast.Constant(value=True),  # `while True:`
            body=[condition_check, assignment],
            orelse=[]
        )

        return [while_node]

    def _maybe_transform_match_tail_recursion(self, funcdef_node):
        """
        Look for a 1-statement function body:
            match <expr>:
                case <pattern1>:
                    return <base_expr1>
                ...
                case _:
                    return func(<updated_args>)
        Rewrite it into a `while True:` loop.
        """
        if len(funcdef_node.body) != 1:
            return None
        
        match_stmt = funcdef_node.body[0]
        if not isinstance(match_stmt, ast.Match):
            return None

        # We expect exactly one case whose body does a tail call to the same function.
        tail_call_case_idx = -1
        for i, match_case in enumerate(match_stmt.cases):
            if len(match_case.body) == 1 and isinstance(match_case.body[0], ast.Return):
                maybe_call = match_case.body[0].value
                if (isinstance(maybe_call, ast.Call)
                    and isinstance(maybe_call.func, ast.Name)
                    and maybe_call.func.id == self.func_name):
                    # Found the tail call
                    if tail_call_case_idx != -1:
                        # Multiple tail calls not supported in this simplistic approach
                        return None
                    tail_call_case_idx = i
        
        if tail_call_case_idx == -1:
            # No tail call found
            return None

        # We'll transform the tail-call case into assignment of updated args
        tail_call_case = match_stmt.cases[tail_call_case_idx]
        return_stmt = tail_call_case.body[0]
        call_node = return_stmt.value
        assignment = self._make_assignment_from_call(funcdef_node, call_node)
        if assignment is None:
            return None

        # Replace the tail call return with that assignment
        tail_call_case.body = [assignment]

        # Wrap the entire match statement in `while True:`
        while_node = ast.While(
            test=ast.Constant(value=True),
            body=[match_stmt],
            orelse=[]
        )
        return [while_node]

    def _make_assignment_from_call(self, funcdef_node, call_node):
        """
        Build an ast.Assign that reassigns the function's parameters from the call arguments.
        
        For example: 
          return func(n-1, acc*n)
        becomes:
          n, acc = (n-1), (acc*n)
        """
        param_names = [arg.arg for arg in funcdef_node.args.args]
        if len(call_node.args) != len(param_names):
            return None  # Mismatched parameter count

        target_list = []
        value_list = []
        for pname, arg in zip(param_names, call_node.args):
            target_list.append(ast.Name(id=pname, ctx=ast.Store()))
            value_list.append(arg)

        assignment = ast.Assign(
            targets=[ast.Tuple(elts=target_list, ctx=ast.Store())],
            value=ast.Tuple(elts=value_list, ctx=ast.Load())
        )
        return assignment


def tail_recursive(func):
    """
    Decorator that transforms a simple tail-recursive function into
    an iterative version at definition time. Supports top-level if or match.
    
    Usage:
        @tail_recursive
        def factorial(n, acc=1):
            match n:
                case 0 | 1:
                    return acc
                case _:
                    return factorial(n - 1, acc * n)
                    
    OR:
    
        @tail_recursive
        def factorial(n, acc=1):
            if n <= 1:
                return acc
            return factorial(n - 1, acc * n)
    """
    print("first")
    source = inspect.getsource(func)
    # dedent in case the function is indented (e.g. in a class or nested function)
    source = textwrap.dedent(source)
    
    print("parsing")
    tree = ast.parse(source)
    transformer = TailRecursionTransformer(func.__name__)
    transformed_tree = transformer.visit(tree)
    ast.fix_missing_locations(transformed_tree)
    
    print("before compile")
    code_obj = compile(transformed_tree, filename="<ast>", mode="exec")

    # We'll run the code in the original function's globals, so it can reference the same environment
    namespace = {}
    exec(code_obj, func.__globals__, namespace)
    new_func = namespace[func.__name__]
    
    # Preserve metadata
    new_func.__doc__ = func.__doc__
    new_func.__name__ = func.__name__
    
    return new_func


# Example 1: match-based tail-recursive factorial
@tail_recursive
def factorial_match(n, acc=1):
    """Tail-recursive factorial using match."""
    match n:
        case 0 | 1:
            return acc
        case _:
            return factorial_match(n - 1, acc * n)

# Example 2: if-based tail-recursive factorial
@tail_recursive
def factorial_if(n, acc=1):
    """Tail-recursive factorial using if."""
    if n <= 1:
        return acc
    return factorial_if(n - 1, acc * n)

# -----------------------------
# DEMO USAGE (Python 3.10+)
# -----------------------------
if __name__ == "__main__":
    print("factorial_match(5) =", factorial_match(5))  # 120

    print("factorial_if(5) =", factorial_if(5))  # 120

    # Check large input doesn't cause recursion error
    print("factorial_match(1000) =", factorial_match(1000))
    print("factorial_if(1000) =", factorial_if(1000))
