'''
filter map reduce的作用
'''

a = [1,2,3,4,5]

# filter(条件函数， 迭代对象) 过滤序列， 返回可迭代对象
f = filter(lambda x :x %2 ==0, a)
print(f)  # <filter object at 0x000001AE745816D8>
print(f.__next__())
print(f.__next__())
for i in f:
    print(i)

# reduce(函数， 可迭代对象) 对元素进行累计, 数字计算， 字符串拼接
s = ["你好", "世界"]
from functools import reduce  # py3需要引入，py2直接用
r = reduce(lambda x,y : x+y,s)
print(r)  # 你好世界

# map(函数，可迭代对象)：对元组按照函数规则做映射
m = map(lambda x :x/2 , a)
print(m)
for i in m:
    print(i)