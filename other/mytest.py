import pandas as pd
from pandas import Series,DataFrame

print ('用一维数组生成Series')
x = Series([1,2,3,4])
print (x)
print (x.values)
for i in range(1000):
    print(i)
