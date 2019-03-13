import pyecharts

# TODO 快速上手
bar = pyecharts.Bar("标题：第一个图表","副标题：柱状图") # 初始化图表，并设置标题信息
# 使用主题,有默认主题，可以使用主题插件
bar.use_theme("dark")
bar.add("图例名称1",["x轴1","x轴2"],[1,2],is_more_utils=True,mark_line=["average"],mark_point=["max","min"]) # 添加图表信息, is_more_utils=True--显示所有工具箱，默认False，工具箱为下载，刷新，数据视图
bar.render("./pyecharts_html/first_bar.html") # 生成一个HTML文件
# bar.render("./pyecharts_html/bar.png") # 生成一个图片，需要有node环境，安装 npm install -g phantomjs-prebuilt
# bar.print_echarts_options() # 打印配置项

# TODO 链式调用 ,V0.5.9 +
# (pyecharts.Bar()
#     .add()
#     .add()
#     .render())

# TODO 多次显示图表，使用一个引擎，减少部分重复操作，速度有所提高
from pyecharts.engine import create_default_environment

# 为渲染创建一个默认的配置环境
env = create_default_environment("html") # 参数['html', 'svg', 'png', 'jpeg', 'gif' , 'pdf]
# 渲染
env.render_chart_to_file(bar,path="./pyecharts_html/env_bar.html")

# TODO 自定义类-Overlap
line = pyecharts.Line()
line.add("图例名称2",["x轴1","x轴2"],[1,2],is_more_utils=True,mark_line=["average"],mark_point=["max","min"])

overlap = pyecharts.Overlap() # 初始化自定义类
# 组合表
overlap.add(bar)
overlap.add(line)
# 渲染组合后的图表
env.render_chart_to_file(overlap,path='./pyecharts_html/overlap.html')