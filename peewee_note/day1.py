
#%%
from peewee import *

#连接数据库
db = SqliteDatabase('people.db')

# 定义person类
class Person(Model):
    name = CharField()
    birthday = DateField()

    class Meta:
        database = db


class Pet(Model):
    owner = ForeignKeyField(Person, backref='pets')
    name = CharField()
    animal_type = CharField()

    class Meta:
        database = db

#%%
# 实例化上面的类，可创建一个表
db.connect()
db.create_tables([Person, Pet])
#%%
from datetime import date

uncle_bob = Person(name = 'Bob', birthday = date(1960, 1, 15))
uncle_bob.save()

# %%
#其他方式创建一条新纪录

grandma = Person.create(name = 'Grandma',birthday = date(1935, 3, 1))
herb = Person.create(name = 'Herb', birthday = date(1950, 5, 5))
# %%
# 更新一列数据 update
grandma.name = 'Grandma L.'
grandma.save()
# %%
#跨表之间的关联
bob_kitty = Pet.create(owner=uncle_bob, name = 'Kitty', animal_type = 'cat')
herb_fido = Pet.create(owner=herb, name='Fido', animal_type='dog')
herb_mittens = Pet.create(owner=herb, name='Mittens', animal_type='cat')
herb_mittens_jr = Pet.create(owner=herb, name='Mittens_jr', animal_type='cat')

#%%
#删除一条记录
herb_mittens.delete_instance()
# %%
#跨表之间的 关联关系变更
herb_fido.owner = uncle_bob
herb_fido.save()
# %%
# 取一条数据的值
grandma = Person.select().where(Person.name == 'Grandma L.').get()
# %%
# 或者直接使用Person.get():
grandma = Person.get(Person.name == 'Grandma L.')
# %%
# 取出所有记录的某个数据
for person in Person.select():
    print(person.name, person.birthday)

# %%
# 取出所有🐱的主人名字
query = Pet.select().where(Pet.animal_type == 'cat')
for pet in query:
    print(pet.name, pet.owner.name)

# %%
'''
There is a big problem with the previous query: 
because we are accessing and we did not select 
this relation in our original query, peewee will 
have to perform an additional query to retrieve 
the pet’s owner. This behavior is referred to 
as N+1 and it should generally be avoided.pet.owner.name

我理解的N+1是指n条信息都要做一边查询，但使用jion(),
则是把两张比合成一张表，那就只需要做一次查询，效率更高些。

'''

#%%
qurey = (Pet
         .select(Pet, Person)
         .join(Person)
         .where(Pet.animal_type == 'cat'))

for pet in query:
    print(pet.name, pet.owner.name)
# %%
# 排序

for pet in Pet.select().where(Pet.owner == uncle_bob).order_by(Pet.name):
    print(pet.name)
# %%
for person in Person.select().order_by(Person.birthday.desc()):
    print(person.name, person.birthday)
# %%
d1940 = date(1940, 1, 1)
d1960 = date(1960, 1, 1)
query = (Person
         .select()
         .where((Person.birthday < d1940) | (Person.birthday > d1960)))

for person in query:
    print(person.name, person.birthday)
# %%
query = (Person
         .select()
         .where(Person.birthday.between(d1940, d1960)))
        # = (Person.birthday > d1940) & (Person.birthday < d1960)
for person in query:
    print(person.name, person.birthday)
# %%
# 数据汇总 聚合和预装 Aggregates and Prefetch
for person in Person.select():
    print(person.name, person.pets.count(), 'Pets')

# %%
qurey = (Person
         .select(Person, fn.COUNT(pet.id).alias('pet_count'))
         .join(Pet, JOIN.LEFT_OUTER) #包含people，但是不包含pets
         .group_by(Person)
         .order_by(Person.name))
for person in qurey:
    # pet_count 变成了person实例的属性
    print(person.name, person.pet_count, 'pets')

'''
fn()用来调用任意SQL函数：：COUNT(pet.id) AS pet_count
'''
# %%
qurey = (Person
         .select(Person, Pet)
         .join(Pet, JOIN.LEFT_OUTER)
         .order_by(Person.name, Pet.name))

for person in query:
    
    if hasattr(person, 'pet'):
        print(person.name, person.pet.name)
    else:
        print(person.name, 'no pets')
# %%
qurey = Person.select().order_by(Person.name).prefetch(Pet)

for person in query:
    print(person.name)
    for pet in person.pets:
        print('  *', pet.name)
# %%
expression = fn.Lower(fn.Substr(Person.name, 1, 1)) == 'g'
for person in Person.select().where(expression):
    print(person.name)
# %%
db.close()
# %%
