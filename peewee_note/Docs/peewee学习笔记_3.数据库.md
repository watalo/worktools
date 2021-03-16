# Database模块

因为我暂时只用SQlite，所以其他数据库的我就不翻译了。

Peewee [ Database ](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database)对象表示到数据库的连接。[' Database '](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database)类被实例化，包含了打开数据库连接所需的所有信息，然后可以用于:

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

用[' SqliteDatabase() '](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase)连接SQLite数据库，第一个参数是数据库的文件名（或者路径），或者字符串`:memory:`可以创建内存中的数据库。在数据库文件名之后，可以指定一个列表或pragmas或任何其他任意[sqlite3参数](https://docs.python.org/2/library/sqlite3.html#sqlite3.connect)。

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

动态配置`PRAGMAs`可以使用[`pragma()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase.pragma)方法或['SqliteDatabase'](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase)对象的特殊属性:

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

- 函数 —接受任意数量的参数并返回单个值。
- Aggregate(聚合) —从多行聚合参数并返回单个值。
- Collations() —描述如何对某个值排序。

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

有时数据库连接设置直到运行时才知道，而运行时这些值可能从配置文件或环境加载。在这些情况下，您可以通过指定' None '作为database_name来*延迟*数据库的初始化。

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

如果您计划在一个多线程应用程序运行时更改数据库，将模型的数据库存储在本地线程可以防止竞争条件(race-conditions)。可以通过自定义模型' Metadata '类来实现:

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

要打开到数据库的连接，请使用[`database .connect()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.connect)方法:

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

为了防止引发此异常，可以调用'`connect()`，并添加一个参数， `reuse_if_open`:

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

```
>>> db.is_closed()
True
```

### 自动连接

It is not necessary to explicitly connect to the database before using it if the database is initialized with `autoconnect=True` (the default). Managing connections explicitly is considered a **best practice**, therefore you may consider disabling the `autoconnect` behavior.

It is very helpful to be explicit about your connection lifetimes. If the connection fails, for instance, the exception will be caught when the connection is being opened, rather than some arbitrary time later when a query is executed. Furthermore, if using a [connection pool](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#pool), it is necessary to call [`connect()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.connect) and [`close()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.close) to ensure connections are recycled properly.

For the best guarantee of correctness, disable `autoconnect`:

如果数据库是用`autoconnect=True`(默认值)初始化的，那么在使用它之前不需要显式地连接到数据库。显式管理连接被认为是**最佳实践**，因此你可以考虑禁用' autoconnect '行为。

搞清楚连接的存续时期是非常有用。例如，如果连接失败，则在打开连接时捕获异常，而不是在执行查询时捕获异常。此外，如果使用[连接池](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html #池)，[`connect ()`] (http://docs.peewee-orm.com/en/latest/peewee/api.html Database.connect)和(“关闭()”)(http://docs.peewee-orm.com/en/latest/peewee/api.html # Database.close),以确保连接正确回收。

为了最好地保证正确性，请禁用' autoconnect ':





```
db = PostgresqlDatabase('my_app', user='postgres', autoconnect=False)
```

### Thread Safety

Peewee keeps track of the connection state using thread-local storage, making the Peewee [`Database`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database) object safe to use with multiple threads. Each thread will have it’s own connection, and as a result any given thread will only have a single connection open at a given time.

### Context managers

The database object itself can be used as a context-manager, which opens a connection for the duration of the wrapped block of code. Additionally, a transaction is opened at the start of the wrapped block and committed before the connection is closed (unless an error occurs, in which case the transaction is rolled back).

```
>>> db.is_closed()
True
>>> with db:
...     print(db.is_closed())  # db is open inside context manager.
...
False
>>> db.is_closed()  # db is closed.
True
```

If you want to manage transactions separately, you can use the [`Database.connection_context()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.connection_context) context manager.

```
>>> with db.connection_context():
...     # db connection is open.
...     pass
...
>>> db.is_closed()  # db connection is closed.
True
```

The `connection_context()` method can also be used as a decorator:

```
@db.connection_context()
def prepare_database():
    # DB connection will be managed by the decorator, which opens
    # a connection, calls function, and closes upon returning.
    db.create_tables(MODELS)  # Create schema.
    load_fixture_data(db)
```

### DB-API Connection Object

To obtain a reference to the underlying DB-API 2.0 connection, use the [`Database.connection()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.connection) method. This method will return the currently-open connection object, if one exists, otherwise it will open a new connection.

```
>>> db.connection()
<sqlite3.Connection object at 0x7f94e9362f10>
```



## Connection Pooling

Connection pooling is provided by the [pool module](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#pool), included in the [playhouse](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#playhouse) extensions library. The pool supports:

- Timeout after which connections will be recycled.
- Upper bound on the number of open connections.

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

The following pooled database classes are available:

- [`PooledPostgresqlDatabase`](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#PooledPostgresqlDatabase)
- [`PooledPostgresqlExtDatabase`](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#PooledPostgresqlExtDatabase)
- [`PooledMySQLDatabase`](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#PooledMySQLDatabase)
- [`PooledSqliteDatabase`](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#PooledSqliteDatabase)
- [`PooledSqliteExtDatabase`](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#PooledSqliteExtDatabase)

For an in-depth discussion of peewee’s connection pool, see the [Connection pool](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#pool) section of the [playhouse](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#playhouse) documentation.



## Testing Peewee Applications

When writing tests for an application that uses Peewee, it may be desirable to use a special database for tests. Another common practice is to run tests against a clean database, which means ensuring tables are empty at the start of each test.

To bind your models to a database at run-time, you can use the following methods:

- [`Database.bind_ctx()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.bind_ctx), which returns a context-manager that will bind the given models to the database instance for the duration of the wrapped block.
- [`Model.bind_ctx()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.bind_ctx), which likewise returns a context-manager that binds the model (and optionally its dependencies) to the given database for the duration of the wrapped block.
- [`Database.bind()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.bind), which is a one-time operation that binds the models (and optionally its dependencies) to the given database.
- [`Model.bind()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.bind), which is a one-time operation that binds the model (and optionally its dependencies) to the given database.

Depending on your use-case, one of these options may make more sense. For the examples below, I will use [`Model.bind()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.bind).

Example test-case setup:

```
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

As an aside, and speaking from experience, I recommend testing your application using the same database backend you use in production, so as to avoid any potential compatibility issues.

If you’d like to see some more examples of how to run tests using Peewee, check out Peewee’s own [test-suite](https://github.com/coleifer/peewee/tree/master/tests).

## Async with Gevent

[gevent](http://www.gevent.org/) is recommended for doing asynchronous I/O with Postgresql or MySQL. Reasons I prefer gevent:

- No need for special-purpose “loop-aware” re-implementations of *everything*. Third-party libraries using asyncio usually have to re-implement layers and layers of code as well as re-implementing the protocols themselves.
- Gevent allows you to write your application in normal, clean, idiomatic Python. No need to litter every line with “async”, “await” and other noise. No callbacks, futures, tasks, promises. No cruft.
- Gevent works with both Python 2 *and* Python 3.
- Gevent is *Pythonic*. Asyncio is an un-pythonic abomination.

Besides monkey-patching socket, no special steps are required if you are using **MySQL** with a pure Python driver like [pymysql](https://github.com/PyMySQL/PyMySQL) or are using [mysql-connector](https://dev.mysql.com/doc/connector-python/en/) in pure-python mode. MySQL drivers written in C will require special configuration which is beyond the scope of this document.

For **Postgres** and [psycopg2](http://initd.org/psycopg), which is a C extension, you can use the following code snippet to register event hooks that will make your connection async:

```
from gevent.socket import wait_read, wait_write
from psycopg2 import extensions

# Call this function after monkey-patching socket (etc).
def patch_psycopg2():
    extensions.set_wait_callback(_psycopg2_gevent_callback)

def _psycopg2_gevent_callback(conn, timeout=None):
    while True:
        state = conn.poll()
        if state == extensions.POLL_OK:
            break
        elif state == extensions.POLL_READ:
            wait_read(conn.fileno(), timeout=timeout)
        elif state == extensions.POLL_WRITE:
            wait_write(conn.fileno(), timeout=timeout)
        else:
            raise ValueError('poll() returned unexpected result')
```

**SQLite**, because it is embedded in the Python application itself, does not do any socket operations that would be a candidate for non-blocking. Async has no effect one way or the other on SQLite databases.



## Framework Integration

For web applications, it is common to open a connection when a request is received, and to close the connection when the response is delivered. In this section I will describe how to add hooks to your web app to ensure the database connection is handled properly.

These steps will ensure that regardless of whether you’re using a simple SQLite database, or a pool of multiple Postgres connections, peewee will handle the connections correctly.

Note

Applications that receive lots of traffic may benefit from using a [connection pool](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#pool) to mitigate the cost of setting up and tearing down connections on every request.

### Flask

Flask and peewee are a great combo and my go-to for projects of any size. Flask provides two hooks which we will use to open and close our db connection. We’ll open the connection when a request is received, then close it when the response is returned.

```
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

### Django

While it’s less common to see peewee used with Django, it is actually very easy to use the two. To manage your peewee database connections with Django, the easiest way in my opinion is to add a middleware to your app. The middleware should be the very first in the list of middlewares, to ensure it runs first when a request is handled, and last when the response is returned.

If you have a django project named *my_blog* and your peewee database is defined in the module `my_blog.db`, you might add the following middleware class:

```
# middleware.py
from my_blog.db import database  # Import the peewee database instance.


def PeeweeConnectionMiddleware(get_response):
    def middleware(request):
        database.connect()
        try:
            response = get_response(request)
        finally:
            if not database.is_closed():
                database.close()
        return response
    return middleware


# Older Django < 1.10 middleware.
class PeeweeConnectionMiddleware(object):
    def process_request(self, request):
        database.connect()

    def process_response(self, request, response):
        if not database.is_closed():
            database.close()
        return response
```

To ensure this middleware gets executed, add it to your `settings` module:

```
# settings.py
MIDDLEWARE_CLASSES = (
    # Our custom middleware appears first in the list.
    'my_blog.middleware.PeeweeConnectionMiddleware',

    # These are the default Django 1.7 middlewares. Yours may differ,
    # but the important this is that our Peewee middleware comes first.
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

# ... other Django settings ...
```

### Bottle

I haven’t used bottle myself, but looking at the documentation I believe the following code should ensure the database connections are properly managed:

```
# app.py
from bottle import hook  #, route, etc, etc.
from peewee import *

db = SqliteDatabase('my-bottle-app.db')

@hook('before_request')
def _connect_db():
    db.connect()

@hook('after_request')
def _close_db():
    if not db.is_closed():
        db.close()

# Rest of your bottle app goes here.
```

### Web.py

See the documentation for [application processors](http://webpy.org/cookbook/application_processors).

```
db = SqliteDatabase('my_webpy_app.db')

def connection_processor(handler):
    db.connect()
    try:
        return handler()
    finally:
        if not db.is_closed():
            db.close()

app.add_processor(connection_processor)
```

### Tornado

It looks like Tornado’s `RequestHandler` class implements two hooks which can be used to open and close connections when a request is handled.

```
from tornado.web import RequestHandler

db = SqliteDatabase('my_db.db')

class PeeweeRequestHandler(RequestHandler):
    def prepare(self):
        db.connect()
        return super(PeeweeRequestHandler, self).prepare()

    def on_finish(self):
        if not db.is_closed():
            db.close()
        return super(PeeweeRequestHandler, self).on_finish()
```

In your app, instead of extending the default `RequestHandler`, now you can extend `PeeweeRequestHandler`.

Note that this does not address how to use peewee asynchronously with Tornado or another event loop.

### Wheezy.web

The connection handling code can be placed in a [middleware](https://pythonhosted.org/wheezy.http/userguide.html#middleware).

```
def peewee_middleware(request, following):
    db.connect()
    try:
        response = following(request)
    finally:
        if not db.is_closed():
            db.close()
    return response

app = WSGIApplication(middleware=[
    lambda x: peewee_middleware,
    # ... other middlewares ...
])
```

Thanks to GitHub user *@tuukkamustonen* for submitting this code.

### Falcon

The connection handling code can be placed in a [middleware component](https://falcon.readthedocs.io/en/stable/api/middleware.html).

```
import falcon
from peewee import *

database = SqliteDatabase('my_app.db')

class PeeweeConnectionMiddleware(object):
    def process_request(self, req, resp):
        database.connect()

    def process_response(self, req, resp, resource, req_succeeded):
        if not database.is_closed():
            database.close()

application = falcon.API(middleware=[
    PeeweeConnectionMiddleware(),
    # ... other middlewares ...
])
```

### Pyramid

Set up a Request factory that handles database connection lifetime as follows:

```
from pyramid.request import Request

db = SqliteDatabase('pyramidapp.db')

class MyRequest(Request):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db.connect()
        self.add_finished_callback(self.finish)

    def finish(self, request):
        if not db.is_closed():
            db.close()
```

In your application main() make sure MyRequest is used as request_factory:

```
def main(global_settings, **settings):
    config = Configurator(settings=settings, ...)
    config.set_request_factory(MyRequest)
```

### CherryPy

See [Publish/Subscribe pattern](http://docs.cherrypy.org/en/latest/extend.html#publish-subscribe-pattern).

```
def _db_connect():
    db.connect()

def _db_close():
    if not db.is_closed():
        db.close()

cherrypy.engine.subscribe('before_request', _db_connect)
cherrypy.engine.subscribe('after_request', _db_close)
```

### Sanic

In Sanic, the connection handling code can be placed in the request and response middleware [sanic middleware](http://sanic.readthedocs.io/en/latest/sanic/middleware.html).

```
# app.py
@app.middleware('request')
async def handle_request(request):
    db.connect()

@app.middleware('response')
async def handle_response(request, response):
    if not db.is_closed():
        db.close()
```

### FastAPI

Similar to Flask, FastAPI provides two event based hooks which we will use to open and close our db connection. We’ll open the connection when a request is received, then close it when the response is returned.

```
from fastapi import FastAPI
from peewee import *

db = SqliteDatabase('my_app.db')
app = FastAPI()

# This hook ensures that a connection is opened to handle any queries
# generated by the request.
@app.on_event("startup")
def startup():
    db.connect()


# This hook ensures that the connection is closed when we've finished
# processing the request.
@app.on_event("shutdown")
def shutdown():
    if not db.is_closed():
        db.close()
```

### Other frameworks

Don’t see your framework here? Please [open a GitHub ticket](https://github.com/coleifer/peewee/issues/new) and I’ll see about adding a section, or better yet, submit a documentation pull-request.

## Executing Queries

SQL queries will typically be executed by calling `execute()` on a query constructed using the query-builder APIs (or by simply iterating over a query object in the case of a [`Select`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select) query). For cases where you wish to execute SQL directly, you can use the [`Database.execute_sql()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.execute_sql) method.

```
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



## Managing Transactions

Peewee provides several interfaces for working with transactions. The most general is the [`Database.atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic) method, which also supports nested transactions. [`atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic) blocks will be run in a transaction or savepoint, depending on the level of nesting.

If an exception occurs in a wrapped block, the current transaction/savepoint will be rolled back. Otherwise the statements will be committed at the end of the wrapped block.

Note

While inside a block wrapped by the [`atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic) context manager, you can explicitly rollback or commit at any point by calling `Transaction.rollback()` or `Transaction.commit()`. When you do this inside a wrapped block of code, a new transaction will be started automatically.

```
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

Note

[`atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic) can be used as either a **context manager** or a **decorator**.

### Context manager

Using `atomic` as context manager:

```
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

You can use the `atomic` method to perform *get or create* operations as well:

```
try:
    with db.atomic():
        user = User.create(username=username)
    return 'Success'
except peewee.IntegrityError:
    return 'Failure: %s is already in use.' % username
```

### Decorator

Using `atomic` as a decorator:

```
@db.atomic()
def create_user(username):
    # This statement will run in a transaction. If the caller is already
    # running in an `atomic` block, then a savepoint will be used instead.
    return User.create(username=username)

create_user('charlie')
```

### Nesting Transactions

[`atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic) provides transparent nesting of transactions. When using [`atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic), the outer-most call will be wrapped in a transaction, and any nested calls will use savepoints.

```
with db.atomic() as txn:
    perform_operation()

    with db.atomic() as nested_txn:
        perform_another_operation()
```

Peewee supports nested transactions through the use of savepoints (for more information, see [`savepoint()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.savepoint)).

### Explicit transaction

If you wish to explicitly run code in a transaction, you can use [`transaction()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.transaction). Like [`atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic), [`transaction()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.transaction) can be used as a context manager or as a decorator.

If an exception occurs in a wrapped block, the transaction will be rolled back. Otherwise the statements will be committed at the end of the wrapped block.

```
db = SqliteDatabase(':memory:')

with db.transaction() as txn:
    # Delete the user and their associated tweets.
    user.delete_instance(recursive=True)
```

Transactions can be explicitly committed or rolled-back within the wrapped block. When this happens, a new transaction will be started.

```
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

Note

If you attempt to nest transactions with peewee using the [`transaction()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.transaction) context manager, only the outer-most transaction will be used. However if an exception occurs in a nested block, this can lead to unpredictable behavior, so it is strongly recommended that you use [`atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic).

### Explicit Savepoints

Just as you can explicitly create transactions, you can also explicitly create savepoints using the [`savepoint()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.savepoint) method. Savepoints must occur within a transaction, but can be nested arbitrarily deep.

```
with db.transaction() as txn:
    with db.savepoint() as sp:
        User.create(username='mickey')

    with db.savepoint() as sp2:
        User.create(username='zaizee')
        sp2.rollback()  # "zaizee" will not be saved, but "mickey" will be.
```

Warning

If you manually commit or roll back a savepoint, a new savepoint **will not** automatically be created. This differs from the behavior of `transaction`, which will automatically open a new transaction after manual commit/rollback.

### Autocommit Mode

By default, Peewee operates in *autocommit mode*, such that any statements executed outside of a transaction are run in their own transaction. To group multiple statements into a transaction, Peewee provides the [`atomic()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.atomic) context-manager/decorator. This should cover all use-cases, but in the unlikely event you want to temporarily disable Peewee’s transaction management completely, you can use the [`Database.manual_commit()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.manual_commit) context-manager/decorator.

Here is how you might emulate the behavior of the [`transaction()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.transaction) context manager:

```
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

Again – I don’t anticipate anyone needing this, but it’s here just in case.



## Database Errors

The Python DB-API 2.0 spec describes [several types of exceptions](https://www.python.org/dev/peps/pep-0249/#exceptions). Because most database drivers have their own implementations of these exceptions, Peewee simplifies things by providing its own wrappers around any implementation-specific exception classes. That way, you don’t need to worry about importing any special exception classes, you can just use the ones from peewee:

- `DatabaseError`
- `DataError`
- `IntegrityError`
- `InterfaceError`
- `InternalError`
- `NotSupportedError`
- `OperationalError`
- `ProgrammingError`

Note

All of these error classes extend `PeeweeException`.

## Logging queries

All queries are logged to the *peewee* namespace using the standard library `logging` module. Queries are logged using the *DEBUG* level. If you’re interested in doing something with the queries, you can simply register a handler.

```
# Print all queries to stderr.
import logging
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
```

## Adding a new Database Driver

Peewee comes with built-in support for Postgres, MySQL and SQLite. These databases are very popular and run the gamut from fast, embeddable databases to heavyweight servers suitable for large-scale deployments. That being said, there are a ton of cool databases out there and adding support for your database-of-choice should be really easy, provided the driver supports the [DB-API 2.0 spec](http://www.python.org/dev/peps/pep-0249/).

The DB-API 2.0 spec should be familiar to you if you’ve used the standard library sqlite3 driver, psycopg2 or the like. Peewee currently relies on a handful of parts:

- Connection.commit
- Connection.execute
- Connection.rollback
- Cursor.description
- Cursor.fetchone

These methods are generally wrapped up in higher-level abstractions and exposed by the [`Database`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database), so even if your driver doesn’t do these exactly you can still get a lot of mileage out of peewee. An example is the [apsw sqlite driver](http://code.google.com/p/apsw/) in the “playhouse” module.

The first thing is to provide a subclass of [`Database`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database) that will open a connection.

```
from peewee import Database
import foodb  # Our fictional DB-API 2.0 driver.


class FooDatabase(Database):
    def _connect(self, database, **kwargs):
        return foodb.connect(database, **kwargs)
```

The [`Database`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database) provides a higher-level API and is responsible for executing queries, creating tables and indexes, and introspecting the database to get lists of tables. The above implementation is the absolute minimum needed, though some features will not work – for best results you will want to additionally add a method for extracting a list of tables and indexes for a table from the database. We’ll pretend that `FooDB` is a lot like MySQL and has special “SHOW” statements:

```
class FooDatabase(Database):
    def _connect(self, database, **kwargs):
        return foodb.connect(database, **kwargs)

    def get_tables(self):
        res = self.execute('SHOW TABLES;')
        return [r[0] for r in res.fetchall()]
```

Other things the database handles that are not covered here include:

- [`last_insert_id()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.last_insert_id) and [`rows_affected()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.rows_affected)
- `param` and `quote`, which tell the SQL-generating code how to add parameter placeholders and quote entity names.
- `field_types` for mapping data-types like INT or TEXT to their vendor-specific type names.
- `operations` for mapping operations such as “LIKE/ILIKE” to their database equivalent

Refer to the [`Database`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database) API reference or the [source code](https://github.com/coleifer/peewee/blob/master/peewee.py). for details.

Note

If your driver conforms to the DB-API 2.0 spec, there shouldn’t be much work needed to get up and running.

Our new database can be used just like any of the other database subclasses:

```
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

[Next ](http://docs.peewee-orm.com/en/latest/peewee/models.html)[ Previous](http://docs.peewee-orm.com/en/latest/peewee/contributing.html)