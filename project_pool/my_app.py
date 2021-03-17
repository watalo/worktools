#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   app.py
@Time    :   2021/03/16 02:01:26
@Author  :   watalo 
@Version :   1.0
@Contact :   watalo@163.com
'''

# here put the import lib
from peewee import *
from datetime import date


# 为了搞清楚背后的动作，官方推荐使用：
# import logging
# logger = logging.getLogger('peewee')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)

# 前期配置
database = SqliteDatabase('pool.db')

# 数据结构
class BaseModel(Model):
   class Meta():
       database = database

class Member(BaseModel):
    name    = CharField()


class Project(BaseModel):
    name    = CharField(unique=True)
    member  = ForeignKeyField(Member, backref='projs')
    status  = CharField()
    scheme  = CharField()

    def progress(self):
        pass


class Product(BaseModel):
    proj     = ForeignKeyField(Project, backref='prods')
    member   = ForeignKeyField(Member, backref='prods')
    catagory = CharField()
    amount   = FloatField()
    balance  = FloatField()
    bargain  = FloatField()
    start_date  = DateField()
    end_date    = DateField()


# 调用函数
def db_init():
    if database.is_closed():
        database.connect()
        database.create_tables([Member, Project, Product])
    else:
        database.create_tables([Member, Project, Product])

    database.close()

def db_connect():
    try:
        database.connect()
    except:
        database.close()

def new_member(name_):
    Member.create(name = name_)
    print('{}已加入团队!'.format(name_))

def new_project(name_, member, scheme_):
    x = Project.create(name = name_, member = Member.select().where(Member.name == member), status = '营销中', scheme = scheme_)
    res = '新项目:{n}授信项目已记录，由{m}管理，目前状态为{s}'.format(n = name_, m = x.member.name, s = x.status)
    print(res)
    return res

def new_product(name_, catagory_, amount_, balance_, bargain_, start_date_, end_date_):
    prod = Product.create(
        proj = Project.select().where(Project.name == name_), 
        member = Member.select().join(Project).where(Project.name == name_),
        catagory = catagory_, 
        amount = amount_, 
        balance = balance_, 
        bargain = bargain_, 
        start_date = start_date_, 
        end_date = end_date_,
    )
    res = '新增投放：{}{}{}'.format(name_, catagory_, amount_)
    print(res)
    return res

def change_prod(attr_option, name, new):
    '''
    不太好弄啊，产品的不同通过名字唯一确定，通过其他属性都不行。
    @attr_option:Product属性：
        所属项目 --> -p
        执行人员 --> -m
        产品品种 --> -c
        初始金额 --> -a
        存量余额 --> -bl  
        派生存款 --> -bg  
        起始日期 --> -sd  
        到期日期 --> -ed
    '''
    pass

def change_proj(attr_option, name, new):
    '''
    @attr_option: Project属性：
        名称 -->  -n
        成员 -->  -m
        状态 -->  -s
        方案 -->  -sh
    '''
    if attr_option in ['-n', '-m', '-s', '-sh']:
        proj = Project.get(Project.name == name)
        if attr_option == '-n':
            proj.name = new
        elif attr_option == '-m':
            proj.member = Member.get(Member.name == new)
        elif attr_option == '-s':
            proj.status = new
        elif attr_option == '-sh':
            proj.scheme = new
        proj.save()
        return '修改成功！'
    else:
        return '可选属性：-n：名称 -m：成员 -s：状态 -sh：方案，请再次输入。'

    

def change_menb(name_changed, new_name):
    memb_obj = Member.get(Member.name == name_changed)
    memb_obj.name = new_name
    memb_obj.save()
    print('{}已更正为{}'.format(name_changed, new_name))





# new_member('test')
# memb1 = Member.create(name = '小明')
# memb2 = Member.create(name = '阿呆')


# proj1 = Project.create(
#     name = '一公司',
#     status = '已批复',
#     scheme = '综合授信5000万元',
#     member = memb1
#     )

# proj2 = Project.create(
#     name = '二公司',
#     status = '已上报',
#     scheme = '综合授信3000万元',
#     member = memb1
#     )

# proj3 = Project.create(
#     name = '三公司',
#     status = '营销中',
#     scheme = '综合授信2000万元',
#     member = memb2
#     )

# prod1 = Product.create(
#     proj = proj1, 
#     member = memb1,
#     catagory = '流动资金贷款',
#     amount = 500, balance = 500, bargain = 0, 
#     start_date = date(2021, 3, 16), 
#     end_date = date(2021, 3, 15),
#     )

# prod2 = Product.create(
#     proj = proj1, 
#     member = memb1,
#     catagory = '流动资金贷款',
#     amount = 500, balance = 500, bargain = 500, 
#     start_date = date(2021, 3, 17), 
#     end_date = date(2021, 3, 16),
#     )


# '''
# 查询member
# '''

# query1 = Member.select()
# query2 = Project.select()
# query3 = Product.select()

# print('查询对象的结果是',query1, query2, query2)


# for member in query1:
#     print(member.name)

# for proj in query2:
#     print(proj.name, proj.member.name, proj.scheme, proj.status)

# for prod in query3:
#     print(prod.proj.name, 
#           prod.member.name,
#           prod.catagory,
#           prod.amount,prod.balance, prod.bargain,
#           prod.start_date, prod.end_date)
# # %%
# '''
# 查询项目
# '''

# prod2.catagory = '银行承兑汇票'
# prod2.save()
# # %%

# {}
# prod_xiaoming = (Product
#                  .select()
#                  .join(Member)
#                  .where(Member.name == '阿呆'))

# for prod in prod_xiaoming:
#     print(prod.proj.name, 
#         prod.member.name,
#         prod.catagory,
#         prod.amount,prod.balance, prod.bargain,
#         prod.start_date, prod.end_date)


