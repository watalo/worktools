# Query operators 查询操作符

The following types of comparisons are supported by peewee:

peewee支持以下类型的比较:

| Comparison | Meaning                                 |
| ---------- | --------------------------------------- |
| `==`       | x equals y                              |
| `<`        | x is less than y                        |
| `<=`       | x is less than or equal to y            |
| `>`        | x is greater than y                     |
| `>=`       | x is greater than or equal to y         |
| `!=`       | x is not equal to y                     |
| `<<`       | x IN y, where y is a list or query      |
| `>>`       | x IS y, where y is None/NULL            |
| `%`        | x LIKE y where y may contain wildcards  |
| `**`       | x ILIKE y where y may contain wildcards |
| `^`        | x XOR y                                 |
| `~`        | Unary negation (e.g., NOT x)            |

Because I ran out of operators to override, there are some additional query operations available as methods:

因为我没有操作符可以覆盖，所以有一些额外的查询操作可以作为方法:

| Method                | Meaning                                         |
| --------------------- | ----------------------------------------------- |
| `.in_(value)`         | IN lookup (identical to `<<`).                  |
| `.not_in(value)`      | NOT IN lookup.                                  |
| `.is_null(is_null)`   | IS NULL or IS NOT NULL. Accepts boolean param.  |
| `.contains(substr)`   | Wild-card search for substring.                 |
| `.startswith(prefix)` | Search for values beginning with `prefix`.      |
| `.endswith(suffix)`   | Search for values ending with `suffix`.         |
| `.between(low, high)` | Search for values between `low` and `high`.     |
| `.regexp(exp)`        | Regular expression match (case-sensitive).      |
| `.iregexp(exp)`       | Regular expression match (case-insensitive).    |
| `.bin_and(value)`     | Binary AND.                                     |
| `.bin_or(value)`      | Binary OR.                                      |
| `.concat(other)`      | Concatenate two strings or objects using `||`.  |
| `.distinct()`         | Mark column for DISTINCT selection.             |
| `.collate(collation)` | Specify column with the given collation.        |
| `.cast(type)`         | Cast the value of the column to the given type. |

To combine clauses using logical operators, use:

要使用逻辑运算符组合子句，请使用:

| Operator   | Meaning              | Example                                              |
| ---------- | -------------------- | ---------------------------------------------------- |
| `&`        | AND                  | `(User.is_active == True) & (User.is_admin == True)` |
| `|` (pipe) | OR                   | `(User.is_admin) | (User.is_superuser)`              |
| `~`        | NOT (unary negation) | `~(User.username.contains('admin'))`                 |

Here is how you might use some of these query operators:

以下是如何使用这些查询操作符:

```python
# Find the user whose username is "charlie".
User.select().where(User.username == `charlie`)

# Find the users whose username is in [charlie, huey, mickey]
User.select().where(User.username.in_([`charlie`, `huey`, `mickey`]))

Employee.select().where(Employee.salary.between(50000, 60000))

Employee.select().where(Employee.name.startswith(`C`))

Blog.select().where(Blog.title.contains(search_string))
```

Here is how you might combine expressions. Comparisons can be arbitrarily complex.

Note

Note that the actual comparisons are wrapped in parentheses. Python’s operator precedence necessitates that comparisons be wrapped in parentheses.

下面是如何组合表达式。比较可以是任意复杂的。

请注意

注意，实际的比较是用括号括起来的。Python的操作符优先级要求比较必须用圆括号括起来。

```python
# Find any users who are active administrations.
User.select().where(
  (User.is_admin == True) &
  (User.is_active == True))

# Find any users who are either administrators or super-users.
User.select().where(
  (User.is_admin == True) |
  (User.is_superuser == True))

# Find any Tweets by users who are not admins (NOT IN).
admins = User.select().where(User.is_admin == True)
non_admin_tweets = Tweet.select().where(Tweet.user.not_in(admins))

# Find any users who are not my friends (strangers).
friends = User.select().where(User.username.in_([`charlie`, `huey`, `mickey`]))
strangers = User.select().where(User.id.not_in(friends))
```

Warning

Although you may be tempted to use python’s `in`, `and`, `or` and `not` operators in your query expressions, these **will not work.** The return value of an `in` expression is always coerced to a boolean value. Similarly, `and`, `or` and `not` all treat their arguments as boolean values and cannot be overloaded.

So just remember:

- Use `.in_()` and `.not_in()` instead of `in` and `not in`
- Use `&` instead of `and`
- Use `|` instead of `or`
- Use `~` instead of `not`
- Use `.is_null()` instead of `is None` or `== None`.
- **Don’t forget to wrap your comparisons in parentheses when using logical operators.**

For more examples, see the [Expressions](http://docs.peewee-orm.com/en/latest/peewee/query_operators.html#expressions) section.

警告

尽管你可能想在你的查询表达式中使用python的` in `， ` and `， ` or ` and ` not `操作符，但这些**不起作用。** ` in `表达式的返回值总是强制转换为布尔值。类似地，` and `， ` or `和` not `都将它们的参数视为布尔值，并且不能重载。

所以请记住:

- 使用` .in_() `和` .not_in() `来代替` in `和` not in `

- 用`&`代替`and`
- 使用`|`代替`或`
- 用`~`代替`not`
- 使用` .is_null() `代替` is None `或` == None `。
- **在使用逻辑运算符时，不要忘记把比较用括号括起来**

要了解更多示例，请参见[Expressions](http://docs.peewee-orm.com/en/latest/peewee/query_operators.html#expressions)一节。



Note

**LIKE and ILIKE with SQLite**

Because SQLite’s `LIKE` operation is case-insensitive by default, peewee will use the SQLite `GLOB` operation for case-sensitive searches. The glob operation uses asterisks for wildcards as opposed to the usual percent-sign. If you are using SQLite and want case-sensitive partial string matching, remember to use asterisks for the wildcard.

请注意

**LIKE和ILIKE与SQLite**

因为SQLite的 `LIKE` 操作默认情况下不区分大小写，peewee将使用SQLite的“GLOB”操作进行区分大小写的搜索。 `GLOB` 操作使用星号作为通配符，而不是通常的百分号。如果您正在使用SQLite并希望区分大小写的部分字符串匹配，请记住使用星号作为通配符。

## Three valued logic 三值逻辑

Because of the way SQL handles `NULL`, there are some special operations available for expressing:

- `IS NULL`
- `IS NOT NULL`
- `IN`
- `NOT IN`

While it would be possible to use the `IS NULL` and `IN` operators with the negation operator (`~`), sometimes to get the correct semantics you will need to explicitly use `IS NOT NULL` and `NOT IN`.

The simplest way to use `IS NULL` and `IN` is to use the operator overloads:

由于SQL处理` NULL `的方式，有一些特殊的操作可以表示:

- `IS NULL`
- `IS NOT NULL`
- `IN`
- `NOT IN`

虽然可以将` IS NULL `和` IN `操作符与否定操作符(` ~ `)一起使用，但有时为了获得正确的语义，需要显式地使用` IS NOT NULL `和` NOT IN `。

使用` IS NULL `和` IN `的最简单方法是使用操作符重载:

```python
# Get all User objects whose last login is NULL.
User.select().where(User.last_login >> None)

# Get users whose username is in the given list.
usernames = [`charlie`, `huey`, `mickey`]
User.select().where(User.username << usernames)
```

If you don’t like operator overloads, you can call the Field methods instead:

如果你不喜欢操作符重载，你可以调用字段方法:

```python
# Get all User objects whose last login is NULL.
User.select().where(User.last_login.is_null(True))

# Get users whose username is in the given list.
usernames = [`charlie`, `huey`, `mickey`]
User.select().where(User.username.in_(usernames))
```

To negate the above queries, you can use unary negation, but for the correct semantics you may need to use the special `IS NOT` and `NOT IN` operators:

要否定上述查询，你可以使用一元否定，但为了正确的语义，你可能需要使用特殊的` IS NOT `和` NOT IN `操作符:

```python
# Get all User objects whose last login is *NOT* NULL.
User.select().where(User.last_login.is_null(False))

# Using unary negation instead.
User.select().where(~(User.last_login >> None))

# Get users whose username is *NOT* in the given list.
usernames = [`charlie`, `huey`, `mickey`]
User.select().where(User.username.not_in(usernames))

# Using unary negation instead.
usernames = [`charlie`, `huey`, `mickey`]
User.select().where(~(User.username << usernames))
```



## Adding user-defined operators 添加用户定义的操作符

Because I ran out of python operators to overload, there are some missing operators in peewee, for instance `modulo`. If you find that you need to support an operator that is not in the table above, it is very easy to add your own.

Here is how you might add support for `modulo` in SQLite:

因为我用完了要重载的python操作符，所以在peewee中缺少了一些操作符，例如` modulo `。如果您发现您需要支持的运算符不在上面的表中，那么添加您自己的运算符是非常容易的。

下面是如何在SQLite中添加对“modulo”的支持:

```python
from peewee import *
from peewee import Expression # the building block for expressions

def mod(lhs, rhs):
    return Expression(lhs, `%`, rhs)
```

Now you can use these custom operators to build richer queries:

现在你可以使用这些自定义操作符来构建更丰富的查询:

```python
# Users with even ids.
User.select().where(mod(User.id, 2) == 0)
```

For more examples check out the source to the `playhouse.postgresql_ext` module, as it contains numerous operators specific to postgresql’s hstore.

要了解更多的例子，请查看`playhouse.postgresql_ext `模块，因为它包含许多特定于 postgresql 的 hstore 操作符。

## Expressions 表达式

Peewee is designed to provide a simple, expressive, and pythonic way of constructing SQL queries. This section will provide a quick overview of some common types of expressions.

There are two primary types of objects that can be composed to create expressions:

- [`Field`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Field) instances
- SQL aggregations and functions using [`fn`](http://docs.peewee-orm.com/en/latest/peewee/api.html#fn)

We will assume a simple “User” model with fields for username and other things. It looks like this:

Peewee旨在提供一种简单、富有表现力和python风格的方法来构造SQL查询。本节将快速概述一些常见的表达式类型。

有两种主要类型的对象可以用来创建表达式:

- [`Field`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Field) instances
- SQL aggregations and functions using [`fn`](http://docs.peewee-orm.com/en/latest/peewee/api.html#fn)

我们将假设一个简单的“User”模型，其中包含用于用户名和其他内容的字段。它是这样的:

```python
class User(Model):
    username = CharField()
    is_admin = BooleanField()
    is_active = BooleanField()
    last_login = DateTimeField()
    login_count = IntegerField()
    failed_logins = IntegerField()
```

Comparisons use the [Query operators](http://docs.peewee-orm.com/en/latest/peewee/query_operators.html#query-operators):

比较使用[查询操作符](http://docs.peewee-orm.com/en/latest/peewee/query_operators.html#query-operators):

```python
# username is equal to `charlie`
User.username == `charlie`

# user has logged in less than 5 times
User.login_count < 5
```

Comparisons can be combined using **bitwise** *and* and *or*. Operator precedence is controlled by python and comparisons can be nested to an arbitrary depth:

比较可以使用**位** *、*和*或*结合使用。操作符优先级由python控制，比较可以嵌套到任意深度:

```python
# User is both and admin and has logged in today
(User.is_admin == True) & (User.last_login >= today)

# User`s username is either charlie or charles
(User.username == `charlie`) | (User.username == `charles`)
```

Comparisons can be used with functions as well:

比较也可以用于函数:

```python
# user`s username starts with a `g` or a `G`:
fn.Lower(fn.Substr(User.username, 1, 1)) == `g`
```

We can do some fairly interesting things, as expressions can be compared against other expressions. Expressions also support arithmetic operations:

我们可以做一些相当有趣的事情，因为表达式可以与其他表达式进行比较。表达式也支持算术操作:

```python
# users who entered the incorrect more than half the time and have logged
# in at least 10 times
(User.failed_logins > (User.login_count * .5)) & (User.login_count > 10)
```

Expressions allow us to do *atomic updates*:

表达式允许我们做*atomic*更新:

```python
# when a user logs in we want to increment their login count:
User.update(login_count=User.login_count + 1).where(User.id == user_id)
```

Expressions can be used in all parts of a query, so experiment!

表达式可以用于查询的所有部分，所以实验吧!

### Row values

Many databases support [row values](https://www.sqlite.org/rowvalue.html), which are similar to Python tuple objects. In Peewee, it is possible to use row-values in expressions via [`Tuple`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Tuple). For example,

许多数据库支持[row values](https://www.sqlite.org/rowvalue.html)，它类似于Python元组对象。在Peewee中，可以通过[` Tuple `](http://docs.peewee-orm.com/en/latest/peewee/api.html#Tuple)在表达式中使用行值。例如,

```python
# If for some reason your schema stores dates in separate columns ("year",
# "month" and "day"), you can use row-values to find all rows that happened
# in a given month:
Tuple(Event.year, Event.month) == (2019, 1)
```

The more common use for row-values is to compare against multiple columns from a subquery in a single expression. There are other ways to express these types of queries, but row-values may offer a concise and readable approach.

For example, assume we have a table “EventLog” which contains an event type, an event source, and some metadata. We also have an “IncidentLog”, which has incident type, incident source, and metadata columns. We can use row-values to correlate incidents with certain events:

行值更常见的用途是在单个表达式中比较来自子查询的多个列。还有其他方法可以表示这些类型的查询，但是行值可能提供了一种简明易读的方法。

例如，假设我们有一个表“EventLog”，其中包含一个事件类型、一个事件源和一些元数据。我们还有一个“IncidentLog”，它包含事件类型、事件源和元数据列。我们可以使用行值将事件与某些事件关联起来:

```python
class EventLog(Model):
    event_type = TextField()
    source = TextField()
    data = TextField()
    timestamp = TimestampField()

class IncidentLog(Model):
    incident_type = TextField()
    source = TextField()
    traceback = TextField()
    timestamp = TimestampField()

# Get a list of all the incident types and sources that have occured today.
incidents = (IncidentLog
             .select(IncidentLog.incident_type, IncidentLog.source)
             .where(IncidentLog.timestamp >= datetime.date.today()))

# Find all events that correlate with the type and source of the
# incidents that occured today.
events = (EventLog
          .select()
          .where(Tuple(EventLog.event_type, EventLog.source).in_(incidents))
          .order_by(EventLog.timestamp))
```

Other ways to express this type of query would be to use a [join](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#relationships) or to [join on a subquery](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#join-subquery). The above example is there just to give you and idea how [`Tuple`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Tuple) might be used.

You can also use row-values to update multiple columns in a table, when the new data is derived from a subquery. For an example, see [here](https://www.sqlite.org/rowvalue.html#update_multiple_columns_of_a_table_based_on_a_query).

表示这种查询类型的其他方法是使用[join](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#relationships)或[子查询上的join](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#join-subquery)。上面的例子只是为了让你知道如何使用[` Tuple `](http://docs.peewee-orm.com/en/latest/peewee/api.html#Tuple)。

当从子查询派生新数据时，还可以使用行值来更新表中的多个列。例如，请参见[here](https://www.sqlite.org/rowvalue.html#update_multiple_columns_of_a_table_based_on_a_query)。

## SQL Functions

SQL functions, like `COUNT()` or `SUM()`, can be expressed using the [`fn()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#fn) helper:

SQL函数，如` COUNT() `或` SUM() `，可以使用[` fn() `](http://docs.peewee-orm.com/en/latest/peewee/api.html#fn)助手来表示:

```python
# Get all users and the number of tweets they`ve authored. Sort the
# results from most tweets -> fewest tweets.
query = (User
         .select(User, fn.COUNT(Tweet.id).alias(`tweet_count`))
         .join(Tweet, JOIN.LEFT_OUTER)
         .group_by(User)
         .order_by(fn.COUNT(Tweet.id).desc()))
for user in query:
    print(`%s -- %s tweets` % (user.username, user.tweet_count))
```

The `fn` helper exposes any SQL function as if it were a method. The parameters can be fields, values, subqueries, or even nested functions.

` fn `助手将任何SQL函数作为方法公开。
参数可以是字段、值、子查询，甚至是嵌套函数。

### Nesting function calls

Suppose you need to want to get a list of all users whose username begins with *a*. There are a couple ways to do this, but one method might be to use some SQL functions like *LOWER* and *SUBSTR*. To use arbitrary SQL functions, use the special [`fn()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#fn) object to construct queries:

假设您需要获得用户名以*a*开头的所有用户的列表。有几种方法可以做到这一点，但其中一种方法可能是使用一些SQL函数，如*LOWER*和*SUBSTR*。要使用任意的SQL函数，可以使用特殊的[` fn() `](http://docs.peewee-orm.com/en/latest/peewee/api.html#fn)对象来构造查询:

```python
# Select the user`s id, username and the first letter of their username, lower-cased
first_letter = fn.LOWER(fn.SUBSTR(User.username, 1, 1))
query = User.select(User, first_letter.alias(`first_letter`))

# Alternatively we could select only users whose username begins with `a`
a_users = User.select().where(first_letter == `a`)

>>> for user in a_users:
...    print(user.username)
```

## SQL Helper SQL助手

There are times when you may want to simply pass in some arbitrary sql. You can do this using the special [`SQL`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SQL) class. One use-case is when referencing an alias:

有时，您可能只是想传入一些任意的sql。您可以使用特殊的[` SQL `](http://docs.peewee-orm.com/en/latest/peewee/api.html#SQL)类来实现这一点。一个用例是在引用别名时:

```python
# We`ll query the user table and annotate it with a count of tweets for
# the given user
query = (User
         .select(User, fn.Count(Tweet.id).alias(`ct`))
         .join(Tweet)
         .group_by(User))

# Now we will order by the count, which was aliased to "ct"
query = query.order_by(SQL(`ct`))

# You could, of course, also write this as:
query = query.order_by(fn.COUNT(Tweet.id))
```

There are two ways to execute hand-crafted SQL statements with peewee:

1. [`Database.execute_sql()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.execute_sql) for executing any type of query
2. [`RawQuery`](http://docs.peewee-orm.com/en/latest/peewee/api.html#RawQuery) for executing `SELECT` queries and returning model instances.

使用peewee执行手工编写的SQL语句有两种方式:

1. [` Database.execute_sql() `](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.execute_sql)用于执行任何类型的查询

2. [` RawQuery `](http://docs.peewee-orm.com/en/latest/peewee/api.html#RawQuery)用于执行` SELECT `查询和返回模型实例。

## Security and SQL Injection 安全性和SQL注入

By default peewee will parameterize queries, so any parameters passed in by the user will be escaped. The only exception to this rule is if you are writing a raw SQL query or are passing in a `SQL` object which may contain untrusted data. To mitigate this, ensure that any user-defined data is passed in as a query parameter and not part of the actual SQL query:

默认情况下，peewee将参数化查询，因此用户传入的任何参数都将被转义。这个规则的唯一例外是如果你正在编写一个原始的SQL查询或传入一个可能包含不可信数据的` SQL `对象。为了减轻这种情况，确保任何用户定义的数据都是作为查询参数传入的，而不是实际SQL查询的一部分:

```python
# Bad! DO NOT DO THIS!
query = MyModel.raw(`SELECT * FROM my_table WHERE data = %s` % (user_data,))

# Good. `user_data` will be treated as a parameter to the query.
query = MyModel.raw(`SELECT * FROM my_table WHERE data = %s`, user_data)

# Bad! DO NOT DO THIS!
query = MyModel.select().where(SQL(`Some SQL expression %s` % user_data))

# Good. `user_data` will be treated as a parameter.
query = MyModel.select().where(SQL(`Some SQL expression %s`, user_data))
```

Note

MySQL and Postgresql use ``%s`` to denote parameters. SQLite, on the other hand, uses ``?``. Be sure to use the character appropriate to your database. You can also find this parameter by checking `Database.param`.

请注意

MySQL和Postgresql使用`%s`来表示参数。另一方面，SQLite使用`?`请确保使用适合您的数据库的字符。你也可以通过检查`Database.param`来找到这个参数。

[Next ](http://docs.peewee-orm.com/en/latest/peewee/relationships.html)[ Previous](http://docs.peewee-orm.com/en/latest/peewee/querying.html)