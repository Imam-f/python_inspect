import inspect

class MyClass:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        return f"Hello, {self.name}!"

# Get the source code of MyClass
class_source = inspect.getsource(MyClass)

# Print or use the string representation of the class declaration
print(class_source)

"""
class MyClass:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        return f"Hello, {self.name}!"

"""