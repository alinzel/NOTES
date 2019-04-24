import re

'''
    re模块的match和search区别
'''
# match:从头开始匹配，如果开头就不符合，就返回None
# search:是查找方式，从头查找，开头不匹配会继续向后查找，直到找到第一个匹配的元素，否则返回none

s = "function"

match = re.match("fun", s)
print(match.group())
print(match.span())  # span返回结果位置

search = re.search("n", s)  # 只会匹配到第一个结果，后面还有就不匹配了
print(search.group())
print(search.span())