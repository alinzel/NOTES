a = [{"issue":"123"},{"issue":"234"},{"issue":"345"}]
# for i in a :
#     if "123" not in i["issue"]:
#         print(i)

res = [i for i in a if ("123" not in i["issue"]) and ("234" not in i["issue"]) ]

res = [i for i in a if "123" and "234" not in i["issue"]  ]

print(res)