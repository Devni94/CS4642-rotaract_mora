import scrapy
import re
from scrapy.linkextractor import LinkExtractor

class RotaractSpider(scrapy.Spider):
    name = "rotaract"
    start_urls = [
	'http://rotaractmora.org/blog/',
    ]
    url_matcher = re.compile('\http\:\/\/rotaractmora\.org\/blog\/category\/')

    def parse(self, response):
		link_extractor = LinkExtractor(allow=RotaractSpider.url_matcher)
		links = [link.url for link in link_extractor.extract_links(response)]

		for link in links:
			flag = True
			article_links = []
			yield scrapy.Request(url=link, callback=self.parse_articles,meta={'article_links':article_links,'flag':flag})
	   	
    def parse_articles(self,response):
		flag = response.meta['flag']
		article_links = response.meta['article_links']
		if (flag == True):
			top_links = response.css('div.category-item-caption h4 a::attr(href)').extract()

			for t_link in top_links:
				article_links.append(t_link)
				yield scrapy.Request(url=t_link, callback=self.extract_info)
				flag = False

		other_links = response.css('div.image-post-thumb a::attr(href)').extract()	
		
		for o_link in other_links:
			if (o_link not in article_links):
				article_links.append(o_link)
				yield scrapy.Request(url=o_link, callback=self.extract_info)

		if (response.css('div.pagination').extract() != []):
			if (response.css('div.pagination a::text').extract()[-1] == "Next Page"):
				next = response.css('div.pagination a::attr(href)').extract()[-1]
				yield scrapy.Request(url=next, callback=self.parse_articles,meta={'article_links':article_links,'flag':flag})
				
    def extract_info(self,response):
	
		data = response.css('div.single_post_entry_content')
		yield {
			'url' : response.url,
			'name': data.css('h1::text').extract_first(),
			'category': data.css('a::text').extract_first(),
			'author': data.css('a::text').extract()[1],
			'date': response.css('div.single_post_entry_content span::text').extract_first().split("- ")[1],
			'views': data.css('span.love_post_view::text').extract_first()
		}
			
		
				
				
				
				
