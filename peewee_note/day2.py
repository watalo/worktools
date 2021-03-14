#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   d2.py
@Time    :   2021/03/13 23:38:30
@Author  :   watalo 
@Version :   1.0
@Contact :   watalo@163.com
'''

# 导入库
from peewee import *
from datetime import date

# 为了搞清楚peewee背后执行的过程，官方推荐使用：
import logging
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# 最经典的用法：创建数据库-->构建基类-->Model全部继承基类
db = SqliteDatabase('another_.db')

class BaseModel():  # 强烈建议使用这种代码机构来构建项目，这样可以很好的避免重复的指定数据库
    class Meta:
        database = db

class Customer(BaseModel): # 直接继承基类，绑定数据库
    name = CharField(unique=True)
    manager = CharField()
    status = CharField()
    progress = CharField()

class Product(BaseModel):
    corp_name = ForeignKeyField(Customer, backref='products')
    catagory = CharField()
    initial_amount = FloatField()
    balance_amount = FloatField()
    margain_amount = FloatField()
    start_date = DateTimeField()
    end_date = DateTimeField()
    duration = DateTimeField()

