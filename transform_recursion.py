import ast
import inspect
import textwrap
import types

class TailRecursionTransformer(ast.NodeTransformer):
    """
    This AST transformer can handle *either* a top-level 'if' statement
    OR a top-level 'match' statement with a single fallback case that
    does the tail call.
    
    Pattern handled:
    
    def func(...):
        match <expr>:
            case <pattern1>:
                return <base_expr1>
            case <pattern2>:
                return <base_expr2>
            ...
            case _:
                return func(<updated_args>)
                
    OR
    
    def func(...):
        if <condition>:
            return <base_expr>
        return func(<updated_args>)
    """
    
    def __init__(self, func_name):
        super().__init__()
        self.func_name = func_name

    def visit_FunctionDef(self, node):
        if node.name != self.func_name:
            return node  # only transform the function we're targeting
        
        # We expect exactly one top-level statement that is either:
        #   1) an if-statement with a single return in body, and a single tail-call return afterwards
        #   2) or a match-statement with multiple 'case' arms, exactly one of which does the tail call
        #
        # Then the function must have a 'return func(...)' tail call somewhere.
        #
        # For demonstration, let's allow the function body to have either:
        #   1) two statements (the if + return pattern)
        #   2) a single match statement
        #
        # We transform them into a single `while True:` that replicates the logic.

        new_body = self._maybe_transform_if_tail_recursion(node)
        if new_body is not None:
            node.body = new_body
            return node
        
        new_body = self._maybe_transform_match_tail_recursion(node)
        if new_body is not None:
            node.body = new_body
            return node
        
        return node  # no transformation

    def _maybe_transform_if_tail_recursion(self, node):
        """
        Attempt to transform a function with the pattern:
        
            if <condition>:
                return <base_expr>
            return func(<updated_args>)
            
        into:
        
            while True:
                if <condition>:
                    return <base_expr>
                # reassign ...
        """
        if len(node.body) != 3:
            return None
        
        if_stmt = node.body[1]
        return_stmt = node.body[2]
        
        if not (isinstance(if_stmt, ast.If) and isinstance(return_stmt, ast.Return)):
            return None
        
        # Check if the if-statement has exactly one return statement in its body
        if len(if_stmt.body) != 1 or not isinstance(if_stmt.body[0], ast.Return):
            return None
        if if_stmt.orelse:
            # We only handle if with no else
            return None
        
        # Check if the second statement is a tail call to the same function
        if not isinstance(return_stmt.value, ast.Call):
            return None
        call_node = return_stmt.value
        if not (isinstance(call_node.func, ast.Name) and call_node.func.id == self.func_name):
            return None
        
        # If we've gotten here, we have the pattern we're looking for.
        condition_check = ast.If(
            test=if_stmt.test,
            body=[if_stmt.body[0]],
            orelse=[]
        )
        
        assignment = self._make_assignment_from_call(node, call_node)
        if assignment is None:
            return None
        
        while_node = ast.While(
            test=ast.Constant(value=True),
            body=[condition_check, assignment],
            orelse=[]
        )
        return [while_node]

    def _maybe_transform_match_tail_recursion(self, node):
        """
        Attempt to transform a function with a single top-level match statement, e.g.
        
            match <expr>:
                case <pattern1>:
                    return <base_expr1>
                case <pattern2>:
                    return <base_expr2>
                ...
                case _:
                    return func(<updated_args>)
                    
        We'll convert it to:
        
            while True:
                match <expr>:
                    case <pattern1>:
                        return <base_expr1>
                    case <pattern2>:
                        return <base_expr2>
                    ...
                    case _:
                        # reassign ...
        """
        if len(node.body) != 2:
            return None
        
        match_stmt = node.body[1]
        if not isinstance(match_stmt, ast.Match):
            return None
        
        # We expect exactly one case whose body is a tail call, and one or more that are base-case returns
        # We'll parse the match statement to see if it fits the pattern
        tail_call_case_idx = -1
        for idx, match_case in enumerate(match_stmt.cases):
            if len(match_case.body) == 1 and isinstance(match_case.body[0], ast.Return):
                ret = match_case.body[0].value
                if isinstance(ret, ast.Call) and isinstance(ret.func, ast.Name) and ret.func.id == self.func_name:
                    # found the tail call
                    if tail_call_case_idx != -1:
                        # multiple tail calls not supported
                        return None
                    tail_call_case_idx = idx
        
        if tail_call_case_idx == -1:
            # no tail call found
            return None
        
        # Construct a new 'while True:' containing a single match block.
        # Inside that match block, all cases remain the same *except* the tail call case
        # is replaced with an assignment statement (param re-bind).
        
        # We'll figure out the function's parameter names:
        param_names = [arg.arg for arg in node.args.args]
        
        # The tail call case (match_stmt.cases[tail_call_case_idx]) calls the function with updated arguments
        tail_call_case = match_stmt.cases[tail_call_case_idx]
        return_stmt = tail_call_case.body[0]  # the Return node
        call_node = return_stmt.value
        assignment = self._make_assignment_from_call(node, call_node)
        if assignment is None:
            return None
        
        # Replace the tail call return with that assignment
        tail_call_case.body = [assignment]
        
        # Wrap this entire match in `while True: match <expr>:` ...
        while_node = ast.While(
            test=ast.Constant(value=True),
            body=[match_stmt],
            orelse=[]
        )
        return [while_node]

    def _make_assignment_from_call(self, funcdef_node, call_node):
        """
        Build an ast.Assign that reassigns the function parameters from the call arguments.
        If the call has mismatch of param count, return None.
        
        For example, if the tail call is:
            return func_name(n-1, acc*n)
            
        we build an assignment:
            n, acc = (n-1), (acc*n)
        """
        param_names = [arg.arg for arg in funcdef_node.args.args]
        if len(call_node.args) != len(param_names):
            return None
        
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
    source = inspect.getsource(func)
    # dedent in case the function is indented (e.g. in a class or nested function)
    # print(*source)
    source = "\n".join(str(textwrap.dedent(source)).split("\n")[1:])

    tree = ast.parse(source)
    transformer = TailRecursionTransformer(func.__name__)
    transformed_tree = transformer.visit(tree)
    ast.fix_missing_locations(transformed_tree)
    
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
