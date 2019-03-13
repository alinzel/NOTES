# TODO xlrd--一个从excel文件中读取和格式化数据信息的库，无论是xls还是xlsx文件

import xlrd

# 打开excel文件，返回实例对象-<xlrd.book.Book object at 0x000001ED41180898>
excel = xlrd.open_workbook(r"./excel/2017年人员电子档案.xlsx") #r-->保持原始字符串，不转义

# 获取sheet的名字，返回名字列表-['2017-6-22', '测试']
sheet_names = excel.sheet_names()
# 获取sheet对象，返回对象列表-[<xlrd.sheet.Sheet object at 0x0000023A57014CC0>, <xlrd.sheet.Sheet object at 0x0000023A57014CF8>]
sheets = excel.sheets()
# 获取sheet总数,返回数字-2
sheet_num = excel.nsheets

# 获取某一个sheet对象
sheet_index = excel.sheet_by_index(0)  # 根据索引
sheet_name = excel.sheet_by_name("测试")  # 根据名称
# 获取sheet对象相关信息
name = sheet_index.name  # 返回sheet名称
rows = sheet_index.nrows  # 返回行数
cols = sheet_index.ncols  # 返回列数

# 批量获取单元格信息
row_value = sheet_index.row_values(2, 0, 4)  # 获取某一行的值，返回列表，TODO 参数依次，第二行，从0开始，到第4列
col_value = sheet_index.col_values(0, 0, 4)
row = sheet_index.row(2)  # 获取某一行的值和类型，不支持切片-[text:'123', text:'456', text:'789', text:'147', text:'11111111', text:'258', text:'']
col = sheet_index.col(1)
slice_row = sheet_index.row_slice(2, 0, 4)  # 获取某一行的值和类型，支持切片
slice_col = sheet_index.col_slice(0, 0, 4)

# 获取特定单元格
cell_value = sheet_index.cell(1,2).value  # 获取第2行，第三列的值
cell_value_ = sheet_index.cell_value(1,2)

# 获取单元格栏信息
print(xlrd.cellname(0,1))
print(xlrd.cellnameabs(0,1))
print(xlrd.colname(8))


# 写入数据库
import pymysql

# 连接数据库
coon = pymysql.connect(
    host="192.168.200.10",
    db="test_zwl",
    user="bdsdata",
    password="357135",
    port=3306
)
cur = coon.cursor()
# TODO 查询
# sql = "select * from file"
# cur.execute(sql)
# result = cur.fetchone()
# print(result)
# TODO 插入数据
row_num = sheet_index.nrows
col_num = sheet_index.ncols
# 构造sql语句，批量插入数据库 values(),(),(),没有选择一条一条的插入
sql = "insert into file values"
for i in range(1,row_num): # 控制每一行
    for j in range(0,col_num): # 控制列
        item = sheet_index.cell_value(i, j) # 获取指定单元格数值
        # TODO 数据库中的空值两种形式，一种空字符串--数据库显示空白，另一种是null,且不能用引号包裹起来--数据库显示为null
        if item == "":
            item = "Null"
            value = str(item)
        else:
            value = '"' + str(item) + '"'
        if i != row_num-1:
            if j == 0 :
                sql += "(" + str(i) + ","+ value + ","  # TODO 插入的item 要用 ”“包起来，不然报错 1064，但是null不可以包
            elif j == col_num-1:
                sql += value + "),"
            else:
                sql += value + ","
        else:
            if j == 0 :
                sql += "(" + str(i) + ","+ value + ","
            elif j == col_num-1:
                sql += value + ")"
            else:
                sql += value + ","
    # break
# print(sql)
# try:
#     cur.execute(sql)
#     coon.commit()  # TODO 不要忘记提交啊
# except:
#     coon.rollback()

value_list = []
for i in range(1,row_num):
    row_v = sheet_index.row_values(i)
    row_v = [None if row == "" else row for row in row_v ] # None在数据库显示为Null
    value_list.append(row_v)
sql_many = "insert into file (name,area,department,job_state,phone,in_date,out_date)values(%s,%s,%s,%s,%s,%s,%s)"

try:
    cur.executemany(sql_many,value_list)
    coon.commit()  # TODO 不要忘记提交啊
except Exception as e:
    print(e)
    coon.rollback()

cur.close()
coon.close()