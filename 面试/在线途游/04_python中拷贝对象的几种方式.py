from copy import copy, deepcopy

# TODO python中拷贝的几种方式：赋值，深拷贝， 浅拷贝

# 可变对象
l = ["1", "2", ["3"]]
# 不可变对象
s = "123"

# TODO 赋值:将已创建对象的内存地址赋值给新对象, 即指向同一个内存地址
ll = l
ss = s
l.append("4")
s = "4"
print(l, ll)  # ['1', '2', ['3'], '4'] ['1', '2', ['3'], '4']
print(s, ss)  # 4 123

# TODO 浅拷贝:不会为子对象开辟新空间，所以操作元数据的子对象，子对象会改变
l_copy = copy(l)
s_copy = copy(s)

l.append("4")
l[2].append("5")
s = "45"

print(l, l_copy)
print(s, s_copy)

# TODO 深浅拷贝：会为子对象开辟新的空间，相当于备份了一份，怎么操作元数据，都不会影响赋值的数据
l_deepcopy = deepcopy(l)
s_deepcopy = deepcopy(s)

l.append("4")
l[2].append("5")
s = "45"

print(l, l_deepcopy)
print(s, s_deepcopy)