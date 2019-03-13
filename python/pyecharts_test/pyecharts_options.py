import pyecharts
from pyecharts.engine import create_default_environment


# TODO 图表初始化参数 -- 通用
pie = pyecharts.Pie(title="标题\n换个行",  # 标题，默认为“”
                    subtitle="副标题\n换个行",  # 副标题, 默认为""
                    width=500,  # 画布的宽度，默认=800，为int类型
                    height=600,  # 画布的高度，默认=400，为int类型
                    title_pos="right",  # 标题距离左侧的位置，默认=left,可选有['auto', 'left', 'right', 'center'可选，也可为百分比或整数]
                    title_top="80%",   # 标题距离顶部的位置，默认=top,可选有['top', 'middle', 'bottom'可选，也可为百分比或整数]
                    title_color="red",  # 标题颜色，默认黑色
                    subtitle_color="green",  # 副标题颜色，默认为灰色
                    title_text_size=22,  # 标题中字体大小，默认=18，int类型
                    subtitle_text_size=18,  # 副标题中字体大小，默认=12，int类型
                    background_color="pink",  # 画布背景颜色，默认白色
                    page_title="html中的<title>内容</title>",  # html中的<title></title>标签的值
                    renderer="svg",  # 渲染方式，默认=canvas，可选["svg","canvas"]
                    extra_html_text_label=["额外的HTML -p- 标签这是第一个参数，为显示的内容，其他参数，配置样式","color:blue"],  # 画布中添加额外的p标签，值为list
                    is_animation = True  # 是否开启动画，默认=True,鼠标浮动的动画
                    )

pie.add("图例",["a","b","c"],[10,20,30])
env = create_default_environment("html")
env.render_chart_to_file(pie, path="./pyecharts_html/初始化参数.html")

# TODO xyAxis--平面直角坐标系中的xy轴，[折线，柱状，散点，EffectScatter，k线图等]
bar = pyecharts.Bar("特殊散点图，测试xy轴配置项")
bar.add("图例",["x1","x2"],[3,4],
        is_convert= False,  # 调换x,y轴，默认=False
        is_xaxislabel_align= True,  # x 轴刻度线和标签是否对齐 默认=False
        is_yaxislabel_align= True,  # y 轴刻度线和标签是否对齐 默认=False
        is_xaxis_inverse = False,  # 是否反向 x 轴，默认=False, TODO x 轴在下，x轴数据倒序
        is_yaxis_inverse = True,  # 是否反向 y 轴，默认=False, TODO x 轴在上，y轴数据倒序
        is_xaxis_boundarygap= True,  # x轴两边 默认留白 默认=True
        is_yaxis_boundarygap= True,  # y轴两边 默认留白 默认=True
        is_xaxis_show= True,  # 是否显示 x 轴，
        is_yaxis_show= True,  # 是否显示 y 轴,
        is_splitline_show= False,  # 是否显示网格线。默认=True
        xaxis_interval= 0,  # x轴标签显示的间隔，TODO 0=全部，1=隔一个显示一个，2=隔两个显示一个，以次类推
        xaxis_margin= 20,  # x轴标签文字，距离轴距离，默认=8
        xaxis_name= "x轴名字",  # 配置x轴名字
        xaxis_name_size= 12 ,  # x轴名字字体大小。默认=14
        xaxis_name_gap= 10,  # x轴名称与轴线的距离 默认=25
        xaxis_name_pos= "start",  # x轴名字位置，可选['start'，'middle'，'end']
        xaxis_pos= "top",  # x轴位置，可选['top','bottom'] TODO x轴在上，y轴要倒置
        xaxis_label_textcolor= "green",  # x轴文字的颜色
        xaxis_label_textsize= "14" ,  # x轴文字的大小
        xaxis_line_color= "red" ,  # x轴颜色
        xaxis_line_width= 10 ,  # x轴宽度
        xaxis_type = "category",  # x轴类型，可选["value","category","log"]
        xaxis_rotate= 0,  # int类型  文字标签旋转的角度 0=不旋转 区间=-90-90
        xaxis_formatter = "件",  # x轴标签格式器，TODO 直接使用 会覆盖原标签，可使用回调函数
        # TODO xaxis的配置，y轴也有，不一一测试了
             )
env.render_chart_to_file(bar,path="./pyecharts_html/平面直角坐标系中的x_y轴的配置项.html")


# TODO dataZoom --> 用于区域缩放调，[Line、Bar、Scatter、EffectScatter、Kline]
line = pyecharts.Line("测试datazoom组件，区域缩放")
line = line.add("line",["测试1","测试2"],[45,50],
                # TODO 默认缩放条配置
                is_datazoom_show= True, # 开启缩放，默认=False
                datazoom_type= "both", # 缩放方式，['slider', 'inside', 'both']
                datazoom_range=[0,50], # 缩放范围 默认=[50,100]
                datazoom_orient= 'vertical',  # 显示方向 默认=horizontal（横向）["horizontal","vertical"]

                #TODO 额外缩放条配置
                is_datazoom_extra_show= True, # 是否开启额外的缩放条
                datazoom_extra_type= "both",
                datazoom_extra_orient="horizontal", # 默认纵向
                datazoom_extra_range=[50,100]
              )
env.render_chart_to_file(line,path="./pyecharts_html/区域缩放配置项.html")


# TODO legend 图例组件
pie = pyecharts.Pie("测试legend组件，图例控制")
pie = pie.add("pie",["测试1","测试2"],[45,50],
              is_legend_show= True, # 是否显示图例，默认=True
              legend_orient= "vertical", # 图例显示方向
              legend_pos= "80%" , # 距离左侧的位置，["百分比",'left', 'center', 'right']
              legend_top= "60%", # 距离上边的位置，["百分比",'left', 'center', 'right']
              legend_selectedmode= "multiple", # 图例选择状态，single->显示一个选中，multiple->多个都被选中
              legend_text_color= "green", # 图例文字的颜色
              legend_text_size= 10 # 图例字体大小
              )
env.render_chart_to_file(pie,path="./pyecharts_html/图例配置项.html")


# TODO label->文本标签组件，用于说明图形的一些数据信息
bar = pyecharts.Bar("测试label组件")
bar.add("label",["测试1","测试2"],[1,2],
        is_random= True, # 是否随机选择颜色，默认=False
        label_color=["red","blue","pink"], # 候选颜色列表
        label_formatter= {"c"},
        # TODO 标签信息
        is_label_show= True, # 是否显示标签信息，即个点的数据项信息, 默认=False
        label_pos= "inside", # 标签显示位置，['top', 'left', 'right', 'bottom', 'inside','outside']
        label_text_color="blue",  # 标签文本颜色
        label_text_size= 20, # 文本标签字体
        # TODO 高亮标签信息
        is_label_emphasis= True,  # 悬浮是否高亮显示数据信息,默认=True
        label_emphasis_pos= "outside", # 高亮标签显示位置 ['top', 'left', 'right', 'bottom', 'inside','outside']
        # 同label配置项，不一一测试
        )
env.render_chart_to_file(bar,path="./pyecharts_html/文本标签配置项.html")

# TODO linestyle->带线图形的线条风格配置
line = pyecharts.Line("linestyle线条设置的配置信息测试")
line.add("line",["测试1","测试2","测试3"],[1,2,0],
         line_width= 5, # 线条宽度，默认=1
         line_opacity= 0.5, # 线条的透明图 0-1，0=完全透明，1=完全不透明
         line_curve=0.5, # 线条弯曲程度，0-1， 0=完全不弯曲，1=最弯曲 TODO 未测试出效果
         line_type= 'dotted',  # 线条的样式 ['solid', 'dashed', 'dotted']
         line_color= "yellow" # 线条的颜色
         )
env.render_chart_to_file(line,path="./pyecharts_html/带线图形的线条配置项.html")

# TODO visualMap->视觉映射组件，用于进行『视觉编码』，也就是将数据映射到视觉元素（视觉通道）
line = pyecharts.Line("linestyle线条设置的配置信息测试")
line.add("line",["测试1","测试2","测试3"],[10,80,0],
         is_visualmap= True, # 开始视觉映射
         visual_type= "color", # 视觉映射的类型，默认=color,即通过颜色来映射数值，size,通过点的大小来映射数值
         visual_range=[0,80], # 允许的范围，最大和最小 默认=[0,100]
         visual_text_color=["red","green"], # 两端文本颜色，对应 high low
         visual_range_color= ["red","orange","yellow","green","blue"], # 过渡颜色,对应visual_type= "color"
         visual_range_size= [10,60], # 图形点的大小范围，对应visual_type= "size"
         visual_orient= "horizontal" , # 方向 ['vertical', 'horizontal']
         visual_pos="left", # 距离左侧的位置
         visual_top="bottom", # 距离上边的位置
         visual_dimension= 1, # 映射哪个维度，x=0,y=1
         is_calculable= True, # 是否开启拖拽手柄，可以选取范围
         is_piecewise= True, # 是否转化为分段，默认=false，连续的
         pieces= [{"min": 10, "max": 200, "label": '10 到 200（自定义label）'},
                    {"value": 123, "label": '123（自定义特殊颜色）', "color": 'grey'}] # 自定义分段信息
         )
env.render_chart_to_file(line,path="./pyecharts_html/视觉映射配置项.html")


# TODO toolbox->工具箱
line = pyecharts.Line("toolbox工具箱配置信息测试")
line.add("line",["测试1","测试2","测试3"],[10,80,0],
        is_toolbox_show= True, # 是否开启工具箱
         is_more_utils= True # 是否显示更多工具
         )
env.render_chart_to_file(line,path="./pyecharts_html/工具箱配置项.html")


# TODO mark-line,mark-point->图形标记组件标记线和点[Bar、Line、Kline]
line = pyecharts.Line("toolbox工具箱配置信息测试")
line.add("line",["测试1","测试2","测试3"],[10,80,0],
         # TODO mark-point 标记点
         mark_point=["min","max",{"coord": ["测试1",10], "name": "自定义的标记点"}], # 标记点，默认['min', 'max', 'average'],支持自定义，{'coord' 对应为 x y 轴坐标， 'name' 为标记点名称}
         mark_point_symbol="arrow" ,# 标记点的形状，['circle', 'rect', 'roundRect', 'triangle', 'diamond', 'pin', 'arrow']
         mark_point_symbolsize= 20, # # 标记点的大小，默认=50
         mark_point_textcolor="white" , # 标记点文字的颜色
         # TODO mark-line 标记线
         mark_line=["min","max","average"] ,# 标记线，三个可选项
         mark_line_symbolsize= 20 , # 标记线的两个端点的大小
         )
env.render_chart_to_file(line,path="./pyecharts_html/标记线和点配置项.html")


# TODO tooltip->悬浮框组件，用于移动或点击鼠标鼠标时候弹出数据内容
line = pyecharts.Line("tooltip提示框配置信息测试")
line.add("line~~~",["测试1","测试2","测试3"],[10,80,0],
         tooltip_trigger="axis" , # 触发类型，item=数据项触发，默认，主要在散点图，饼图等无类目图中使用，xais=坐标轴触发，主要在柱状图，折线图等有类目的途中使用，none=什么都不触发
         tooltip_trigger_on="click", # 触发条件, mousemove=鼠标移动的时候，click=电机的时候，mousemove|click=点击或移动的时候，none=不触发
         tooltip_axispointer_type="cross", # 指示器类型，默认=line，直线，shadow=隐形，cross=十字准星
         tooltip_formatter= '{c}', # str类型，{a}=系列名称add第一个参数，{b}=对应的x轴值，{c}=x,y坐标
         tooltip_text_color= "red", # 提示框文本的颜色
         tooltip_font_size=20, # 提示框字体的大小
         tooltip_background_color="pink", # 提示框背景色
         tooltip_border_color="green", # 提示框边框的颜色
         tooltip_border_width=10, # 边框的宽度
         )
env.render_chart_to_file(line,path="./pyecharts_html/提示框配置项.html")