from urllib import request, parse, error

# urlopen(url, data)
resp = request.urlopen("http://shuyantech.com/api/cndbpedia/avpair?q=%E6%B8%85%E5%8D%8E%E5%A4%A7%E5%AD%A6")  # 一个http响应对象
res = resp.read()  # 返回值为bytes编码对象
res = res.decode("utf-8")  # 对其解码
print(res)

# data: 像url中动态传参数,使用此方法后不再是get请求，而是post请求
params = {"q":"清华大学"}  # 定义参数
# urlencode(dict)将参数字典转化为字符串
data = parse.urlencode(params)  # q=%E6%B8%85%E5%8D%8E%E5%A4%A7%E5%AD%A6
# bytes(str,encode)将字符串转化为字节流类型，并制定编码格式
data = bytes(data, encoding="utf8")  # b'q=%E6%B8%85%E5%8D%8E%E5%A4%A7%E5%AD%A6'
resp = request.urlopen("http://shuyantech.com/api/cndbpedia/avpair?", data)
res = resp.read() # b'{"status": "ok", "ret": [["\xe4\xb8\xad\xe6\x96\x87\xe5\x90\x8d", "\xe6\xb8\x85\xe5\x8d\x8e\xe5\xa4\xa7\xe5\xad\xa6"],
res = res.decode("utf-8")  # {"status": "ok", "ret": [["中文名", "清华大学"],
print(res)

# timeout，设置超时时间，单位为秒
try:
    resp = request.urlopen("http://shuyantech.com/api/cndbpedia/avpair?q=%E6%B8%85%E5%8D%8E%E5%A4%A7%E5%AD%A6", timeout=0.01)
    print(resp)  # urllib.error.URLError: <urlopen error timed out>
except error.URLError as e:
    print(e.reason)  # timed out
    # isinstance,判断对象是否为已知类型，与type的区别，isinstance() 会认为子类是一种父类类型，考虑继承关系，type则不考虑继承关系
    import socket
    if isinstance(e.reason, socket.timeout):
        print("超时了")

# 加入请求头等信息Request(url, data=None, headers={}, origin_req_host=None, unverifiable=False,method=None)
# url:必传，请求的资源地址
# data：必须是bytes(字节流)类型的
# headers:字典形式，构造请求头信息，例如User-Agent
# origin_req_host:请求方的host和ip
# unverifiable:验证用户有没有权限接受请求结果
# method：字符串，指定请求方式

from urllib import request, parse
url = "http://httpbin.org/post"
data = {
    "name":"Request"
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36",
    "Host": "httpbin.org"
}
method = "POST"
# 构造请求信息
req = request.Request(method=method, url=url, headers=headers, data=bytes(parse.urlencode(data), encoding="utf8") )
resp = request.urlopen(req)
res = resp.read().decode("utf-8")
print(res)

# handler各种处理器
# HTTPBasicAuthHandler：用于管理认证，当一个连接打开时，需要登录，可以用它来解决认证问题
# HTTPCookieProcessor：用于处理cookie
# HTTPPasswordMgr:用于管理密码，维护了用户名和密码的表
# HTTPRedirectHandler：用于重定向
# ProxyHandler：用于设置代理，默认代理为空

# 代理
from urllib.request import ProxyHandler, build_opener
from urllib.error import URLError

url = "https://www.baidu.com"

# 实例化代理
p_handler = ProxyHandler({
    "http":"http://39.134.66.14:8080",
    "https":"https://218.38.52.132:80"
})
opener = build_opener(p_handler)  # build_opener(实例化的handler处理器)

try:
    res = opener.open(url)
    html = res.read().decode("utf-8")
    print(html)
except URLError as e:
    print(e.reason)

# 异常处理 error模块中定义了由request模块产生的错误
# URLError:error模块的基类，由request模块产生的异常都可以通过这个类捕获，存在reason属性
# HTTPError: URLError的子类，专门处理HTTP请求错误 属性code:返回的HTTP状态码，reason:错误原因 headers:返回请求头

from urllib import error,request

try:
    resp = request.urlopen("http://cuiqingcai.com/index.html")
except error.HTTPError as e:
    print("返回的状态码%s" % e.code)
    print("返回的错误原因%s" % e.reason)
    print("返回的请求头%s" % e.headers)
except error.URLError as e:
    print("异常原因%s" % e.reason)
else:
    print("成功")


# parse：解析链接，实现url各部分的抽取、合并、以及链接的转换
# urlparse：实现url的分段和识别，分成六段 scheme://netloc/path;params?query#fragment
  # scheme:表示协议
  # netloc:表示域名
  # path：表示访问路径
  # params:代表参数，;后
  # query：代表查新条件，?后
  # fragment:表示锚点，#后
  # urlparse(url, scheme,allow_fragments)
    # url:必填，待解析的url
    # scheme:默认的协议，假如传入的连接没带协议，会采取这个默认的协议
    # allow_fragments:是否忽略锚点部分，值为布尔类型
# urlunparse:根据参数，生成链接，参数为可迭代对象，且长度为6

from urllib import parse
res = parse.urlparse("http:www.baidu.com/index.html;user?id=5#comment")
# 返回结果为元组，res[0],res.scheme
print(res, res[0], res.scheme)  # ParseResult(scheme='http', netloc='', path='www.baidu.com/index.html', params='user', query='id=5', fragment='comment')
data = ["http", "www.baidu.com", "index.html", "user", "d=5", "comment"]
res = parse.urlunparse(data)
print(res)
