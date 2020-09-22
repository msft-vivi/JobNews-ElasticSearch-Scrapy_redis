# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html
import scrapy
from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join


class JobNewsItem(Item):
    job = scrapy.Field()
    salary_min = scrapy.Field()
    salary_max = scrapy.Field()
    publishdate = scrapy.Field()
    zone = scrapy.Field()
    educated = scrapy.Field()
    experience = scrapy.Field()
    description = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    logo = scrapy.Field()
    kind_max = scrapy.Field()
    kind_min = scrapy.Field()


