import c_sample
import importlib

print(c_sample.b)
c_sample.b = 10
print(c_sample.b)
importlib.reload(c_sample)
print(c_sample.b)
c_sample.b = 30

from sys import modules
print(dir(modules))
print(dir(c_sample))
this_module = modules['c_sample']
print(dir(this_module))
# del c_sample
del modules['c_sample']
import c_sample
print(c_sample.b)


