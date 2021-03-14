#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   d3.py
@Time    :   2021/03/11 14:15:49
@Author  :   watalo 
@Version :   1.0
@Contact :   watalo@163.com
peewee -- relationships and joins
'''

#%%
import datetime
from peewee import *
import logging

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

db = SqliteDatabase(':memory:')

class BaseModel(Model): # 声明一个基类，绑定数据库文件，后面所有的tables都继承这个基类，
                        # 好处：不用每次写那么多代码，避免出现数据库不对
    class Meta:
        database = db

class User(BaseModel):
    username = TextField()

class Tweet(BaseModel):
    content = TextField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(User, backref='tweets')

class Favorite(BaseModel):
    user = ForeignKeyField(User, backref='favorites')
    tweet = ForeignKeyField(Tweet, backref='favorites')

def populate_test_data():
    db.create_tables([User, Tweet, Favorite])

    data = (
        ('huey', ('meow', 'hiss', 'purr')),
        ('mickey', ('woof', 'whine')),
        ('zaizee', ()))
    for username, tweets in data:
        user = User.create(username=username)
        for tweet in tweets:
            Tweet.create(user=user, content=tweet)

    # Populate a few favorites for our users, such that:
    favorite_data = (
        ('huey', ['whine']),
        ('mickey', ['purr']),
        ('zaizee', ['meow', 'purr']))
    for username, favorites in favorite_data:
        user = User.get(User.username == username)
        for content in favorites:
            tweet = Tweet.get(Tweet.content == content)
            Favorite.create(user=user, tweet=tweet)

populate_test_data()
# %%


# query = Tweet.select().join(User).where(User.username == 'huey')

query = (Tweet
         .select()
         .join(User, on=(Tweet.user == User.id))
         .where(User.username == 'huey'))

for tweet in query:
    print(tweet.content)
# %%
huey = User.get(User.username == 'huey')
for tweet in huey.tweets:
    print(tweet.content)
# %%
query = (User
         .select(User.username, fn.COUNT(Favorite.id).alias('count'))
         .join(Tweet, JOIN.LEFT_OUTER)
         .join(Favorite, JOIN.LEFT_OUTER)
         .group_by(User.username))

for user in query:
    print(user.username, user.count)
# %%
query = (User
         .select(User.user, fn.COUNT(Favorite.id).alias('count'))
         .join(Tweet, JOIN.LEFT_OUTER)
         .join(Favorite, JOIN.LEFT_OUTER)
         .group_by(User.username))
    