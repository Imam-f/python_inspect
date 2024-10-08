import ast
import inspect

# Path to the script file
script_path = 'c_sample.py'

# Parse the script
with open(script_path, "r") as file:
    tree = ast.parse(file.read())

# Get all class names
class_names = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]
print("Classes found:", class_names)

# Import the module to retrieve class source code
import c_sample

# Use inspect to get the full source code of each class
class_sources = {name: inspect.getsource(getattr(c_sample, name)) for name in class_names}

# Print each class source code
for class_name, source in class_sources.items():
    print(f"\nClass: {class_name}\n")
    print(source)

"""
Classes found: ['A', 'B', 'C']

Class: A

class A:
    class_var_A = 1

    def __init__(self):
        self.instance_var_A = 'A'

    def method_a(self):
        pass


Class: B

class B(A):
    class_var_B = 2

    def __init__(self):
        super().__init__()
        self.instance_var_B = 'B'

    def method_b(self):
        pass


Class: C

class C(B):
    class_var_C = 3

    def __init__(self):
        super().__init__()
        self.instance_var_C = 'C'

    def method_c(self):
        pass
"""