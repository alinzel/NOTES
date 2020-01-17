a = [1, 2]
b = [1, 2]
c = b

print(id(a), id(b), id(c))

print(a == b)
print(a is b)

print(b == c)
print(b is c)
