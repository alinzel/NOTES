import requests

# get请求 requests.get(url, params, headers)
url = "http://httpbin.org/get"  # 请求的url
# 请求参数
params = {
    "name":"Arale",
    "age":25
}
# 请求头
headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
}
# 发送get请求，得到响应
resp = requests.get(url, params=params, headers=headers)
print(resp.url)  # 打印请求的url 参数在url http://httpbin.org/get?name=Arale&age=25

# post请求 requests.post(url, data, headers)
url = "http://httpbin.org/post"  # 请求的url
# 发送post请求
resp = requests.post(url, data=params, headers=headers)
print(resp.url)  # 打印请求的url 参数在请求体中 http://httpbin.org/post

# 响应属性方法
print(resp.text)  # 打印str文本数据
print(resp.content)  # 处理二进制数据，例如图片
print(resp.url)  # http://httpbin.org/post
print(resp.headers)  # {'Access-Control-Allow-Credentials': 'true', 'Access-Control-Allow-Origin': '*', 'Content-Encoding': 'gzip', 'Content-Type': 'application/json', 'Date': 'Thu, 28 Mar 2019 01:53:32 GMT', 'Server': 'nginx', 'Content-Length': '343', 'Connection': 'keep-alive'}
print(resp.cookies)  # <RequestsCookieJar[]>
print(resp.status_code)  # 200
print(resp.history)  # []

# 上传文件
files = {
    "file": open("01_urllib的使用.py", "rb")
}
resp = requests.post(url, files=files)  # 注意key必须为files否则报错
print(resp.text)  # 返回内容会多一个files字段

# cookie的使用
headers = {
    # 此cookie为登录网站后的cookie,
    "Cookie": "Hm_lvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1553742403; sajssdk_2015_cross_new_user=1; locale=zh-CN; read_mode=day; default_font=font2; remember_user_token=W1sxMjE1NTM2Ml0sIiQyYSQxMSRmZEdzaHlpLnFsYnZpMG9PbFRQLk91IiwiMTU1Mzc0MjQxMC44MTg2OTc3Il0%3D--48708ad37562cd9a12cfaac066b92cc24e4305d3; _m7e_session_core=167a540dc0e51fd3bb10e0e502e174de; __yadk_uid=8uaAcl2jljk5KfYwGemwVKFoMN89sBuC; Hm_lpvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1553742450; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22169c243959d13-00d4259c8ce7dd-7a1b34-1296000-169c243959e606%22%2C%22%24device_id%22%3A%22169c243959d13-00d4259c8ce7dd-7a1b34-1296000-169c243959e606%22%2C%22props%22%3A%7B%7D%2C%22first_id%22%3A%22%22%7D",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36",
    "Referer": "https://www.jianshu.com/writer"
}
url = "https://www.jianshu.com/writer#/notebooks/35136025/notes/43035331"
resp = requests.get(url, headers=headers)
print(resp.status_code)  # 设置cookie,可以访问需要登录才能看见的页面200
# 查看cookie,并可以得到cookie的key value
cookie = requests.get("https://www.baidu.com/").cookies
print(cookie)
for k, v in cookie.items():
    print(k + "=" + v)

# session：维持会话
session = requests.Session()  # 实例化session类，使请求为同一示例，即维持同一会话
session.get("https://www.httpbin.org/cookies/set/arale/123456")
resp = session.get("https://www.httpbin.org/cookies")
print(resp.text)

# ssl证书的验证，verify参数默认为True
try:
    resp = requests.get("https://inv-veri.chinatax.gov.cn/")
    print(resp.status_code)  # requests.exceptions.SSLError会报错，默认会验证CA证书
except Exception as e:
    # from requests.packages import urllib3
    # urllib3.disable_warnings()  # 忽略警告
    import logging
    logging.captureWarnings(True)  # 捕获警告到日志的方式忽略警告
    resp = requests.get("https://inv-veri.chinatax.gov.cn/", verify=False)  # 不去验证证书
    print(resp.status_code)

# 代理ip的设置
proxies = {
    "http":"http://47.107.227.104:8888",
}
resp = requests.get("https://www.baidu.com/", proxies=proxies)
print(resp.status_code)

# 设置超时
try:
    resp = requests.get("https://www.baidu.com/", timeout=0.001)
    print(resp.status_code)  # requests.exceptions.ConnectTimeout
except Exception as e:
    print(e)

# 身份认证
# 传入auth=(元组)
# resp = requests.get("url", auth=("user", "pwd"))

# prepared requests对象
s = requests.Session()  # 实例化session对象
req = requests.Request("get", "https://www.baidu.com/")  # 构造请求对象
pre = s.prepare_request(req)  # 通过session准备请求数据
resp = s.send(pre)  # 发送请求数据，返回响应
print(resp.status_code)