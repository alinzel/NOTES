from pyecharts import Graph

nodes = [{"name": "结点1", "symbolSize": 1},
         {"name": "结点2", "symbolSize": 2},
         {"name": "结点3", "symbolSize": 3},
         {"name": "结点4", "symbolSize": 4},
         {"name": "结点5", "symbolSize": 5},
         ]
links = []
for i in nodes:
    for j in nodes:
        links.append({"source": i.get('name'), "target": j.get('name')})

graph = Graph("关系图示例")
graph.add("",nodes,links,
        categories=None, # 结点分类的类目，结点可以指定分类，也可以不指定。
        is_focusnode=True, # 是否在鼠标移到节点上的时候突出显示节点以及节点的边和邻接节点。默认为 True
        is_roam=True,
        is_rotatelabel=True, # 是否旋转标签，默认为 False
        graph_layout="force", # 布局类型，默认force=力引导图，circular=环形布局
        graph_edge_length=300, # 力布局下边的两个节点之间的距离，这个距离也会受 repulsion 影响。默认为 50，TODO 值越大则长度越长
        graph_gravity=0.5, # 点受到的向中心的引力因子。TODO 该值越大节点越往中心点靠拢。默认为 0.2
        graph_repulsion=100, # 节点之间的斥力因子。默认为 50，TODO 值越大则斥力越大
        is_label_show=True,
        line_curve=0.2 # 线的弯曲度
          )
graph.render("./pyecharts_html/关系图系列.html")