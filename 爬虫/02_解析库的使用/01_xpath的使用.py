from lxml import etree

html_text = '''
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

html = etree.HTML(html_text)  # 实例化HTML文本， <Element html at 0x1b12559c108>
data = html.xpath("//dd")  # nodename:获取此节点的所有子节点
data = html.xpath("//dd/div/@class")  # / 获取dd下的直接div子节点
data = html.xpath("//dd//div/@class")  # // 获取dd下的所有div子孙节点
data = html.xpath("//dd/div/div/.")  # . 获取当前元素,即最后一层div
data = html.xpath("//dd/div/div/..")  # .. 获取当前元素的父元素, 即最后一层div的父元素
data = html.xpath("//dd/div/div/../@class")  # @class 获取class属性值
data = html.xpath("//p[@class='releasetime']")  # [@属性名称=属性值] 匹配符合属性的节点
data = html.xpath("//p[@class='releasetime']/text()")  # text()，获取直接子节点的文本
# 属性多值匹配:当属性有多个值时候，需要用contains()
data = html.xpath("//p[@class='board-index']/text()")  # 返回[]， 因为属性为只为board-index不存在
data = html.xpath("//i[contains(@class,'board-index')]/text()")  # ["1"]
# 多属性匹配，多个属性值匹配一个目标节点 使用运算符连接
data = html.xpath("//a[@title='霸王别姬' and @class='image-link']/img")
# 按序选择
data = html.xpath("//dd//div[1]")  # 选取第一个div
data = html.xpath("//dd//div[position()<2]")  # 选取位置小于2的
data = html.xpath("//dd//div/div[last()]")  # 选取最后一个
# 节点轴选择
data = html.xpath("//i[contains(@class,'board-index')]/ancestor::*")  # 获取i所有的祖先节点
data = html.xpath("//i[contains(@class,'board-index')]/ancestor::dd")  # 获取i标签祖先为dd的节点
data = html.xpath("//i/attribute::*")  # 获取i标签所有的属性值
data = html.xpath("//dd/child::*")  # 获取dd标签的直接子节点
data = html.xpath("//dd/div/div/descendant::*")  # 获取子孙节点
data = html.xpath("//dd/i/following::*")  # 获取i标签后的所有节点，包括子孙
data = html.xpath("//dd/i/following-sibling::*")  # 获取同级节点
print(data)
