# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import json
from datetime import datetime

from models.es_type import JobNewsType


class JsonWriterPipeline(object):
    def __init__(self):
        print("Enter JsonWriterPipeline...")
        self.file = open('sxu_news.json', 'w',encoding='utf-8')

    def process_item(self, item, spider):
        if item is None:
            print("Item is None")
        else:
            print("process item ", item)
            line = json.dumps(dict(item),ensure_ascii=False) + "\n"
            self.file.write(line)
            return item


class ElasticSearchPipeline(object):
    def __init__(self):
        print("Enter ElasticSearch Pipeline...")
    def process_item(self, item, spider):

        # 将item转换为ES的数据
        customer = JobNewsType()
        customer.job = item['job']
        customer.add_salary(item['salary_min'],item['salary_max'])
        # customer.Salary().min = item['salary_min']
        # customer.Salary().max = item['salary_max']
        customer.publishdate = item['publishdate']
        customer.zone = item['zone']
        customer.educated = item['educated']
        customer.experience = item['experience']
        customer.description = item['description']
        customer.company = item['company']
        customer.location = item['location']
        customer.logo = item['logo']
        customer.add_kind(item['kind_max'],item['kind_min'])
        # customer.Kind().kind1 = item['kind_max']
        # customer.Kind().kind2 = item['kind_min']

        if customer.save(index='jobnews'):
            print("Successfully add an item to ElasticSearch.")

        return item