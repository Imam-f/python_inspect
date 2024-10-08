def inspect_object(obj):
    print(f"Instance of: {obj.__class__}\n")
    
    # 1. Attributes (Properties)
    print("Attributes (Properties):")
    attributes = vars(obj)
    if attributes:
        for attr, value in attributes.items():
            print(f"  {attr} = {value}")
    else:
        print("  No instance attributes.")
    print()
    
    # 2. Methods
    print("Methods:")
    methods = [method_name for method_name in dir(obj)
               if callable(getattr(obj, method_name)) and not method_name.startswith("__")]
    if methods:
        for method in methods:
            print(f"  {method}")
    else:
        print("  No public methods.")
    print()
    
    # 3. Class
    print(f"Class:")
    print(f"  {obj.__class__.__name__}")
    print()
    
    # 4. Inherited Attributes and Methods
    print("Inherited Attributes and Methods:")
    mro = obj.__class__.mro()[1:]  # Exclude the object's own class
    for base_class in mro:
        print(f"  From {base_class.__name__}:")
        base_attrs_methods = [attr for attr in dir(base_class) if not attr.startswith("__")]
        if base_attrs_methods:
            for attr in base_attrs_methods:
                print(f"    {attr}")
        else:
            print("    No public attributes or methods.")
    print()
    
    # 5. Type and ID
    print(f"Type: {type(obj)}")
    print(f"ID: {id(obj)}\n")
    
    # 6. Documentation (Docstrings)
    print("Documentation (Docstrings):")
    doc = obj.__doc__
    if doc:
        print(doc.strip())
    else:
        print("  No documentation available.")
    print()
    
    # 7. Special Methods and Properties
    print("Special Methods and Properties:")
    special_attrs = [attr for attr in dir(obj) if attr.startswith("__") and attr.endswith("__")]
    if special_attrs:
        for attr in special_attrs:
            print(f"  {attr}")
    else:
        print("  No special methods or properties.")
    print()
    
    # 8. State (if applicable)
    print("State:")
    if attributes:
        print("  Internal state is represented by the instance attributes above.")
    else:
        print("  No internal state to display.")

class A:
    def __init__(self, x, y):
        self.x = x
        self.y = y

print("A:")
print(inspect_object(A(1, 2)))

"""
A:
Instance of: <class '__main__.A'>

Attributes (Properties):
  x = 1
  y = 2

Methods:
  No public methods.

Class:
  A

Inherited Attributes and Methods:
  From object:
    No public attributes or methods.

Type: <class '__main__.A'>
ID: 2377993109024

Documentation (Docstrings):
  No documentation available.

Special Methods and Properties:
  __class__
  __delattr__
  __dict__
  __dir__
  __doc__
  __eq__
  __format__
  __ge__
  __getattribute__
  __gt__
  __hash__
  __init__
  __init_subclass__
  __le__
  __lt__
  __module__
  __ne__
  __new__
  __reduce__
  __reduce_ex__
  __repr__
  __setattr__
  __sizeof__
  __str__
  __subclasshook__
  __weakref__

State:
  Internal state is represented by the instance attributes above.
None
"""