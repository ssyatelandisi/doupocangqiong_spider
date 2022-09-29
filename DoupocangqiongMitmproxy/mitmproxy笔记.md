针对 http，常用的 API

# http.HTTPFlow 实例 flow

- flow.request.headers #获取所有头信息，包含 Host、User-Agent、Content-type 等字段
- flow.request.url #完整的请求地址，包含域名及请求参数，但是不包含放在 body 里面的请求参数
- flow.request.pretty_url #同 flow.request.url 目前没看出什么差别
- flow.request.host #域名
- flow.request.method #请求方式。POST、GET 等
- flow.request.scheme #什么请求 ，如 https
- flow.request.path # 请求的路径，url 除域名之外的内容
- flow.request.get_text() #请求中 body 内容，有一些 http 会把请求参数放在 body 里面，那么可通过此方法获取，返回字典类型
- flow.request.query #返回 MultiDictView 类型的数据，url 直接带的键值参数
- flow.request.get_content()#bytes,结果如 flow.request.get_text()
- flow.request.raw_content #bytes,结果如 flow.request.get_content()
- flow.request.urlencoded_form #MultiDictView，content-type：application/x-www-form-urlencoded 时的请求参数，不包含 url 直接带的键值参数
- flow.request.multipart_form #MultiDictView，content-type：multipart/form-data 时的请求参数，不包含 url 直接带的键值参数

对于 response，同理

- flow.response.status_code #状态码
- flow.response.text #返回内容，已解码
- flow.response.content #返回内容，二进制
- flow.response.setText() #修改返回内容，不需要转码

Mitmproxy 截获数据导出到剪贴板

# 在命令界面按下分号:键，输入下列（任选其一）命令并回车

`export.clip curl @focus`
`export.clip httpie @focus`
`export.clip raw @focus`
`export.clip raw_request @focus`
`export.clip raw_response @focus`
`save.file @focus 文件名` #导出当前选中为文件

#添加快捷键

vim ~/.mitmproxy/keys.yaml

```
-
  key: c
  cmd: export.clip curl @focus
-
  key: x
  cmd: cut.clip @focus request.url
```
