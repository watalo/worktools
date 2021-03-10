# peewee非官方文档

# 1.Peewee 使用

[![img](https://cdn2.jianshu.io/assets/default_avatar/4-3397163ecdb3855a0a4139c34a695885.jpg)](https://www.jianshu.com/u/cff84d29084f)

[liuchungui](https://www.jianshu.com/u/cff84d29084f)关注

22018.04.21 23:08:46字数 789阅读 29,786

Peewee系列：
[Peewee 使用](https://www.jianshu.com/p/8d1bdd7f4ff5)
[Peewee使用之事务](https://www.jianshu.com/p/915b012a1d91)
[Peewee批量插入数据](https://www.jianshu.com/p/bd51bcdce67d)
[Peewee 使用（二）——增删改查更详细使用](https://www.jianshu.com/p/ba8a27cf7da1)

------

[Peewee](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Fcoleifer%2Fpeewee)是一个简单小巧的Python ORM，它非常容易学习，并且使用起来很直观。

如果想快速入门，请参考[官方的Quckstart](https://links.jianshu.com/go?to=http%3A%2F%2Fdocs.peewee-orm.com%2Fen%2Flatest%2Fpeewee%2Fquickstart.html%23quickstart)。

本文，只是写今天在使用过程中的一些记录。

## 1.1.基本知识

在[官方的Quckstart](https://links.jianshu.com/go?to=http%3A%2F%2Fdocs.peewee-orm.com%2Fen%2Flatest%2Fpeewee%2Fquickstart.html%23quickstart)中，我了解到，Peewee中`Model`类、`fields`和`model实例`与数据库的映射关系如下：

![img](https://upload-images.jianshu.io/upload_images/3120119-3d0648e53fcb2784.png?imageMogr2/auto-orient/strip|imageView2/2/w/436/format/webp)

也就是说，`一个Model类代表一个数据库的表`，`一个Field字段代表数据库中的一个字段`，`而一个model类实例化对象则代表数据库中的一行`。

至于Peewee的实现原理，我暂时没有看源代码，但觉得和廖雪峰老师的[使用元类](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.liaoxuefeng.com%2Fwiki%2F001374738125095c955c1e6d8bb493182103fac9270762a000%2F001386820064557c69858840b4c48d2b8411bc2ea9099ba000)这个文章的例子实现类似。

## 1.2.实践

而使用过程，分成两步：

### 定义Model，建立数据库

在使用的时候，根据需求先定义好Model，然后可以通过`create_tables()`创建表，若是已经创建好数据库表了，可以通过`python -m pwiz`脚本工具直接创建Model。

#### 第一种方式：

先定义Model，然后通过`db.create_tables()`创建或`Model.create_table()`创建表。

例如，我们需要建一个Person表，里面有`name`、`birthday`和`is_relative`三个字段，我们定义的Model如下：

```python
from peewee import *

# 连接数据库
database = MySQLDatabase('test', user='root', host='localhost', port=3306)

# 定义Person
class Person(Model):
    name = CharField()
    birthday = DateField()
    is_relative = BooleanField()

    class Meta:
        database = database
```

然后，我们就可以创建表了

```bash
# 创建表
Person.create_table()

# 创建表也可以这样, 可以创建多个
# database.create_tables([Person])
```

其中，CharField、DateField、BooleanField等这些类型与数据库中的数据类型一一对应，我们直接使用它就行，至于`CharField => varchar(255)`这种转换Peewee已经为我们做好了 。

#### 第二种方式：

已经存在过数据库，则直接通过`python -m pwiz`批量创建Model。
例如，上面我已经创建好了`test`库，并且创建了`Person`表，表中拥有`id`、`name`、`birthday`和`is_relative`字段。那么，我可以使用下面命令：

```bash
# 指定mysql，用户为root，host为localhost，数据库为test
python -m pwiz -e mysql -u root -H localhost --password test > testModel.py
```

然后，输入密码，`pwiz`脚本会自动创建Model，内容如下：

```python
from peewee import *

database = MySQLDatabase('test', **{'charset': 'utf8', 'use_unicode': True, 'host': 'localhost', 'user': 'root', 'password': ''})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Person(BaseModel):
    birthday = DateField()
    is_relative = IntegerField()
    name = CharField()

    class Meta:
        table_name = 'person'
```

## 1.3.操作数据库

操作数据库，就是增、删、改和查。

### 1.3.1.增

直接创建示例，然后使用save()就添加了一条新数据

```php
# 添加一条数据
p = Person(name='liuchungui', birthday=date(1990, 12, 20), is_relative=True)
p.save()
```

### 1.3.2.删

使用delete().where().execute()进行删除，where()是条件，execute()负责执行语句。若是已经查询出来的实例，则直接使用delete_instance()删除。

```bash
# 删除姓名为perter的数据
Person.delete().where(Person.name == 'perter').execute()

# 已经实例化的数据, 使用delete_instance
p = Person(name='liuchungui', birthday=date(1990, 12, 20), is_relative=False)
p.id = 1
p.save()
p.delete_instance()
```

### 1.3.2.改

若是，已经添加过数据的的实例或查询到的数据实例，且表拥有`primary key`时，此时使用save()就是修改数据；若是未拥有实例，则使用update().where()进行更新数据。

```bash
# 已经实例化的数据,指定了id这个primary key,则此时保存就是更新数据
p = Person(name='liuchungui', birthday=date(1990, 12, 20), is_relative=False)
p.id = 1
p.save()

# 更新birthday数据
q = Person.update({Person.birthday: date(1983, 12, 21)}).where(Person.name == 'liuchungui')
q.execute()
```

### 1.3.4.查

单条数据使用Person.get()就行了，也可以使用Person.select().where().get()。若是查询多条数据，则使用Person.select().where()，去掉get()就行了。语法很直观，select()就是查询，where是条件，get是获取第一条数据。

```csharp
# 查询单条数据
p = Person.get(Person.name == 'liuchungui')
print(p.name, p.birthday, p.is_relative)

# 使用where().get()查询
p = Person.select().where(Person.name == 'liuchungui').get()
print(p.name, p.birthday, p.is_relative)

# 查询多条数据
persons = Person.select().where(Person.is_relative == True)
for p in persons:
    print(p.name, p.birthday, p.is_relative)
```

# 2.Peewee使用之事务

](https://www.jianshu.com/u/cff84d29084f)

[liuchungui](https://www.jianshu.com/u/cff84d29084f)关注

2018.04.28 23:19:16字数 790阅读 4,166

------

上周学习了下基本的[Peewee使用](https://www.jianshu.com/p/8d1bdd7f4ff5)，知道了基本的增删改查和建数据库。不过，在项目中同步数据的时候，需要用到事务，于是赶紧补充了官方的[Transactions](https://links.jianshu.com/go?to=http%3A%2F%2Fdocs.peewee-orm.com%2Fen%2Flatest%2Fpeewee%2Ftransactions.html)，然后写个总结。

## 2.1.常用方法

[Peewee](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Fcoleifer%2Fpeewee)实现事务最常用的方法是`Database.atomic()`方法，非常简单，代码示例如下：

```python
from xModels import XUser, database

with database.atomic() as transaction:
    XUser.create(phone='184738373833', password='123456')
    XUser.create(phone='184738373833332323232', password='123456')
```

当事务执行成功之后，它会自动`commit()`，不需要我们手动调。当事务的代码块中抛出异常时，它会自动调用`rollback()`。

例如，如果上面的phone设置了长度限制，第二条语句中的phone太长，那么就会抛出异常，然后上面结果是两个用户都不会被添加到数据库中。

**注意**：上面database是在xModels文件中MySQLDatabase的一个实例，创建方法如下：

```python
from peewee import MySQLDatabase
database = MySQLDatabase('test', **{'charset': 'utf8', 'use_unicode': True, 'host': 'localhost', 'user': 'root', 'password': ''})
```

除了自动`commit()`和`rollback()`之外，我们也可以手动调用`commit()`和`rollback()`方法。

例如：

```dart
with database.atomic() as transaction:
    XUser.create(phone='199999999999', password='123456')
    transaction.commit()
    XUser.create(phone='188888888888', password='123456')
    transaction.rollback()
```

结果：手动调用了`commit()`，phone为**199999999999**的用户成功添加，而**188888888888**因为`rollback()`，不会被添加到数据库中。

## 2.2.两种使用方式

Peewee中实现事务有两种使用方式，一种是将`atomic`当做`Context manager`使用，另外一种将`atomic`当[修饰器](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.liaoxuefeng.com%2Fwiki%2F001374738125095c955c1e6d8bb493182103fac9270762a000%2F001386819879946007bbf6ad052463ab18034f0254bf355000)使用。

### Context manager

这种方式，就是我们前面已经使用过了，示例如下：

```jsx
from xModels import XUser, database

with database.atomic() as transaction:
    XUser.create(phone='184738373833', password='123456')
    XUser.create(phone='184738373833332323232', password='123456')
```

### 修饰器

```python
@database.atomic()
def create_user(phone, password):
    XUser.create(phone=phone, password=password)
    raise Exception('just a test')

create_user(phone='184738373833', password='383838')
```

上面，由于`create_user()`中抛出了一个异常，修饰器中会执行rollback()，从而导致创建用户失败。

## 2.3.事务嵌套使用

Peewee中事务还可以进行嵌套，示例如下：

```dart
with database.atomic() as txn:
    XUser.create(phone='18734738383')

    with database.atomic() as nested_txn:
        XUser.create(phone='1883328484')
```

当上面没有抛出异常时，两个用户同时被添加；当其中任何一条语句抛出异常时，两个用户都不会添加。

不过，它还是跟非嵌套有些区别的，看下面示例。

第一种情况，在嵌套事务中执行rollback()，代码如下：

```dart
with database.atomic() as txn:
    XUser.create(phone='188888888')

    with database.atomic() as nested_txn:
        XUser.create(phone='199999999')
        nested_txn.rollback()
```

**结果**：`188888888`用户被添加，而`199999999`不会被添加。

第二种情况，在外层的事务中执行rollback()，代码如下：

```dart
with database.atomic() as txn:
    XUser.create(phone='188888888')

    with database.atomic() as nested_txn:
        XUser.create(phone='199999999')

    txn.rollback()
```

**结果**：两个用户都不会被添加。

也就是说，外层的`rollback()`会将嵌套中的事务也回滚，而嵌套中的事务不能回滚外层的内容。当然，这只是我的一个尝试，可能还有其他的不同，还需要再探索。

## 2.3.全手动实现事务

全手动实现事务使用的是`Database.manual_commit()`方法，它也有`Context manager`和`修饰器`两种方式。

下面，我们使用`Context manager`方式来实现前面说的`atomic()`方法，示例代码如下：

```python
with database.manual_commit():
    database.begin()  # 开始事务
    try:
        XUser.create(phone='188888888') # 添加用户
    except:
        database.rollback()  # 执行rollback
        raise
    else:
        try:
            database.commit()  # 没有发生异常，执行commit
        except:
            database.rollback() #commit发生异常时，执行rollback
            raise
```

## 2.4.总结

Peewee实现事务最简单的方法就是`atomic()`，它可以使用`Context manager`和`修饰器`两种方式，它也可以手动调用`commit()`和`rollback()`。

# 3.Peewee批量插入数据

------

最近，需要同步数据到Mysql中，数据量有几百万。但是，自己写一个for循环，然后使用`Model.create()`添加，发现这种方式特别慢。难道，像去年爬数据一样，将几百万的数据从Redis取出来，然后使用多线程进行保存？

在Google上搜索了之后，找到一种更简单的方式，那就是使用Peewee原生的方法`insert_many()`，进行批量数据插入。

那么，它的速度有多快？

下面，是我简单的比较了插入10000条数据到本地数据库中，四种方式所需要的时间。

## 3.1. 第一种，for循环和Model.create()

代码如下：

```go
from xModels import XUser, database
import time

NUM = 10000
start_time = time.time()

users = []
for i in range(NUM):
    XUser.create(phone='13847374833', password='123456')

print("插入{}条数据, 花费: {:.3}秒".format(NUM, time.time()-start_time))
```

结果：插入10000条数据, 花费: 10.5秒

## 3.2.第二种，for循环和Model.create()，并放入事务中

代码如下：

```python
from xModels import XUser, database
import time

NUM = 10000
start_time = time.time()

with database.atomic():
    for i in range(NUM):
        XUser.create(phone='13847374833', password='123456')

print("插入{}条数据, 花费: {:.3}秒".format(NUM, time.time()-start_time))
```

结果：插入10000条数据, 花费: 4.94秒

## 3.3.第三种，使用原生的insert_many()方法

```go
from xModels import XUser, database
import time

NUM = 10000
data = [{
            'phone': '13847374833',
            'password': '123456'
        } for i in range(NUM)]

start_time = time.time()

for i in range(0, NUM, 100):
    XUser.insert_many(data[i:i + 100]).execute()

print("插入{}条数据, 花费: {:.3}秒".format(NUM, time.time()-start_time))
```

结果：插入10000条数据, 花费: 0.505秒

## 3.4.第四种，使用原生的insert_many()方法，并放入事务中

```python
from xModels import XUser, database
import time

NUM = 10000
data = [{
            'phone': '13847374833',
            'password': '123456'
        } for i in range(NUM)]

start_time = time.time()

with database.atomic():
    for i in range(0, NUM, 100):
        # 每次批量插入100条，分成多次插入
        XUser.insert_many(data[i:i + 100]).execute()

print("插入{}条数据, 花费: {:.3}秒".format(NUM, time.time()-start_time))
```

结果：插入10000条数据, 花费: 0.401秒

## 3.5.结论

- `insert_many()`比使用for+Model.create()方式快很多，在上面例子中快了十倍不止
- 使用事务，可以些许提升

## 参考

[Python中peewee模块](https://links.jianshu.com/go?to=https%3A%2F%2Fblog.csdn.net%2Fqq_25621385%2Farticle%2Fdetails%2F45848771)

# 4.Peewee 使用——增删改查更详细使用

在四月份刚接触Peewee的时候，写过一篇[Peewee 使用](https://www.jianshu.com/p/8d1bdd7f4ff5)。而后，在使用的过程中，发现很多常用的内容需要搜索查阅，今天就在这里整理一下。

## 4.1.插入数据

插入数据，我们可以实例化一个`Model`，然后再使用`save()`的方法插入到数据库中。如下：

```php
# 插入一条数据
p = Person(name='liuchungui', birthday=date(1990, 12, 20), is_relative=True)
p.save()
```

除了上面，我最常用的是`insert()`方法直接插入数据，它会返回新插入数据的`主键`给我们。

```bash
# 插入一条数据
p_id = Person.insert({
    'name': 'liuchungui'
}).execute()
 # 打印出新插入数据的id
print(p_id)
```

上面都是插入一条数据，若是有很多数据需要插入，例如几万条数据，**为了性能**，这时就需要使用`insert_many()`，如下：

```go
NUM = 10000
data = [{
            'name': '123'
        } for i in range(NUM)]

with database.atomic():
    for i in range(0, NUM, 100):
        # 每次批量插入100条，分成多次插入
        Person.insert_many(data[i:i + 100]).execute()
```

至于为啥要使用`insert_many()`，可以看看我前面写的[Peewee批量插入数据](https://www.jianshu.com/p/bd51bcdce67d)。

## 4.2.查询数据

### 4.2.1.查询单条数据

我们可以直接使用`get()`获取单条数据，在参数中传递查询条件。

```bash
# 查询name为liuchungui的Person
p = Person.get(Person.name == 'liuchungui')
print(p.name) # 打印出liuchungui
```

### 4.2.2.查询多条数据

使用`select()`查询，后面不添加where()是查询整个表的内容。

```bash
# 查询Person整张表的数据
persons = Person.select()
# 遍历数据
for p in persons:
    print(p.name, p.birthday, p.is_relative)
```

我们可以在`select()`后面添加`where()`当做查询条件

```bash
# 获取is_relative为True的数据
persons = Person.select().where(Person.is_relative == True)
for p in persons:
    print(p.name, p.birthday, p.is_relative)
```

我们可以通过`sql()`方法转换为`SQL语句`进行查看理解

```bash
persons = Person.select().where(Person.is_relative == True)
# 打印出的结果为：('SELECT `t1`.`id`, `t1`.`name`, `t1`.`is_relative` FROM `Person` AS `t1` WHERE (`t1`.`is_relative` = %s)', [True])
print(persons.sql())
```

### 4.2.3.查询数据条数、排序、Limit

查询数据条数，直接在后面加上`count()`就行了

```csharp
# 查询整张表的数据条数
total_num = Person.select().count()

# 查询name为liuchungui的Person数量, 返回数量为1
num = Person.select().where(Person.name == 'liuchungui').count()
```

排序，使用的是`order_by()`，参数内加上按对应字段进行排序

```csharp
# 按照创建时间降序排序
persons = Person.select().order_by(Person.create_time.desc())

# 按照创建时间升序排序
persons = Person.select().order_by(Person.create_time.asc())
```

Limit是使用`limit()`，传递一个数字，例如2就是获取前两条数据，它可以搭配`offset()`一起使用

```bash
# 相当于sql语句: select * from person order by create_time desc limit 5
persons = Person.select().order_by(Person.create_time.asc()).limit(5)

# 相当于sql语句中：select * from person order by create_time desc limit 2, 5
persons = Person.select().order_by(Person.create_time.asc()).limit(5).offset(2)
```

## 4.3.更新数据

当一个Model实例拥有主键时，此时使用save()就是修改数据

```php
# 已经实例化的数据,指定了id这个primary key,则此时保存就是更新数据
p = Person(name='liuchungui', birthday=date(1990, 12, 20), is_relative=False)
p.id = 1
p.save()
```

也可以使用`update()`来更新数据，一般都会搭配`where()`使用

```bash
# 更新birthday数据
q = Person.update({Person.height: 1.75}).where(Person.name == 'Jack')
q.execute()
```

当然，除了使用Model的属性，我们可以直接使用字典结构来更新数据

```bash
q = Person.update({
    'height': 1.75
}).where(Person.name == 'Jack')
q.execute()
```

## 4.4.查询操作符

在查询、更新、删除数据的时候，经常会带有Where条件语句。而Peewee支持以下类型比较符：

![img](https:////upload-images.jianshu.io/upload_images/3120119-840871078affeecf.png?imageMogr2/auto-orient/strip|imageView2/2/w/372/format/webp)

其中，==、<、<=、>、>=、!=是很容易理解的，重点提下`<<`、`>>`和`%`。用示例说明：

```kotlin
# <<使用，查询省份属于湖北和湖南的，对应sql语句：select * from person where province in ('湖南', '湖北')
persons = Person.select().where(Person.province << ['湖南', '湖北'])

# >>使用，查询省份为空的，sql语句: select * from person where province is Null
persons = Person.select().where(Person.province >> None)

# %使用，查询省份中含有 湖 字，sql语句：select * from person where province like '%湖%'
persons = Person.select().where(Person.province % '%湖%')
```

有时，我们查询条件不止一个，需要使用逻辑运算符连接，而Python中的`and`、`or`在Peewee是不支持的，此时我们需要使用Peewee封装好的运算符，如下：

![img](https:////upload-images.jianshu.io/upload_images/3120119-fb979d611d73c520.png?imageMogr2/auto-orient/strip|imageView2/2/w/628/format/webp)

使用示例如下：

```csharp
# 查询湖南和湖北的, 注意需要用()将Person.province == '湖南'包一层
persons = Person.select().where((Person.province == '湖南') | (Person.province == '湖北'))

# 查询湖南和身高1.75
persons = Person.select().where((Person.province == '湖南') & (Person.height == 1.75))
```

**注意**：使用的时候，需要内部还使用()将Person.province == '湖南'包起来，否则不会生效。示例：persons = Person.select().where(**(Person.province == '湖南')** | **(Person.province == '湖北')**)

除了上面的操作符以外，Peewee还有更多没有重载的操作符，如下：

![img](https:////upload-images.jianshu.io/upload_images/3120119-34f9c3cff173f8af.png?imageMogr2/auto-orient/strip|imageView2/2/w/1200/format/webp)

## 4.5.联表查询

有时，我们需要查询两个表中的数据，在Peewee中也可以实现，官方示例如下：

```csharp
query = (Tweet
         .select(Tweet.content, Tweet.timestamp, User.username)
         .join(User, on=(User.id == Tweet.user_id))
         .order_by(Tweet.timestamp.desc()))
```

上面查询的结果，会在Tweet的Model中添加一个属性`user`，此时我们可以通过`user`来访问到查询到的User表信息，如下：

```css
for tweet in query:
    print(tweet.content, tweet.timestamp, tweet.user.username)
```

## 4.6.事务

[Peewee](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Fcoleifer%2Fpeewee)实现事务最常用的方法是`Database.atomic()`方法，使用起来非常简单，如下：

```jsx
from xModels import XUser, database

with database.atomic() as transaction:
    XUser.create(phone='184738373833', password='123456')
    XUser.create(phone='184738373833332323232', password='123456')
```

更多可参考我前面写的[Peewee使用之事务](https://www.jianshu.com/p/915b012a1d91)

## 参考

[Peewee querying](https://links.jianshu.com/go?to=http%3A%2F%2Fdocs.peewee-orm.com%2Fen%2Flatest%2Fpeewee%2Fquerying.html%23querying)
 [peewee 查询](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.cnblogs.com%2Fmiaojiyao%2Farticles%2F5217757.html)









作者：liuchungui
链接：https://www.jianshu.com/p/ba8a27cf7da1
来源：简书
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。



