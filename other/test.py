# import math
# a = [1,2,3,4,5,6]
#
# new_list = []
#
# lengh = math.ceil(len(a) / 4)
#
# index = 0
# while len(new_list) != lengh:
#     item = a[index:index+4]
#     new_list.append(item)
#     index = index +4
#
# print(new_list)

import itchat

import itchat

@itchat.msg_register(itchat.content.TEXT)
def print_content(msg):
    # print(msg['Text'])
    return msg["Text"]

itchat.auto_login()
itchat.run()