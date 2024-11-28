import ast
import astor
import inspect

def insert_custom_print_with_context(source_code, line_number, variables_to_print=None):
    """
    Insert a custom print function that can access local variables
    
    Args:
        source_code (str): Original source code
        line_number (int): Line number to insert print
        variables_to_print (list): List of variable names to print
    
    Returns:
        str: Modified source code with context-aware print
    """
    class ContextualPrintInserter(ast.NodeTransformer):
        def __init__(self, target_line, print_vars=None):
            self.target_line = target_line
            self.current_line = 0
            self.inserted = False
            self.print_vars = print_vars or []
        
        def visit(self, node):
            # Track current line number
            if hasattr(node, 'lineno'):
                self.current_line = node.lineno
            
            # Insert print at specific line
            if (not self.inserted and 
                self.current_line == self.target_line and 
                isinstance(node, (ast.stmt, ast.expr))):
                
                # Create custom debug print function
                debug_print_func = ast.FunctionDef(
                    name='__debug_print__',
                    args=ast.arguments(
                        posonlyargs=[],
                        args=[],
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[]
                    ),
                    body=[
                        # Create print statements for specified variables
                        ast.Expr(
                            value=ast.Call(
                                func=ast.Name(id='print', ctx=ast.Load()),
                                args=[
                                    ast.JoinedStr(
                                        values=[
                                            # Variable name
                                            ast.Constant(value=f"{var}: "),
                                            # Variable value
                                            ast.FormattedValue(
                                                value=ast.Name(id=var, ctx=ast.Load()),
                                                conversion=-1
                                            )
                                        ]
                                    )
                                    for var in self.print_vars
                                ],
                                keywords=[]
                            )
                        ),
                        # Return to maintain function structure
                        ast.Return(value=None)
                    ],
                    decorator_list=[],
                    returns=None
                )
                
                # Create call to debug print function
                debug_print_call = ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id='__debug_print__', ctx=ast.Load()),
                        args=[],
                        keywords=[]
                    )
                )
                
                # Mark as inserted to prevent multiple insertions
                self.inserted = True
                
                # Return a list with debug function and print call, followed by original node
                return [debug_print_func, debug_print_call, node]
            
            # Continue traversing the AST
            return super().visit(node)
    
    # Parse the source code into an Abstract Syntax Tree
    tree = ast.parse(source_code)
    
    # Create and apply the transformer
    transformer = ContextualPrintInserter(line_number, variables_to_print)
    modified_tree = transformer.visit(tree)
    
    # Convert modified AST back to source code
    return astor.to_source(modified_tree)

# Comprehensive Example
def demonstrate_variable_print(source_code):
    # Insert custom print for specific variables at line 3
    modified_source = insert_custom_print_with_context(
        source_code, 
        line_number=5,
        variables_to_print=['x', 'y', 'a']
    )
    
    return modified_source

# Advanced Version with More Flexibility
class AdvancedContextualPrinter:
    @staticmethod
    def insert_debug_print(
        source_code, 
        line_number, 
        variables_to_print=None, 
        print_format='detailed'
    ):
        """
        More flexible approach to inserting contextual prints
        
        Args:
            source_code (str): Original source code
            line_number (int): Line to insert print
            variables_to_print (list): Variables to print
            print_format (str): 'simple', 'detailed', or 'dict'
        
        Returns:
            str: Modified source code
        """
        class FlexiblePrintInserter(ast.NodeTransformer):
            def __init__(self, target_line, print_vars=None, format_style='detailed'):
                self.target_line = target_line
                self.current_line = 0
                self.inserted = False
                self.print_vars = print_vars or []
                self.format_style = format_style
            
            def _create_print_body(self):
                """Generate different print styles"""
                if self.format_style == 'simple':
                    # Simple print of variable values
                    return [
                        ast.Expr(
                            value=ast.Call(
                                func=ast.Name(id='print', ctx=ast.Load()),
                                args=[
                                    ast.JoinedStr(
                                        values=[
                                            ast.Constant(value=f"{var}: "),
                                            ast.FormattedValue(
                                                value=ast.Name(id=var, ctx=ast.Load()),
                                                conversion=-1
                                            )
                                        ]
                                    )
                                    for var in self.print_vars
                                ],
                                keywords=[]
                            )
                        )
                    ]
                
                elif self.format_style == 'detailed':
                    # Detailed print with more context
                    return [
                        ast.Expr(
                            value=ast.Call(
                                func=ast.Name(id='print', ctx=ast.Load()),
                                args=[
                                    ast.Constant(value=f"DEBUG: Line {self.target_line}")
                                ],
                                keywords=[]
                            )
                        ),
                        ast.Expr(
                            value=ast.Call(
                                func=ast.Name(id='print', ctx=ast.Load()),
                                args=[
                                    ast.JoinedStr(
                                        values=[
                                            ast.Constant(value=f"{var}: "),
                                            ast.FormattedValue(
                                                value=ast.Name(id=var, ctx=ast.Load()),
                                                conversion=-1
                                            )
                                        ]
                                    )
                                    for var in self.print_vars
                                ],
                                keywords=[]
                            )
                        )
                    ]
                
                elif self.format_style == 'dict':
                    # Create a dictionary of variables
                    return [
                        ast.Expr(
                            value=ast.Call(
                                func=ast.Name(id='print', ctx=ast.Load()),
                                args=[
                                    ast.Dict(
                                        keys=[ast.Constant(value=var) for var in self.print_vars],
                                        values=[
                                            ast.Name(id=var, ctx=ast.Load()) 
                                            for var in self.print_vars
                                        ]
                                    )
                                ],
                                keywords=[]
                            )
                        )
                    ]
                
                return []
            
            def visit(self, node):
                # Track current line number
                if hasattr(node, 'lineno'):
                    self.current_line = node.lineno
                
                # Insert print at specific line
                if (not self.inserted and 
                    self.current_line == self.target_line and 
                    isinstance(node, (ast.stmt, ast.expr))):
                    
                    # Create debug print function body
                    print_body = self._create_print_body()
                    
                    # Mark as inserted
                    self.inserted = True
                    
                    # Return print statements before original node
                    return print_body + [node]
                
                return super().visit(node)
        
        # Parse source code to AST
        tree = ast.parse(source_code)
        
        # Create and apply transformer
        transformer = FlexiblePrintInserter(
            line_number, 
            variables_to_print, 
            print_format
        )
        modified_tree = transformer.visit(tree)
        
        # Convert back to source code
        return astor.to_source(modified_tree)

def complex_calculation(x, y):
    a = x + 1
    b = y * 2
    result = a * b
    return result

def main():
    p = 10
    q = 20
    final = complex_calculation(p, q)
    print(final)
    return final

# Demonstration
def runner():
    # Original source code example
    import inspect
    source_code_1 = inspect.getsource(complex_calculation)
    source_code_2 = inspect.getsource(main)
    source_code = source_code_1 + "\n" + source_code_2
    
    print("Original Source Code:")
    print(source_code)
    main()
    print()

    print("Modified Source Code:")
    modified_source = demonstrate_variable_print(source_code)
    print(modified_source)
    print(exec(modified_source, globals()))
    main()

    # Different print styles
    print("\nSimple Print Style:")
    simple_source = AdvancedContextualPrinter.insert_debug_print(
        source_code, 
        line_number=5, 
        variables_to_print=['x', 'y', 'a'], 
        print_format='simple'
    )
    print(simple_source)
    print(exec(simple_source, globals()))
    main()

    print("\nDetailed Print Style:")
    detailed_source = AdvancedContextualPrinter.insert_debug_print(
        source_code, 
        line_number=5, 
        variables_to_print=['x', 'y', 'a'], 
        print_format='detailed'
    )
    print(detailed_source)
    print(exec(detailed_source, globals()))
    main()

    print("\nDictionary Print Style:")
    dict_source = AdvancedContextualPrinter.insert_debug_print(
        source_code, 
        line_number=5, 
        variables_to_print=['x', 'y', 'a'], 
        print_format='dict'
    )
    print(dict_source)
    print(exec(dict_source, globals()))
    main()

# Run the demonstration
if __name__ == '__main__':
    runner()