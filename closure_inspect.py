def add_n_generator(n):
    returns = []
    for i in range(n):
        whatnot = dict({"what": i})
        # def lambda_func(x):
        #     return lambda y: y + x['what']
        # returns.append(lambda_func(whatnot))
        returns.append((lambda x: lambda y: y + x['what'])(whatnot))
    return returns

tests = add_n_generator(3)
print(  add_n_generator.__code__.co_varnames, 
        add_n_generator.__code__.co_freevars, 
        add_n_generator.__code__.co_cellvars, 
        add_n_generator.__closure__)
for i in range(3):
    print(tests[i].__code__.co_varnames, 
          tests[i].__code__.co_freevars, 
          tests[i].__code__.co_cellvars, 
          tests[i].__closure__,
          tests[i].__closure__[0].cell_contents['what'])
    print(tests[i](10))

"""
('n', 'returns', 'i', 'whatnot') () () None
('y',) ('x',) () (<cell at 0x000001D7653E3640: dict object at 0x000001D765438040>,) 0
10
('y',) ('x',) () (<cell at 0x000001D7653E1D80: dict object at 0x000001D7654381C0>,) 1
11
('y',) ('x',) () (<cell at 0x000001D7653E2E00: dict object at 0x000001D765438200>,) 2
12
"""