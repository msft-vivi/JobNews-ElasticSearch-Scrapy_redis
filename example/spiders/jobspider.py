from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

from scrapy_redis.spiders import RedisCrawlSpider

from items import JobNewsItem


class MyCrawler(RedisCrawlSpider):
    """Spider that reads urls from redis queue (myspider:start_urls)."""
    name = 'jobnews'
    redis_key = 'jobnews:start_urls'

    rules = [
        # Rule(LinkExtractor(allow='http://www.job5156.com/index/zhaopin_(php|java|c|net|zwpython|Android|zwrjgcs)'),follow=True),
        Rule(LinkExtractor(allow='http://www.job5156.com/index/zhaopin_[\S]+'),follow=True),
        Rule(LinkExtractor(allow=r'http://www.job5156.com/[\S]+\/job_[0-9]+'), callback='parse_page', follow=False),
    ]


    '''
        # 这是个坑，spider-redis官方给的代码，domain相当于最小的范围
        如下配置不能follow，暂时不知道为啥
        # Dynamically define the allowed domains list.
        # domain = kwargs.pop('www.job5156.com', '')
        # self.allowed_domains = filter(None, domain.split(','))
    '''
    def __init__(self, *args, **kwargs):
        self.allowed_domains = ['www.job5156.com']
        super(MyCrawler, self).__init__(*args, **kwargs)

    def parse_page(self, response):

        try:
            job = response.xpath('/html/body/div[2]/div/div/div/div[1]/h1/text()').get()
        except RuntimeError:
            job = None


        try:
            salary = response.xpath('/html/body/div[2]/div/div/div/div[1]/span/text()').getall()
            salary_min = float(salary[0].split('/')[0].split('-')[0])
            if '千' in salary[0].split('/')[0].split('-')[1]:
                salary_max = float(salary[0].split('/')[0].split('-')[1].split('千')[0])
            if '万' in salary[0].split('/')[0].split('-')[1]:  # 假设月薪过万的使用类似2.5万/月表示方法
                salary_max = float(salary[0].split('/')[0].split('-')[1].split('万')[0]) * 10
                salary_min = salary_min * 10
            if salary[0].split('/')[1] == '年':
                salary_min = salary_min / 12
                salary_max = salary_max / 12
        except RuntimeError:
            salary = None
        try:
            xueli = response.xpath('/html/body/div[2]/div/div/div/div[2]/ul/li[1]/p/text()').get()
        except RuntimeError:
            xueli = -10 # 表示异常数据

        try:
            experience = response.xpath('/html/body/div[2]/div/div/div/div[2]/ul/li[2]/p/text()').get()
        except RuntimeError:
            experience = None
        try:
            zone = response.xpath('/html/body/div[2]/div/div/div/div[2]/ul/li[3]/p/text()').get()
        except RuntimeError:
            zone = None
        try:
            date = response.xpath('/html/body/div[2]/div/div/div/div[2]/p/text()').get()
        except RuntimeError:
            date = None
        try:
            description = response.xpath('/html/body/div[3]/div/div[2]/div/div[1]/pre/text()').get()
        except RuntimeError:
            description = None

        try:
            location = response.xpath('/html/body/div[3]/div/div[2]/div/div[3]/div[2]/p/text()').get()
        except RuntimeError:
            location = None
        try:
            company = response.xpath('/html/body/div[3]/div/div[2]/div/div[4]/div[2]/ul/li[1]/strong/text()').get()
        except RuntimeError:
            company = None
        try:
            logo = response.xpath('/html/body/div[3]/div/div[1]/div[2]/a[1]/img/@src').get()
        except RuntimeError:
            logo = None
        try:
            kind_max = response.xpath('//*[@class="crumbs_cont"]//p[1]/a[2]/text()').get()
            kind_min = response.xpath('//*[@class="crumbs_cont"]//p[1]/a[3]/text()').get()
        except RuntimeError:
            kind_max = None
            kind_min = None
        data = {
            "job":job,
            "salary":salary,
            "xueli":xueli,
            "experience":experience,
            "zone":zone,
            "date":date,
            "description":description,
            # "location":location, # 暂时允许为空
            "company":company,
            "logo":logo,
            "kind_max":kind_max,
            "kind_min": kind_min,
        }
        # 如果有空值，则返回空item
        if not self.isValid(data):
            return None

        #  学历 进行从1到8编码
        if '不限' in xueli:
            xueli_num = 1
        elif '初中及以下' in xueli:
            xueli_num = 2
        elif '中专' in xueli:
            xueli_num = 3
        elif '高中' in xueli:
            xueli_num = 4
        elif '大专' in xueli:
            xueli_num = 5
        elif '本科' in xueli:
            xueli_num = 6
        elif '硕士' in xueli:
            xueli_num = 7
        elif '博士' in xueli:
            xueli_num = 8
        else:
            xueli_num = 1
        # 工作经历 编码
        if '年' in experience:
            experience_num = int(experience.split('年')[0])
        elif '在读学生' in experience:
            experience_num = -1
        elif '应届毕业生' in experience:
            experience_num = 0
        else:
            experience_num = -2

        item = JobNewsItem()
        item['job'] = job
        item['salary_min'] = str(salary_min)
        item['salary_max'] = str(salary_max)
        item['publishdate'] = date
        item['zone'] = zone

        if len(location) == 0:
            item['location'] = []
        else:
            item['location'] = location[0]

        item['educated'] = xueli_num
        item['experience'] = experience_num
        item['description'] = description
        item['company'] = company
        item['location'] = location
        item['logo'] = logo
        item['kind_max'] = kind_max
        item['kind_min'] = kind_min
        yield item

    def isValid(self,data):
        for x in data:
            if data.get(x) is None:
                return False
        return True