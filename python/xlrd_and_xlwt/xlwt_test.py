import xlwt

# TODO xlwt--一个生成excel的库

# 关于样式
style_head = xlwt.XFStyle() # 初始化样式

font = xlwt.Font() # 初始化字体相关
font.name = "微软雅黑"
font.bold = True
font.colour_index = 1 # TODO 必须是数字索引

bg = xlwt.Pattern() # 初始背景图案
bg.pattern = xlwt.Pattern.SOLID_PATTERN # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
bg.pattern_fore_colour = 4 # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , almost brown), 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray

# 设置字体
style_head.font = font
# 设置背景
style_head.pattern = bg


# 创建一个excel
excel = xlwt.Workbook()
# 添加工作区
sheet = excel.add_sheet("档案")

# 标题信息
head = ["姓名","年龄","性别"]
for index,value in enumerate(head):
    sheet.write(0,index,value,style_head)

# 内容信息
content = [("张张张","12","男"),("嘿嘿嘿","25","女")]
for index,value_list in enumerate(content,1):
    for i,value in enumerate(value_list):
        sheet.write(index,i,value)

# 保存excel
excel.save("./excel/write.xlsx")




'''
官方例子
'''
# from datetime import datetime
#
# style0 = xlwt.easyxf('font: name Times New Roman, bold on',
#     num_format_str='#,##0.00')
# style1 = xlwt.easyxf(num_format_str='D-MMM-YY')
#
# wb = xlwt.Workbook()
# ws = wb.add_sheet('A Test Sheet')
#
# ws.write(0, 0, 1234.56, style0)
# ws.write(1, 0, datetime.now(), style1)
# ws.write(2, 0, 1)
# ws.write(2, 1, 1)
# ws.write(2, 2, xlwt.Formula("A3+B3"))
#
# wb.save('example.xls')

'''
设置单元格样式合并单元格
'''

# def set_style(name, height, bold=False):
#     style = xlwt.XFStyle()  # 初始化样式
#
#     font = xlwt.Font()  # 为样式创建字体
#     font.name = name  # 'Times New Roman'
#     font.bold = bold
#     font.color_index = 4
#     font.height = height
#
#     # borders= xlwt.Borders()
#     # borders.left= 6
#     # borders.right= 6
#     # borders.top= 6
#     # borders.bottom= 6
#
#     style.font = font
#     # style.borders = borders
#
#     return style
#
#
# # 写excel
# def write_excel():
#     f = xlwt.Workbook()  # 创建工作簿
#
#     '''
#     创建第一个sheet:
#       sheet1
#     '''
#     sheet1 = f.add_sheet(u'sheet1', cell_overwrite_ok=True)  # 创建sheet
#     row0 = [u'业务', u'状态', u'北京', u'上海', u'广州', u'深圳', u'状态小计', u'合计']
#     column0 = [u'机票', u'船票', u'火车票', u'汽车票', u'其它']
#     status = [u'预订', u'出票', u'退票', u'业务小计']
#
#     # 生成第一行
#     for i in range(0, len(row0)):
#         sheet1.write(0, i, row0[i], set_style('Times New Roman', 220, True))
#
#     # 生成第一列和最后一列(合并4行)
#     i, j = 1, 0
#     while i < 4 * len(column0) and j < len(column0):
#         sheet1.write_merge(i, i + 3, 0, 0, column0[j], set_style('Arial', 220, True))  # 第一列
#         sheet1.write_merge(i, i + 3, 7, 7)  # 最后一列"合计"
#         i += 4
#         j += 1
#
#     sheet1.write_merge(21, 21, 0, 1, u'合计', set_style('Times New Roman', 220, True))
#
#     # 生成第二列
#     i = 0
#     while i < 4 * len(column0):
#         for j in range(0, len(status)):
#             sheet1.write(j + i + 1, 1, status[j])
#         i += 4
#
#     f.save('demo1.xlsx')  # 保存文件
#
#
# if __name__ == '__main__':
#     # generate_workbook()
#     # read_excel()
#     write_excel()