'''
    将list转成有序的dict(和list的顺序一样，但是值不同)
    list = ["a","b","c","d"]
    dict = {"a":"d", "b":"c","c":"b","d":"a"}
'''

list = ["a", "b", "c", "d"]


# TODO 利用zip实现
def list_to_dict(list):
    value_list = sorted(list, reverse=True)  # 将列表倒序， sorted有返回值
    list_tuple = zip(list, value_list)  # 将参数中对应的元素 打包成元组，并返回元组组成的列表可迭代对象
    # for tuple in list_tuple:  # 此对象只能遍历一次
    #     print(tuple)  # ('a', 'd') ('b', 'c') ('c', 'b') ('d', 'a')
    d = dict(list_tuple)
    return d

d = list_to_dict(list)
print(d)  # {'a': 'd', 'b': 'c', 'c': 'b', 'd': 'a'}


# TODO 利用列表推导式
def list_to_dic(list):
    # 返回字典形式，且用if else
    d = { key:list[index] if index< len(list) else list[0] for index, key in enumerate(list,1) }
    return d

d = list_to_dic(list)
print(d)  # {'a': 'd', 'b': 'c', 'c': 'b', 'd': 'a'}