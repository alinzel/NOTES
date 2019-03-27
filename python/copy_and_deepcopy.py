from copy import copy,deepcopy
'''
a是引用，[1,2,[3]]是对象
可变类型：可以改变对象的内容，引用的内存地址不变
不可变类型：不能改变对象的内容，只能将其引用指向另一个内存地址
'''
a = [1,2,[3]]

b = a # 引用，即同用一个id地址，随a变化
a_copy = copy(a)
a_deepcopy = deepcopy(a)

print(b,a_copy,a_deepcopy) # [1, 2, [3], 4] [1, 2, [3]] [1, 2, [3]]

a.append(4)
print(b,a_copy,a_deepcopy) # [1, 2, [3], 4] [1, 2, [3]] [1, 2, [3]]

a[2].append(5)
print(b,a_copy,a_deepcopy)  # [1, 2, [3, 5], 4] [1, 2, [3, 5]] [1, 2, [3]]
'''
    不可变类型--无论是赋值，还是深浅拷贝，都是指向对元数据的id地址，当元数据改变，指向另一个新id地址，
    可变类型--赋值是对原对象地址的引用，深浅拷贝都会产生新对象，改变元数据，不会对深浅拷贝产生影响，但是对于浅拷贝，如果对象中还存在可变类型，即是引用地址，而不是一个新的对象。
'''
