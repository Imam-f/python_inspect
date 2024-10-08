import ast
import sys

class FunctionCallGraphBuilder(ast.NodeVisitor):
    def __init__(self):
        self.current_function = '<module>'
        self.call_graph = {}  # Mapping from function names to sets of called functions
        self.function_stack = ['<module>']
        self.class_stack = []
        self.instance_methods = {}

    def visit_ClassDef(self, node):
        # Track the current class name
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()

    def visit_FunctionDef(self, node):
        # Determine full function name, including class if applicable
        func_name = node.name
        if self.class_stack:
            full_func_name = f"{self.class_stack[-1]}.{func_name}"
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
        # Capture instances assigned to variables within functions
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            class_name = node.value.func.id
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.instance_methods[target.id] = class_name
        self.generic_visit(node)

    def visit_Call(self, node):
        if self.current_function:
            func_name = self.get_called_function_name(node)
            if func_name:
                self.call_graph[self.current_function].add(func_name)
        self.generic_visit(node)

    def get_called_function_name(self, node):
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            # Check if the method is called on an instance of a known class
            if isinstance(node.func.value, ast.Name):
                instance_name = node.func.value.id
                if instance_name in self.instance_methods:
                    class_name = self.instance_methods[instance_name]
                    return f"{class_name}.{node.func.attr}"
            elif isinstance(node.func.value, ast.Attribute):
                return node.func.attr
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
