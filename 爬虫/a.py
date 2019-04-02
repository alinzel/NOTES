l = [["中文名称", "清华大学"], ["CATEGORY_ZH", "大学"], ["CATEGORY_ZH", "985高校"]]
for item in l:
    if "CATEGORY_ZH" in item:
        print(item[1])

gen = (item for item in [1,2,3])
gen2 = (item for item in [4,5,6])
print(gen)

l = []
print(l+ list(gen) + list(gen2))