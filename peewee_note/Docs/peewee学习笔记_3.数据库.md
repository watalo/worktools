# Database模块

因为我暂时只用SQlite，所以其他数据库的我就不翻译了。

------
[TOC]



------

Peewee [ Database ](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database)对象表示到数据库的连接。[`Database`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database)类被实例化，包含了打开数据库连接所需的所有信息，然后可以用于:

-  打开和关闭连接.
- 执行查询.
- 管理事务(和保存点).
- 内设表、列、索引和限制条件

Peewee支持SQLite, MySQL和Postgres。每个数据库类都提供一些基本的、特定于数据库的配置选项。

```python
from peewee import *

# SQLite database using WAL journal mode and 64MB cache.
sqlite_db = SqliteDatabase('/path/to/app.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1024 * 64})

# MySQL
mysql_db = MySQLDatabase('my_app', user='app', password='db_password',
                         host='10.1.0.8', port=3306)

# Postgres
pg_db = PostgresqlDatabase('my_app', user='postgres', password='secret',
                           host='10.1.0.9', port=5432)
```

Peewee通过特定的扩展模块提供了对SQLite、Postgres和CockroachDB的高级支持。要使用这些扩展功能，需要导入特定的数据模块并使用:

```python
from playhouse.sqlite_ext import SqliteExtDatabase

# Use SQLite (will register a REGEXP function and set busy timeout to 3s).
db = SqliteExtDatabase('/path/to/app.db', regexp_function=True, timeout=3,
                       pragmas={'journal_mode': 'wal'})


from playhouse.postgres_ext import PostgresqlExtDatabase

# Use Postgres (and register hstore extension).
db = PostgresqlExtDatabase('my_app', user='postgres', register_hstore=True)


from playhouse.cockroachdb import CockroachDatabase

# Use CockroachDB.
db = CockroachDatabase('my_app', user='root', port=26257, host='10.1.0.8')
```

更多扩展库信息可以看下面的文档:

- [Postgresql Extensions](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#postgres-ext)
- [SQLite Extensions](http://docs.peewee-orm.com/en/latest/peewee/sqlite_ext.html#sqlite-ext)
- [Cockroach Database](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#crdb)
- [Sqlcipher backend](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#sqlcipher-ext) (encrypted SQLite database).
- [apsw, an advanced sqlite driver](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#apsw)
- [SqliteQ](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#sqliteq)

## 初始化数据库

[Database ](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database)初始化方法将数据库的名称作为第一个参数。在建立连接时，后续关键字参数将传递给底层数据库驱动程序。

For instance, with Postgresql it is common to need to specify the `host`, `user` and `password` when creating your connection. These are not standard Peewee [`Database`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database) parameters, so they will be passed directly back to `psycopg2` when creating connections:

```
db = PostgresqlDatabase(
    'database_name',  # Required by Peewee.
    user='postgres',  # Will be passed directly to psycopg2.
    password='secret',  # Ditto.
    host='db.mysite.com')  # Ditto.
```

As another example, the `pymysql` driver accepts a `charset` parameter which is not a standard Peewee [`Database`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database) parameter. To set this value, simply pass in `charset` alongside your other values:

```
db = MySQLDatabase('database_name', user='www-data', charset='utf8mb4')
```

Consult your database driver’s documentation for the available parameters:

- Postgres: [psycopg2](http://initd.org/psycopg/docs/module.html#psycopg2.connect)
- MySQL: [MySQLdb](http://mysql-python.sourceforge.net/MySQLdb.html#some-mysql-examples)
- MySQL: [pymysql](https://github.com/PyMySQL/PyMySQL/blob/f08f01fe8a59e8acfb5f5add4a8fe874bec2a196/pymysql/connections.py#L494-L513)
- SQLite: [sqlite3](https://docs.python.org/2/library/sqlite3.html#sqlite3.connect)
- CockroachDB: see [psycopg2](http://initd.org/psycopg/docs/module.html#psycopg2.connect)

## 使用SQLite

用[`SqliteDatabase()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase)连接SQLite数据库，第一个参数是数据库的文件名（或者路径），或者字符串`:memory:`可以创建内存中的数据库。在数据库文件名之后，可以指定一个列表或pragmas或任何其他任意[sqlite3参数](https://docs.python.org/2/library/sqlite3.html#sqlite3.connect)。

```python
sqlite_db = SqliteDatabase('my_app.db', pragmas={'journal_mode': 'wal'})

class BaseModel(Model):
    """A base model that will use our Sqlite database."""
    class Meta:
        database = sqlite_db

class User(BaseModel):
    username = TextField()
    # etc, etc
```

Peewee的[SQLite扩展模块](http://docs.peewee-orm.com/en/latest/peewee/sqlite_ext.html sqlite-ext)提供了许多SQLite-specific特性,比如[全文搜索](http://docs.peewee-orm.com/en/latest/peewee/sqlite_ext.html # sqlite-fts), [json扩展支持](http://docs.peewee-orm.com/en/latest/peewee/sqlite_ext.html # sqlite-json1)等等，用[`SqliteExtDatabase`](http://docs.peewee-orm.com/en/latest/peewee/sqlite_ext.html#SqliteExtDatabase)中的`playhouse.sqlite_ext`模块:

```python
from playhouse.sqlite_ext import SqliteExtDatabase

sqlite_db = SqliteExtDatabase('my_app.db', pragmas={
    'journal_mode': 'wal',  # WAL-mode.
    'cache_size': -64 * 1000,  # 64MB cache.
    'synchronous': 0})  # Let the OS manage syncing.
```

### PRAGMA声明

SQLite允许通过`PRAGMA`语句配置大量参数([SQLite文档](https://www.sqlite.org/pragma.html))。这些语句通常在创建新的数据库连接时运行。要对新连接运行一个或多个`PRAGMA`语句，可以将它们指定为一个字典或包含PRAGMA名称和值的二元组列表::

```python
db = SqliteDatabase('my_app.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': 10000,  # 10000 pages, or ~40MB
    'foreign_keys': 1,  # Enforce foreign-key constraints
})
```

动态配置`PRAGMAs`可以使用[`pragma()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase.pragma)方法或[`SqliteDatabase`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase)对象的特殊属性:

```python
# Set cache size to 64MB for *current connection*.
db.pragma('cache_size', -1024 * 64)

# Same as above.
db.cache_size = -1024 * 64

# Read the value of several pragmas:
print('cache_size:', db.cache_size)
print('foreign_keys:', db.foreign_keys)
print('journal_mode:', db.journal_mode)
print('page_size:', db.page_size)

# Set foreign_keys pragma on current connection *AND* on all
# connections opened subsequently.
db.pragma('foreign_keys', 1, permanent=True)
```

⚠️**注意**

默认情况下，使用[`pragma()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase.pragma)方法设置的Pragmas在连接关闭后不会持久化。要在打开连接时配置pragma，需要指定`permanent=True`。

🐶**提示**

关于PRAGMA的完整信息: http://sqlite.org/pragma.html

### 推荐配置

Peewee作者用SQLite搭建web应用数据库时的配置：

| pragma                   | 推荐配置          | 解释                                           |
| ------------------------ | ----------------- | ---------------------------------------------- |
| journal_mode             | wal               | allow readers and writers to co-exist          |
| cache_size               | -1 * data_size_kb | set page-cache size in KiB, e.g. -32000 = 32MB |
| foreign_keys             | 1                 | enforce foreign-key constraints                |
| ignore_check_constraints | 0                 | enforce CHECK constraints                      |
| synchronous              | 0                 | let OS handle fsync (use with caution)         |

案例:

```python
db = SqliteDatabase('my_app.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1 * 64000,  # 64MB
    'foreign_keys': 1,
    'ignore_check_constraints': 0,
    'synchronous': 0})
```

### 用户自定义函数

SQLite可以用用户自定义的Python代码进行扩展。[`SqliteDatabase`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase)类支持三种类型的用户定义扩展:

- Functions函数 —接受任意数量的参数并返回单个值。
- Aggregate聚合 —从多行聚合参数并返回单个值。
- Collations整理 —描述如何对某个值排序。

🐶**提示**

更多扩展, 可以查`playhouse.sqlite_ext` module中的[`SqliteExtDatabase`](http://docs.peewee-orm.com/en/latest/peewee/sqlite_ext.html#SqliteExtDatabase),  

functions案例:

```python
db = SqliteDatabase('analytics.db')

from urllib.parse import urlparse

@db.func('hostname')
def hostname(url):
    if url is not None:
        return urlparse(url).netloc

# Call this function in our code:
# The following finds the most common hostnames of referrers by count:
query = (PageView
         .select(fn.hostname(PageView.referrer), fn.COUNT(PageView.id))
         .group_by(fn.hostname(PageView.referrer))
         .order_by(fn.COUNT(PageView.id).desc()))
```

aggregate案例:

```python
from hashlib import md5

@db.aggregate('md5')
class MD5Checksum(object):
    def __init__(self):
        self.checksum = md5()

    def step(self, value):
        self.checksum.update(value.encode('utf-8'))

    def finalize(self):
        return self.checksum.hexdigest()

# Usage:
# The following computes an aggregate MD5 checksum for files broken
# up into chunks and stored in the database.
query = (FileChunk
         .select(FileChunk.filename, fn.MD5(FileChunk.data))
         .group_by(FileChunk.filename)
         .order_by(FileChunk.filename, FileChunk.sequence))
```

collation案例:

```python
@db.collation('ireverse')
def collate_reverse(s1, s2):
    # Case-insensitive reverse.
    s1, s2 = s1.lower(), s2.lower()
    return (s1 < s2) - (s1 > s2)  # Equivalent to -cmp(s1, s2)

# To use this collation to sort books in reverse order...
Book.select().order_by(collate_reverse.collation(Book.title))

# Or...
Book.select().order_by(Book.title.asc(collation='reverse'))
```

 自定义table-value 函数 ([`TableFunction`](http://docs.peewee-orm.com/en/latest/peewee/sqlite_ext.html#TableFunction) 和 [`table_function`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase.table_function)):

```python
from playhouse.sqlite_ext import TableFunction

db = SqliteDatabase('my_app.db')

@db.table_function('series')
class Series(TableFunction):
    columns = ['value']
    params = ['start', 'stop', 'step']

    def initialize(self, start=0, stop=None, step=1):
        """
        Table-functions declare an initialize() method, which is
        called with whatever arguments the user has called the
        function with.
        """
        self.start = self.current = start
        self.stop = stop or float('Inf')
        self.step = step

    def iterate(self, idx):
        """
        Iterate is called repeatedly by the SQLite database engine
        until the required number of rows has been read **or** the
        function raises a `StopIteration` signalling no more rows
        are available.
        """
        if self.current > self.stop:
            raise StopIteration

        ret, self.current = self.current, self.current + self.step
        return (ret,)

# Usage:
cursor = db.execute_sql('SELECT * FROM series(?, ?, ?)', (0, 5, 2))
for value, in cursor:
    print(value)

# Prints:
# 0
# 2
# 4
```

官方文档链接:

- [`SqliteDatabase.func()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase.func)
- [`SqliteDatabase.aggregate()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase.aggregate)
- [`SqliteDatabase.collation()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase.collation)
- [`SqliteDatabase.table_function()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase.table_function)
-  [SQLite Extensions](http://docs.peewee-orm.com/en/latest/peewee/sqlite_ext.html#sqlite-ext)

### 为事务设置锁定模式

SQLite事务(transactions)可以用三种方式打开:

- *Deferred* (**default**) - 仅在执行读或写操作时获取锁。第一次读创建了一个[共享锁](https://sqlite.org/lockingv3.html#locking)，第一次写创建了一个[保留锁](https://sqlite.org/lockingv3.html#locking)。因为获取锁的操作会延迟到实际需要时才进行，所以在当前线程的BEGIN操作执行之后，另一个线程或进程可能会创建一个单独的事务并写入数据库。
- *Immediate* - 立即获得一个[保留锁](https://sqlite.org/lockingv3.html#locking)。在这种模式下，其他数据库不能写入数据库，也不能打开一个*immediate*或*exclusive*事务。但是，其他进程可以继续从数据库中读取数据。
- *Exclusive* - 打开一个[排他锁](https://sqlite.org/lockingv3.html#locking)，阻止所有(除了read uncommitted)连接访问数据库，直到事务完成。

锁模式的案例:

```python
db = SqliteDatabase('app.db')

with db.atomic('EXCLUSIVE'):
    do_something()


@db.atomic('IMMEDIATE')
def some_other_function():
    # This function is wrapped in an "IMMEDIATE" transaction.
    do_something_else()
```

更多信息，请参阅SQLite[锁定文档](https://sqlite.org/lockingv3.html#locking)。要了解更多关于Peewee中的事务，请参阅[管理事务](http://docs.peewee-orm.com/en/latest/peewee/database.html#transactions)文档。

### APSW（Another Python SQLite Wrapper）🤯

Peewee还附带了一个使用[APSW（一个高级SQLite驱动程序）](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#apsw)的备选SQLite数据库，这是一个高级Python SQLite驱动程序。有关APSW项目的更多信息，请访问[APSW项目网站](https://code.google.com/p/apsw/)。APSW提供特殊功能，如:

- 虚拟表、虚拟文件系统、Blob I/O、备份和文件控制。
- 连接可以在线程之间共享，而不需要任何额外的锁。
- 事务由你的代码显式管理。
- Unicode处理*正确*。
- APSW比标准库sqlite3模块更快。
- 将几乎整个SQLite C API展示给你的Python应用程序。

如果你想使用APSW，请使用apsw_ext模块中的[' APSWDatabase '](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#APSWDatabase):

```python
from playhouse.apsw_ext import APSWDatabase

apsw_db = APSWDatabase('my_app.db')
```



## 用Database URL建立连接

playhouse模块[Database URL](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html)提供了一个辅助函数[`connect()`](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html连接)。接受一个`Database URL`返回一个[`Database`](http://docs.peewee-orm.com/en/latest/peewee/api.html)实例。

Example code: 

```python
import os

from peewee import *
from playhouse.db_url import connect

# Connect to the database URL defined in the environment, falling
# back to a local Sqlite database if no database URL is specified.
db = connect(os.environ.get('DATABASE') or 'sqlite:///default.db')

class BaseModel(Model):
    class Meta:
        database = db
```

Example database URLs:

- `sqlite:///my_database.db` will create a [`SqliteDatabase`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase) instance for the file `my_database.db` in the current directory.
- `sqlite:///:memory:` will create an in-memory [`SqliteDatabase`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase) instance.
- `postgresql://postgres:my_password@localhost:5432/my_database` will create a [`PostgresqlDatabase`](http://docs.peewee-orm.com/en/latest/peewee/api.html#PostgresqlDatabase) instance. A username and password are provided, as well as the host and port to connect to.
- `mysql://user:passwd@ip:port/my_db` will create a [`MySQLDatabase`](http://docs.peewee-orm.com/en/latest/peewee/api.html#MySQLDatabase) instance for the local MySQL database *my_db*.
- [More examples in the db_url documentation](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#db-url).



## 运行时数据库配置

有时数据库连接设置直到运行时才知道，而运行时这些值可能从配置文件或环境加载。在这些情况下，您可以通过指定`None`作为database_name来*延迟*数据库的初始化。

```python
database = PostgresqlDatabase(None)  # Un-initialized database.

class SomeModel(Model):
    class Meta:
        database = database
```

如果你在数据库未初始化的情况下尝试连接或发出任何查询，会得到一个异常:

```bash
>>> database.connect()
Exception: Error, database not properly initialized before opening connection
```

要初始化数据库，使用数据库名称和任何其他关键字参数调用[`init() `](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.init)方法:

```python
database_name = input('What is the name of the db? ')
database.init(database_name, host='localhost', user='postgres')
```



## 动态定义数据库

为了更好地控制数据库的定义/初始化方式，可以使用[`DatabaseProxy`](http://docs.peewee-orm.com/en/latest/peewee/api.html#DatabaseProxy)。[`DatabaseProxy`](http://docs.peewee-orm.com/en/latest/peewee/api.html#DatabaseProxy)对象充当占位符，然后在运行时您可以将其替换为其他对象。在下面的例子中，我们将根据应用的配置来交换数据库:

```python
database_proxy = DatabaseProxy()  # Create a proxy for our db.

class BaseModel(Model):
    class Meta:
        database = database_proxy  # Use proxy for our DB.

class User(BaseModel):
    username = CharField()

# Based on configuration, use a different database.
if app.config['DEBUG']:
    database = SqliteDatabase('local.db')
elif app.config['TESTING']:
    database = SqliteDatabase(':memory:')
else:
    database = PostgresqlDatabase('mega_production_db')

# Configure our proxy to use the db we specified in config.
database_proxy.initialize(database)
```

**⚠️警告**

只有在实际的数据库驱动程序在运行时发生变化时才使用此方法。例如，如果您的测试和本地开发环境运行在SQLite上，但您部署的应用程序使用PostgreSQL，您可以使用[`DatabaseProxy`](http://docs.peewee-orm.com/en/latest/peewee/api.html#DatabaseProxy)在运行时更换引擎。

但是，如果只有连接值在运行时不同，比如数据库文件或数据库主机的路径，则应该使用[`database.init()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.init)。请参阅[运行时数据库配置](http://docs.peewee-orm.com/en/latest/peewee/database.html#deferring-initialization)了解更多细节。

**⚠️请注意**

避免使用[`DatabaseProxy`](http://docs.peewee-orm.com/en/latest/peewee/api.html#DatabaseProxy)，使用[`database. bind()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.bind)和相关方法来设置或更改数据库可能更容易。请参见[运行时设置数据库](http://docs.peewee-orm.com/en/latest/peewee/database.html#binding-database)。



## 在运行时设置数据库

有三种方法:

```python
# The usual way:
db = SqliteDatabase('my_app.db', pragmas={'journal_mode': 'wal'})


# Specify the details at run-time:
db = SqliteDatabase(None)
...
db.init(db_filename, pragmas={'journal_mode': 'wal'})


# Or use a placeholder:
db = DatabaseProxy()
...
db.initialize(SqliteDatabase('my_app.db', pragmas={'journal_mode': 'wal'}))
```

Peewee还可以为您的模型类设置或更改数据库。在运行测试时，Peewee测试套件使用这种技术将测试模型类绑定到各种数据库实例。

有两套互补的方法:

- [`database. bind()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.bind)和[`Model.bind()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.bind) —将一个或多个模型绑定到数据库
- [`Database.bind_ctx ()`](http://docs.peewee-orm.com/en/latest/peewee/api.html Database.bind_ctx)和[`Model.bind_ctx ()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.bind_ctx)——与`bind()`类似,但返回的时context-manager，在数据库只做暂时改变时有用。

例如，我们将声明两个模型而不指定任何数据库:

```python
class User(Model):
    username = TextField()

class Tweet(Model):
    user = ForeignKeyField(User, backref='tweets')
    content = TextField()
    timestamp = TimestampField()
```

将这两个模型绑定到正在运行的数据:

```python
postgres_db = PostgresqlDatabase('my_app', user='postgres')
sqlite_db = SqliteDatabase('my_app.db')

# At this point, the User and Tweet models are NOT bound to any database.

# Let's bind them to the Postgres database:
postgres_db.bind([User, Tweet])

# Now we will temporarily bind them to the sqlite database:
with sqlite_db.bind_ctx([User, Tweet]):
    # User and Tweet are now bound to the sqlite database.
    assert User._meta.database is sqlite_db

# User and Tweet are once again bound to the Postgres database.
assert User._meta.database is postgres_db
```

给定model时，用[`Model.bind()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.bind) 和 [`Model.bind_ctx()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.bind_ctx)方法：

```python
# Bind the user model to the sqlite db. By default, Peewee will also
# bind any models that are related to User via foreign-key as well.
User.bind(sqlite_db)

assert User._meta.database is sqlite_db
assert Tweet._meta.database is sqlite_db  # Related models bound too.

# Here we will temporarily bind *just* the User model to the postgres db.
with User.bind_ctx(postgres_db, bind_backrefs=False):
    assert User._meta.database is postgres_db
    assert Tweet._meta.database is sqlite_db  # Has not changed.

# And now User is back to being bound to the sqlite_db.
assert User._meta.database is sqlite_db
```



## 线程安全和多数据库

如果您计划在一个多线程应用程序运行时更改数据库，将模型的数据库存储在本地线程可以防止竞争条件(race-conditions)。可以通过自定义模型`Metadata`类来实现:

```python
import threading
from peewee import Metadata

class ThreadSafeDatabaseMetadata(Metadata):
    def __init__(self, *args, **kwargs):
        # database attribute is stored in a thread-local.
        self._local = threading.local()
        super(ThreadSafeDatabaseMetadata, self).__init__(*args, **kwargs)

    def _get_db(self):
        return getattr(self._local, 'database', self._database)
    def _set_db(self, db):
        self._local.database = self._database = db
    database = property(_get_db, _set_db)


class BaseModel(Model):
    class Meta:
        # Instruct peewee to use our thread-safe metadata implementation.
        model_metadata_class = ThreadSafeDatabaseMetadata
```



## 连接管理

要打开到数据库的连接，请使用[`database.connect()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.connect)方法:

```python
>>> db = SqliteDatabase(':memory:')  # In-memory SQLite database.
>>> db.connect()
True
```

对一个已经打开的数据库调用`connect()`会抛出`OperationalError`:

```python
>>> db.connect()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/charles/pypath/peewee.py", line 2390, in connect
    raise OperationalError('Connection already opened.')
peewee.OperationalError: Connection already opened.
```

为了防止引发此异常，可以调用`connect()`，并添加一个参数， `reuse_if_open`:

```python
>>> db.close()  # Close connection.
True
>>> db.connect()
True
>>> db.connect(reuse_if_open=True)
False
```

注意，如果数据库连接已经打开，则对`connect()`的调用将返回` False `。

要关闭连接，请使用[`Database.close()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.close)方法:

```python
>>> db.close()
True
```

在已经关闭的连接上调用`close()`不会导致异常，但会返回`False`:

```python
>>> db.connect()  # Open connection.
True
>>> db.close()  # Close connection.
True
>>> db.close()  # Connection already closed, returns False.
False
```

可以使用[`database .is_closed()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.is_closed)方法测试数据库是否关闭:

```python
>>> db.is_closed()
True
```

### 自动连接

如果数据库是用`autoconnect=True`(默认值)初始化的，那么在使用它之前不需要显式地连接到数据库。显式管理连接被认为是**最佳实践**，因此你可以考虑禁用`autoconnect`行为。

搞清楚连接的存续时期是非常有用。例如，如果连接失败，则在打开连接时捕获异常，而不是在执行查询时捕获异常。此外，如果使用[连接池](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html #池)，调用[`connect ()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.connect)和[`close()`](http://docs.peewee-orm.com/en/latest/peewee/api.html # Database.close)以确保连接正确回收。

为了最好地保证正确性，请禁用`autoconnect`:

```python
db = PostgresqlDatabase('my_app', user='postgres', autoconnect=False)
```

### 线程安全

Peewee使用线程本地存储来跟踪连接状态，使得Peewee [`Database`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database)对象可以安全地与多个线程一起使用。每个线程都有它自己的连接，因此任何给定的线程在给定的时间只打开一个连接。

### 上下文管理器

数据库对象本身可以用作上下文管理器，它在包装的代码块的持续时间内打开连接，进一步说，事务在包装块的开始处打开，执行提交后关闭连接（除非发生错误，在这种情况下事务被回滚）。

```python
>>> db.is_closed()
True
>>> with db:
...     print(db.is_closed())  # db is open inside context manager.
...
False
>>> db.is_closed()  # db is closed.
True
```

如果你想单独管理事务，你可以使用[`Database.connection_context()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.connection_context)上下文管理器。

```python
>>> with db.connection_context():
...     # db connection is open.
...     pass
...
>>> db.is_closed()  # db connection is closed.
True
```

`connection_context()`方法也可以用作装饰器:

```python
@db.connection_context()
def prepare_database():
    # DB connection will be managed by the decorator, which opens
    # a connection, calls function, and closes upon returning.
    db.create_tables(MODELS)  # Create schema.
    load_fixture_data(db)
```

### DB-API 连接对象

要获取对底层DB-API 2.0连接的引用，请使用[`Database.connection()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.connection)方法。这个方法将返回当前打开的连接对象(如果存在的话)，否则它将打开一个新的连接。

```
>>> db.connection()
<sqlite3.Connection object at 0x7f94e9362f10>
```



## Connection Pooling

连接池由[pool module](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#pool)提供，包含在[playhouse](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#playhouse)扩展库中。连接池支持:

- 超时设置，超过此时间连接将被回收。

- 连接数上限设置。

```
from playhouse.pool import PooledPostgresqlExtDatabase

db = PooledPostgresqlExtDatabase(
    'my_database',
    max_connections=8,
    stale_timeout=300,
    user='postgres')

class BaseModel(Model):
    class Meta:
        database = db
```

以下连接池都可以使用:

- [`PooledPostgresqlDatabase`](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#PooledPostgresqlDatabase)
- [`PooledPostgresqlExtDatabase`](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#PooledPostgresqlExtDatabase)
- [`PooledMySQLDatabase`](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#PooledMySQLDatabase)
- [`PooledSqliteDatabase`](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#PooledSqliteDatabase)
- [`PooledSqliteExtDatabase`](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#PooledSqliteExtDatabase)

参考： [Connection pool](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#pool)  或者 [playhouse](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#playhouse) .



## 测试Peewee应用

当为使用Peewee的应用程序编写测试时，使用一个特殊的数据库进行测试可能是可取的。另一个常见的方式是对一个空数据库运行测试，需要确保每个测试开始时表是空的。

要在运行时将模型绑定到数据库，可用以下方法:

- [`database.bind_ctx()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.bind_ctx)，它返回一个上下文管理器，在包装块的持续时间内将给定的模型绑定到数据库实例。
- [`model.bind_ctx()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.bind_ctx)，它同样返回一个上下文管理器，在包装块的持续时间内将模型(及其可选的依赖项)绑定到给定的数据库。
- [`database.bind()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.bind)，这是一个一次性操作，它将模型(及其可选的依赖项)绑定到给定的数据库。
- [`model.bind()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.bind)，这是一个一次性操作，它将模型(及其可选的依赖项)绑定到给定的数据库。

根据您的用例，其中一个选项可能更有意义。对于下面的例子，我将使用[`Model.bind()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.bind)。

测试用例设置示例:

```python
# tests.py
import unittest
from my_app.models import EventLog, Relationship, Tweet, User

MODELS = [User, Tweet, EventLog, Relationship]

# use an in-memory SQLite for tests.
test_db = SqliteDatabase(':memory:')

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        test_db.connect()
        test_db.create_tables(MODELS)

    def tearDown(self):
        # Not strictly necessary since SQLite in-memory databases only live
        # for the duration of the connection, and in the next step we close
        # the connection...but a good practice all the same.
        test_db.drop_tables(MODELS)

        # Close connection to db.
        test_db.close()

        # If we wanted, we could re-bind the models to their original
        # database here. But for tests this is probably not necessary.
```

另外，从经验来看，我建议使用与生产中使用的相同的数据库后端来测试应用程序，以避免任何潜在的兼容性问题。

如果您想了解更多如何使用Peewee运行测试的示例，请查看Peewee自己的[测试套件](https://github.com/coleifer/peewee/tree/master/tests)。



## 框架集成

对于web应用程序，通常是在收到请求时打开连接，在传递响应时关闭连接。在这一节中，我将描述如何向web应用程序添加钩子，以确保数据库连接得到正确处理.

这些步骤将确保无论您使用的是简单的SQLite数据库，还是多个Postgres连接池，peewee都将正确处理连接。

⚠️注意

接收大量流量的应用程序可能受益于使用[连接池](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#pool)，以减少针对每个请求建立和断开连接的成本。

### Flask

Flask和peewee是一个很好的组合，并且是任何规模的项目的首选。Flask提供了两个挂钩，我们将使用它们来打开和关闭我们的db连接。我们将在收到请求时打开连接，然后在返回响应时关闭连接。

```python
from flask import Flask
from peewee import *

database = SqliteDatabase('my_app.db')
app = Flask(__name__)

# This hook ensures that a connection is opened to handle any queries
# generated by the request.
@app.before_request
def _db_connect():
    database.connect()

# This hook ensures that the connection is closed when we've finished
# processing the request.
@app.teardown_request
def _db_close(exc):
    if not database.is_closed():
        database.close()
```



## 执行查询

SQL查询通常通过在使用查询生成器api构造的查询上调用`execute()`来执行(或者在[`Select`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select)查询的情况下简单地遍历查询对象)。对于希望直接执行SQL的情况，可以使用[`Database.execute_sql()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.execute_sql)方法。

```python
db = SqliteDatabase('my_app.db')
db.connect()

# Example of executing a simple query and ignoring the results.
db.execute_sql("ATTACH DATABASE ':memory:' AS cache;")

# Example of iterating over the results of a query using the cursor.
cursor = db.execute_sql('SELECT * FROM users WHERE status = ?', (ACTIVE,))
for row in cursor.fetchall():
    # Do something with row, which is a tuple containing column data.
    pass
```



## 管理事务

Peewee提供了几个处理事务的接口。最常用的是[`Database.atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic)方法，它也支持嵌套事务。[`atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic)块将在事务或savepoint中运行，这取决于嵌套的级别。

如果在包装的块中发生异常，则当前事务/保存点将回滚。否则，语句将在被包装的块的末尾被提交。

⚠️注意

在由[`atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic)上下文管理器封装的块中，您可以通过调用`Transaction.rollback()`或`Transaction.commit()`在任何点显式地回滚或提交。当您在封装的代码块中执行此操作时，一个新的事务将自动启动。

```python
with db.atomic() as transaction:  # Opens new transaction.
    try:
        save_some_objects()
    except ErrorSavingData:
        # Because this block of code is wrapped with "atomic", a
        # new transaction will begin automatically after the call
        # to rollback().
        transaction.rollback()
        error_saving = True

    create_report(error_saving=error_saving)
    # Note: no need to call commit. Since this marks the end of the
    # wrapped block of code, the `atomic` context manager will
    # automatically call commit for us.
```

⚠️注意

[`atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic)可以用作**上下文管理器**或**装饰器**。

### 上下文管理器用法

```python
db = SqliteDatabase(':memory:')

with db.atomic() as txn:
    # This is the outer-most level, so this block corresponds to
    # a transaction.
    User.create(username='charlie')

    with db.atomic() as nested_txn:
        # This block corresponds to a savepoint.
        User.create(username='huey')

        # This will roll back the above create() query.
        nested_txn.rollback()

    User.create(username='mickey')

# When the block ends, the transaction is committed (assuming no error
# occurs). At that point there will be two users, "charlie" and "mickey".
```

你也可以使用`atomic`方法来执行*get或create*操作:

```python
try:
    with db.atomic():
        user = User.create(username=username)
    return 'Success'
except peewee.IntegrityError:
    return 'Failure: %s is already in use.' % username
```

### 装饰器用法

```python
@db.atomic()
def create_user(username):
    # This statement will run in a transaction. If the caller is already
    # running in an `atomic` block, then a savepoint will be used instead.
    return User.create(username=username)

create_user('charlie')
```

### 嵌套事务

[`atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic)提供了透明的事务嵌套。当使用[`atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic)时，最外层的调用将被包装在一个事务中，任何嵌套调用都将使用保存点。

```python
with db.atomic() as txn:
    perform_operation()

    with db.atomic() as nested_txn:
        perform_another_operation()
```

Peewee通过使用保存点支持嵌套事务(有关更多信息，请参见[`savepoint()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.savepoint))。

### 显式事务

如果希望显式地在事务中运行代码，可以使用[`transaction()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.transaction)。像[`atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic)一样，[`transaction()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.transaction)可以用作上下文管理器或装饰器。

如果在包装的块中发生异常，则事务将回滚。否则，语句将在被包装的块的末尾被提交。

```python
db = SqliteDatabase(':memory:')

with db.transaction() as txn:
    # Delete the user and their associated tweets.
    user.delete_instance(recursive=True)
```

Transactions can be explicitly committed or rolled-back within the wrapped block. When this happens, a new transaction will be started.

```python
with db.transaction() as txn:
    User.create(username='mickey')
    txn.commit()  # Changes are saved and a new transaction begins.
    User.create(username='huey')

    # Roll back. "huey" will not be saved, but since "mickey" was already
    # committed, that row will remain in the database.
    txn.rollback()

with db.transaction() as txn:
    User.create(username='whiskers')
    # Roll back changes, which removes "whiskers".
    txn.rollback()

    # Create a new row for "mr. whiskers" which will be implicitly committed
    # at the end of the `with` block.
    User.create(username='mr. whiskers')
```

⚠️注意

如果您试图使用[`transaction()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.transaction)上下文管理器将事务嵌套到peewee中，则只会使用最外层的事务。但是，如果在嵌套块中发生异常，这可能会导致不可预知的行为，因此强烈建议您使用[`atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic)。

### 显式保存点

正如您可以显式地创建事务一样，您也可以使用[`savepoint()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.savepoint)方法显式地创建保存点。保存点必须发生在事务中，但可以嵌套任意深度。

```python
with db.transaction() as txn:
    with db.savepoint() as sp:
        User.create(username='mickey')

    with db.savepoint() as sp2:
        User.create(username='zaizee')
        sp2.rollback()  # "zaizee" will not be saved, but "mickey" will be.
```

⛔️警告

如果您手动提交或回滚一个保存点，将**不会**自动创建一个新的保存点。这与`事务`的行为不同，后者会在手动提交/回滚后自动打开一个新事务。

### Autocommit模式

默认情况下，Peewee以*autocommit模式*运行，这样任何在事务之外执行的语句都运行在它们自己的事务中。为了将多个语句分组到一个事务中，Peewee提供了[`atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic)上下文管理器/装饰器。这应该涵盖所有用例，但在不太可能的情况下，您想要暂时完全禁用Peewee的事务管理，您可以使用[`Database.manual_commit()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.manual_commit)上下文管理器/装饰器。

下面是如何模拟[`transaction()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.transaction)上下文管理器的行为:

```python
with db.manual_commit():
    db.begin()  # Have to begin transaction explicitly.
    try:
        user.delete_instance(recursive=True)
    except:
        db.rollback()  # Rollback! An error occurred.
        raise
    else:
        try:
            db.commit()  # Commit changes.
        except:
            db.rollback()
            raise
```

再说一遍，Peewee作者不认为有人会需要这个，但它只是以防万一。人家叫我们不用，我就不用呗。

## 数据库错误类型

Python DB-API 2.0规范描述了[几种类型的异常](https://www.python.org/dev/peps/pep-0249/#exceptions)。因为大多数数据库驱动程序都有它们自己的这些异常实现，所以Peewee通过提供它自己的包装器来简化这些事情，这些包装器围绕着任何特定于实现的异常类。这样，你不需要担心导入任何特殊的异常类，你可以使用来自peewee的异常类:

- `DatabaseError`
- `DataError`
- `IntegrityError`
- `InterfaceError`
- `InternalError`
- `NotSupportedError`
- `OperationalError`
- `ProgrammingError`

⚠️注意

所有这些错误类都扩展了“PeeweeException”。

## 日志查询

使用标准库的“logging”模块，所有查询都被记录到*peewee*命名空间。查询使用*DEBUG*级别记录。如果您对使用查询做一些事情感兴趣，您可以简单地注册一个处理程序。

```python
# Print all queries to stderr.
import logging
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
```

## 添加一个新的数据库驱动程序

Peewee内置支持Postgres、MySQL和SQLite。这些数据库非常流行，从快速的嵌入式数据库到适合大规模部署的重量级服务器。也就是说，有很多很酷的数据库，如果驱动程序支持[DB-API 2.0规范](http://www.python.org/dev/peps/pep-0249/)，那么添加对所选数据库的支持应该非常容易。

如果您使用过标准库sqlite3驱动程序、psycopg2或类似的程序，那么您应该熟悉DB-API 2.0规范。目前，Peewee只依赖于几个部分:

- Connection.commit
- Connection.execute
- Connection.rollback
- Cursor.description
- Cursor.fetchone

这些方法通常被封装在更高级别的抽象中，并由[`Database`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database)公开，所以即使你的驱动程序不完全这样做，你仍然可以从peewee得到很多里程。`playhouse`模块中的[apsw sqlite驱动程序](http://code.google.com/p/apsw/)就是一个例子。

第一件事是提供[`Database`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database)的一个子类来打开一个连接。

```python
from peewee import Database
import foodb  # Our fictional DB-API 2.0 driver.


class FooDatabase(Database):
    def _connect(self, database, **kwargs):
        return foodb.connect(database, **kwargs)
```

[`Database`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database)提供了更高级别的API，负责执行查询、创建表和索引，以及内省数据库以获取表列表。上面的实现绝对是最不需要的，但是有些特性将不起作用——为了获得最好的结果，您需要另外添加一个方法，用于从数据库中提取表的列表和表的索引。我们假设`FooDB`很像MySQL，并且有特殊的" SHOW "语句:

```python
class FooDatabase(Database):
    def _connect(self, database, **kwargs):
        return foodb.connect(database, **kwargs)

    def get_tables(self):
        res = self.execute('SHOW TABLES;')
        return [r[0] for r in res.fetchall()]
```

这里没有涉及到数据库处理的其他事项包括:

- [`last_insert_id()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.last_insert_id)和[`rows_affected()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.rows_affected)
- `param `和`quote`，它们告诉sql生成代码如何添加参数占位符和引用实体名称。
- `field_types`用于将数据类型(如INT或TEXT)映射到它们特定供应商的类型名。
- `operations`用于映射操作，如“LIKE/ILIKE”到它们的数据库等价

请参阅[' Database '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database) API参考或[源代码](https://github.com/coleifer/peewee/blob/master/peewee.py)。获取详细信息。

⚠️注意

如果你的驱动程序符合DB-API 2.0规范，那么启动和运行应该不需要做太多的工作。

我们的新数据库可以像其他任何数据库子类一样使用:

```python
from peewee import *
from foodb_ext import FooDatabase

db = FooDatabase('my_database', user='foo', password='secret')

class BaseModel(Model):
    class Meta:
        database = db

class Blog(BaseModel):
    title = CharField()
    contents = TextField()
    pub_date = DateTimeField()
```

