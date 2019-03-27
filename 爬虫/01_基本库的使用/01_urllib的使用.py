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
# urlsplit: 与urlparse一样，参数也形同解析url,分成五段，将params与path部分合并
  # urlsplit(url, scheme,allow_fragments)
# urlunsplit: 参数为可迭代对象，且长度为5
# urljoin:生成链接，效果同urlunparse和urlunsplit，但此方法不需要长度
  # urljoin(base_url,str) 将两个参数合并对base_url的协议、域名、路径进行补充，base_url其他三个部分则不起作用
# urlencode:将字典对象序列化成符合url参数格式的字符串,一般往url传参中用
# parse_qs:将url中的参数转成字典
# parse_qsl:将url中的参数转化为元组组成的列表
# quote:将数据转化为url格式的编码，一般参数为中文的时候使用
# unquote:将url格式的编码进行解码

from urllib import parse
res = parse.urlparse("http:www.baidu.com/index.html;user?id=5#comment")
# 返回结果为元组，res[0],res.scheme
print(res, res[0], res.scheme)  # ParseResult(scheme='http', netloc='', path='www.baidu.com/index.html', params='user', query='id=5', fragment='comment')

data = ["http", "www.baidu.com", "index.html", "user", "d=5", "comment"]
res = parse.urlunparse(data)
print(res)  # http://www.baidu.com/index.html;user?d=5#comment

res = parse.urlsplit("http:www.baidu.com/index.html;user?id=5#comment")
print(res)  # SplitResult(scheme='http', netloc='', path='www.baidu.com/index.html;user', query='id=5', fragment='comment')

data = ["http", "www.baidu.com", "index.html", "d=5", "comment"]
res = parse.urlunsplit(data)
print(res)  # http://www.baidu.com/index.html?d=5#comment

res = parse.urljoin("http://www.baidu.com", "index.html")
print(res)  # http://www.baidu.com/index.html ,注意合并的规则

data= {
    "name":"bob",
    "age":18
}
res = parse.urlencode(data, encoding="utf8")
print(res)  # name=bob&age=18

res = parse.parse_qs("http:www.baidu.com/index.html;user?id=5&name=3")
print(res)  # {'user?id': ['5'], 'name': ['3#comment']}

res = parse.parse_qsl("http:www.baidu.com/index.html;user?id=5&name=3")
print(res)  # [('user?id', '5'), ('name', '3')]

q= "张三"
res = "http:www.baidu.com/index.html?q=%s " % parse.quote(q)  # 编码
print(res)  # http:www.baidu.com/index.html?q=%E5%BC%A0%E4%B8%89
res = parse.unquote(res)  # 解码
print(res)  # http:www.baidu.com/index.html?q=张三


# robotparse:分析robot协议
  # robots.txt:网站爬虫协议，全称网络爬虫排除标准，一般存放于网站的根目录下
    # 返回的内容：
      # user-agent:设置可以爬取网站的爬虫名称
      # disallow:设置哪些路径不能爬取
      # allow:设置哪些路径可以爬取
  # RobotFileParser(url="") # 根据网站的robot协议来判断爬虫是否有权限爬取
    # set_url():设置robots.txt文件的连接
    # read():读取robots.txt文件并分析,无返回值，必须调用
    # parse():解析robots.txt文件
    # can_fetch(User-agent, url)：返回值为布尔类型，判断此user-agent是否可以爬取此url
    # mtime():返回值为上次抓取分析robots的时间
    # modified():将当前时间设置为上次抓取的时间

from urllib import robotparser

rp = robotparser.RobotFileParser()  # 实例化分析类
rp.set_url("https://www.jd.com/robots.txt")  # 添加robots地址
rp.read()  # 读取robot协议
print(rp.can_fetch("*", "https://www.jd.com/")) # 判断当前爬虫是否可以爬取， True
print(rp.mtime())  # 上次抓取的时间 1553685029.0578604
print(rp.modified())  # 设置抓取的时间 none