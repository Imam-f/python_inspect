def outer_function(x):
    def inner_function():
        return x  # x becomes a cell variable in inner_function
    return inner_function

closure_function = outer_function(10)
print(closure_function.__closure__)  # Outputs cell objects containing the variable x's value
print(closure_function())  # Output: 10
