"""
如何配置将facebook app的webhook，以获取page的updates?

1. 将app加入到page的subscribed apps列表中

   * 登录developer.facebook.com
   * 确保你的账户是app的管理员
   * 确保你的账户是page的管理员
   * 前往[graph API explorer]
     - 确保Application是你要配置的app, 而不是"Graph API Explorer"(右上角)
     - 在Access Token中获取page access token
     - 调用`POST /<page_id>/subscribed_apps`, 无需任何参数
     - 调用`GET /<page_id>/subscribed_apps`, 验证返回值中包含你的app

2. 在app的后台的products中，添加webhooks

   根据文档添加回调地址和verify_token

"""
from .signal_handlers import *  # noqa
