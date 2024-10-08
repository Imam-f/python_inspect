import ast
import sys

class FunctionCallGraphBuilder(ast.NodeVisitor):
    def __init__(self):
        self.current_function = '<module>'
        self.call_graph = {'<module>': set()}  # Initialize '<module>' to handle top-level calls
        self.class_methods = {}  # Maps each class to its methods
        self.class_hierarchy = {}  # Maps each class to its parent class (inheritance)
        self.function_stack = ['<module>']
        self.class_stack = []
        self.instance_methods = {}

    def visit_ClassDef(self, node):
        # Record class and parent class if present
        class_name = node.name
        parent_classes = [base.id for base in node.bases if isinstance(base, ast.Name)]
        self.class_hierarchy[class_name] = parent_classes if parent_classes else None

        # Track methods within the class
        self.class_stack.append(class_name)
        self.class_methods.setdefault(class_name, set())
        
        # Visit the class body
        self.generic_visit(node)
        
        # Pop the class stack
        self.class_stack.pop()

    def visit_FunctionDef(self, node):
        # Full function name, including class if applicable
        func_name = node.name
        if self.class_stack:
            full_func_name = f"{self.class_stack[-1]}.{func_name}"
            self.class_methods[self.class_stack[-1]].add(func_name)  # Add to class methods
        else:
            full_func_name = func_name

        # Initialize call graph entry for this function
        self.call_graph.setdefault(full_func_name, set())
        self.function_stack.append(full_func_name)
        self.current_function = full_func_name

        # Visit function body
        self.generic_visit(node)
        
        # Restore function context
        self.function_stack.pop()
        self.current_function = self.function_stack[-1] if self.function_stack else None

    def visit_Assign(self, node):
        # Capture instances assigned to variables
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            class_name = node.value.func.id
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.instance_methods[target.id] = class_name
        self.generic_visit(node)

    def visit_Call(self, node):
        # Ensure that the current function is in the call graph
        if self.current_function not in self.call_graph:
            self.call_graph[self.current_function] = set()

        func_name = self.get_called_function_name(node)
        if func_name:
            self.call_graph[self.current_function].add(func_name)
        self.generic_visit(node)

    def get_called_function_name(self, node):
        # Get the function name from a Call node
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            # Handle method calls, including inheritance
            if isinstance(node.func.value, ast.Name):
                instance_name = node.func.value.id
                if instance_name in self.instance_methods:
                    class_name = self.instance_methods[instance_name]
                    return self.resolve_method(class_name, node.func.attr)
        return None

    def resolve_method(self, class_name, method_name):
        # Recursively check class hierarchy to resolve method calls
        if class_name in self.class_methods and method_name in self.class_methods[class_name]:
            return f"{class_name}.{method_name}"
        elif class_name in self.class_hierarchy and self.class_hierarchy[class_name]:
            # Check parent classes if method isn't in the current class
            for parent_class in self.class_hierarchy[class_name]:
                resolved = self.resolve_method(parent_class, method_name)
                if resolved:
                    return resolved
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <source_file.py>")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, 'r') as f:
        source = f.read()

    tree = ast.parse(source, filename)
    builder = FunctionCallGraphBuilder()
    builder.visit(tree)

    for func, calls in builder.call_graph.items():
        print(f"Function '{func}' calls functions: {sorted(calls)}")

"""
Function '<module>' calls functions: ['foo']
Function 'MyClass.method1' calls functions: ['helper_function']
Function 'MyClass.method2' calls functions: []
Function 'helper_function' calls functions: []
Function 'foo' calls functions: ['MyClass', 'MyClass.method1']
"""