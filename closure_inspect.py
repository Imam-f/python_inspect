def add_n_generator(n):
    returns = []
    for i in range(n):
        whatnot = dict({"what": i})
        # returns.append(lambda x, i=i: i + x)
        # def lambda_func(x):
        #     return lambda k: k + x
        returns.append((lambda x: lambda y: y + x['what'])(whatnot))
        # returns.append(lambda x: x + whatnot['what'])
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
