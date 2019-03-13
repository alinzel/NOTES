# TODO 对列表排序
a = [1,3,4,2]
a_ = sorted(a,reverse=True) # 倒序
print(a_)

# TODO 按照指定元素排序
b = [("a",1),("s",3),("c",2)]
b_ = sorted(b,key=lambda x:x[0]) # x指每一个元组
print(b_)  # [('a', 1), ('c', 2), ('s', 3)]

# TODO 对列表中的字典排序，key相同，按指的大小排序
c = [{"z":12},{"z":3},{"z":1}]
c_ = sorted(c,key=lambda x:x["z"])
print(c_)

