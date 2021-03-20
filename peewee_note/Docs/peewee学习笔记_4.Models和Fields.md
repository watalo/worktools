# Models and Fields

[TOC]

------



[`Model`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model) 类, [`Field`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Field) 实例和model实例都对应有数据库概念:

| Things         | Corresponds to…         |
| -------------- | ----------------------- |
| Model class    | Database table          |
| Field instance | Column on a table       |
| Model instance | Row in a database table |

下面的代码展示了定义数据库连接（databass connection）和Model类的典型方式：

```python
import datetime
from peewee import *

db = SqliteDatabase('my_app.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = CharField(unique=True)

class Tweet(BaseModel):
    user = ForeignKeyField(User, backref='tweets')
    message = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)
    is_published = BooleanField(default=True)
```

1. 创建一个数据库实例 [`Database`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database).

   ```python
   db = SqliteDatabase('my_app.db')
   ```
   
   `db` 管理着Sqlite数据库的连接. 在上面案例里用到了 [`SqliteDatabase`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase)，但我们同样可以使用其他的 [database engines](http://docs.peewee-orm.com/en/latest/peewee/database.html#database).

2. 创建一个基类连接数据库

   ```python
   class BaseModel(Model):
   	class Meta:
        	database = db
   ```
   
   定义基类来建立数据库连接的好处：
   
   - 保持代码简洁，不用对后面的Model类们不停的去指定数据库。
   - Model类的配置保存在Meta类的命名空间中，换句话说。Meta类的配资通过继承传递给了所有的子类。
   
   - *Model.Meta*.还有[许多不同属性](http://docs.peewee-orm.com/en/latest/peewee/models.html#model-options) 可以配置

3. 定义一个model实例

   ```python
   class User(BaseModel):
   	username = CharField(unique=True)
   ```
   
   Model 定义用的是ORMs的声明方式，类似于SQLAlchemy或Django。 注意：User继承了Basemodel，所以User也将继承数据库连接。我们明确的定义了username的唯一行限制。因为我们没有指明一个主键，所以peewee会自动增加一个自增长的整数作为主键——id。

> Note
>
> 如果我们有个现成的数据库，可以使用pwiz来自动生成。
>
> ```python
> python -m pwiz -e sqlite path/to/sqlite_database.db
> ```
>
> 其他数据库参考：[pwiz, a model generator](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#pwiz) 
>



## Fields()：字段

[`Field`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Field)类用于描述[`Model`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model)属性到数据库列的映射。每个字段类型都有相应的SQL存储类(即varchar、int)， python数据类型和底层存储之间的转换是透明处理的。

当创建[`Model`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model)类时，字段被定义为类属性。这对于django框架的用户来说应该很熟悉。这里有一个例子:

```python
class User(Model):
    username = CharField()
    join_date = DateTimeField()
    about_me = TextField()
```

在上面的例子中，因为没有一个字段被初始化为`primary_key=True`，一个自动递增的主键将被自动创建并命名为`id`。Peewee使用[`AutoField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#AutoField)表示一个自动递增的整型主键，这意味着`primary_key=True`。有一种特殊类型的字段，[`ForeignKeyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ForeignKeyField)，它允许你直观地表示模型之间的外键关系:

```python
class Message(Model):
    user = ForeignKeyField(User, backref='messages')
    body = TextField()
    send_date = DateTimeField(default=datetime.datetime.now)
```

这允许你像下面这样写代码::

```python
>>> print(some_message.user.username)
Some User

>>> for message in some_user.messages:
...     print(message.body)
some message
another message
yet another message
```

> ⚠注意
>
> 有关外键、模型之间的连接和关系的深入讨论，请参阅[Relationships and Joins](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#relationships)文档。
>
> 有关字段的完整文档，请参阅[Fields API notes](http://docs.peewee-orm.com/en/latest/peewee/api.html#fields-api)
>



### 字段类型表

| 字段类型            | Sqlite        | Postgresql       | MySQL            |
| ------------------- | ------------- | ---------------- | ---------------- |
| `AutoField`         | integer       | serial           | integer          |
| `BigAutoField`      | integer       | bigserial        | bigint           |
| `IntegerField`      | integer       | integer          | integer          |
| `BigIntegerField`   | integer       | bigint           | bigint           |
| `SmallIntegerField` | integer       | smallint         | smallint         |
| `IdentityField`     | not supported | int identity     | not supported    |
| `FloatField`        | real          | real             | real             |
| `DoubleField`       | real          | double precision | double precision |
| `DecimalField`      | decimal       | numeric          | numeric          |
| `CharField`         | varchar       | varchar          | varchar          |
| `FixedCharField`    | char          | char             | char             |
| `TextField`         | text          | text             | text             |
| `BlobField`         | blob          | bytea            | blob             |
| `BitField`          | integer       | bigint           | bigint           |
| `BigBitField`       | blob          | bytea            | blob             |
| `UUIDField`         | text          | uuid             | varchar(40)      |
| `BinaryUUIDField`   | blob          | bytea            | varbinary(16)    |
| `DateTimeField`     | datetime      | timestamp        | datetime         |
| `DateField`         | date          | date             | date             |
| `TimeField`         | time          | time             | time             |
| `TimestampField`    | integer       | integer          | integer          |
| `IPField`           | integer       | bigint           | bigint           |
| `BooleanField`      | integer       | boolean          | bool             |
| `BareField`         | untyped       | not supported    | not supported    |
| `ForeignKeyField`   | integer       | integer          | integer          |

> ⚠注意
>
> 在上面的表格中没有看到你要找的字段吗?创建自定义字段类型并在模型中使用它们是很容易的。
>
> - [创建自定义字段](http://docs.peewee-orm.com/en/latest/peewee/models.html#custom-fields)
> - [`Database`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database)，特别是' fields '参数。
>



### 字段初始化参数

所有字段类型接受的参数及其默认值:

- `null = False` – 允许空值
- `index = False` – 在此列上创建索引
- `unique = False` – 在此列上创建唯一索引。参阅 [adding composite indexes](http://docs.peewee-orm.com/en/latest/peewee/models.html#model-indexes).
- `column_name = None` –在数据库中显式地指定列名
- `default = None` – 用于未初始化模型的任何值或可调用的默认值
- `primary_key = False` – 表的主键
- `constraints = None` - 一个或多个约束条件, e.g. `[Check('price > 0')]`
- `sequence = None` – 序列名称(如果后端支持)
- `collation = None` – 用于排序字段/索引的排序规则
- `unindexed = False` – 指定虚拟表上的字段不应该被索引(**SQLite-only**)
- `choices = None` – 包含 `value`, `display`的2元元组的可选迭代器
- `help_text = None` – 表示此字段的帮助文本
- `verbose_name = None` – 表示此字段“用户友好”名称的字符串
- `index_type = None` – 指定一个自定义索引类型，例如对于Postgres，你可以指定一个`BRIN`或`GIN`索引。



### 有些字段有特殊的参数…

| 字段类型                                                     | 特殊参数                                                     |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [`CharField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#CharField) | `max_length`                                                 |
| [`FixedCharField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#FixedCharField) | `max_length`                                                 |
| [`DateTimeField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#DateTimeField) | `formats`                                                    |
| [`DateField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#DateField) | `formats`                                                    |
| [`TimeField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#TimeField) | `formats`                                                    |
| [`TimestampField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#TimestampField) | `resolution`, `utc`                                          |
| [`DecimalField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#DecimalField) | `max_digits`, `decimal_places`, `auto_round`, `rounding`     |
| [`ForeignKeyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ForeignKeyField) | `model`, `field`, `backref`, `on_delete`, `on_update`, `deferrable` `lazy_load` |
| [`BareField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BareField) | `adapt`                                                      |

> 注意
>
> `default`和`choices`都可以在数据库级别上分别实现为 *DEFAULT* 和 *CHECK CONSTRAINT* ，但是任何应用程序的更改都需要更改模式。正因如此，`default`完全是在python中实现的，而`choices`则不经过验证，只用于元数据目的而存在。
>
> 要添加数据库(服务器端)约束，请使用`constraints`参数。



### 默认字段值

在创建对象时，Peewee可以为字段提供默认值。例如，让`IntegerField`默认值为0而不是`NULL`，你可以用默认值声明字段:

```python
class Message(Model):
    context = TextField()
    read_count = IntegerField(default=0)
```

在某些情况下，可以将默认值设置为动态的。一种常见的场景是使用当前日期和时间。Peewee允许您在这些情况下指定一个函数，该函数的返回值将在创建对象时使用。注意，我们只提供了函数，实际上并没有*调用*它:

```python
class Message(Model):
    context = TextField()
    timestamp = DateTimeField(default=datetime.datetime.now)
```

> 注意
>
> 如果你正在使用一个接受可变类型(list, dict，等等)的字段，并且想要提供一个默认值，将默认值包装在一个简单的函数中是一个好主意，这样多个模型实例就不会共享对相同底层对象的引用:

```python
def house_defaults():
    return {'beds': 0, 'baths': 0}

class House(Model):
    number = TextField()
    street = TextField()
    attributes = JSONField(default=house_defaults)
```

数据库还可以为字段提供默认值。虽然peewee没有明确提供设置服务器端默认值的API，你可以使用`constraints`参数来指定服务器端默认值:

```python
class Message(Model):
    context = TextField()
    timestamp = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
```

> 请注意
>
> **记住:**当使用`default`参数时，值是由Peewee设置的，而不是作为实际表和列定义的一部分。



### 外键字段ForeignKeyField

[`ForeignKeyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ForeignKeyField)是一种特殊的字段类型，允许一个模型引用另一个模型。通常，外键将包含与之相关的模型的主键(但您可以通过指定`field`来指定特定的列)。

外键允许数据[规范化](http://en.wikipedia.org/wiki/Database_normalization)。在我们的示例模型中，有一个从`Tweet`到`User`的外键。这意味着所有用户都存储在自己的表中，推文也是如此，并且从tweet到user的外键允许每个tweet指向特定的user对象。

> 注意
>
> 参考[Relationships and Joins](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#relationships)文档，深入讨论外键、模型之间的连接和关系。

在peewee中，访问[`ForeignKeyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ForeignKeyField)的值将返回整个相关对象，例如:

```python
tweets = (Tweet
          .select(Tweet, User)
          .join(User)
          .order_by(Tweet.created_date.desc()))
for tweet in tweets:
    print(tweet.user.username, tweet.message)
```

> 注意
>
> 在上面的示例中，`User`数据被选择为查询的一部分。有关此技术的更多示例，请参见[避免N+1](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#nplusone)文档。

但是，如果我们没有选择`User`，那么将发出一个**额外的查询**来获取相关的`User`数据:

```python
tweets = Tweet.select().order_by(Tweet.created_date.desc())
for tweet in tweets:
    # WARNING: an additional query will be issued for EACH tweet
    # to fetch the associated User data.
    print(tweet.user.username, tweet.message)
```

有时，您只需要外键列的相关主键值。在这种情况下，Peewee遵循Django建立的约定，允许你通过在外键字段的名称后面加上`"_id"`来访问原始的外键值:

```python
tweets = Tweet.select()
for tweet in tweets:
    # Instead of "tweet.user", we will just get the raw ID value stored
    # in the column.
    print(tweet.user_id, tweet.message)
```

为了防止意外解析外键并触发额外的查询，[`ForeignKeyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ForeignKeyField)支持初始化参数`lazy_load`，当被禁用时，它的行为类似于`"_id"`属性。例如:

```python
class Tweet(Model):
    # ... same fields, except we declare the user FK to have
    # lazy-load disabled:
    user = ForeignKeyField(User, backref='tweets', lazy_load=False)

for tweet in Tweet.select():
    print(tweet.user, tweet.message)

# With lazy-load disabled, accessing tweet.user will not perform an extra
# query and the user ID value is returned instead.
# e.g.:
# 1  tweet from user1
# 1  another from user1
# 2  tweet from user2

# However, if we eagerly load the related user object, then the user
# foreign key will behave like usual:
for tweet in Tweet.select(Tweet, User).join(User):
    print(tweet.user.username, tweet.message)

# user1  tweet from user1
# user1  another from user1
# user2  tweet from user1
```



### 外键反向引用(back-refences)

[`ForeignKeyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ForeignKeyField)允许反向引用属性绑定到目标模型。隐式地，这个属性将被命名为`classname_set`，其中`classname `是类的小写名称，但可以使用参数`backref`覆盖:

```python
class Message(Model):
    from_user = ForeignKeyField(User, backref='outbox')
    to_user = ForeignKeyField(User, backref='inbox')
    text = TextField()

for message in some_user.outbox:
    # We are iterating over all Messages whose from_user is some_user.
    print(message)

for message in some_user.inbox:
    # We are iterating over all Messages whose to_user is some_user
    print(message)
```



### DateTimeField、DateField和TimeField

这三个用于处理日期和时间的字段有特殊的属性，允许访问年、月、小时等。

[`DateField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#DateField) 属性:

- `year`
- `month`
- `day`

[`TimeField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#TimeField) 属性:

- `hour`
- `minute`
- `second`

[`DateTimeField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#DateTimeField) 以上都有。

这些属性可以像任何其他表达式一样使用。假设我们有一个事件日历，想要突出显示当前月份中有一个事件的所有日子:

```python
# Get the current time.
now = datetime.datetime.now()

# Get days that have events for the current month.
Event.select(Event.event_date.day.alias('day')).where(
    (Event.event_date.year == now.year) &
    (Event.event_date.month == now.month))
```

> 注意
>
> SQLite没有日期类型，所以日期存储在格式化的文本列中。为了确保可以进行比较，需要对日期进行格式化，以便按字典顺序排序。这就是为什么默认情况下，它们被存储为`YYYY-MM-DD HH:MM:SS`。



### BitField 和 BigBitField

[`BitField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BitField)和[`BigBitField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BigBitField)在3.0.0中新增。前者提供了[`IntegerField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#IntegerField)的一个子类，适合将特性切换存储为整数位掩码。后者适用于存储大型数据集的位图，例如表示成员或位图类型的数据。

作为使用[`BitField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BitField)的一个例子，让我们假设我们有一个*Post*模型，我们希望存储关于Post的某些True/False标志。我们可以将所有这些特性切换存储在它们自己的[`boolean`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BooleanField)对象中，或者我们可以使用[`BitField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BitField)来代替:

```python
class Post(Model):
    content = TextField()
    flags = BitField()

    is_favorite = flags.flag(1)
    is_sticky = flags.flag(2)
    is_minimized = flags.flag(4)
    is_deleted = flags.flag(8)
```

使用这些标记非常简单:

```python
>>> p = Post()
>>> p.is_sticky = True
>>> p.is_minimized = True
>>> print(p.flags)  # Prints 4 | 2 --> "6"
6
>>> p.is_favorite
False
>>> p.is_sticky
True
```

我们还可以使用Post类上的标记在查询中构建表达式:

```python
# Generates a WHERE clause that looks like:
# WHERE (post.flags & 1 != 0)
favorites = Post.select().where(Post.is_favorite)

# Query for sticky + favorite posts:
sticky_faves = Post.select().where(Post.is_sticky & Post.is_favorite)
```

因为[`BitField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BitField)是以整数形式存储的，所以最多可以表示64个标志(64位是整数列的通用大小)。为了存储任意大的位图，你可以使用[`BigBitField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BigBitField)，它使用一个自动管理的字节缓冲区，存储在[`BlobField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BlobField)。

当批量更新[`BitField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BitField)中的一个或多个位时，你可以使用位操作符来设置或清除一个或多个位:

```python
# Set the 4th bit on all Post objects.
Post.update(flags=Post.flags | 8).execute()

# Clear the 1st and 3rd bits on all Post objects.
Post.update(flags=Post.flags & ~(1 | 4)).execute()
```

For simple operations, the flags provide handy `set()` and `clear()` methods for setting or clearing an individual bit:

对于简单的操作，标记提供了方便的`set()`和`clear()`方法来设置或清除单个位:

```python
# Set the "is_deleted" bit on all posts.
Post.update(flags=Post.is_deleted.set()).execute()

# Clear the "is_deleted" bit on all posts.
Post.update(flags=Post.is_deleted.clear()).execute()
```

示例使用:

```python
class Bitmap(Model):
    data = BigBitField()

bitmap = Bitmap()

# Sets the ith bit, e.g. the 1st bit, the 11th bit, the 63rd, etc.
bits_to_set = (1, 11, 63, 31, 55, 48, 100, 99)
for bit_idx in bits_to_set:
    bitmap.data.set_bit(bit_idx)

# We can test whether a bit is set using "is_set":
assert bitmap.data.is_set(11)
assert not bitmap.data.is_set(12)

# We can clear a bit:
bitmap.data.clear_bit(11)
assert not bitmap.data.is_set(11)

# We can also "toggle" a bit. Recall that the 63rd bit was set earlier.
assert bitmap.data.toggle_bit(63) is False
assert bitmap.data.toggle_bit(63) is True
assert bitmap.data.is_set(63)
```



### BareField

[`BareField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BareField)类仅用于SQLite。由于SQLite使用动态类型，而数据类型没有被强制执行，所以可以很好的声明没有任何数据类型的字段。在这些情况下，您可以使用[`BareField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BareField)。使用meta-columns或无类型的列SQLite虚拟表也是常见的，所以对于这些情况下,您可能希望使用一个无类型字段(尽管对于全文搜索，您应该使用[`SearchField`](http://docs.peewee-orm.com/en/latest/peewee/sqlite_ext.html)作为替换 )。

[`BareField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BareField)接受一个特殊参数`adapt `。此参数是一个函数，它接受来自数据库的值，并将其转换为适当的Python类型。例如，如果你有一个包含无类型列的虚拟表，但你知道它将返回`int`对象，你可以指定`adapt=int`。

例子:

```python
db = SqliteDatabase(':memory:')

class Junk(Model):
    anything = BareField()

    class Meta:
        database = db

# Store multiple data-types in the Junk.anything column:
Junk.create(anything='a string')
Junk.create(anything=12345)
Junk.create(anything=3.14159)
```



### 创建自定义字段

在peewee中支持很方便的添加自定义字段类型的支持。在这个例子中，我们将为postgresql创建一个UUID字段(它有一个本地的UUID列类型)。

要添加自定义字段类型，首先需要确定字段数据将存储在哪种类型的列中。如果你只是想添加python行为，比如，一个十进制字段(例如创建一个货币字段)，你只需要子类[`DecimalField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#DecimalField)。另一方面，如果数据库提供了定制的列类型，则需要让peewee知道。这是由`Filed.field_type`属性控制。

> 注意
>
> Peewee使用[`UUIDField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#UUIDField)发送，下面的代码只是作为示例。

让我们从定义UUID字段开始:

```python
class UUIDField(Field):
    field_type = 'uuid'
```

我们将把UUID存储在本地UUID列中。由于psycopg2默认情况下将数据作为字符串处理，我们将在字段中添加两个要处理的方法:

- 来自数据库的数据将用于我们的应用程序

- 数据从我们的python应用程序进入数据库

```python
import uuid

class UUIDField(Field):
    field_type = 'uuid'

    def db_value(self, value):
        return value.hex  # convert UUID to hex string.

    def python_value(self, value):
        return uuid.UUID(value) # convert hex string to UUID
```

**此步骤是可选的。**默认情况下，`field_type`值将用于数据库模式中的列数据类型。如果你需要支持使用不同数据类型的字段数据的多个数据库，我们需要让数据库知道如何将这个*uuid*标签映射到数据库中的实际*uuid*列类型。在[`Database`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database)构造函数中指定重写:

```python
# Postgres, we use UUID data-type.
db = PostgresqlDatabase('my_db', field_types={'uuid': 'uuid'})

# Sqlite doesn't have a UUID type, so we use text type.
db = SqliteDatabase('my_db', field_types={'uuid': 'text'})
```

就是它!有些字段可能支持外来操作，比如postgresql的HStore字段就像一个键/值存储，并且有自定义的操作符，比如*contains*和*update*。您还可以指定[自定义操作](http://docs.peewee-orm.com/en/latest/peewee/query_operators.html#custom-operators)。例如代码，请在`playhouse.postgres_ext`中查看['`HStoreField`](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#HStoreField)的源代码。



### 字段命名冲突

类实现的类实例方法,例如[`Model.save ()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.save)或[`Model.create ()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.create)。如果您声明的字段名称与模型方法一致

，则可能会导致问题。考虑:

```python
class LogEntry(Model):
    event = TextField()
    create = TimestampField()  # Uh-oh.
    update = TimestampField()  # Uh-oh.
```

为了避免在数据库模式中仍然使用所需的列名时出现这个问题，可以显式指定`column_name`，同时为字段属性提供另一个名称:

```python
class LogEntry(Model):
    event = TextField()
    create_ = TimestampField(column_name='create')
    update_ = TimestampField(column_name='update')
```



## 创建模型表

为了开始使用我们的模型，有必要先打开到数据库的连接并创建表。Peewee将运行必要的*CREATE TABLE*查询，另外创建任何约束和索引。

```python
# Connect to our database.
db.connect()

# Create the tables.
db.create_tables([User, Tweet])
```

> 注意
>
> 严格地说，没有必要调用[`connect()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.connect)，但显式调用是一个好做法。这样，如果出现错误，错误发生在连接步骤，而不是在某个任意时间之后。

> 注意
>
> 默认情况下，Peewee在创建表时包含`IF NOT EXISTS`子句。如果你想禁用它，指定`safe=False`。

在你创建了你的表之后，如果你选择修改你的数据库模式（schema）(通过添加，删除或以其他方式改变列)，你需要:

- 删除表并重新创建。 
- 执行一个或多个*ALTER TABLE*查询。Peewee附带了一个模式迁移工具，可以极大地简化这个过程。请查看[schema migrations](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#migrate)文档了解详细信息。



## 模型选项和表的元数据（metadata）

为了不污染模型命名空间，特定于模型的配置被放在一个名为*Meta*的特殊类中(这是从django框架借来的约定):

```python
from peewee import *

contacts_db = SqliteDatabase('contacts.db')

class Person(Model):
    name = CharField()

    class Meta:
        database = contacts_db
```

这指示peewee，每当对*Person*执行查询时，都要使用`contact.db`数据库。

> 注意
>
> 看看[示例模型](http://docs.peewee-orm.com/en/latest/peewee/models.html#blog-models)——您会注意到我们创建了一个定义数据库的“BaseModel”，然后进行了扩展。
> 这是定义数据库和创建模型的首选方法。

一旦定义了类，就不应该访问`ModelClass`，而使用`ModelClass._meta`:

```python
>>> Person.Meta
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: type object 'Person' has no attribute 'Meta'

>>> Person._meta
<peewee.ModelOptions object at 0x7f51a2f03790>
```

`ModelOptions`类实现了几个可能用于检索模型元数据的方法(如字段列表、外键关系等)。

```python
>>> Person._meta.fields
{'id': <peewee.AutoField object at 0x7f51a2e92750>,
 'name': <peewee.CharField object at 0x7f51a2f0a510>}

>>> Person._meta.primary_key
<peewee.AutoField object at 0x7f51a2e92750>

>>> Person._meta.database
<peewee.SqliteDatabase object at 0x7f519bff6dd0>
```

有几个选项你可以指定为`Meta`属性。虽然大多数选项是可继承的，但有些选项是特定于表的，不会被子类继承。

| 选项                 | 意义                                                         | 能否继承? |
| -------------------- | ------------------------------------------------------------ | --------- |
| `database`           | database for model                                           | yes       |
| `table_name`         | name of the table to store data                              | no        |
| `table_function`     | function to generate table name dynamically                  | yes       |
| `indexes`            | a list of fields to index                                    | yes       |
| `primary_key`        | a [`CompositeKey`](http://docs.peewee-orm.com/en/latest/peewee/api.html#CompositeKey) instance | yes       |
| `constraints`        | a list of table constraints                                  | yes       |
| `schema`             | the database schema for the model                            | yes       |
| `only_save_dirty`    | when calling model.save(), only save dirty fields            | yes       |
| `options`            | dictionary of options for create table extensions            | yes       |
| `table_settings`     | list of setting strings to go after close parentheses        | yes       |
| `temporary`          | indicate temporary table                                     | yes       |
| `legacy_table_names` | use legacy table name generation (enabled by default)        | yes       |
| `depends_on`         | indicate this table depends on another for creation          | no        |
| `without_rowid`      | indicate table should not have rowid (SQLite only)           | no        |

下面是一个显示可继承属性和不可继承属性的示例:

```python
>>> db = SqliteDatabase(':memory:')
>>> class ModelOne(Model):
...     class Meta:
...         database = db
...         table_name = 'model_one_tbl'
...
>>> class ModelTwo(ModelOne):
...     pass
...
>>> ModelOne._meta.database is ModelTwo._meta.database
True
>>> ModelOne._meta.table_name == ModelTwo._meta.table_name
False
```

### Meta.primary_key

`Meta.primary_key`属性用于指定[`CompositeKey`](http://docs.peewee-orm.com/en/latest/peewee/api.html#CompositeKey)或表示模型无主键。复合主键在这里有更详细的讨论:[复合主键](http://docs.peewee-orm.com/en/latest/peewee/models.html#composite-key)。

要指出模型不应该有主键，则设置`primary_key = False`。

```python
class BlogToTag(Model):
    """A simple "through" table for many-to-many relationship."""
    blog = ForeignKeyField(Blog)
    tag = ForeignKeyField(Tag)

    class Meta:
        primary_key = CompositeKey('blog', 'tag')

class NoPrimaryKey(Model):
    data = IntegerField()

    class Meta:
        primary_key = False
```



### 表的名字

默认情况下，Peewee会根据模型类的名称自动生成一个表名。表名的生成方式取决于`Meta.legacy_table_names`的值。默认情况下，`legacy_table_names=True`以避免破坏向后兼容性。但是，如果您希望使用新的和改进的表名生成，您可以指定`legacy_table_names=False`。

根据`legacy_table_names`的值，这个表显示了模型名转换为SQL表名的不同之处:

| Model name       | legacy_table_names=True | legacy_table_names=False (new) |
| ---------------- | ----------------------- | ------------------------------ |
| User             | user                    | user                           |
| UserProfile      | userprofile             | user_profile                   |
| APIResponse      | apiresponse             | api_response                   |
| WebHTTPRequest   | webhttprequest          | web_http_request               |
| mixedCamelCase   | mixedcamelcase          | mixed_camel_case               |
| Name2Numbers3XYZ | name2numbers3xyz        | name2_numbers3_xyz             |

> 注意
>
> 为了保持向后兼容性，当前版本(Peewee 3.x)默认指定`legacy_table_names=True`。
>
> 在下一个主要版本(Peewee 4.0)中，`legacy_table_names`的默认值为`False`。

要显式地为模型类指定表名，请使用`table_name`元选项。这个特性对于处理现有的数据库模式很有用，这些模式可能使用了笨拙的命名约定:

```python
class UserProfile(Model):
    class Meta:
        table_name = 'user_profile_tbl'
```

如果你想实现自己的命名约定，你可以指定`table_function`元选项。这个函数将与您的模型类一起调用，并且应该以字符串的形式返回所需的表名。假设我们的公司指定表名应该是小写的，并且以“_tbl”结尾，我们可以将其作为一个表函数来实现:

```python
def make_table_name(model_class):
    model_name = model_class.__name__
    return model_name.lower() + '_tbl'

class BaseModel(Model):
    class Meta:
        table_function = make_table_name

class User(BaseModel):
    # table_name will be "user_tbl".

class UserProfile(BaseModel):
    # table_name will be "userprofile_tbl".
```



## 索引和约束

Peewee可以在单个或多个列上创建索引，可以选择包含一个*UNIQUE*约束。Peewee还支持对模型和字段的用户定义约束。

### 单列索引和约束

使用字段初始化参数定义单列索引。在`username`字段添加唯一索引，在`email`字段添加普通索引，示例如下:

```python
class User(Model):
    username = CharField(unique=True)
    email = CharField(index=True)
```

要在列上添加用户定义的约束，可以使用`constraints`参数传入。你可能希望指定一个默认值作为模式的一部分，或者添加一个` CHECK `约束，例如:

```python
class Product(Model):
    name = CharField(unique=True)
    price = DecimalField(constraints=[Check('price < 10000')])
    created = DateTimeField(
        constraints=[SQL("DEFAULT (datetime('now'))")])
```

### 多列索引

可以使用嵌套的元组将多列索引定义为`Meta`属性。每个数据库索引都是一个2元组，第一部分是字段名的元组，第二部分是一个布尔值，指示索引是否应该是唯一的。

```python
class Transaction(Model):
    from_acct = CharField()
    to_acct = CharField()
    amount = DecimalField()
    date = DateTimeField()

    class Meta:
        indexes = (
            # create a unique on from/to/date
            (('from_acct', 'to_acct', 'date'), True),

            # create a non-unique on from/to
            (('from_acct', 'to_acct'), False),
        )
```

> 请注意
>
> 如果你的索引元组只包含一个条目，记得在后面加一个**逗号**:
>
> ```python
> class Meta:
>     indexes = (
>         (('first_name', 'last_name'), True),  # Note the trailing comma!
>     )
> ```
>



### 高级索引生成器

Peewee支持使用[`model .add_index() `](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.add_index)方法或直接使用[`ModelIndex`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ModelIndex)助手类等更结构化的API来声明模型上的索引。

示例:

```python
class Article(Model):
    name = TextField()
    timestamp = TimestampField()
    status = IntegerField()
    flags = IntegerField()

# Add an index on "name" and "timestamp" columns.
Article.add_index(Article.name, Article.timestamp)

# Add a partial index on name and timestamp where status = 1.
Article.add_index(Article.name, Article.timestamp,
                  where=(Article.status == 1))

# Create a unique index on timestamp desc, status & 4.
idx = Article.index(
    Article.timestamp.desc(),
    Article.flags.bin_and(4),
    unique=True)
Article.add_index(idx)
```

> 警告
>
> SQLite不支持参数化的`CREATE INDEX`查询。这意味着，当使用SQLite创建涉及表达式或标量值的索引时，您需要使用[`SQL `](http://docs.peewee-orm.com/en/latest/peewee/api.html#SQL)助手声明索引:

```python
# SQLite does not support parameterized CREATE INDEX queries, so
# we declare it manually.
Article.add_index(SQL('CREATE INDEX ...'))
```

详情请参见[`add_index()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.add_index)。

更多信息，请参见:

- [`Model.add_index()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.add_index)
- [`Model.index()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.index)
- [`ModelIndex`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ModelIndex)
- [`Index`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Index)



### 表格限制

Peewee允许您向[`Model`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model)添加任意约束，当创建模式时，这将成为表定义的一部分。

例如，假设您有一个*people*表，其中有两列的复合主键，即人名的姓和名。你希望有另一个表与*people*表相关，为了做到这一点，你需要定义一个外键约束:

```python
class Person(Model):
    first = CharField()
    last = CharField()

    class Meta:
        primary_key = CompositeKey('first', 'last')

class Pet(Model):
    owner_first = CharField()
    owner_last = CharField()
    pet_name = CharField()

    class Meta:
        constraints = [SQL('FOREIGN KEY(owner_first, owner_last) '
                           'REFERENCES person(first, last)')]
```

你也可以在表这个层级实现`CHECK`约束:

```python
class Product(Model):
    name = CharField(unique=True)
    price = DecimalField()

    class Meta:
        constraints = [Check('price < 10000')]
```



## 主键，组合键和其他技巧

[`AutoField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#AutoField)用于标识一个自动递增的整数主键。如果您没有指定主键，Peewee将自动创建一个名为`id`的自动递增主键。

要使用不同的字段名指定一个自动递增的ID，你可以这样写:

```python
class Event(Model):
    event_id = AutoField()  # Event.event_id will be auto-incrementing PK.
    name = CharField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    metadata = BlobField()
```

您可以将不同的字段标识为主键，在这种情况下，将不会创建`id`列。在这个例子中，我们将使用一个人的电子邮件地址作为主键:

```python
class Person(Model):
    email = CharField(primary_key=True)
    name = TextField()
    dob = DateField()
```

> 警告
>
> 我经常看到人们写以下代码，期望一个自动递增的整数主键:

```python
class MyModel(Model):
    id = IntegerField(primary_key=True)
```

Peewee将上述模型声明理解为一个具有整数主键的模型，但是该ID的值由应用程序确定。要创建一个自动递增的integer主键，你可以这样写:

```python
class MyModel(Model):
    id = AutoField()  # primary_key=True is implied.
```

复合主键可以使用[`CompositeKey`]声明(http://docs.peewee-orm.com/en/latest/peewee/api.html#CompositeKey)。注意，这样做可能会导致[`ForeignKeyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ForeignKeyField)的问题，因为Peewee不支持“复合外键”的概念。因此，我发现只在少数情况下使用复合主键是明智的，比如简单的多对多连接表:

```python
class Image(Model):
    filename = TextField()
    mimetype = CharField()

class Tag(Model):
    label = CharField()

class ImageTag(Model):  # Many-to-many relationship.
    image = ForeignKeyField(Image)
    tag = ForeignKeyField(Tag)

    class Meta:
        primary_key = CompositeKey('image', 'tag')
```

在极其罕见的情况下，你希望声明一个有*no*主键的模型，你可以在模型的`Meta`选项指定`primary_key = False`。

### 非整数主键

如果你想使用一个非整数主键(我通常不推荐)，当创建一个字段你可以指定`primary_key=True`。当您希望使用非自动递增主键为模型创建一个新实例时，您需要确保您[` save() `](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.save)指定了`force_insert=True`。

```python
from peewee import *

class UUIDModel(Model):
    id = UUIDField(primary_key=True)
```

自动递增id，顾名思义，是在向数据库中插入新行时自动生成的。当您调用[`save()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.save)时，peewee根据主键值的存在来决定是执行*INSERT*还是*UPDATE*。在我们的uuid示例中，数据库驱动程序不会生成新的ID，所以我们需要手动指定它。当我们第一次调用save()时，传入`force_insert = True`:

```python
# This works because .create() will specify `force_insert=True`.
obj1 = UUIDModel.create(id=uuid.uuid4())

# This will not work, however. Peewee will attempt to do an update:
obj2 = UUIDModel(id=uuid.uuid4())
obj2.save() # WRONG

obj2.save(force_insert=True) # CORRECT

# Once the object has been created, you can call save() normally.
obj2.save()
```

> 注意
>
> 任何具有非整数主键的模型的外键都有一个' ForeignKeyField '，它使用与它们相关的主键相同的底层存储类型。



### 复合主键

Peewee对复合键有非常基本的支持。为了使用复合键，必须将模型选项的`primary_key`属性设置为[`CompositeKey`](http://docs.peewee-orm.com/en/latest/peewee/api.html#CompositeKey)实例:

```python
class BlogToTag(Model):
    """A simple "through" table for many-to-many relationship."""
    blog = ForeignKeyField(Blog)
    tag = ForeignKeyField(Tag)

    class Meta:
        primary_key = CompositeKey('blog', 'tag')
```

警告

对于定义[`CompositeKey`](http://docs.peewee-orm.com/en/latest/peewee/api.html#CompositeKey)主键的模型，Peewee不支持外键。如果你想在一个有复合主键的模型中添加外键，复制相关模型上的列并添加一个自定义访问器(例如一个属性)。



### 手动指定主键

有时，您不希望数据库为主键自动生成一个值，例如在批量加载关系数据时。一次性处理，你可以告诉peewee在导入期间关闭`auto_increment`:

```python
data = load_user_csv() # load up a bunch of data

User._meta.auto_increment = False # turn off auto incrementing IDs
with db.atomic():
    for row in data:
        u = User(id=row[0], username=row[1])
        u.save(force_insert=True) # <-- force peewee to insert row

User._meta.auto_increment = True
```

更好的实现上述目标的方法是使用[`Model.insert_many()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.insert_many) 

```python
data = load_user_csv()
fields = [User.id, User.username]
with db.atomic():
    User.insert_many(data, fields=fields).execute()
```

如果你总是想要可以控制的主键，不使用[`AutoField`](http://docs.peewee-orm.com/en/latest/peewee/api.html AutoField)字段类型,但使用正常[`ntegerField`](http://docs.peewee-orm.com/en/latest/peewee/api.html # IntegerField)(或其他列类型):

```python
class User(BaseModel):
    id = IntegerField(primary_key=True)
    username = CharField()

>>> u = User.create(id=999, username='somebody')
>>> u.id
999
>>> User.get(User.username == 'somebody').id
999
```



### 没有主键的模型

如果你想创建一个没有主键的模型，你可以在内部的元类中指定`primary_key = False`:

```python
class MyData(BaseModel):
    timestamp = DateTimeField()
    value = IntegerField()

    class Meta:
        primary_key = False
```

这将产生以下DDL:

```python
CREATE TABLE "mydata" (
  "timestamp" DATETIME NOT NULL,
  "value" INTEGER NOT NULL
)
```

> 警告
>
> 一些模型api可能不会正常工作模式没有一个主键，例如[`save ()`](http://docs.peewee-orm.com/en/latest/peewee/api.html Model.save)和[`delete_instance ()`](http://docs.peewee-orm.com/en/latest/peewee/api.html Model.delete_instance)（您可以使用[`insert()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.insert),[`update()`](http://docs.peewee-orm.com/en/latest/peewee/api.html Model.update)和[`delect()`](http://docs.peewee-orm.com/en/latest/peewee/api.html Model.delete)）



## 自引用外键

当创建层次结构时，有必要创建一个自引用的外键，它将子对象链接到其父对象。因为model类在实例化self- reference外键时没有定义，所以使用特殊字符串`'self' `来表示self- reference外键:

```python
class Category(Model):
    name = CharField()
    parent = ForeignKeyField('self', null=True, backref='children')
```

如您所见，外键指向父对象*`向上`*，而反向引用被称为*`子对象`*。

> 注意
>
> 自引用外键应该始终为` null=True `。
>

在查询包含自引用外键的模型时，有时可能需要执行自连接。在这些情况下，您可以使用[`Model.alias()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.alias)来创建一个表引用。下面是如何使用自连接查询类别和父模型:

```python
Parent = Category.alias()
GrandParent = Category.alias()
query = (Category
         .select(Category, Parent)
         .join(Parent, on=(Category.parent == Parent.id))
         .join(GrandParent, on=(Parent.parent == GrandParent.id))
         .where(GrandParent.name == 'some category')
         .order_by(Category.name))
```



## 循环外键依赖

有时，您会在两个表之间创建循环依赖关系。

> 注意
>
> 我个人的观点是，循环外键是一种代码气味，应该被重构(例如，通过添加一个中间表)。
>

使用peewee添加循环外键有点棘手，因为在定义任何一个外键时，它所指向的模型都还没有定义，这会导致`NameError`。

```python
class User(Model):
    username = CharField()
    favorite_tweet = ForeignKeyField(Tweet, null=True)  # NameError!!

class Tweet(Model):
    message = TextField()
    user = ForeignKeyField(User, backref='tweets')
```

一种方法是简单地使用[` IntegerField `](http://docs.peewee-orm.com/en/latest/peewee/api.html#IntegerField)来存储原始ID:

```python
class User(Model):
    username = CharField()
    favorite_tweet_id = IntegerField(null=True)
```

通过使用[`DeferredForeignKey`](http://docs.peewee-orm.com/en/latest/peewee/api.html#DeferredForeignKey)，我们可以绕过这个问题，仍然使用外键字段:

```python
class User(Model):
    username = CharField()
    # Tweet has not been defined yet so use the deferred reference.
    favorite_tweet = DeferredForeignKey('Tweet', null=True)

class Tweet(Model):
    message = TextField()
    user = ForeignKeyField(User, backref='tweets')

# Now that Tweet is defined, "favorite_tweet" has been converted into
# a ForeignKeyField.
print(User.favorite_tweet)
# <ForeignKeyField: "user"."favorite_tweet">
```

不过这里还有一个需要注意的怪癖。当您调用[`create_table`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.create_table)时，我们将再次遇到相同的问题。因此，peewee不会自动为任何`延迟`外键创建外键约束。

要创建表*和*外键约束，可以使用[`SchemaManager.create_foreign_key()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SchemaManager.create_foreign_key)方法在创建表后创建约束:

```python
# Will create the User and Tweet tables, but does *not* create a
# foreign-key constraint on User.favorite_tweet.
db.create_tables([User, Tweet])

# Create the foreign-key constraint:
User._schema.create_foreign_key(User.favorite_tweet)
```

> 注意
>
> 因为SQLite对修改表的支持有限，所以在创建表之后，不能向表添加外键约束。

