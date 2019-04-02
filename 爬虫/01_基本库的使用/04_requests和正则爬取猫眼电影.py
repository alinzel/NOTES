import requests
import re
import time
import xlwt


# 爬取网页
def get_page(url, headers):
    resp = requests.get(url, headers)
    return resp.text


# 解析返回的结果
def parse_res(res):
    '''<dd>
        <i class="board-index board-index-1">1</i>
        <a href="/films/1203" title="霸王别姬" class="image-link" data-act="boarditem-click" data-val="{movieId:1203}">
          <img src="//s0.meituan.net/bs/?f=myfe/mywww:/image/loading_2.e3d934bf.png" alt="" class="poster-default">
          <img data-src="https://p0.meituan.net/movie/223c3e186db3ab4ea3bb14508c709400427933.jpg@160w_220h_1e_1c" alt="乱世佳人" class="board-img" />
        </a>
        <div class="board-item-main">
          <div class="board-item-content">
            <div class="movie-item-info">
                <p class="name"><a href="/films/1203" title="霸王别姬" data-act="boarditem-click" data-val="{movieId:1203}">霸王别姬</a></p>
                <p class="star">
                    主演：张国荣,张丰毅,巩俐
                </p>
                <p class="releasetime">上映时间：1993-01-01</p>
            </div>
            <div class="movie-item-number score-num">
                <p class="score">
                    <i class="integer">9.</i>
                    <i class="fraction">5</i>
                </p>
            </div>
          </div>
        </div>
       </dd>
    '''
    par = re.compile(r'<dd>.*?'
                     r'<i.*?>(\d+)</i>'
                     r'.*?data-src="(.*?)"'
                     r'.*?class="name"><a .*?>(.*?)</a>'
                     r'.*?class="star">(.*?)</p>'
                     r'.*?releasetime">(.*?)</p>'
                     r'.*?class="integer">(.*?)</i>'
                     r'.*?class="fraction">(.*?)</i>'
                     r'.*?</dd>', re.S)
    items = re.findall(par, res)  # 返回list
    for item in items:
        # 利用生成器返回数据,或者构造元组，存放在list中用return返回
        # TODO 返回这样格式是写入excel需要
        yield [
            item[0],
            item[1],
            item[2],
            item[3].strip()[3:],
            item[4][5:],
            item[5]+item[6]
        ]


# 写入文件
def write_to_excel(items):
    # 创建一个excel
    excel = xlwt.Workbook()
    # 添加一个工作区
    sheet = excel.add_sheet("电影排名")
    # 构造表头信息
    head = ["序号", "海报", "名称", "主演", "上映时间", "评分"]
    # 将头部信息写入excel表头
    for index, value in enumerate(head):
        sheet.write(0, index, value)
    # 将内容写入excel
    for row, item in enumerate(items, 1):  # 行数据
        for col in range(0, len(item)):  # 列数据
            sheet.write(row, col, item[col])

    excel.save("./猫眼电影排名.xlsx")


# 主程序入口
def main(offset):
    url = "https://maoyan.com/board/4?offset=" + str(offset)
    headers = {
        "User-Agent": '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) 
                        AppleWebKit/537.36(KHTML, like Gecko) Chrome
                        /73.0.3683.75 Safari/537.36'''
    }
    res = get_page(url, headers)  # 请求url
    items = parse_res(res)  # 解析结果，返回生成器
    print(items.__next__())  # python3改为__next__(),之前版本为next()
    return items  # 返回解析后的结果，生成器



if __name__ == "__main__":
    items = []
    offset = None
    for i in range(0, 10):
        item= main(i*10)  # 分页爬取
        items += list(item)  # 将每页结果进行拼接
        time.sleep(1)  # 每页休眠一秒钟，反扒措施
    write_to_excel(items)  # 将所有结果一次性写入文件，不一次一次写，因为会覆盖
