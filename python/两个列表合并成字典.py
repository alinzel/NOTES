list1 = ['k1', 'k2', 'k3']
list2 = ['v1', 'v2', 'v3']

# TODO 利用zip,将对应元素打包成元组，返回由元组组成的列表[(),()]
a = dict(zip(list1, list2))
print(a)  # {'k1': 'v1', 'k2': 'v2', 'k3': 'v3'}

# TODO 列表推导式
b = {k:v for k,v in zip(list1, list2)}
print(b)   # 'k1': 'v1', 'k2': 'v2', 'k3': 'v3'}

# TODO 利用map生成映射
dic = dict(map(lambda x, y: [x, y], list1, list2))
print(dic)  # {'k1': 'v1', 'k2': 'v2', 'k3': 'v3'}
