import pprint
import pickle

def inspect_object(obj):
    print(f"Instance of: {obj.__class__}\n")
    
    # 1. Attributes (Properties)
    print("Attributes (Properties):")
    # attributes = vars(obj)
    attributes = False
    if attributes:
        for attr, value in attributes.items():
            print(f"  {attr} = \t", end="")
            pprint.pprint(value)
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
            if callable(getattr(obj, attr)):
                print(f"  c||{attr}")
            else:
                print(f"  p||{attr}")
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

def hello(x):
    data = x
    for i in range(10):
        yield data + i

if __name__ == "__main__":
    print("A:")
    a = A(1, ([2, 3], {"4": (6.7)}))
    inspect_object(a)
    gen = hello(5)
    inspect_object(hello)
    inspect_object(gen)
    value = next(gen)
    inspect_object(gen)
    pickle.dump(a, open("a.pkl", "wb"))

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
ID: 1844309605920

Documentation (Docstrings):
  No documentation available.

Special Methods and Properties:
  c||__class__
  c||__delattr__
  p||__dict__
  c||__dir__
  p||__doc__
  c||__eq__
  c||__format__
  c||__ge__
  c||__getattribute__
  c||__gt__
  c||__hash__
  c||__init__
  c||__init_subclass__
  c||__le__
  c||__lt__
  p||__module__
  c||__ne__
  c||__new__
  c||__reduce__
  c||__reduce_ex__
  c||__repr__
  c||__setattr__
  c||__sizeof__
  c||__str__
  c||__subclasshook__
  p||__weakref__

State:
  Internal state is represented by the instance attributes above.
None
"""
