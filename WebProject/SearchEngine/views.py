import math

from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt
from elasticsearch import Elasticsearch
import time

# client = Elasticsearch(hosts=["172.21.201.147:9202"])
client = Elasticsearch(hosts=["127.0.0.1:9200"])

# Create your views here.
def search(request):
    return render_to_response('search.html')

@csrf_exempt # 表示该视图可以被跨域访问
def result(request):

    keyword = request.GET.get('keyword')
    p = request.GET.get('page')
    zone = request.GET.get('zone')
    educated = request.GET.get('education')
    # if keyword is None or keyword == '':
    #     return render_to_response('search.html')
    try:
        p = int(p)
    except:
        print('P值有错误...')
        p = 0

    try:
        educated = int(educated)
        if keyword and keyword != '':
            if zone == '' or zone == '不限':
                must = [{"match":{"job": keyword}},{"range":{"educated":{"lte":educated}}}]
            else:
                must = [{"match":{"job": keyword}},{"match":{"zone": zone}},{"range":{"educated":{"lte":educated}}}]
        else:
            if zone != '' and zone != '不限' and zone != None:
                must = [{"match":{"zone":zone}},{"range": {"educated": {"lte": educated}}}]
            else:
                must = [{"match_all": {}}, {"range": {"educated": {"lte": educated}}}]
    except:
        must = [{"match":{"job": keyword}},{"range":{"educated":{"lte":educated}}}]

    ###################
    query = {"query": { "match": { "job": keyword} }, "size":10,"from":p*10}
    query_body = {
            "query":{
                "bool":{
                    "must":must
                }
            }, "size":10,"from":p*10
    }

    start_time = time.time()
    res = client.search(index="jobnews",body=query_body)
    end_time = time.time()

    #############
    count = res['hits']['total']['value']
    times = '%.2f' % (end_time - start_time)
    hits = res['hits']['hits']
    contents = []

    #换页
    if p < 5:
        pages = [i for i in range(0,min(count//10+1 if count%10 == 0 else count//10,10))]
    elif p > count//10 - 5 :
        pages = [i for i in range(max(0,count//10-10),count//10+1 if count%10 else count//10)]
    else:
        pages= [i for i in range(p-5,p+5)]

    if educated and zone:
        page_urls = [[i,'?keyword='+ str(keyword) +'&zone='+ str(zone) +'&education='+ str(educated) +'&page='+str(i)] for i in pages]
  
    elif (not educated) and (not zone):
        page_urls = [[i,'?keyword='+ str(keyword) +'&page='+str(i)] for i in pages]

    experience = {'-2':'经验不限','-1':'在读学生','0':'应届毕业生','1':'一年','2':'两年','3':'三年','4':'四年','5':'五年','6':'六年','7':'七年','8':'八年','9':'九年','10':'十年及以上'}
    educated = {'1':'学历不限','2':'初中及以下','3':'中专','4':'高中','5':'大专','6':'本科','7':'硕士','8':'博士'}
    contents = []
    for i in hits:
        temp = dict()
        temp['url'] = '/show/?id='+i['_id']
        if "http" not in i['_source']['logo']:
            temp['logo'] = 'http://www.job5156.com/static/style/v4/images/default_com.jpg'
        else:
            temp['logo'] = i['_source']['logo']
        temp['salary'] = i['_source']['salary']
        temp['job'] = i['_source']['job']
        temp['zone'] = i['_source']['zone']
        
        temp['experience'] = experience[str(i['_source']['experience'])]
        temp['educated'] = educated[str(i['_source']['educated'])]
        if len(i['_source']['description']) <= 250:
            temp['description'] = i['_source']['description']
        else:
            temp['description'] = i['_source']['description'][:250] + '...'
        contents.append(temp)
    return render_to_response('result.html',locals())

def show(request):
    id = request.GET.get('id') # id 为elasticsearch 中的 编号id
    query = {"query": { "match": { "_id": id } }}
    print(query)
    res = client.search(index="jobnews",body=query)
    content = res['hits']['hits'][0]['_source']

    experience = {'-2':'经验不限','-1':'在读学生','0':'应届毕业生','1':'一年','2':'两年','3':'三年','4':'四年','5':'五年','6':'六年','7':'七年','8':'八年','9':'九年','10':'十年及以上'}
    educated = {'1':'学历不限','2':'初中及以下','3':'中专','4':'高中','5':'大专','6':'本科','7':'硕士','8':'博士'}
    
    content['experience'] = experience[str(content['experience'])]
    content['educated'] = educated[str(content['educated'])]
    return render_to_response('show.html',locals())
