from django.shortcuts import render
from pyecharts import Line3D
import math

# Create your views here.

REMOTE_HOST = "https://pyecharts.github.io/assets/js"

def index(request):
    l3d = line3d()
    context = {
        "myechart": l3d.render_embed(), # 返回给前端的实例图表
        "host":REMOTE_HOST, # 所需的js
        "script_list":l3d.get_js_dependencies() # 所需的js
    }
    return render(request,"app_name/line3d.html", context)

def line3d():
    _data = []
    for t in range(0, 25000):
        _t = t / 1000
        x = (1 + 0.25 * math.cos(75 * _t)) * math.cos(_t)
        y = (1 + 0.25 * math.cos(75 * _t)) * math.sin(_t)
        z = _t + 2.0 * math.sin(75 * _t)
        _data.append([x, y, z])
    range_color = [
        '#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf',
        '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
    line3d = Line3D("3D line plot demo", width=1200, height=600)
    line3d.add("", _data, is_visualmap=True,
               visual_range_color=range_color, visual_range=[0, 30],
               is_grid3D_rotate=True, grid3D_rotate_speed=180)
    return line3d