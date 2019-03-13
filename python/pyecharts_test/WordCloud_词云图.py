from pyecharts import WordCloud

name = [
    'Sam S Club', 'Macys', 'Amy Schumer', 'Jurassic World', 'Charter Communications',
    'Chick Fil A', 'Planet Fitness', 'Pitch Perfect', 'Express', 'Home', 'Johnny Depp',
    'Lena Dunham', 'Lewis Hamilton', 'KXAN', 'Mary Ellen Mark', 'Farrah Abraham',
    'Rita Ora', 'Serena Williams', 'NCAA baseball tournament', 'Point Break']
value = [
    10000, 6181, 4386, 4055, 2467, 2244, 1898, 1484, 1112,
    965, 847, 582, 555, 550, 462, 366, 360, 282, 273, 265]

wc = WordCloud("词云图示例")
wc.add("",name,value,
        word_size_range=[20, 50], # 单词字体大小范围，默认为 [12, 60]。
        shape="triangle-forward", # 词云形状，有'circle', 'cardioid', 'diamond', 'triangle-forward', 'triangle', 'pentagon', 'star'可选
        word_gap=10, # 单词间隔，默认为 20
        rotate_step=60 # 旋转单词角度,TODO 仅shape=“circle”有效
       )
wc.render("./pyecharts_html/词云图系列.html")