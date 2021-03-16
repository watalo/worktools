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
from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap


# 为了搞清楚背后的动作，官方推荐使用：
import logging
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# 前期配置
database = SqliteDatabase('pool.db')


# 网页启动
from flask import Flask
app = Flask(__name__)


@app.route('/')
def index():
    return 'Index Page'


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)



# 数据结构
class BaseModel(Model):
   class Meta():
       database = database

class Project(BaseModel):
    pass

class Product(BaseModel):
    pass

class Member(BaseModel):
    pass




if __name__ == '__main__':
    app.run()