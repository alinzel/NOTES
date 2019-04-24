'''
    有两个序列a,b，大小都为n,序列元素的值任意整形数，无序； 要求：通过交换a,b中的元素，使[序列a元素的和]与[序列b元素的和]之间的差最小
'''
# 思路：保存当前的两个序列的的元素的和的最小差，通过两个序列的交换，保存临时值，
#      当临时值小于我们保存的值的时候，那么交换两个序列的元素，等我们遍历完了，
#      比较得到的最小值和之前保存的最小值之间的关系，如果相等，则说明已经得到最小的了，如果不相等则令x=y=0，继续比较

# 定义两个列表
a = [1,5,4,7,2]
b = [3,4,2,7,9]

# 定义两个初始值，标志循环的次数
x = y = 0
min = abs(sum(a) - sum(b))  # 求当前两个序列的差值
print(min)
tag = 1  # 开关变量
while tag:
    old = min  # 将最小值，赋值给一个变量，当交换后比较大小
    while x < len(a):
        while y < len(b):
            a[x], b[y] = b[y], a[x]
            tmp = abs(sum(a) - sum(b))
            if min > tmp:
                min = tmp
            else:
                a[x], b[y] = b[y], a[x]
            y = y + 1
        x = x + 1
        y = 0
    if min == old:
        tag = 0
    else:
        print(min)
        x = y = 0

print(min)
print(a)
print(b)