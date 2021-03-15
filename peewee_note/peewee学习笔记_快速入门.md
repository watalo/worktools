# peewee学习笔记

[TOC]



> ### 起点很低
>
> - 数据库零基础
>
> - 看了sqlite3文档不到3分钟，被SQL语句折磨的受不了
>

## 1. 安装

`pip install peewee`

## 2. 基本操作

### 2.1. 创建一个数据库

#### peewee标准打开方式：

```python
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
class Person(BaseModel): #继承BaseModel：连接数据库
    name = CharField(unique=True) 
    birthday = DateField()

# 4.实例化一个数据库，在数据库中创建一个表
db.connect()
db.create_tables([Person,]) # create_tables()的变量是一个列表，可以一次添加多个表
```

==**官方强烈推荐使用：交互式方式来学习**==

我用的VScode编辑器，在代码块上一行输入：

```python
#%%
```

为了更清楚的了解这个库执行中是怎么管理和调用各种表的，官方还推荐了代码块：

```python
# 为了搞清楚背后的动作，官方推荐使用：
import logging
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
```

如果已经有一个现成的数据库，peewee可以很方便的使用pwiz来自动生成代码，更具体看官方文档的：[pwiz, a model generator](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#pwiz) 章节。使用命令：

```bash
python -m pwiz -e sqlite path/to/sqlite_database.db
```

#### 需要恶补的数据库知识

在此之前，有必要搞清楚Database、Model、Field之间的关系。

| 代码里的东西      | 对应数据库里的东西      | 我理解的                        |
| ----------------- | ----------------------- | ------------------------------- |
| Database instance | database.db             | 比如example.db文件              |
| Model class       | Database table          | Model类定义时设属性就是表的表头 |
| Field instance    | Column on a table       | 表头中某一项对应的这一列        |
| Model instance    | Row in a database table | 表中的某一行                    |

### 2.2. 在数据库中增加表

- 在`Database实例`中增加`Model类`, `Model类` = `数据库中的表`

```python
# 3.定义一个Model类，就是数据库重的表单
class Person(BaseModel):
    name = CharField(unique=True) 
    birthday = DateField()

# 5.比如再定义一个与Person关联的Model类
class Pet(BaseModel):
    owner = ForeignKeyField(Person, backref='pets')
    name = CharField()
    animal_typle = CharField()
    
# 4.实例化一个数据库，在数据库中创建一个表
db.connect() #先连接数据库才能生成people.db
db.create_tables([Person, Pet]) # create_tables()的变量是一个列表，可以一次添加多个表
```

> 经典案例可以参考官方文档里面的案例：[Tweet案例](http://docs.peewee-orm.com/en/latest/peewee/example.html#running-the-example)

### 2.3. 在表中增加数据

在`Database实例`中增加`Row`，`Row` = `Model实例`，用 [`save()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.save) 和 [`create()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.create) 方法来新增和更新数据

#### 方法1：`save()`

直接实例化Model类，再`Model().save()`

```python
from datetime import date

xiaoming = Person(name='小明', birthday = date(2000, 1, 2))
xiaoming.save() # Model.save() --> 将数据保存到数据库
```

#### 方法2：`create()`

用`create()`新增数据，不用调用`save()`

```python
xiaodai = Person.create(name = '小呆', birthday = date(2001, 5, 1))
xiaoba  = Person.create(name = '小八', birthday = date(2003, 5, 1))
```

### 2.4. 修改已有数据

```python
xiaodai.name = '小呆呆'
xiaodai.save() #修改完了要记得保存
```

给这几个人安排几只宠物，比如说：

```python
donggua = Pet.create(owner=xiaodai, name='冬瓜', animal_type='dog')
jianhetao = Pet.create(owner=xiaoba, name='尖核桃', animal_type='dog')
zhuer = Pet.create(owner=xiaoming, name='猪儿', animal_type='cat')
zhuer2 = Pet.create(owner=xiaoming, name='二猪儿', animal_type='cat')
```

### 2.5. 删除一条数据

`model.delet_instance()`删除这个model实例。

```python
zhuer.delete_instance() # 猪儿死了，小明很伤心
# Returns: 1
```

### 2.6.  数据关系转移

小八又不想养狗了，于是小呆呆就收养了。

```python
jianhetao.owner = xiaodai # 其实也就是修改已有数据，但是这个是外键的变化
jianhetao.save()
```

对model的属性直接定义，需要用`save()`来确保数据库中的数据进行了更新。

到此先总结下：

| 步骤             | 方法                                                         | 备注                       |
| :--------------- | ------------------------------------------------------------ | -------------------------- |
| 创建数据库       | `SqliteDatabess()`                                           | `db.connect()`后才能实例化 |
| 创建表           | `class Model():`                                             | 属性就是`Filed`            |
| 在数据库中增加表 | `db.create_tables([])`                                       | 变量是列表                 |
| 在表中增加数据   | 方法1:<br />`model = Model( attr1 = '', attr2 = 2)`<br />`model.save()`<br />方法2:<br />`model.create()` |                            |
| 修改已有数据     | `model.attr1 = 'xxx'`<br />`model.save()`                    |                            |
| 删除数据         | `model.delete_instance()`                                    |                            |

## 3、查询数据

### 3.1 查单条数据

```python
# 取出单条数据 Select.get()
xiaoming = Person.select().where(Person.name == '小明').get()
```

快捷用法：

```python
xiaodai = Person.get(Person.name == '小呆呆')
```

### 3.2 查多条数据

#### 列出所有 `select()`

```python
for person in Person.select(): # 取出所有数据
    print(person.name)
```

#### 条件查询 `where()`

```python
qurey = Pet.select().where(Pet.animal_type == 'dog') #按条件取出 
for pet in qurey:
    print(pet.owner.name, pet.name)
```

需要注意的是，这里有个 `pet.owner.name`，这是一种叫做 N+1的问题，应该尽量避免。N+1问题是指，初始查询中没有这种关联关系，需要再执行一次查询才能得到结果。

#### 联表查询 `join()`

```python
query = (Pet
        .select()
        .join(Person) # 联表查询的关键方法
        .where(Pet.animal_type == 'dog'))

for pet in query:
    print(pet.owner.name, pet.name)
```

无论是输出结果还是查询条件，只要是需要跨表查询，都可以用 `join()`来关联不同的表。

```python
query = Pet.select().join(Person).where(Person.name == '小呆呆')
for pet in query:
    print(pet.name)
```

因为我们之前已经有`xiaodai`这个实例，这段代码与下面的等效：

```python
query = Pet.select().where(Pet.owner == xiaodai) # 这个不用联表
for pet in query:
    print(pet.name)
```

#### 排序查询 `order_by()`

如果是字符串，按字母顺序

```python
query = Pet.select().where(Pet.owner == xiaodai).order_by(Pet.name) # 按字母顺序
for pet in query:
    print(pet.name)
```

数字的可以正序、倒序

```python
query = Person.select().order_by(Person.birthday.desc()) #加.desc()倒序
for person in query:                                     #不加，正序
    print(person.name, person.birthday)
```

#### 组合条件筛选

```python
day2000 = date(2000, 1, 1)
day2002 = date(2002, 1, 1)
query = Person.select().where(
    (Person.birthday < day2000) | (Person.birthday > day2002)
)
for person in query:
    print(person.name, person.birthday)
```

`|`、 `&` 等运算符都可以用，还可以使用`between()`.

```python
query = Person.select().where(Person.birthday.between(day2000,day2002))
for person in query:
    print(person.name, person.birthday)
```

#### 汇总和预装

```python
for person in Person.select():
    print(person.name, '有', person.pets.count(), '只宠物')
```

上面这段代码又出现了`N+1`的问题，要用`join()`来处理：

```python
query = (Person
        .select(Person, fn.COUNT(Pet.id).alias('pet_count'))
        .join(Pet, JOIN.LEFT_OUTER) #
        .group_by(Person)
        .order_by(Person.name))

for i in query:
    print(i.name, '有', i.pet_count, '只宠物')
```

`fn()`函数用来执行SQL语句：`fn.COUNT(Pet.id).alias('pet_count')`  =  `COUNT(pet.id) AS pet_count`

再来列出所有的人和他们的宠物。这里有个问题，小八他没有宠物。先分析下数据结构：

- 每个宠物都有一个主人，但是人不一定有宠物、
- `Pet()`对`Person()`是一对一关系，`Person()`对`Pet()`可能是1对0，1对1，1对n。

```python
query = (Person
        .select(Person, Pet)
        .join(Pet, JOIN.LEFT_OUTER)
        .order_by(Person.name))

for person in query:
    if hasattr(person, 'pet'):
        print(person.name, person.pet.name)
    else:
        print(person.name, '没有宠物')
```

这种方法确实可以实现目的，但是peewee有个更好的方法`prefetch()`。

```python
query = Person.select().order_by(Person.name).prefetch(Pet)
for person in query:
    print(person.name)
    for pet in person.pets:
        print('  *', pet.name)
```



#### SQL函数方法

还可以通过`fn()`来执行SQL语句，设置各种查询条件。

## 4、数据库操作的最后一步

```python
db.close()
```

