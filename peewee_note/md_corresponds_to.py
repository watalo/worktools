#%%
# 导入peewee
from enum import unique
from peewee import *

# 为了搞清楚背后的动作，官方推荐使用：
import logging
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# 1.构建一个Database实例，Sqlite用SqliteDatabase()，其他的查文档。
db = SqliteDatabase('people.db')

# 2.创建一个指明数据库的基类，好处：后面的代码不需要重复，可以直接继承。
class BaseModel(Model):
    class Meta:
        database = db

# 3.定义一个Model类，就是数据库重的表单
class Person(BaseModel):
    name = CharField(unique=True) 
    birthday = DateField()

# 5.比如再定义一个与Person关联的Model类
class Pet(BaseModel):
    owner = ForeignKeyField(Person, backref='pets')
    name = CharField()
    animal_type = CharField()

# 4.实例化一个数据库，在数据库中创建一个表
db.connect()
db.create_tables([Person, Pet]) # create_tables()的变量是一个列表，可以一次添加多个表

#%%
from datetime import date

xiaoming = Person(name='小明', birthday = date(2000, 1, 2))
xiaoming.save()
# %%
xiaohong = Person(name='小红', birthday=date(2000, 3, 1))
xiaohong.save()
# %%

xiaodai = Person.create(name='小呆', birthday=date(2001, 5, 1))
xiaoba = Person.create(name='小八', birthday=date(2003, 5, 1))
# %%
xiaodai.name = '小呆呆'
xiaodai.save()
# %%
donggua = Pet.create(owner=xiaodai, name='冬瓜', animal_type='dog')
jianhetao = Pet.create(owner=xiaoba, name='尖核桃', animal_type='dog')
zhuer = Pet.create(owner=xiaoming, name='猪儿', animal_type='cat')
zhuer2 = Pet.create(owner=xiaoming, name='二猪儿', animal_type='cat')

# %%
zhuer.delete_instance() # he had a great life
# Returns: 1
# %%
jianhetao.owner = xiaodai
jianhetao.save()
# %%
# 取出单条数据
xiaoming = Person.select().where(Person.name == '小明').get()
# %%
# 可以使用快捷方式，get()
xiaodai = Person.get(Person.name == '小呆呆')
# %%
# 取一列数据
for person in Person.select(): # 取出所有数据
    print(person.name)

# %%
query = Pet.select().where(Pet.animal_type == 'dog') #按条件取出 
for pet in query:
    print(pet.owner.name, pet.name)
# %%
query = (Pet
        .select()
        .join(Person)
        .where(Pet.animal_type == 'dog'))

for pet in query:
    print(pet.owner.name, pet.name)
# %%
# 这段代码有问题
# query = (Person
#         .select()
#         .join(Pet)
#         .where(Person.name == '小呆呆'))
# for person in query:
#     print(person.name, person.pets.name)

# %%
query = Pet.select().join(Person).where(Person.name == '小呆呆')
for pet in query:
    print(pet.name)

# %%
query = Pet.select().where(Pet.owner == xiaodai)
for pet in query:
    print(pet.name)

# %%
#排序 order_by()
query = Pet.select().where(Pet.owner == xiaodai).order_by(Pet.name)
for pet in query:
    print(pet.name)
# %%
query = Person.select().order_by(Person.birthday.desc()) #加.desc()倒序
for person in query:                                     #不加，正序
    print(person.name, person.birthday)

# %%
# 组合筛选条件的表达
day2000 = date(2000, 1, 1)
day2002 = date(2002, 1, 1)
query = Person.select().where(
    (Person.birthday > day2000) & (Person.birthday < day2002)
)
for person in query:
    print(person.name, person.birthday)

# %%
# between()
query = Person.select().where(Person.birthday.between(day2000,day2002))
for person in query:
    print(person.name, person.birthday)
# %%
# 聚合与预装
# 汇总计数
for person in Person.select():
    print(person.name, '有', person.pets.count(), '只宠物') # N+1问题

# %%
# 汇总计数
query = (Person
        .select(Person, fn.COUNT(Pet.id).alias('pet_count'))
        .join(Pet, JOIN.LEFT_OUTER) # 包含没有宠物的人.
        .group_by(Person)
        .order_by(Person.name))

for i in query:
# "pet_count" 变成查询结果i的一个属性.
    print(i.name, '有', i.pet_count, '只宠物')
# %%
# 尝试下列出所有人和他们的宠物
query = (Person
        .select(Person, Pet)
        .join(Pet, JOIN.LEFT_OUTER)
        .order_by(Person.name))

for person in query:
    if hasattr(person, 'pet'):
        print(person.name, person.pet.name)
    else:
        print(person.name, '没有宠物')
# %%
# prefetch()方法
query = Person.select().order_by(Person.name).prefetch(Pet)
for person in query:
    print(person.name)
    for pet in person.pets:
        print('  *', pet.name)
# %%
# 使用SQL函数
# expression 
db.close()
# %%
