import re
'''
    读取data.txt 写成 cleandata.txt文件
'''
# 读取文件 encoding="UTF8" 解决编码报错问题 f.read() UnicodeDecodeError: 'gbk' codec can't decode byte 0xaf in position 42: illegal multibyte sequence
with open("./data.txt", "r", encoding="UTF8") as f:
    res = f.readlines()
    f.close()

# 构造要写入文件的列表
clean_list = ["餐厅名称", "\t", "评论数","\t" "口味", "\t""环境","\t" "服务", "\n"]
# 清洗读出来的数据
for item in res:
    item_list = item.split("|")
    clean_list.append(item_list[0].strip())
    clean_list.append("\t")
    comment = re.match("(\d+).*", item_list[1])
    if comment:
        clean_list.append(" %s" % comment.group(1))
    else:
        clean_list.append(" ")
    clean_list.append("\t\t")
    score = re.match(".*?(\d+\.\d+).*?(\d+\.\d+).*?(\d+\.\d+)", item_list[2])
    if score:
        clean_list.append(score.group(1))
        clean_list.append("\t")
        clean_list.append(score.group(2))
        clean_list.append("\t")
        clean_list.append(score.group(3))
    clean_list.append("\n")
# 写入文件
with open("./cleandata.txt", "a+", encoding="UTF8") as f:
    f.writelines(clean_list)
    f.close()