# Example usage
class A:
    class_var_A = 1

    def __init__(self):
        self.instance_var_A = 'A'

    def method_a(self):
        pass

class B(A):
    class_var_B = 2

    def __init__(self):
        super().__init__()
        self.instance_var_B = 'B'

    def method_b(self):
        pass

class C(B):
    class_var_C = 3

    def __init__(self):
        super().__init__()
        self.instance_var_C = 'C'

    def method_c(self):
        pass
