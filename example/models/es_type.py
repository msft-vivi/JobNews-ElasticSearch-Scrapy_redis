# -*- coding:utf-8 -*-

from elasticsearch_dsl import Nested,Date,Boolean,analyzer,Completion,Text,Keyword,Integer,InnerDoc,Document,connections

# 新建连接
connections.create_connection(hosts=['localhost'])


class Kind(InnerDoc):
    kind1 = Text()
    kind2 = Text()

class Salary(InnerDoc):
    max = Text()
    min = Text()

class JobNewsType(Document):

    job = Text(analyzer="ik_max_word")
    publishdate = Text()

    zone = Text(analyzer="ik_max_word")
    educated = Integer()

    description = Text(analyzer="ik_max_word")
    company = Text()

    experience = Integer()
    location = Text(analyzer="ik_max_word")

    logo = Text()
    salary = Nested(Salary)
    kind = Nested(Kind)

    def add_kind(self, one, two):
        self.kind.append(
            Kind(kind1=one, kind2=two))

    def add_salary(self, one, two):
        self.salary.append(
            Salary(max=one, min=two))

if __name__ == '__main__':
    JobNewsType.init(index="jobnews")
