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


if __name__ == '__main__':
    # 实例化上面的类，可创建一个表
    db.connect()
    db.create_tables([Person, Pet])
    
    from datetime import date

    # uncle_bob = Person(name = 'Bob', birthday = date(1960, 1, 15))
    # uncle_bob.save()

    

