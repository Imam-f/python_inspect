class MyClass:
    def method1(self):
        self.method2()
        helper_function()

    def method2(self):
        pass

def helper_function():
    pass

def foo():
    obj = MyClass()
    obj.method1()

foo()
