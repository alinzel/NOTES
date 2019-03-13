from operator import itemgetter #itemgetter用来去dict中的key，省去了使用lambda函数
from itertools import groupby #itertool还包含有其他很多函数，比如将多个list联合起来。。

list_ = [
    {'name':'zhangsan','age':20,'country':'China'},
    {'name':'wangwu','age':19,'country':'USA'},
    {'name':'lisi','age':22,'country':'JP'},
    {'name':'zhaoliu','age':22,'country':'USA'},
    {'name':'pengqi','age':22,'country':'USA'},
    {'name':'lijiu','age':22,'country':'China'}
]

print(list_)
#通过country进行分组：

list_.sort(key=itemgetter('country')) #需要先排序，然后才能groupby。lst排序后自身被改变
print(list_)
lstg = groupby(list_,itemgetter('country'))
#lstg = groupby(lst,key=lambda x:x['country']) 等同于使用itemgetter()


# print ([{"name":key,'children':list(group)} for key,group in lstg])