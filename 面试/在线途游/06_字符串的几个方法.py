'''
join split lstrip rstrip strip的作用
'''

s = " 你好,世界 "

# join返回一个新字符串，接受可迭代的对象，将可迭代对象中的元素用s连接成新字符串
s_join = s.join(("说 ", " ！"))
print(s_join)  # 说 你好， 世界 ！

# split: 返回列表， 以指定字符切割
s_split = s.split(",")
print(s_split)  # ['你好', '世界']

# 去除空格函数
s_lstrip = s.lstrip()
print(s_lstrip)

s_rstrip = s.rstrip()
print(s_rstrip)

s_strip = s.strip()
print(s_strip)
