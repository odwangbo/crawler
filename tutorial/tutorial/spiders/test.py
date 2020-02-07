# 试用scrapy框架
"""
    Scrapy会调度Spider方法scrapy.Request返回的对象start_requests。
    在收到每个响应后，它实例化Response对象并调用与请求相关的回调方法（在本例中为 parse方法），将响应作为参数传递。
"""
import scrapy


class QuotesSpider(scrapy.Spider):

    # 识别蜘蛛。它在项目中必须是唯一的，也就是说，您不能为不同的Spiders设置相同的名称。
    name = "quotes"

    # 必须返回一个可迭代的请求（您可以返回请求列表或编写生成器函数），Spider将开始从中爬行。后续请求将从这些初始请求中连续生成。
    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # 将调用一个方法来处理为每个请求下载的响应。响应参数是TextResponse保存页面内容的实例，并具有处理它的其他有用方法。
    # 该parse()方法通常解析响应，将抽取的数据提取为dicts，并查找要遵循的新URL并Request从中创建新的request（）。
    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

