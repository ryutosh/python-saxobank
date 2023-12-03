import scrapy

# from dataclasses import dataclass

REQ_PARAMETERS = "/html/body/div[5]/div[2]/div/div/div/main/article/section/ul/li[1]/section/table"
RESP_PARAMETERS = "/html/body/div[5]/div[2]/div/div/div/main/article/section/ul/li[2]/section/table"


# @dataclass
# class RequestParameter:
#     Name: str
#     Type: str
#     Origin: str
#     Description: str


class ChartsSpider(scrapy.Spider):
    name = "charts"
    allowed_domains = ["www.developer.saxo"]
    start_urls = [
        "https://www.developer.saxo/openapi/referencedocs/chart/v1/charts",
        "https://www.developer.saxo/openapi/referencedocs/chart/v1/charts/getchartdataasync/387cfc61d3292d9237095b9144ac4733",
    ]

    def parse_subwindow(self, response):
        pass

    def handle_subwindow(self, path):
        pass

    def parse(self, response):
        req_table = response.xpath(REQ_PARAMETERS)
        for req_param in req_table.xpath("./tbody/tr"):
            yield {
                "Name": req_param.xpath("./td[1]").get(),
                "Required": bool(req_param.xpath("./td[1]/span[contains(@class,'refdoc-parameter--required')]") is not None),
            }
        resp = response.xpath(RESP_PARAMETERS)
        yield {"request_parameters": req, "response_parameters": req}

        #    for book in books:
        #         yield {
        #             'Title': book.xpath('.//a/@title').get(),
        #             'URL': book.xpath('.//a/@href').get()
        #             # 'Title': book.css('a::attr(title)').get(),
        #             # 'URL': book.css('a::attr(href)').get()
        #         }

        next_page = response.xpath('//li[@class="next"]/a/@href').get()
        # next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse)
