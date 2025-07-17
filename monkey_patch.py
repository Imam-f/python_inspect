from forbiddenfruit import curse

def words_of_wisdom(self):
    return self * "blah "

curse(int, "words_of_wisdom", words_of_wisdom)
assert (2).words_of_wisdom() == "blah blah "
print((2).words_of_wisdom())
