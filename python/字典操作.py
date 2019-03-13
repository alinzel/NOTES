d = {
    "key":"value",
    "a":"b"
}

print(d) # {'key': 'value', 'a': 'b'}

pop_ = d.pop("key") # TODO 有返回值，返回对应的value
print(pop_) # value
print(d) # {'a': 'b'}

del d
print(d) # 报错 name 'd' is not defined