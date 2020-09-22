import redis


client = redis.Redis(host='localhost',port=6379)
# for x in ['php','java','c','net','zwpython','Android','zwrjgcs']:
#     client.lpush("jobnews:start_urls","http://www.job5156.com/index/zhaopin_{}".format(x))


client.lpush("jobnews:start_urls","http://www.job5156.com")