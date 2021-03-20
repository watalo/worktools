# 查询Querying

本节将介绍通常在关系数据库上执行的基本CRUD操作::

- [`Model.create()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.create), for executing *INSERT* queries.
- [`Model.save()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.save) and [`Model.update()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.update), for executing *UPDATE* queries.
- [`Model.delete_instance()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.delete_instance) and [`Model.delete()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.delete), for executing *DELETE* queries.
- [`Model.select()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.select), for executing *SELECT* queries.

> 注意
>
> 还有大量来自[Postgresql习题](https://pgexercises.com/)网站的查询示例。示例请参见“[查询示例](http://docs.peewee-orm.com/en/latest/peewee/query_examples.html#query-examples)”文档。

## 创建新记录

您可以使用[`model .create()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.create)来创建一个新的模型实例。此方法接受关键字参数，其中的关键字对应于模型字段的名称.返回一个新的实例，并向表中添加一行。

```python
>>> User.create(username='Charlie')
<__main__.User object at 0x2529350>
```

这将插入一个新行到数据库中。主键将被自动检索并存储在模型实例中。

或者，您可以通过编程方式构建一个模型实例，然后调用[`save()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.save):

```python
>>> user = User(username='Charlie')
>>> user.save()  # save() returns the number of rows modified.
1
>>> user.id
1
>>> huey = User()
>>> huey.username = 'Huey'
>>> huey.save()
1
>>> huey.id
2
```

当一个模型有一个外键时，您可以在创建一个新记录时直接将一个模型实例分配给外键字段。

```python
>>> tweet = Tweet.create(user=huey, message='Hello!')
```

你也可以使用相关对象的主键值:

```python
>>> tweet = Tweet.create(user=2, message='Hello again!')
```

如果您只是希望插入数据而不需要创建模型实例，可以使用[`model .insert()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.insert):

```python
>>> User.insert(username='Mickey').execute()
3
```

执行insert查询之后，将返回新行的主键。

> 注意
>
> 有几种方法可以加速批量插入操作。请查看[批量插入](http://docs.peewee-orm.com/en/latest/peewee/querying.html#bulk-inserts)配方部分以获取更多信息。
>



## 批量插入Bulk inserts

有几种方法可以快速加载大量数据。简单的方法是循环调用[`Model.create()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.create):

```python
data_source = [
    {'field1': 'val1-1', 'field2': 'val1-2'},
    {'field1': 'val2-1', 'field2': 'val2-2'},
    # ...
]

for data_dict in data_source:
    MyModel.create(**data_dict)
```

上述方法之所以缓慢，有以下几个原因:

1. 如果你没有将循环包装在一个事务中，那么每次对[' create() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.create)的调用都会发生在它自己的事务中。那将会非常缓慢!

2. 有相当多的Python逻辑阻碍你，每个`InsertQuery`都必须生成并解析为SQL。

3. 您要发送到数据库以进行解析的大量数据(以SQL的原始字节计算)。

4. 我们正在检索*最后一个插入id*，这在某些情况下会导致执行额外的查询。


您可以通过简单地使用`atomic()`将其包装在一个事务中来获得显著的加速。

```python
# This is much faster.
with db.atomic():
    for data_dict in data_source:
        MyModel.create(**data_dict)
```

上述代码仍然受到第2、3和4点的影响。我们可以通过使用[`insert_many()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.insert_many)获得另一个巨大的提升。该方法接受元组或字典的列表，并在单个查询中插入多个行:

```python
data_source = [
    {'field1': 'val1-1', 'field2': 'val1-2'},
    {'field1': 'val2-1', 'field2': 'val2-2'},
    # ...
]

# Fastest way to INSERT multiple rows.
MyModel.insert_many(data_source).execute()
```

[`insert_many() `](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.insert_many)方法也接受一个元组列表，前提是你还指定了相应的字段:

```python
# We can INSERT tuples as well...
data = [('val1-1', 'val1-2'),
        ('val2-1', 'val2-2'),
        ('val3-1', 'val3-2')]

# But we need to indicate which fields the values correspond to.
MyModel.insert_many(data, fields=[MyModel.field1, MyModel.field2]).execute()
```

在事务中封装批量插入也是一个很好的做法:

```python
# You can, of course, wrap this in a transaction as well:
with db.atomic():
    MyModel.insert_many(data, fields=fields).execute()
```

> 注意
>
> SQLite用户在使用批量插入时应该注意一些注意事项。具体来说，SQLite3的版本必须是3.7.11.0或更新版本，才能利用批量插入API。另外，默认情况下，对于3.32.0(2020-05-22)之前的SQLite版本，SQLite将SQL查询中绑定变量的数量限制为“999”，而对于3.32.0之后的SQLite版本，则限制为32766。
>



### Inserting rows in batches 批量插入行

根据数据源中的行数，您可能需要将其分解为块。SQLite通常具有[999或32766](https://www.sqlite.org/limits.html#max_variable_number)每个查询的变量(这样批处理大小就会是999 //行长度或32766 //行长度)。

你可以写一个循环来批处理你的数据到块(在这种情况下，它是**强烈建议**你使用事务):

```python
# Insert rows 100 at a time.
with db.atomic():
    for idx in range(0, len(data_source), 100):
        MyModel.insert_many(data_source[idx:idx+100]).execute()
```

Peewee提供了一个[`chunked()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#chunked)帮助函数，你可以使用它来*有效*地将一个通用的可迭代对象分块为一系列*batch*大小的可迭代对象:

```python
from peewee import chunked

# Insert rows 100 at a time.
with db.atomic():
    for batch in chunked(data_source, 100):
        MyModel.insert_many(batch).execute()
```

### Alternatives 选择

[`Model.bulk_create ()`](http://docs.peewee-orm.com/en/latest/peewee/api.html Model.bulk_create)方法的行为很像[`Model.insert_many()`](http://docs.peewee-orm.com/en/latest/peewee/api.html # Model.insert_many)，而是它接受一个未保存的模型实例插入列表，并且接受批量大小可选参数。使用[`bulk_create()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.bulk_create) API:

```python
# Read list of usernames from a file, for example.
with open('user_list.txt') as fh:
    # Create a list of unsaved User instances.
    users = [User(username=line.strip()) for line in fh.readlines()]

# Wrap the operation in a transaction and batch INSERT the users
# 100 at a time.
with db.atomic():
    User.bulk_create(users, batch_size=100)
```

> 注意
>
> 如果您正在使用Postgresql(它支持`RETURNING `子句)，那么之前未保存的模型实例将自动填充它们新的主键值。
>

此外，Peewee还提供了[`Model.bulk_update()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.bulk_update)，它可以有效地更新模型列表上的一个或多个列。例如:

```python
# First, create 3 users with usernames u1, u2, u3.
u1, u2, u3 = [User.create(username='u%s' % i) for i in (1, 2, 3)]

# Now we'll modify the user instances.
u1.username = 'u1-x'
u2.username = 'u2-y'
u3.username = 'u3-z'

# Update all three users with a single UPDATE query.
User.bulk_update([u1, u2, u3], fields=[User.username])
```

Note

For large lists of objects, you should specify a reasonable batch_size and wrap the call to [`bulk_update()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.bulk_update) with [`Database.atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic):

请注意

对于大型对象列表，应该指定一个合理的batch_size，并使用[' Database.atomic() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic):)包装对[' bulk_update() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.bulk_update)的调用

```python
with database.atomic():
    User.bulk_update(list_of_users, fields=['username'], batch_size=50)
```

Alternatively, you can use the [`Database.batch_commit()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.batch_commit) helper to process chunks of rows inside *batch*-sized transactions. This method also provides a workaround for databases besides Postgresql, when the primary-key of the newly-created rows must be obtained.

另外，你也可以使用[' Database.batch_commit() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.batch_commit)帮助器在批量大小的事务中处理行块。该方法还为Postgresql以外的数据库提供了一种解决方案，当必须获取新创建行的主键时。

```python
# List of row data to insert.
row_data = [{'username': 'u1'}, {'username': 'u2'}, ...]

# Assume there are 789 items in row_data. The following code will result in
# 8 total transactions (7x100 rows + 1x89 rows).
for row in db.batch_commit(row_data, 100):
    User.create(**row)
```

### Bulk-loading from another table 从另一张桌子上散装货物

If the data you would like to bulk load is stored in another table, you can also create *INSERT* queries whose source is a *SELECT* query. Use the [`Model.insert_from()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.insert_from) method:

如果要批量加载的数据存储在另一个表中，您还可以创建源为*SELECT*查询的*INSERT*查询。使用[' Model.insert_from() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.insert_from)方法:

```python
res = (TweetArchive
       .insert_from(
           Tweet.select(Tweet.user, Tweet.message),
           fields=[TweetArchive.user, TweetArchive.message])
       .execute())
```

The above query is equivalent to the following SQL:

上面的查询相当于下面的SQL:

```python
INSERT INTO "tweet_archive" ("user_id", "message")
SELECT "user_id", "message" FROM "tweet";
```

## Updating existing records 更新现有的记录

Once a model instance has a primary key, any subsequent call to [`save()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.save) will result in an *UPDATE* rather than another *INSERT*. The model’s primary key will not change:

一旦模型实例有了主键，后续对[' save() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.save)的任何调用都会导致一个*UPDATE*而不是另一个*INSERT*。模型的主键不会改变:

```python
>>> user.save()  # save() returns the number of rows modified.
1
>>> user.id
1
>>> user.save()
>>> user.id
1
>>> huey.save()
1
>>> huey.id
2
```

If you want to update multiple records, issue an *UPDATE* query. The following example will update all `Tweet` objects, marking them as *published*, if they were created before today. [`Model.update()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.update) accepts keyword arguments where the keys correspond to the model’s field names:

如果你想更新多条记录，发出一个* update *查询。下面的例子将更新所有的‘Tweet’对象，如果它们是在今天之前创建的，则将它们标记为*published*。[' model .update() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.update)接受关键字参数，关键字对应模型的字段名:

```python
>>> today = datetime.today()
>>> query = Tweet.update(is_published=True).where(Tweet.creation_date < today)
>>> query.execute()  # Returns the number of rows that were updated.
4
```

For more information, see the documentation on [`Model.update()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.update), [`Update`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Update) and [`Model.bulk_update()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.bulk_update).

Note

If you would like more information on performing atomic updates (such as incrementing the value of a column), check out the [atomic update](http://docs.peewee-orm.com/en/latest/peewee/querying.html#atomic-updates) recipes.

更多信息，请参阅[' Model.update() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.update)， [' Update '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Update)和[' Model.bulk_update() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.bulk_update)的文档。

请注意

如果您想了解有关执行原子更新的更多信息(比如增加列的值)，请查看[atomic update](http://docs.peewee-orm.com/en/latest/peewee/querying.html#atomic-updates)配方。

## tomic updates 原子更新

Peewee allows you to perform atomic updates. Let’s suppose we need to update some counters. The naive approach would be to write something like this:

Peewee允许执行原子更新。让我们假设我们需要更新一些计数器。简单的方法是这样写的:

```python
>>> for stat in Stat.select().where(Stat.url == request.url):
...     stat.counter += 1
...     stat.save()
```

**Do not do this!** Not only is this slow, but it is also vulnerable to race conditions if multiple processes are updating the counter at the same time.

Instead, you can update the counters atomically using [`update()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.update):

不要这样做!**这不仅很慢，而且如果多个进程同时更新计数器，它还容易受到竞争条件的影响。

相反，您可以使用[' update() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.update):)自动更新计数器

```python
>>> query = Stat.update(counter=Stat.counter + 1).where(Stat.url == request.url)
>>> query.execute()
```

You can make these update statements as complex as you like. Let’s give all our employees a bonus equal to their previous bonus plus 10% of their salary:

您可以随心所欲地使这些update语句变得复杂。我们发给所有员工的奖金等于他们上次的奖金加上他们工资的10%:

```python
>>> query = Employee.update(bonus=(Employee.bonus + (Employee.salary * .1)))
>>> query.execute()  # Give everyone a bonus!
```

We can even use a subquery to update the value of a column. Suppose we had a denormalized column on the `User` model that stored the number of tweets a user had made, and we updated this value periodically. Here is how you might write such a query:

我们甚至可以使用子查询来更新列的值。假设我们在“User”模型上有一个非规范化的列，该列存储了用户发出的tweet数量，我们定期更新这个值。下面是如何编写这样的查询:

```python
>>> subquery = Tweet.select(fn.COUNT(Tweet.id)).where(Tweet.user == User.id)
>>> update = User.update(num_tweets=subquery)
>>> update.execute()
```

### Upsert 插入

Peewee provides support for varying types of upsert functionality. With SQLite prior to 3.24.0 and MySQL, Peewee offers the [`replace()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.replace), which allows you to insert a record or, in the event of a constraint violation, replace the existing record.

Example of using [`replace()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.replace) and [`on_conflict_replace()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Insert.on_conflict_replace):

Peewee支持各种类型的upsert功能。在3.24.0之前的SQLite和MySQL中，Peewee提供了[' replace() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.replace)，它允许你插入一条记录，或者在违反约束的情况下，替换现有的记录。

使用[' replace() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.replace)和[' on_conflict_replace() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Insert.on_conflict_replace):

```python
class User(Model):
    username = TextField(unique=True)
    last_login = DateTimeField(null=True)

# Insert or update the user. The "last_login" value will be updated
# regardless of whether the user existed previously.
user_id = (User
           .replace(username='the-user', last_login=datetime.now())
           .execute())

# This query is equivalent:
user_id = (User
           .insert(username='the-user', last_login=datetime.now())
           .on_conflict_replace()
           .execute())
```

Note

In addition to *replace*, SQLite, MySQL and Postgresql provide an *ignore* action (see: [`on_conflict_ignore()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Insert.on_conflict_ignore)) if you simply wish to insert and ignore any potential constraint violation.

**MySQL** supports upsert via the *ON DUPLICATE KEY UPDATE* clause. For example:

请注意

除了*replace*， SQLite, MySQL和Postgresql提供了一个*ignore*操作(参见:[' on_conflict_ignore() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Insert.on_conflict_ignore))，如果你只是想插入和忽略任何潜在的约束违反。

**MySQL**通过*ON DUPLICATE KEY UPDATE*子句支持upsert。例如:

```python 
class User(Model):
    username = TextField(unique=True)
    last_login = DateTimeField(null=True)
    login_count = IntegerField()

# Insert a new user.
User.create(username='huey', login_count=0)

# Simulate the user logging in. The login count and timestamp will be
# either created or updated correctly.
now = datetime.now()
rowid = (User
         .insert(username='huey', last_login=now, login_count=1)
         .on_conflict(
             preserve=[User.last_login],  # Use the value we would have inserted.
             update={User.login_count: User.login_count + 1})
         .execute())
```

In the above example, we could safely invoke the upsert query as many times as we wanted. The login count will be incremented atomically, the last login column will be updated, and no duplicate rows will be created.

**Postgresql and SQLite** (3.24.0 and newer) provide a different syntax that allows for more granular control over which constraint violation should trigger the conflict resolution, and what values should be updated or preserved.

Example of using [`on_conflict()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Insert.on_conflict) to perform a Postgresql-style upsert (or SQLite 3.24+):

在上面的示例中，我们可以按照自己的意愿安全地多次调用upsert查询。登录计数将自动增加，最后的登录列将被更新，并且不会创建重复的行。

**Postgresql和SQLite**(3.24.0及更新版本)提供了不同的语法，允许更细粒度地控制哪些约束违反应该触发冲突解决，以及哪些值应该被更新或保留。



使用[' on_conflict() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Insert.on_conflict)执行postgresql风格的upsert(或SQLite 3.24+)的示例:

```python
class User(Model):
    username = TextField(unique=True)
    last_login = DateTimeField(null=True)
    login_count = IntegerField()

# Insert a new user.
User.create(username='huey', login_count=0)

# Simulate the user logging in. The login count and timestamp will be
# either created or updated correctly.
now = datetime.now()
rowid = (User
         .insert(username='huey', last_login=now, login_count=1)
         .on_conflict(
             conflict_target=[User.username],  # Which constraint?
             preserve=[User.last_login],  # Use the value we would have inserted.
             update={User.login_count: User.login_count + 1})
         .execute())
```

In the above example, we could safely invoke the upsert query as many times as we wanted. The login count will be incremented atomically, the last login column will be updated, and no duplicate rows will be created.

Note

The main difference between MySQL and Postgresql/SQLite is that Postgresql and SQLite require that you specify a `conflict_target`.

Here is a more advanced (if contrived) example using the [`EXCLUDED`](http://docs.peewee-orm.com/en/latest/peewee/api.html#EXCLUDED) namespace. The [`EXCLUDED`](http://docs.peewee-orm.com/en/latest/peewee/api.html#EXCLUDED) helper allows us to reference values in the conflicting data. For our example, we’ll assume a simple table mapping a unique key (string) to a value (integer):



在上面的示例中，我们可以按照自己的意愿安全地多次调用upsert查询。
登录计数将自动增加，最后的登录列将被更新，并且不会创建重复的行。

请注意

MySQL和Postgresql/SQLite的主要区别是，Postgresql和SQLite要求你指定一个“conflict_target”。

下面是一个使用[' EXCLUDED '](http://docs.peewee-orm.com/en/latest/peewee/api.html#EXCLUDED)命名空间的更高级(如果是人为的)示例。
[' EXCLUDED '](http://docs.peewee-orm.com/en/latest/peewee/api.html#EXCLUDED)帮助器允许我们引用冲突数据中的值。
在我们的例子中，我们假设一个简单的表将一个唯一的键(字符串)映射到一个值(整数):

```python
class KV(Model):
    key = CharField(unique=True)
    value = IntegerField()

# Create one row.
KV.create(key='k1', value=1)

# Demonstrate usage of EXCLUDED.
# Here we will attempt to insert a new value for a given key. If that
# key already exists, then we will update its value with the *sum* of its
# original value and the value we attempted to insert -- provided that
# the new value is larger than the original value.
query = (KV.insert(key='k1', value=10)
         .on_conflict(conflict_target=[KV.key],
                      update={KV.value: KV.value + EXCLUDED.value},
                      where=(EXCLUDED.value > KV.value)))

# Executing the above query will result in the following data being
# present in the "kv" table:
# (key='k1', value=11)
query.execute()

# If we attempted to execute the query *again*, then nothing would be
# updated, as the new value (10) is now less than the value in the
# original row (11).
```

For more information, see [`Insert.on_conflict()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Insert.on_conflict) and [`OnConflict`](http://docs.peewee-orm.com/en/latest/peewee/api.html#OnConflict).

更多信息，请参见[' Insert.on_conflict() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Insert.on_conflict)和[' OnConflict '](http://docs.peewee-orm.com/en/latest/peewee/api.html#OnConflict)。

## Deleting records

To delete a single model instance, you can use the [`Model.delete_instance()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.delete_instance) shortcut. [`delete_instance()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.delete_instance) will delete the given model instance and can optionally delete any dependent objects recursively (by specifying recursive=True).

要删除单个模型实例，可以使用 [`Model.delete_instance()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.delete_instance)快捷方式。`delete_instance()`将删除给定的模型实例，并且可以选择性地递归地删除任何依赖对象(指定recursive=True)。

```python
>>> user = User.get(User.id == 1)
>>> user.delete_instance()  # Returns the number of rows deleted.
1

>>> User.get(User.id == 1)
UserDoesNotExist: instance matching query does not exist:
SQL: SELECT t1."id", t1."username" FROM "user" AS t1 WHERE t1."id" = ?
PARAMS: [1]
```

To delete an arbitrary set of rows, you can issue a *DELETE* query. The following will delete all `Tweet` objects that are over one year old:

要删除任意一组行，您可以发出一个*DELETE*查询。下面将删除所有超过一年的`Tweet`对象:

```python
>>> query = Tweet.delete().where(Tweet.creation_date < one_year_ago)
>>> query.execute()  # Returns the number of rows deleted.
7
```

For more information, see the documentation on:

更多信息，请参阅以下文档:

- [`Model.delete_instance()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.delete_instance)
- [`Model.delete()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.delete)
- `DeleteQuery`

## Selecting a single record 选择单个记录

You can use the [`Model.get()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get) method to retrieve a single instance matching the given query. For primary-key lookups, you can also use the shortcut method [`Model.get_by_id()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get_by_id).

This method is a shortcut that calls [`Model.select()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.select) with the given query, but limits the result set to a single row. Additionally, if no model matches the given query, a `DoesNotExist` exception will be raised.

您可以使用 [`Model.get()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get) 方法来检索与给定查询匹配的单个实例。对于主键查找，还可以使用快捷方法 [`Model.get_by_id()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get_by_id).

这个方法是一个快捷方式，它使用给定的查询调用 [`Model.select()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.select)，但是将结果集限制为单个行。此外，如果没有模型匹配给定的查询，将引发 `DoesNotExist` 异常。

```python
>>> User.get(User.id == 1)
<__main__.User object at 0x25294d0>

>>> User.get_by_id(1)  # Same as above.
<__main__.User object at 0x252df10>

>>> User[1]  # Also same as above.
<__main__.User object at 0x252dd10>

>>> User.get(User.id == 1).username
u'Charlie'

>>> User.get(User.username == 'Charlie')
<__main__.User object at 0x2529410>

>>> User.get(User.username == 'nobody')
UserDoesNotExist: instance matching query does not exist:
SQL: SELECT t1."id", t1."username" FROM "user" AS t1 WHERE t1."username" = ?
PARAMS: ['nobody']
```

For more advanced operations, you can use [`SelectBase.get()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SelectBase.get). The following query retrieves the latest tweet from the user named *charlie*:

对于更高级的操作，您可以使用[' SelectBase.get() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#SelectBase.get)。下面的查询检索名为*charlie*的用户的最新tweet:

```python
>>> (Tweet
...  .select()
...  .join(User)
...  .where(User.username == 'charlie')
...  .order_by(Tweet.created_date.desc())
...  .get())
<__main__.Tweet object at 0x2623410>
```

更多信息，请参阅以下文档:

- [`Model.get()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get)
- [`Model.get_by_id()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get_by_id)
- [`Model.get_or_none()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get_or_none) - if no matching row is found, return `None`.如果没有找到匹配的行，则返回` None `'。
- `Model.first()`
- [`Model.select()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.select)
- [`SelectBase.get()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SelectBase.get)

## Create or get 创建或获取

Peewee has one helper method for performing “get/create” type operations: [`Model.get_or_create()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get_or_create), which first attempts to retrieve the matching row. Failing that, a new row will be created.

For “create or get” type logic, typically one would rely on a *unique* constraint or primary key to prevent the creation of duplicate objects. As an example, let’s say we wish to implement registering a new user account using the [example User model](http://docs.peewee-orm.com/en/latest/peewee/models.html#blog-models). The *User* model has a *unique* constraint on the username field, so we will rely on the database’s integrity guarantees to ensure we don’t end up with duplicate usernames:

Peewee有一个帮助器方法来执行“get/create”类型操作[`Model.get_or_create() `](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get_or_create)，它首先尝试检索匹配的行。
否则，将创建一个新行。

对于`create or get`类型逻辑，通常会依赖一个*unique*约束或主键来防止创建重复对象。
例如，假设我们希望使用[示例用户模型](http://docs.peewee-orm.com/en/latest/peewee/models.html#blog-models)实现注册一个新用户帐户。
*User*模型在用户名字段上有*unique*约束，所以我们将依赖数据库的完整性保证来确保我们最终不会有重复的用户名:

```python
try:
    with db.atomic():
        return User.create(username=username)
except peewee.IntegrityError:
    # `username` is a unique column, so this username already exists,
    # making it safe to call .get().
    return User.get(User.username == username)
```

You can easily encapsulate this type of logic as a `classmethod` on your own `Model` classes.

The above example first attempts at creation, then falls back to retrieval, relying on the database to enforce a unique constraint. If you prefer to attempt to retrieve the record first, you can use [`get_or_create()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get_or_create). This method is implemented along the same lines as the Django function of the same name. You can use the Django-style keyword argument filters to specify your `WHERE` conditions. The function returns a 2-tuple containing the instance and a boolean value indicating if the object was created.

Here is how you might implement user account creation using [`get_or_create()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get_or_create):

你可以很容易地将这种逻辑封装为你自己的“模型”类中的“classmethod”。

上面的示例首先尝试创建，然后返回到检索，依赖数据库来强制执行唯一约束。如果您更喜欢先尝试检索记录，您可以使用 [`get_or_create()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get_or_create)。这个方法的实现与同名的Django函数相同。你可以使用django风格的关键字参数过滤器来指定你的`WHERE`条件。该函数返回一个二元组，其中包含实例和一个布尔值，该值指示对象是否被创建。

下面是如何使用 [`get_or_create()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get_or_create)实现用户帐户的创建

```python
user, created = User.get_or_create(username=username)
```

Suppose we have a different model `Person` and would like to get or create a person object. The only conditions we care about when retrieving the `Person` are their first and last names, **but** if we end up needing to create a new record, we will also specify their date-of-birth and favorite color:

假设我们有一个不同的模型“Person”，并希望获得或创建一个Person对象。检索“Person”时，我们关心的唯一条件是他们的姓和名，**但**如果我们最终需要创建一个新记录，我们还将指定他们的出生日期和最喜欢的颜色:



```python
person, created = Person.get_or_create(
    first_name=first_name,
    last_name=last_name,
    defaults={'dob': dob, 'favorite_color': 'green'})
```

Any keyword argument passed to [`get_or_create()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get_or_create) will be used in the `get()` portion of the logic, except for the `defaults` dictionary, which will be used to populate values on newly-created instances.

For more details read the documentation for [`Model.get_or_create()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get_or_create).

传递给[' get_or_create() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get_or_create)的任何关键字参数都将在逻辑的' get() '部分中使用，除了' defaults '字典，它将用于填充新创建实例的值。

要了解更多细节，请阅读[' Model.get_or_create() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get_or_create)的文档。



## Selecting multiple records 选择多个记录

We can use [`Model.select()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.select) to retrieve rows from the table. When you construct a *SELECT* query, the database will return any rows that correspond to your query. Peewee allows you to iterate over these rows, as well as use indexing and slicing operations:



我们可以使用[' Model.select() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.select)从表中检索行。
当您构造一个*SELECT*查询时，数据库将返回与您的查询对应的任何行。
Peewee允许你遍历这些行，以及使用索引和切片操作:

```python
>>> query = User.select()
>>> [user.username for user in query]
['Charlie', 'Huey', 'Peewee']

>>> query[1]
<__main__.User at 0x7f83e80f5550>

>>> query[1].username
'Huey'

>>> query[:2]
[<__main__.User at 0x7f83e80f53a8>, <__main__.User at 0x7f83e80f5550>]
```

[`Select`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select) queries are smart, in that you can iterate, index and slice the query multiple times but the query is only executed once.

In the following example, we will simply call [`select()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.select) and iterate over the return value, which is an instance of [`Select`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select). This will return all the rows in the *User* table:

[' Select '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select)查询是聪明的，因为您可以迭代、索引和切片查询多次，但查询只执行一次。



在下面的示例中，我们将简单地调用[' select() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.select)并迭代返回值，该值是[' select '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select)的一个实例。这将返回*User*表中的所有行:



```python
>>> for user in User.select():
...     print user.username
...
Charlie
Huey
Peewee
```

Note

Subsequent iterations of the same query will not hit the database as the results are cached. To disable this behavior (to reduce memory usage), call `Select.iterator()` when iterating.

When iterating over a model that contains a foreign key, be careful with the way you access values on related models. Accidentally resolving a foreign key or iterating over a back-reference can cause [N+1 query behavior](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#nplusone).

When you create a foreign key, such as `Tweet.user`, you can use the *backref* to create a back-reference (`User.tweets`). Back-references are exposed as [`Select`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select) instances:

请注意



当结果被缓存时，相同查询的后续迭代将不会到达数据库。要禁用此行为(以减少内存使用)，在迭代时调用' Select.iterator() '。

在迭代包含外键的模型时，要小心访问相关模型上的值的方式。意外解析外键或遍历反向引用可能导致[N+1查询行为](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#nplusone)。

当你创建一个外键，例如' Tweet。用户'，你可以使用*backref*创建一个反向引用(' user .tweets ')。反向引用被公开为[' Select '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select)实例:



```python
>>> tweet = Tweet.get()
>>> tweet.user  # Accessing a foreign key returns the related model.
<tw.User at 0x7f3ceb017f50>

>>> user = User.get()
>>> user.tweets  # Accessing a back-reference returns a query.
<peewee.ModelSelect at 0x7f73db3bafd0>
```

You can iterate over the `user.tweets` back-reference just like any other [`Select`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select):

```python
>>> for tweet in user.tweets:
...     print(tweet.message)
...
hello world
this is fun
look at this picture of my food
```

In addition to returning model instances, [`Select`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select) queries can return dictionaries, tuples and namedtuples. Depending on your use-case, you may find it easier to work with rows as dictionaries, for example:

除了返回模型实例，[' Select '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select)查询还可以返回字典、元组和命名元组。根据您的用例，您可能会发现将行作为字典来处理更容易，例如:

```python
>>> query = User.select().dicts()
>>> for row in query:
...     print(row)

{'id': 1, 'username': 'Charlie'}
{'id': 2, 'username': 'Huey'}
{'id': 3, 'username': 'Peewee'}
```

See [`namedtuples()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BaseQuery.namedtuples), [`tuples()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BaseQuery.tuples), [`dicts()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BaseQuery.dicts) for more information.

### Iterating over large result-sets 迭代大型结果集

By default peewee will cache the rows returned when iterating over a [`Select`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select) query. This is an optimization to allow multiple iterations as well as indexing and slicing without causing additional queries. This caching can be problematic, however, when you plan to iterate over a large number of rows.

To reduce the amount of memory used by peewee when iterating over a query, use the [`iterator()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BaseQuery.iterator) method. This method allows you to iterate without caching each model returned, using much less memory when iterating over large result sets.

默认情况下，peewee在迭代[' Select '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select)查询时将缓存返回的行。这是一种优化，允许多次迭代以及索引和切片，而不会导致额外的查询。然而，当您计划遍历大量行时，这种缓存可能会产生问题。

为了减少peewee在迭代查询时所使用的内存，可以使用[' iterator() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#BaseQuery.iterator)方法。该方法允许您在不缓存返回的每个模型的情况下进行迭代，在迭代大型结果集时使用更少的内存。



```python
# Let's assume we've got 10 million stat objects to dump to a csv file.
stats = Stat.select()

# Our imaginary serializer class
serializer = CSVSerializer()

# Loop over all the stats and serialize.
for stat in stats.iterator():
    serializer.serialize_object(stat)
```

For simple queries you can see further speed improvements by returning rows as dictionaries, namedtuples or tuples. The following methods can be used on any [`Select`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select) query to change the result row type:

对于简单的查询，您可以通过将行返回为字典、命名元组或元组来进一步提高速度。以下方法可用于任何[' Select '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select)查询，以更改结果行类型:

- [`dicts()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BaseQuery.dicts)
- [`namedtuples()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BaseQuery.namedtuples)
- [`tuples()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BaseQuery.tuples)

Don’t forget to append the [`iterator()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BaseQuery.iterator) method call to also reduce memory consumption. For example, the above code might look like:

不要忘记附加[' iterator() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#BaseQuery.iterator)方法调用，以减少内存消耗。例如，上面的代码可能看起来像:

```python
# Let's assume we've got 10 million stat objects to dump to a csv file.
stats = Stat.select()

# Our imaginary serializer class
serializer = CSVSerializer()

# Loop over all the stats (rendered as tuples, without caching) and serialize.
for stat_tuple in stats.tuples().iterator():
    serializer.serialize_tuple(stat_tuple)
```

When iterating over a large number of rows that contain columns from multiple tables, peewee will reconstruct the model graph for each row returned. This operation can be slow for complex graphs. For example, if we were selecting a list of tweets along with the username and avatar of the tweet’s author, Peewee would have to create two objects for each row (a tweet and a user). In addition to the above row-types, there is a fourth method [`objects()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BaseQuery.objects) which will return the rows as model instances, but will not attempt to resolve the model graph.

For example:

当迭代大量包含来自多个表的列的行时，peewee将为返回的每一行重构模型图。对于复杂的图形，此操作可能会比较慢。例如，如果我们选择一个tweet列表以及tweet作者的用户名和头像，Peewee就必须为每一行创建两个对象(一条tweet和一个用户)。除了上面的行类型之外，还有第四个方法[' objects() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#BaseQuery.objects)，它将返回作为模型实例的行，但不会尝试解析模型图。

例如:

```python
query = (Tweet
         .select(Tweet, User)  # Select tweet and user data.
         .join(User))

# Note that the user columns are stored in a separate User instance
# accessible at tweet.user:
for tweet in query:
    print(tweet.user.username, tweet.content)

# Using ".objects()" will not create the tweet.user object and assigns all
# user attributes to the tweet instance:
for tweet in query.objects():
    print(tweet.username, tweet.content)
```

For maximum performance, you can execute queries and then iterate over the results using the underlying database cursor. [`Database.execute()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.execute) accepts a query object, executes the query, and returns a DB-API 2.0 `Cursor` object. The cursor will return the raw row-tuples:



为了获得最佳性能，可以执行查询，然后使用底层数据库游标迭代结果。[' Database.execute() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.execute)接受一个查询对象，执行该查询，并返回一个DB-API 2.0 ' Cursor '对象。游标将返回原始的行元组:



```python
query = Tweet.select(Tweet.content, User.username).join(User)
cursor = database.execute(query)
for (content, username) in cursor:
    print(username, '->', content)
```

## Filtering records 过滤记录

You can filter for particular records using normal python operators. Peewee supports a wide variety of [query operators](http://docs.peewee-orm.com/en/latest/peewee/query_operators.html#query-operators).



您可以使用普通的python操作符过滤特定的记录。Peewee支持多种[查询操作符](http://docs.peewee-orm.com/en/latest/peewee/query_operators.html#query-operators)。

```python
>>> user = User.get(User.username == 'Charlie')
>>> for tweet in Tweet.select().where(Tweet.user == user, Tweet.is_published == True):
...     print(tweet.user.username, '->', tweet.message)
...
Charlie -> hello world
Charlie -> this is fun

>>> for tweet in Tweet.select().where(Tweet.created_date < datetime.datetime(2011, 1, 1)):
...     print(tweet.message, tweet.created_date)
...
Really old tweet 2010-01-01 00:00:00
```

You can also filter across joins:

你也可以过滤连接:

```python
>>> for tweet in Tweet.select().join(User).where(User.username == 'Charlie'):
...     print(tweet.message)
hello world
this is fun
look at this picture of my food
```

If you want to express a complex query, use parentheses and python’s bitwise *or* and *and* operators:

如果你想表达一个复杂的查询，使用圆括号和python的按位*或*和*和*操作符:

```python
>>> Tweet.select().join(User).where(
...     (User.username == 'Charlie') |
...     (User.username == 'Peewee Herman'))
```

Note

Note that Peewee uses **bitwise** operators (`&` and `|`) rather than logical operators (`and` and `or`). The reason for this is that Python coerces the return value of logical operations to a boolean value. This is also the reason why “IN” queries must be expressed using `.in_()` rather than the `in` operator.

Check out [the table of query operations](http://docs.peewee-orm.com/en/latest/peewee/query_operators.html#query-operators) to see what types of queries are possible.

Note

A lot of fun things can go in the where clause of a query, such as:

- A field expression, e.g. `User.username == 'Charlie'`
- A function expression, e.g. `fn.Lower(fn.Substr(User.username, 1, 1)) == 'a'`
- A comparison of one column to another, e.g. `Employee.salary < (Employee.tenure * 1000) + 40000`

You can also nest queries, for example tweets by users whose username starts with “a”:



请注意

注意，Peewee使用**位**操作符(' & '和' | ')而不是逻辑操作符(' and '和' or ')。这是因为Python将逻辑操作的返回值强制转换为布尔值。这也是为什么“IN”查询必须使用' .in_() '而不是' IN '操作符来表示的原因。

请参阅[查询操作表](http://docs.peewee-orm.com/en/latest/peewee/query_operators.html#query-operators)，了解可能的查询类型。

请注意

在查询的where子句中可以看到很多有趣的事情，例如:

- 字段表达式，例如。的用户。用户名= =“查理”的

- 一个函数表达式，例如:“fn.Lower (fn.Substr(用户。用户名，1,1))== 'a' '

- 一栏与另一栏的比较，例如:的员工。工资& lt;(员工。任期* 1000)+ 40000 '

您还可以嵌套查询，例如用户名以“a”开头的用户发布的tweet:



```python
# get users whose username starts with "a"
a_users = User.select().where(fn.Lower(fn.Substr(User.username, 1, 1)) == 'a')

# the ".in_()" method signifies an "IN" query
a_user_tweets = Tweet.select().where(Tweet.user.in_(a_users))
```

### More query examples 更多的查询示例

Note

For a wide range of example queries, see the [Query Examples](http://docs.peewee-orm.com/en/latest/peewee/query_examples.html#query-examples) document, which shows how to implements queries from the [PostgreSQL Exercises](https://pgexercises.com/) website.

Get active users:

请注意

有关广泛的示例查询，请参阅[查询示例](http://docs.peewee-orm.com/en/latest/peewee/query_examples.html#query-examples)文档，该文档展示了如何实现[PostgreSQL练习](https://pgexercises.com/)网站的查询。

活跃用户:

```python
User.select().where(User.active == True)
```

Get users who are either staff or superusers:

获取员工用户或超级用户:

```python
User.select().where(
    (User.is_staff == True) | (User.is_superuser == True))
```

Get tweets by user named “charlie”:

通过名为“charlie”的用户获取tweets:



```python
Tweet.select().join(User).where(User.username == 'charlie')
```

Get tweets by staff or superusers (assumes FK relationship):

获取员工或超级用户的推文(假设是FK关系):

```python
Tweet.select().join(User).where(
    (User.is_staff == True) | (User.is_superuser == True))
```

Get tweets by staff or superusers using a subquery:

通过子查询获得员工或超级用户的tweet:

```python
staff_super = User.select(User.id).where(
    (User.is_staff == True) | (User.is_superuser == True))
Tweet.select().where(Tweet.user.in_(staff_super))
```

## Sorting records 整理记录

To return rows in order, use the [`order_by()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Query.order_by) method:

要按顺序返回行，请使用[' order_by() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Query.order_by)方法:

```python
>>> for t in Tweet.select().order_by(Tweet.created_date):
...     print(t.pub_date)
...
2010-01-01 00:00:00
2011-06-07 14:08:48
2011-06-07 14:12:57

>>> for t in Tweet.select().order_by(Tweet.created_date.desc()):
...     print(t.pub_date)
...
2011-06-07 14:12:57
2011-06-07 14:08:48
2010-01-01 00:00:00
```

You can also use `+` and `-` prefix operators to indicate ordering:

还可以使用' + '和' - '前缀操作符来表示顺序:

```python
# The following queries are equivalent:
Tweet.select().order_by(Tweet.created_date.desc())

Tweet.select().order_by(-Tweet.created_date)  # Note the "-" prefix.

# Similarly you can use "+" to indicate ascending order, though ascending
# is the default when no ordering is otherwise specified.
User.select().order_by(+User.username)
```

You can also order across joins. Assuming you want to order tweets by the username of the author, then by created_date:

您还可以跨连接进行排序。假设您想要根据作者的用户名对tweet进行排序，然后按created_date排序:

```python
query = (Tweet
         .select()
         .join(User)
         .order_by(User.username, Tweet.created_date.desc()))
SELECT t1."id", t1."user_id", t1."message", t1."is_published", t1."created_date"
FROM "tweet" AS t1
INNER JOIN "user" AS t2
  ON t1."user_id" = t2."id"
ORDER BY t2."username", t1."created_date" DESC
```

When sorting on a calculated value, you can either include the necessary SQL expressions, or reference the alias assigned to the value. Here are two examples illustrating these methods:

在对计算值进行排序时，可以包括必要的SQL表达式，也可以引用分配给该值的别名。这里有两个例子来说明这些方法:

```python
# Let's start with our base query. We want to get all usernames and the number of
# tweets they've made. We wish to sort this list from users with most tweets to
# users with fewest tweets.
query = (User
         .select(User.username, fn.COUNT(Tweet.id).alias('num_tweets'))
         .join(Tweet, JOIN.LEFT_OUTER)
         .group_by(User.username))
```

You can order using the same COUNT expression used in the `select` clause. In the example below we are ordering by the `COUNT()` of tweet ids descending:

您可以使用与' select '子句中使用的COUNT表达式进行排序。在下面的例子中，我们根据tweet id的' COUNT() '降序排序:

```python
query = (User
         .select(User.username, fn.COUNT(Tweet.id).alias('num_tweets'))
         .join(Tweet, JOIN.LEFT_OUTER)
         .group_by(User.username)
         .order_by(fn.COUNT(Tweet.id).desc()))
```

Alternatively, you can reference the alias assigned to the calculated value in the `select` clause. This method has the benefit of being a bit easier to read. Note that we are not referring to the named alias directly, but are wrapping it using the [`SQL`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SQL) helper:

或者，您可以引用在' select '子句中分配给计算值的别名。这种方法的好处是更容易阅读。注意，我们没有直接引用已命名的别名，而是使用[' SQL '](http://docs.peewee-orm.com/en/latest/peewee/api.html#SQL)帮助器包装它:

```python
query = (User
         .select(User.username, fn.COUNT(Tweet.id).alias('num_tweets'))
         .join(Tweet, JOIN.LEFT_OUTER)
         .group_by(User.username)
         .order_by(SQL('num_tweets').desc()))
```

Or, to do things the “peewee” way:

或者，用“peewee”的方式做事:

```python
ntweets = fn.COUNT(Tweet.id)
query = (User
         .select(User.username, ntweets.alias('num_tweets'))
         .join(Tweet, JOIN.LEFT_OUTER)
         .group_by(User.username)
         .order_by(ntweets.desc())
```

## Getting random records 得到随机记录

Occasionally you may want to pull a random record from the database. You can accomplish this by ordering by the *random* or *rand* function (depending on your database):

Postgresql and Sqlite use the *Random* function:

偶尔您可能想要从数据库中随机提取一条记录。你可以通过*random*或*rand*函数(取决于你的数据库)来实现这一点:

Postgresql和Sqlite使用*Random*函数:

```python
# Pick 5 lucky winners:
LotteryNumber.select().order_by(fn.Random()).limit(5)
```

MySQL uses *Rand*:

```python
# Pick 5 lucky winners:
LotteryNumber.select().order_by(fn.Rand()).limit(5)
```

## Paginating records 分页记录

The [`paginate()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Query.paginate) method makes it easy to grab a *page* or records. [`paginate()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Query.paginate) takes two parameters, `page_number`, and `items_per_page`.

Attention

Page numbers are 1-based, so the first page of results will be page 1.

```python
>>> for tweet in Tweet.select().order_by(Tweet.id).paginate(2, 10):
...     print(tweet.message)
...
tweet 10
tweet 11
tweet 12
tweet 13
tweet 14
tweet 15
tweet 16
tweet 17
tweet 18
tweet 19
```

If you would like more granular control, you can always use [`limit()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Query.limit) and [`offset()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Query.offset).

## Counting records

You can count the number of rows in any select query:

```python
>>> Tweet.select().count()
100
>>> Tweet.select().where(Tweet.id > 50).count()
50
```

Peewee will wrap your query in an outer query that performs a count, which results in SQL like:

```python
SELECT COUNT(1) FROM ( ... your query ... );
```

## Aggregating records

Suppose you have some users and want to get a list of them along with the count of tweets in each.

```python
query = (User
         .select(User, fn.Count(Tweet.id).alias('count'))
         .join(Tweet, JOIN.LEFT_OUTER)
         .group_by(User))
```

The resulting query will return *User* objects with all their normal attributes plus an additional attribute *count* which will contain the count of tweets for each user. We use a left outer join to include users who have no tweets.



Let’s assume you have a tagging application and want to find tags that have a certain number of related objects. For this example we’ll use some different models in a [many-to-many](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#manytomany) configuration:



```python
class Photo(Model):
    image = CharField()

class Tag(Model):
    name = CharField()

class PhotoTag(Model):
    photo = ForeignKeyField(Photo)
    tag = ForeignKeyField(Tag)
```

Now say we want to find tags that have at least 5 photos associated with them:

```python
query = (Tag
         .select()
         .join(PhotoTag)
         .join(Photo)
         .group_by(Tag)
         .having(fn.Count(Photo.id) > 5))
```

This query is equivalent to the following SQL:

```python
SELECT t1."id", t1."name"
FROM "tag" AS t1
INNER JOIN "phototag" AS t2 ON t1."id" = t2."tag_id"
INNER JOIN "photo" AS t3 ON t2."photo_id" = t3."id"
GROUP BY t1."id", t1."name"
HAVING Count(t3."id") > 5
```

Suppose we want to grab the associated count and store it on the tag:

```python
query = (Tag
         .select(Tag, fn.Count(Photo.id).alias('count'))
         .join(PhotoTag)
         .join(Photo)
         .group_by(Tag)
         .having(fn.Count(Photo.id) > 5))
```

## Retrieving Scalar Values

You can retrieve scalar values by calling `Query.scalar()`. For instance:

```python
>>> PageView.select(fn.Count(fn.Distinct(PageView.url))).scalar()
100
```

You can retrieve multiple scalar values by passing `as_tuple=True`:

```python
>>> Employee.select(
...     fn.Min(Employee.salary), fn.Max(Employee.salary)
... ).scalar(as_tuple=True)
(30000, 50000)
```



## Window functions

A [`Window`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Window) function refers to an aggregate function that operates on a sliding window of data that is being processed as part of a `SELECT` query. Window functions make it possible to do things like:

1. Perform aggregations against subsets of a result-set.
2. Calculate a running total.
3. Rank results.
4. Compare a row value to a value in the preceding (or succeeding!) row(s).

peewee comes with support for SQL window functions, which can be created by calling [`Function.over()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Function.over) and passing in your partitioning or ordering parameters.

For the following examples, we’ll use the following model and sample data:

```python
class Sample(Model):
    counter = IntegerField()
    value = FloatField()

data = [(1, 10),
        (1, 20),
        (2, 1),
        (2, 3),
        (3, 100)]
Sample.insert_many(data, fields=[Sample.counter, Sample.value]).execute()
```

Our sample table now contains:

| id   | counter | value |
| ---- | ------- | ----- |
| 1    | 1       | 10.0  |
| 2    | 1       | 20.0  |
| 3    | 2       | 1.0   |
| 4    | 2       | 3.0   |
| 5    | 3       | 100.0 |

### Ordered Windows

Let’s calculate a running sum of the `value` field. In order for it to be a “running” sum, we need it to be ordered, so we’ll order with respect to the Sample’s `id` field:

```python
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(order_by=[Sample.id]).alias('total'))

for sample in query:
    print(sample.counter, sample.value, sample.total)

# 1    10.    10.
# 1    20.    30.
# 2     1.    31.
# 2     3.    34.
# 3   100    134.
```

For another example, we’ll calculate the difference between the current value and the previous value, when ordered by the `id`:

```python
difference = Sample.value - fn.LAG(Sample.value, 1).over(order_by=[Sample.id])
query = Sample.select(
    Sample.counter,
    Sample.value,
    difference.alias('diff'))

for sample in query:
    print(sample.counter, sample.value, sample.diff)

# 1    10.   NULL
# 1    20.    10.  -- (20 - 10)
# 2     1.   -19.  -- (1 - 20)
# 2     3.     2.  -- (3 - 1)
# 3   100     97.  -- (100 - 3)
```

### Partitioned Windows

Let’s calculate the average `value` for each distinct “counter” value. Notice that there are three possible values for the `counter` field (1, 2, and 3). We can do this by calculating the `AVG()` of the `value` column over a window that is partitioned depending on the `counter` field:

```python
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.AVG(Sample.value).over(partition_by=[Sample.counter]).alias('cavg'))

for sample in query:
    print(sample.counter, sample.value, sample.cavg)

# 1    10.    15.
# 1    20.    15.
# 2     1.     2.
# 2     3.     2.
# 3   100    100.
```

We can use ordering within partitions by specifying both the `order_by` and `partition_by` parameters. For an example, let’s rank the samples by value within each distinct `counter` group.

```python
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.RANK().over(
        order_by=[Sample.value],
        partition_by=[Sample.counter]).alias('rank'))

for sample in query:
    print(sample.counter, sample.value, sample.rank)

# 1    10.    1
# 1    20.    2
# 2     1.    1
# 2     3.    2
# 3   100     1
```

### Bounded windows

By default, window functions are evaluated using an *unbounded preceding* start for the window, and the *current row* as the end. We can change the bounds of the window our aggregate functions operate on by specifying a `start` and/or `end` in the call to [`Function.over()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Function.over). Additionally, Peewee comes with helper-methods on the [`Window`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Window) object for generating the appropriate boundary references:

- [`Window.CURRENT_ROW`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Window.CURRENT_ROW) - attribute that references the current row.
- [`Window.preceding()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Window.preceding) - specify number of row(s) preceding, or omit number to indicate **all** preceding rows.
- [`Window.following()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Window.following) - specify number of row(s) following, or omit number to indicate **all** following rows.

To examine how boundaries work, we’ll calculate a running total of the `value` column, ordered with respect to `id`, **but** we’ll only look the running total of the current row and it’s two preceding rows:

```python
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(
        order_by=[Sample.id],
        start=Window.preceding(2),
        end=Window.CURRENT_ROW).alias('rsum'))

for sample in query:
    print(sample.counter, sample.value, sample.rsum)

# 1    10.    10.
# 1    20.    30.  -- (20 + 10)
# 2     1.    31.  -- (1 + 20 + 10)
# 2     3.    24.  -- (3 + 1 + 20)
# 3   100    104.  -- (100 + 3 + 1)
```

Note

Technically we did not need to specify the `end=Window.CURRENT` because that is the default. It was shown in the example for demonstration.

Let’s look at another example. In this example we will calculate the “opposite” of a running total, in which the total sum of all values is decreased by the value of the samples, ordered by `id`. To accomplish this, we’ll calculate the sum from the current row to the last row.

```python
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(
        order_by=[Sample.id],
        start=Window.CURRENT_ROW,
        end=Window.following()).alias('rsum'))

# 1    10.   134.  -- (10 + 20 + 1 + 3 + 100)
# 1    20.   124.  -- (20 + 1 + 3 + 100)
# 2     1.   104.  -- (1 + 3 + 100)
# 2     3.   103.  -- (3 + 100)
# 3   100    100.  -- (100)
```

### Filtered Aggregates

Aggregate functions may also support filter functions (Postgres and Sqlite 3.25+), which get translated into a `FILTER (WHERE...)` clause. Filter expressions are added to an aggregate function with the [`Function.filter()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Function.filter) method.

For an example, we will calculate the running sum of the `value` field with respect to the `id`, but we will filter-out any samples whose `counter=2`.

```python
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).filter(Sample.counter != 2).over(
        order_by=[Sample.id]).alias('csum'))

for sample in query:
    print(sample.counter, sample.value, sample.csum)

# 1    10.    10.
# 1    20.    30.
# 2     1.    30.
# 2     3.    30.
# 3   100    130.
```

Note

The call to [`filter()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Function.filter) must precede the call to [`over()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Function.over).

### Reusing Window Definitions

If you intend to use the same window definition for multiple aggregates, you can create a [`Window`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Window) object. The [`Window`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Window) object takes the same parameters as [`Function.over()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Function.over), and can be passed to the `over()` method in-place of the individual parameters.

Here we’ll declare a single window, ordered with respect to the sample `id`, and call several window functions using that window definition:

```python
win = Window(order_by=[Sample.id])
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.LEAD(Sample.value).over(win),
    fn.LAG(Sample.value).over(win),
    fn.SUM(Sample.value).over(win)
).window(win)  # Include our window definition in query.

for row in query.tuples():
    print(row)

# counter  value  lead()  lag()  sum()
# 1          10.     20.   NULL    10.
# 1          20.      1.    10.    30.
# 2           1.      3.    20.    31.
# 2           3.    100.     1.    34.
# 3         100.    NULL     3.   134.
```

### Multiple window definitions

In the previous example, we saw how to declare a [`Window`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Window) definition and re-use it for multiple different aggregations. You can include as many window definitions as you need in your queries, but it is necessary to ensure each window has a unique alias:

```python
w1 = Window(order_by=[Sample.id]).alias('w1')
w2 = Window(partition_by=[Sample.counter]).alias('w2')
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(w1).alias('rsum'),  # Running total.
    fn.AVG(Sample.value).over(w2).alias('cavg')   # Avg per category.
).window(w1, w2)  # Include our window definitions.

for sample in query:
    print(sample.counter, sample.value, sample.rsum, sample.cavg)

# counter  value   rsum     cavg
# 1          10.     10.     15.
# 1          20.     30.     15.
# 2           1.     31.      2.
# 2           3.     34.      2.
# 3         100     134.    100.
```

Similarly, if you have multiple window definitions that share similar definitions, it is possible to extend a previously-defined window definition. For example, here we will be partitioning the data-set by the counter value, so we’ll be doing our aggregations with respect to the counter. Then we’ll define a second window that extends this partitioning, and adds an ordering clause:

```python
w1 = Window(partition_by=[Sample.counter]).alias('w1')

# By extending w1, this window definition will also be partitioned
# by "counter".
w2 = Window(extends=w1, order_by=[Sample.value.desc()]).alias('w2')

query = (Sample
         .select(Sample.counter, Sample.value,
                 fn.SUM(Sample.value).over(w1).alias('group_sum'),
                 fn.RANK().over(w2).alias('revrank'))
         .window(w1, w2)
         .order_by(Sample.id))

for sample in query:
    print(sample.counter, sample.value, sample.group_sum, sample.revrank)

# counter  value   group_sum   revrank
# 1        10.     30.         2
# 1        20.     30.         1
# 2        1.      4.          2
# 2        3.      4.          1
# 3        100.    100.        1
```



### Frame types: RANGE vs ROWS vs GROUPS

Depending on the frame type, the database will process ordered groups differently. Let’s create two additional `Sample` rows to visualize the difference:

```python
>>> Sample.create(counter=1, value=20.)
<Sample 6>
>>> Sample.create(counter=2, value=1.)
<Sample 7>
```

Our table now contains:

| id   | counter | value |
| ---- | ------- | ----- |
| 1    | 1       | 10.0  |
| 2    | 1       | 20.0  |
| 3    | 2       | 1.0   |
| 4    | 2       | 3.0   |
| 5    | 3       | 100.0 |
| 6    | 1       | 20.0  |
| 7    | 2       | 1.0   |

Let’s examine the difference by calculating a “running sum” of the samples, ordered with respect to the `counter` and `value` fields. To specify the frame type, we can use either:

- [`Window.RANGE`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Window.RANGE)
- [`Window.ROWS`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Window.ROWS)
- [`Window.GROUPS`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Window.GROUPS)

The behavior of [`RANGE`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Window.RANGE), when there are logical duplicates, may lead to unexpected results:

```python
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(
        order_by=[Sample.counter, Sample.value],
        frame_type=Window.RANGE).alias('rsum'))

for sample in query.order_by(Sample.counter, Sample.value):
    print(sample.counter, sample.value, sample.rsum)

# counter  value   rsum
# 1          10.     10.
# 1          20.     50.
# 1          20.     50.
# 2           1.     52.
# 2           1.     52.
# 2           3.     55.
# 3         100     155.
```

With the inclusion of the new rows we now have some rows that have duplicate `category` and `value` values. The [`RANGE`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Window.RANGE) frame type causes these duplicates to be evaluated together rather than separately.

The more expected result can be achieved by using [`ROWS`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Window.ROWS) as the frame-type:

```python
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(
        order_by=[Sample.counter, Sample.value],
        frame_type=Window.ROWS).alias('rsum'))

for sample in query.order_by(Sample.counter, Sample.value):
    print(sample.counter, sample.value, sample.rsum)

# counter  value   rsum
# 1          10.     10.
# 1          20.     30.
# 1          20.     50.
# 2           1.     51.
# 2           1.     52.
# 2           3.     55.
# 3         100     155.
```

Peewee uses these rules for determining what frame-type to use:

- If the user specifies a `frame_type`, that frame type will be used.
- If `start` and/or `end` boundaries are specified Peewee will default to using `ROWS`.
- If the user did not specify frame type or start/end boundaries, Peewee will use the database default, which is `RANGE`.

The [`Window.GROUPS`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Window.GROUPS) frame type looks at the window range specification in terms of groups of rows, based on the ordering term(s). Using `GROUPS`, we can define the frame so it covers distinct groupings of rows. Let’s look at an example:

```python
query = (Sample
         .select(Sample.counter, Sample.value,
                 fn.SUM(Sample.value).over(
                    order_by=[Sample.counter, Sample.value],
                    frame_type=Window.GROUPS,
                    start=Window.preceding(1)).alias('gsum'))
         .order_by(Sample.counter, Sample.value))

for sample in query:
    print(sample.counter, sample.value, sample.gsum)

#  counter   value    gsum
#  1         10       10
#  1         20       50
#  1         20       50   (10) + (20+0)
#  2         1        42
#  2         1        42   (20+20) + (1+1)
#  2         3        5    (1+1) + 3
#  3         100      103  (3) + 100
```

As you can hopefully infer, the window is grouped by its ordering term, which is `(counter, value)`. We are looking at a window that extends between one previous group and the current group.

Note

For information about the window function APIs, see:

- [`Function.over()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Function.over)
- [`Function.filter()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Function.filter)
- [`Window`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Window)

For general information on window functions, read the postgres [window functions tutorial](https://www.postgresql.org/docs/current/tutorial-window.html)

Additionally, the [postgres docs](https://www.postgresql.org/docs/current/sql-select.html#SQL-WINDOW) and the [sqlite docs](https://www.sqlite.org/windowfunctions.html) contain a lot of good information.



## Retrieving row tuples / dictionaries / namedtuples

Sometimes you do not need the overhead of creating model instances and simply want to iterate over the row data without needing all the APIs provided [`Model`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model). To do this, use:

- [`dicts()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BaseQuery.dicts)
- [`namedtuples()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BaseQuery.namedtuples)
- [`tuples()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BaseQuery.tuples)
- [`objects()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BaseQuery.objects) – accepts an arbitrary constructor function which is called with the row tuple.

```python
stats = (Stat
         .select(Stat.url, fn.Count(Stat.url))
         .group_by(Stat.url)
         .tuples())

# iterate over a list of 2-tuples containing the url and count
for stat_url, stat_count in stats:
    print(stat_url, stat_count)
```

Similarly, you can return the rows from the cursor as dictionaries using [`dicts()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BaseQuery.dicts):

```python
stats = (Stat
         .select(Stat.url, fn.Count(Stat.url).alias('ct'))
         .group_by(Stat.url)
         .dicts())

# iterate over a list of 2-tuples containing the url and count
for stat in stats:
    print(stat['url'], stat['ct'])
```



## Returning Clause

[`PostgresqlDatabase`](http://docs.peewee-orm.com/en/latest/peewee/api.html#PostgresqlDatabase) supports a `RETURNING` clause on `UPDATE`, `INSERT` and `DELETE` queries. Specifying a `RETURNING` clause allows you to iterate over the rows accessed by the query.

By default, the return values upon execution of the different queries are:

- `INSERT` - auto-incrementing primary key value of the newly-inserted row. When not using an auto-incrementing primary key, Postgres will return the new row’s primary key, but SQLite and MySQL will not.
- `UPDATE` - number of rows modified
- `DELETE` - number of rows deleted

When a returning clause is used the return value upon executing a query will be an iterable cursor object.

Postgresql allows, via the `RETURNING` clause, to return data from the rows inserted or modified by a query.

For example, let’s say you have an [`Update`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Update) that deactivates all user accounts whose registration has expired. After deactivating them, you want to send each user an email letting them know their account was deactivated. Rather than writing two queries, a `SELECT` and an `UPDATE`, you can do this in a single `UPDATE` query with a `RETURNING` clause:

```python
query = (User
         .update(is_active=False)
         .where(User.registration_expired == True)
         .returning(User))

# Send an email to every user that was deactivated.
for deactivate_user in query.execute():
    send_deactivation_email(deactivated_user.email)
```

The `RETURNING` clause is also available on [`Insert`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Insert) and [`Delete`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Delete). When used with `INSERT`, the newly-created rows will be returned. When used with `DELETE`, the deleted rows will be returned.

The only limitation of the `RETURNING` clause is that it can only consist of columns from tables listed in the query’s `FROM` clause. To select all columns from a particular table, you can simply pass in the [`Model`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model) class.

As another example, let’s add a user and set their creation-date to the server-generated current timestamp. We’ll create and retrieve the new user’s ID, Email and the creation timestamp in a single query:

```python
query = (User
         .insert(email='foo@bar.com', created=fn.now())
         .returning(User))  # Shorthand for all columns on User.

# When using RETURNING, execute() returns a cursor.
cursor = query.execute()

# Get the user object we just inserted and log the data:
user = cursor[0]
logger.info('Created user %s (id=%s) at %s', user.email, user.id, user.created)
```

By default the cursor will return [`Model`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model) instances, but you can specify a different row type:

```python
data = [{'name': 'charlie'}, {'name': 'huey'}, {'name': 'mickey'}]
query = (User
         .insert_many(data)
         .returning(User.id, User.username)
         .dicts())

for new_user in query.execute():
    print('Added user "%s", id=%s' % (new_user['username'], new_user['id']))
```

Just as with [`Select`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select) queries, you can specify various [result row types](http://docs.peewee-orm.com/en/latest/peewee/querying.html#rowtypes).



## Common Table Expressions

Peewee supports the inclusion of common table expressions (CTEs) in all types of queries. CTEs may be useful for:

- Factoring out a common subquery.
- Grouping or filtering by a column derived in the CTE’s result set.
- Writing recursive queries.

To declare a [`Select`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select) query for use as a CTE, use [`cte()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SelectQuery.cte) method, which wraps the query in a [`CTE`](http://docs.peewee-orm.com/en/latest/peewee/api.html#CTE) object. To indicate that a [`CTE`](http://docs.peewee-orm.com/en/latest/peewee/api.html#CTE) should be included as part of a query, use the [`Query.with_cte()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Query.with_cte) method, passing a list of CTE objects.

### Simple Example

For an example, let’s say we have some data points that consist of a key and a floating-point value. Let’s define our model and populate some test data:

```python
class Sample(Model):
    key = TextField()
    value = FloatField()

data = (
    ('a', (1.25, 1.5, 1.75)),
    ('b', (2.1, 2.3, 2.5, 2.7, 2.9)),
    ('c', (3.5, 3.5)))

# Populate data.
for key, values in data:
    Sample.insert_many([(key, value) for value in values],
                       fields=[Sample.key, Sample.value]).execute()
```

Let’s use a CTE to calculate, for each distinct key, which values were above-average for that key.

```python
# First we'll declare the query that will be used as a CTE. This query
# simply determines the average value for each key.
cte = (Sample
       .select(Sample.key, fn.AVG(Sample.value).alias('avg_value'))
       .group_by(Sample.key)
       .cte('key_avgs', columns=('key', 'avg_value')))

# Now we'll query the sample table, using our CTE to find rows whose value
# exceeds the average for the given key. We'll calculate how far above the
# average the given sample's value is, as well.
query = (Sample
         .select(Sample.key, Sample.value)
         .join(cte, on=(Sample.key == cte.c.key))
         .where(Sample.value > cte.c.avg_value)
         .order_by(Sample.value)
         .with_cte(cte))
```

We can iterate over the samples returned by the query to see which samples had above-average values for their given group:

```python
>>> for sample in query:
...     print(sample.key, sample.value)

# 'a', 1.75
# 'b', 2.7
# 'b', 2.9
```

### Complex Example

For a more complete example, let’s consider the following query which uses multiple CTEs to find per-product sales totals in only the top sales regions. Our model looks like this:

```python
class Order(Model):
    region = TextField()
    amount = FloatField()
    product = TextField()
    quantity = IntegerField()
```

Here is how the query might be written in SQL. This example can be found in the [postgresql documentation](https://www.postgresql.org/docs/current/static/queries-with.html).

```python
WITH regional_sales AS (
    SELECT region, SUM(amount) AS total_sales
    FROM orders
    GROUP BY region
  ), top_regions AS (
    SELECT region
    FROM regional_sales
    WHERE total_sales > (SELECT SUM(total_sales) / 10 FROM regional_sales)
  )
SELECT region,
       product,
       SUM(quantity) AS product_units,
       SUM(amount) AS product_sales
FROM orders
WHERE region IN (SELECT region FROM top_regions)
GROUP BY region, product;
```

With Peewee, we would write:

```python
reg_sales = (Order
             .select(Order.region,
                     fn.SUM(Order.amount).alias('total_sales'))
             .group_by(Order.region)
             .cte('regional_sales'))

top_regions = (reg_sales
               .select(reg_sales.c.region)
               .where(reg_sales.c.total_sales > (
                   reg_sales.select(fn.SUM(reg_sales.c.total_sales) / 10)))
               .cte('top_regions'))

query = (Order
         .select(Order.region,
                 Order.product,
                 fn.SUM(Order.quantity).alias('product_units'),
                 fn.SUM(Order.amount).alias('product_sales'))
         .where(Order.region.in_(top_regions.select(top_regions.c.region)))
         .group_by(Order.region, Order.product)
         .with_cte(regional_sales, top_regions))
```

### Recursive CTEs

Peewee supports recursive CTEs. Recursive CTEs can be useful when, for example, you have a tree data-structure represented by a parent-link foreign key. Suppose, for example, that we have a hierarchy of categories for an online bookstore. We wish to generate a table showing all categories and their absolute depths, along with the path from the root to the category.

Peewee支持递归cte。例如，当您有一个由parent-link外键表示的树形数据结构时，递归cte可能会很有用。例如，假设我们有一个在线书店的类别层次结构。我们希望生成一个表，显示所有类别及其绝对深度，以及从根到类别的路径。

We’ll assume the following model definition, in which each category has a foreign-key to its immediate parent category:

我们假设模型定义如下，其中每个类别都有一个直接父类别的外键:

```python
class Category(Model):
    name = TextField()
    parent = ForeignKeyField('self', backref='children', null=True)
```

To list all categories along with their depth and parents, we can use a recursive CTE:

要列出所有类别及其深度和父类别，可以使用递归CTE:

```python
# Define the base case of our recursive CTE. This will be categories that
# have a null parent foreign-key.
Base = Category.alias()
level = Value(1).alias('level')
path = Base.name.alias('path')
base_case = (Base
             .select(Base.id, Base.name, Base.parent, level, path)
             .where(Base.parent.is_null())
             .cte('base', recursive=True))

# Define the recursive terms.
RTerm = Category.alias()
rlevel = (base_case.c.level + 1).alias('level')
rpath = base_case.c.path.concat('->').concat(RTerm.name).alias('path')
recursive = (RTerm
             .select(RTerm.id, RTerm.name, RTerm.parent, rlevel, rpath)
             .join(base_case, on=(RTerm.parent == base_case.c.id)))

# The recursive CTE is created by taking the base case and UNION ALL with
# the recursive term.
cte = base_case.union_all(recursive)

# We will now query from the CTE to get the categories, their levels,  and
# their paths.
query = (cte
         .select_from(cte.c.name, cte.c.level, cte.c.path)
         .order_by(cte.c.path))

# We can now iterate over a list of all categories and print their names,
# absolute levels, and path from root -> category.
for category in query:
    print(category.name, category.level, category.path)

# Example output:
# root, 1, root
# p1, 2, root->p1
# c1-1, 3, root->p1->c1-1
# c1-2, 3, root->p1->c1-2
# p2, 2, root->p2
# c2-1, 3, root->p2->c2-1
```

## Foreign Keys and Joins

This section have been moved into its own document: [Relationships and Joins](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#relationships).

[Next ](http://docs.peewee-orm.com/en/latest/peewee/query_operators.html)[ Previous](http://docs.peewee-orm.com/en/latest/peewee/models.html)

------

© Copyright charles leifer Revision `04520168`.

Built with [Sphinx](http://sphinx-doc.org/) using a [theme](https://github.com/rtfd/sphinx_rtd_theme) provided by [Read the Docs](https://readthedocs.org/).