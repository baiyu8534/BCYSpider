# cos图片爬虫
#### v1.0
- 不需要登录
- 请求多次不会出验证码
- 用scrapy框架
- 在pipeline中用redis进行爬取过的作品去重
- ImagesPipeline下载小尺寸图片和全尺寸图片
- 数据保存到mongodb数据库
- 只需要爬取list数据的一个接口，就可以拿到一页20部作品的全部信息
- 页数写1000即可，会自动去重，根据自己网速和需要，配置settings，是否下载图片和图片保存地址

