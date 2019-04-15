from bs4 import BeautifulSoup

html = '''
<dd>
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

# 实例化解析对象 BeautifulSoup(html文本, 使用的解析器)
soup = BeautifulSoup(html, "lxml")
print(soup.prettify())  # 格式化输出结果，以标准的缩进格式输出
print(soup.dd.i.string)  # 获取dd标签下的i标签的文本