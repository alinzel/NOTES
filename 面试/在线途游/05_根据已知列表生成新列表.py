'''
根据已知列表生成新列表
["1","2"] [1,2]
'''

# 利用列表推导式， 返回list
l = ["1","2"]
new_l = [int(item) for item in l]
print(new_l)


# 利用map(), 返回迭代器
def fun(item):
    return int(item)
new_l = map(fun, l)
print(new_l)
for l in new_l:
    print(type(l), l)
