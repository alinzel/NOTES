from pyecharts import Style, Pie

style = Style(
    title_text_size=22,
    title_pos="center",
    width=1100,
    height=600,
    background_color='#ddd'
)

pie = Pie("各类电影好评占比","数据来源豆瓣", **style.init_style)

pie_style = style.add(
    radius=[18, 24], #
    label_pos="center",
    is_label_show=True,
    label_text_color=None,
    legend_top="bottom",
    legend_pos="10%",
    rosetype="area"
)

pie.add("", ["剧情", ""], [25, 75], center=[10, 30],**pie_style)
pie.add("", ["奇幻", ""], [24, 76], center=[30, 30],**pie_style)
pie.add("", ["爱情", ""], [14, 86], center=[50, 30],**pie_style)
pie.add("", ["惊悚", ""], [11, 89], center=[70, 30],**pie_style)

pie.render("./pyecharts_html/Style_图表风格.html")