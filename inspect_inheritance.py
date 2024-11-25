import inspect
import ast
from textwrap import dedent

def get_class_details(cls):
    """
    Prints the inheritance tree of a given class along with its methods,
    class members, and variables assigned in __init__.

    Parameters:
    cls (type): The class to inspect.

    Returns:
    None: Prints the inheritance hierarchy and details to the console.
    """
    if not inspect.isclass(cls):
        raise ValueError("Provided argument must be a class.")

    print(f"Inheritance tree and details for {cls.__name__}:\n")

    reversed_mro = cls.__mro__[::-1]
    for base in reversed_mro:
        if base is object:
            continue
        indent_level = len(reversed_mro) - cls.__mro__.index(base) - 2
        indent = "  " * indent_level
        print(f"{indent}=> {base.__name__}:")

        # Get methods
        methods = [func for func in dir(base)
                   if callable(getattr(base, func)) and not func.startswith('__') and inspect.isfunction(getattr(base, func))]
        # Get class variables
        class_vars = [var for var in base.__dict__ 
                      if not callable(base.__dict__[var]) and not var.startswith('__')]

        # Variables assigned in __init__
        init_vars = []
        if '__init__' in base.__dict__:
            init_func = base.__dict__['__init__']
            try:
                source = inspect.getsource(init_func)
                # print(source)
                tree = ast.parse(dedent(source))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Attribute):
                                if (isinstance(target.value, ast.Name) and target.value.id == 'self'):
                                    init_vars.append(target.attr)
            except (OSError, TypeError):
                pass  # Source code not available
            except IndentationError:
                print("-->")
                pass
          
        # Variable not assigned in init
        method_vars = []
        for method in methods:
            try:
              source = inspect.getsource(getattr(base, method))
              tree = ast.parse(dedent(source))
              for node in ast.walk(tree):
                  if isinstance(node, ast.Assign):
                      for target in node.targets:
                          if isinstance(target, ast.Attribute):
                              if (isinstance(target.value, ast.Name) and target.value.id == 'self'):
                                  method_vars.append(target.attr)
            except (OSError, TypeError):
                pass  # Source code not available
            except IndentationError:
                print("-->")
                pass

        # Remove duplicates
        init_vars = list(set(init_vars))
        method_vars = list(set(method_vars))

        # Print methods
        if methods:
            print(f"{indent}  Methods:")
            for method in methods:
                print(f"{indent}    {method}")

        # Print class variables
        if class_vars:
            print(f"{indent}  Class Variables:")
            for var in class_vars:
                print(f"{indent}    {var}")

        # Print variables assigned in __init__
        if init_vars:
            print(f"{indent}  Variables assigned in __init__:")
            for var in init_vars:
                print(f"{indent}    {var}")

        # Print variables not assigned in __init__
        if method_vars:
            print(f"{indent}  Variables not assigned in __init__:")
            for var in method_vars:
                print(f"{indent}    {var}")

        print("")  # Empty line for separation

# Example usage
class A:
    class_var_A = 1

    def __init__(self):
        self.instance_var_A = 'A'

    def method_a(self):
        self.instance_var_a = 'a'

class B(A):
    class_var_B = 2

    def __init__(self):
        super().__init__()
        self.instance_var_B = 'B'

    def method_b(self):
        self.instance_var_b = 'b'

class C(B):
    class_var_C = 3

    def __init__(self):
        super().__init__()
        self.instance_var_C = 'C'

    def method_c(self):
        self.instance_var_c = 'c'

get_class_details(C)

"""Inheritance tree and details for C:

=> A:
  Methods:
    method_a
  Class Variables:
    class_var_A
  Variables assigned in __init__:
    instance_var_A
  Variables not assigned in __init__:
    instance_var_a

  => B:
    Methods:
      method_a
      method_b
    Class Variables:
      class_var_B
    Variables assigned in __init__:
      instance_var_B
    Variables not assigned in __init__:
      instance_var_a
      instance_var_b

    => C:
      Methods:
        method_a
        method_b
        method_c
      Class Variables:
        class_var_C
      Variables assigned in __init__:
        instance_var_C
      Variables not assigned in __init__:
        instance_var_a
        instance_var_b
        instance_var_c

"""