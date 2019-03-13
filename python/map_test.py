def add(x,y):
    if x == y:
        return x+y
    else:
        return 0

l = [1,2]
s = [1,1]

n = map(add, l,s) # 返回迭代器
# for i in n:
#     print(i)

# TODO li1 = [{"geuat": "geuat","key": "name_en", "ge": "ge"},{"ge": "ge","key": "name_cn"}]
li = [{"geuat": "geuat","key": "name_en"},{"ge": "ge","key": "_id"},{"ge": "ge","key": "name_en"}]

zz = [{'ge': 'ge', 'key': 'name_en'}, {'ge': 'ge', 'key': '_id'}, {'ge': 'ge', 'key': 'name_cn'},
      {'ge': 'ge', 'key': 'env'}, {'ge': 'ge', 'key': 'ENV'}, {'geuat': 'geuat', 'key': 'domain'},
      {'geuat': 'geuat', 'key': 'name_cn'}, {'geuat': 'geuat', 'key': 'ENV'}, {'geuat': 'geuat', 'key': 'name_en'},
      {'geuat': 'geuat', 'key': '_id'}, {'geuat': 'geuat', 'key': 'deployment_type'}]

index_list = [index  for index,l in enumerate(zz) if l["key"]=="name_en"]

d = {}
li1 = [{}]
def me(index_list):
    global d
    for index,l in enumerate(li):
        if index == index_list:
            li1.remove(d)
            d = dict(d,**l)
            li1.append(d)
            break
        else:
            li1.append(l)

for i in map(me,index_list):
    pass

print(li1)

map(lambda d: dict(d[d.keys()[0]], **d.values()[0]) if d.keys()[0] in d.keys() else  i.values()[0], map(lambda i: {i['key']:i},  li))

a = lambda i: {i['key']: i}
print(a(li))

dc = {}
# for i in map(lambda i: {i['key']: i}, zz):
#     if i.keys()[0] in dc.keys():
#         dc[i.keys()[0]] = dict(dc[i.keys()[0]], **i.values()[0])
#     else:
#         dc[i.keys()[0]] = i.values()[0]
# print (dc.values())