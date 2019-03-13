# TODO 二维列表，对列表中按第二个元素排序

l1 = [[1,40.220,"A"],[3,15.2300000000,"B"],[6,30.123456,"C"]]
new_l1 = sorted(l1, key=lambda x:x[1], reverse=True)
print(new_l1)