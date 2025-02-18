class A:
    def __init__(self):
        print("A", self.__class__.mro())
        pass

class B(A):
    def __init__(self):
        print("B", self.__class__.mro())
        super().__init__()

class P(A):
    def __init__(self):
        print("P", self.__class__.mro())
        super().__init__()

class C(P):
    def __init__(self):
        print("C", self.__class__.mro())
        super().__init__()

class D(B, C):
    def __init__(self):
        print("D", self.__class__.mro())
        super().__init__()

print(C.__mro__)
c = C()

print("--------------")

print(D.__mro__)
d = D()
