# Relationships and Joins

In this document we’ll cover how Peewee handles relationships between models.

在本文档中，我们将介绍Peewee如何处理模型之间的关系。

## Model definitions 模型定义

We’ll use the following model definitions for our examples:

我们将在示例中使用下面的模型定义:

```python
import datetime
from peewee import *


db = SqliteDatabase(':memory:')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = TextField()

class Tweet(BaseModel):
    content = TextField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(User, backref='tweets')

class Favorite(BaseModel):
    user = ForeignKeyField(User, backref='favorites')
    tweet = ForeignKeyField(Tweet, backref='favorites')
```

Peewee uses [`ForeignKeyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ForeignKeyField) to define foreign-key relationships between models. Every foreign-key field has an implied back-reference, which is exposed as a pre-filtered [`Select`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select) query using the provided `backref` attribute.

Peewee使用[`ForeignKeyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ForeignKeyField)定义模型之间的外键关系。每个外键字段都有一个隐含的反向引用，它被公开为使用提供的`backref`属性进行预过滤的[`Select`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Select)查询。



### Creating test data创建测试数据

To follow along with the examples, let’s populate this database with some test data:

为了跟随这些示例，让我们用一些测试数据填充这个数据库:

```python
def populate_test_data():
    db.create_tables([User, Tweet, Favorite])

    data = (
        ('huey', ('meow', 'hiss', 'purr')),
        ('mickey', ('woof', 'whine')),
        ('zaizee', ()))
    for username, tweets in data:
        user = User.create(username=username)
        for tweet in tweets:
            Tweet.create(user=user, content=tweet)

    # Populate a few favorites for our users, such that:
    favorite_data = (
        ('huey', ['whine']),
        ('mickey', ['purr']),
        ('zaizee', ['meow', 'purr']))
    for username, favorites in favorite_data:
        user = User.get(User.username == username)
        for content in favorites:
            tweet = Tweet.get(Tweet.content == content)
            Favorite.create(user=user, tweet=tweet)
```

This gives us the following: 这给了我们以下信息:

| User   | Tweet | Favorited by   |
| ------ | ----- | -------------- |
| huey   | meow  | zaizee         |
| huey   | hiss  |                |
| huey   | purr  | mickey, zaizee |
| mickey | woof  |                |
| mickey | whine | huey           |

Attention

In the following examples we will be executing a number of queries. If you are unsure how many queries are being executed, you can add the following code, which will log all queries to the console:

注意

在下面的示例中，我们将执行一些查询。如果你不确定有多少查询正在执行，你可以添加以下代码，它将把所有查询记录到控制台:

```python
import logging
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
```

Note

In SQLite, foreign keys are not enabled by default. Most things, including the Peewee foreign-key API, will work fine, but ON DELETE behaviour will be ignored, even if you explicitly specify `on_delete` in your [`ForeignKeyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ForeignKeyField). In conjunction with the default [`AutoField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#AutoField) behaviour (where deleted record IDs can be reused), this can lead to subtle bugs. To avoid problems, I recommend that you enable foreign-key constraints when using SQLite, by setting `pragmas={'foreign_keys': 1}` when you instantiate [`SqliteDatabase`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase).

请注意

在SQLite中，默认情况下外键是不启用的。大多数事情，包括Peewee外键API，将工作良好，但删除行为将被忽略，即使你明确指定`on_delete`在你的[`ForeignKeyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ForeignKeyField)。再加上默认的[`AutoField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#AutoField)行为(删除的记录id可以重用)，这可能会导致微妙的bug。为了避免出现问题，我建议在使用SQLite时启用外键约束，在实例化[` SqliteDatabase`](http://docs.peewee-orm.com/en/latest/peewee/api.html#SqliteDatabase)时设置` pragmas={'foreign_keys': 1} `。

```python
# Ensure foreign-key constraints are enforced.
db = SqliteDatabase('my_app.db', pragmas={'foreign_keys': 1})
```

## Performing simple joins

As an exercise in learning how to perform joins with Peewee, let’s write a query to print out all the tweets by “huey”. To do this we’ll select from the `Tweet` model and join on the `User` model, so we can then filter on the `User.username` field:

作为学习如何执行与Peewee的连接的练习，让我们编写一个查询来打印“huey”的所有tweet。为了做到这一点，我们将从`Tweet`模型中选择并加入`User`模型，这样我们就可以过滤`User`。用户名字段:

```python
>>> query = Tweet.select().join(User).where(User.username == 'huey')
>>> for tweet in query:
...     print(tweet.content)
...
meow
hiss
purr
```

Note

We did not have to explicitly specify the join predicate (the “ON” clause), because Peewee inferred from the models that when we joined from Tweet to User, we were joining on the `Tweet.user` foreign-key.

请注意

我们不需要显式地指定连接谓词(“ON”子句)，因为Peewee从模型推断，当我们从Tweet加入到User时，我们正在`Tweet`上加入。用户的外键。

The following code is equivalent, but more explicit:

下面的代码等价，但更显式:

```python
query = (Tweet
         .select()
         .join(User, on=(Tweet.user == User.id))
         .where(User.username == 'huey'))
```

If we already had a reference to the `User` object for “huey”, we could use the `User.tweets` back-reference to list all of huey’s tweets:

如果“huey”已经有了对`User`对象的引用，则可以使用`User.tweets`的反向引用列出所有hury的推文:

```python
>>> huey = User.get(User.username == 'huey')
>>> for tweet in huey.tweets:
...     print(tweet.content)
...
meow
hiss
purr
```

Taking a closer look at `huey.tweets`, we can see that it is just a simple pre-filtered `SELECT` query:

仔细看看`huey.tweets`，我们可以看到，它只是一个简单的预先过滤的`SELECT`查询:

```python
>>> huey.tweets
<peewee.ModelSelect at 0x7f0483931fd0>

>>> huey.tweets.sql()
('SELECT "t1"."id", "t1"."content", "t1"."timestamp", "t1"."user_id"
  FROM "tweet" AS "t1" WHERE ("t1"."user_id" = ?)', [1])
```

## Joining multiple tables 多表连接

Let’s take another look at joins by querying the list of users and getting the count of how many tweet’s they’ve authored that were favorited. This will require us to join twice: from user to tweet, and from tweet to favorite. We’ll add the additional requirement that users should be included who have not created any tweets, as well as users whose tweets have not been favorited. The query, expressed in SQL, would be:

让我们通过查询用户列表并获取他们所撰写的tweet被收藏的数量来进一步了解join。这将要求我们加入两次:从用户到tweet，从tweet到收藏。我们将添加额外的要求，即应该包括那些没有创建任何tweet的用户，以及那些tweet没有被收藏的用户。查询，用SQL表示，将是:

```python
SELECT user.username, COUNT(favorite.id)
FROM user
LEFT OUTER JOIN tweet ON tweet.user_id = user.id
LEFT OUTER JOIN favorite ON favorite.tweet_id = tweet.id
GROUP BY user.username
```

Note

In the above query both joins are LEFT OUTER, since a user may not have any tweets or, if they have tweets, none of them may have been favorited.

Peewee has a concept of a *join context*, meaning that whenever we call the [`join()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ModelSelect.join) method, we are implicitly joining on the previously-joined model (or if this is the first call, the model we are selecting from). Since we are joining straight through, from user to tweet, then from tweet to favorite, we can simply write:

请注意

在上面的查询中，两个连接都位于外部，因为用户可能没有任何tweet，或者如果他们有tweet，也可能没有任何tweet被收藏。

小东西有一个**连接上下文**的概念,也就是说,每当我们所说的[`join()`](http://docs.peewee-orm.com/en/latest/peewee/api.html # ModelSelect.join)方法，我们是隐式地加入previously-joined模型(或者如果这是第一次调用,我们选择的模型)。
因为我们是直接加入的，从用户到推文，再从推文到收藏，我们可以简单地写:

```python
query = (User
         .select(User.username, fn.COUNT(Favorite.id).alias('count'))
         .join(Tweet, JOIN.LEFT_OUTER)  # Joins user -> tweet.
         .join(Favorite, JOIN.LEFT_OUTER)  # Joins tweet -> favorite.
         .group_by(User.username))
```

Iterating over the results:

对结果进行迭代:

```python
>>> for user in query:
...     print(user.username, user.count)
...
huey 3
mickey 1
zaizee 0
```

For a more complicated example involving multiple joins and switching join contexts, let’s find all the tweets by Huey and the number of times they’ve been favorited. To do this we’ll need to perform two joins and we’ll also use an aggregate function to calculate the favorite count.

Here is how we would write this query in SQL:

对于一个涉及多个连接和切换连接上下文的更复杂的示例，让我们找到Huey的所有tweet以及它们被收藏的次数。为此，我们需要执行两个连接，我们还将使用一个聚合函数来计算收藏次数。

下面是我们如何在SQL中写这个查询:

```python
SELECT tweet.content, COUNT(favorite.id)
FROM tweet
INNER JOIN user ON tweet.user_id = user.id
LEFT OUTER JOIN favorite ON favorite.tweet_id = tweet.id
WHERE user.username = 'huey'
GROUP BY tweet.content;
```

Note

We use a LEFT OUTER join from tweet to favorite since a tweet may not have any favorites, yet we still wish to display it’s content (along with a count of zero) in the result set.

With Peewee, the resulting Python code looks very similar to what we would write in SQL:

请注意

我们使用从tweet到favorite的左外连接，因为一条tweet可能没有任何收藏，但是我们仍然希望在结果集中显示它的内容(连同0的计数)。

使用Peewee，得到的Python代码看起来非常类似于我们用SQL编写的代码:

```python
query = (Tweet
         .select(Tweet.content, fn.COUNT(Favorite.id).alias('count'))
         .join(User)  # Join from tweet -> user.
         .switch(Tweet)  # Move "join context" back to tweet.
         .join(Favorite, JOIN.LEFT_OUTER)  # Join from tweet -> favorite.
         .where(User.username == 'huey')
         .group_by(Tweet.content))
```

Note the call to [`switch()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ModelSelect.switch) - that instructs Peewee to set the *join context* back to `Tweet`. If we had omitted the explicit call to switch, Peewee would have used `User` (the last model we joined) as the join context and constructed the join from User to Favorite using the `Favorite.user` foreign-key, which would have given us incorrect results.

If we wanted to omit the join-context switching we could instead use the [`join_from()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ModelSelect.join_from) method. The following query is equivalent to the previous one:

请注意对[`switch()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ModelSelect.switch)的调用——它指示Peewee将*join上下文*设置回`Tweet`。如果我们忽略了对switch的显式调用，Peewee就会使用`User`(我们连接的最后一个模型)作为连接上下文，并使用`Favorite.user`外键构建从用户到收藏的连接。这会给我们不正确的结果。

如果我们想省略连接上下文切换，我们可以使用[`join_from()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ModelSelect.join_from)方法。下面的查询等价于前面的查询:

```python
query = (Tweet
         .select(Tweet.content, fn.COUNT(Favorite.id).alias('count'))
         .join_from(Tweet, User)  # Join tweet -> user.
         .join_from(Tweet, Favorite, JOIN.LEFT_OUTER)  # Join tweet -> favorite.
         .where(User.username == 'huey')
         .group_by(Tweet.content))
```

We can iterate over the results of the above query to print the tweet’s content and the favorite count:

我们可以遍历上述查询的结果来打印tweet的内容和收藏次数:

```python
>>> for tweet in query:
...     print('%s favorited %d times' % (tweet.content, tweet.count))
...
meow favorited 1 times
hiss favorited 0 times
purr favorited 2 times
```



## Selecting from multiple sources 从多个源进行选择

If we wished to list all the tweets in the database, along with the username of their author, you might try writing this:

如果我们想列出数据库中的所有tweet，以及它们的作者的用户名，你可以试着这样写:

```python
>>> for tweet in Tweet.select():
...     print(tweet.user.username, '->', tweet.content)
...
huey -> meow
huey -> hiss
huey -> purr
mickey -> woof
mickey -> whine
```

There is a big problem with the above loop: it executes an additional query for every tweet to look up the `tweet.user` foreign-key. For our small table the performance penalty isn’t obvious, but we would find the delays grew as the number of rows increased.

If you’re familiar with SQL, you might remember that it’s possible to SELECT from multiple tables, allowing us to get the tweet content *and* the username in a single query:

上面的循环有一个大问题: 它对每条tweet执行一个额外的查询来查找 外键`tweet.user`。对于我们的小表，性能损失并不明显，但是我们会发现，随着行数的增加，延迟也会增加。

如果你熟悉SQL，你可能会记得可以从多个表中选择，允许我们在单个查询中获得tweet内容*和*用户名:

```python
SELECT tweet.content, user.username
FROM tweet
INNER JOIN user ON tweet.user_id = user.id;
```

Peewee makes this quite easy. In fact, we only need to modify our query a little bit. We tell Peewee we wish to select `Tweet.content` as well as the `User.username` field, then we include a join from tweet to user. To make it a bit more obvious that it’s doing the correct thing, we can ask Peewee to return the rows as dictionaries.

Peewee让这变得很简单。事实上，我们只需要稍微修改一下我们的查询。我们告诉Peewee我们希望选择`Tweet.content` ，以及 `User.username` 字段，然后我们包含一个从tweet到用户的join。为了更明显地表明它所做的是正确的，我们可以要求Peewee将行作为字典返回。

```python
>>> for row in Tweet.select(Tweet.content, User.username).join(User).dicts():
...     print(row)
...
{'content': 'meow', 'username': 'huey'}
{'content': 'hiss', 'username': 'huey'}
{'content': 'purr', 'username': 'huey'}
{'content': 'woof', 'username': 'mickey'}
{'content': 'whine', 'username': 'mickey'}
```

Now we’ll leave off the call to “.dicts()” and return the rows as `Tweet` objects. Notice that Peewee assigns the `username` value to `tweet.user.username` – NOT `tweet.username`! Because there is a foreign-key from tweet to user, and we have selected fields from both models, Peewee will reconstruct the model-graph for us:

现在我们将停止对" .dicts() "的调用，并将行作为 `Tweet` 对象返回。注意，Peewee将`username` 值分配给`tweet.user.username`' —不是`tweet.username` !因为从tweet到user都有一个外键，并且我们从两个模型中都选择了字段，所以Peewee会为我们重构模型图:

```python
>>> for tweet in Tweet.select(Tweet.content, User.username).join(User):
...     print(tweet.user.username, '->', tweet.content)
...
huey -> meow
huey -> hiss
huey -> purr
mickey -> woof
mickey -> whine
```

If we wish to, we can control where Peewee puts the joined `User` instance in the above query, by specifying an `attr` in the `join()` method:

如果我们愿意，我们可以通过在 `join()` 方法中指定`attr` 来控制Peewee在上面查询中放置已连接的 `User` 实例的位置:

```python
>>> query = Tweet.select(Tweet.content, User.username).join(User, attr='author')
>>> for tweet in query:
...     print(tweet.author.username, '->', tweet.content)
...
huey -> meow
huey -> hiss
huey -> purr
mickey -> woof
mickey -> whine
```

Conversely, if we simply wish *all* attributes we select to be attributes of the `Tweet` instance, we can add a call to [`objects()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ModelSelect.objects) at the end of our query (similar to how we called `dicts()`):

相反，如果我们只是希望我们选择的*所有*属性成为 `Tweet` 实例的属性，我们可以在查询的最后添加一个调用[`objects()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ModelSelect.objects) (类似于我们调用`dicts()`):

```python
>>> for tweet in query.objects():
...     print(tweet.username, '->', tweet.content)
...
huey -> meow
(etc)
```

### More complex example 更复杂的示例

As a more complex example, in this query, we will write a single query that selects all the favorites, along with the user who created the favorite, the tweet that was favorited, and that tweet’s author.

In SQL we would write:

作为一个更复杂的示例，在这个查询中，我们将编写一个查询，选择所有收藏夹、创建收藏夹的用户、被收藏的tweet和该tweet的作者。

在SQL中，我们可以这样写:

```python
SELECT owner.username, tweet.content, author.username AS author
FROM favorite
INNER JOIN user AS owner ON (favorite.user_id = owner.id)
INNER JOIN tweet ON (favorite.tweet_id = tweet.id)
INNER JOIN user AS author ON (tweet.user_id = author.id);
```

Note that we are selecting from the user table twice - once in the context of the user who created the favorite, and again as the author of the tweet.

With Peewee, we use [`Model.alias()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.alias) to alias a model class so it can be referenced twice in a single query:

注意，我们从user表中进行了两次选择——一次是在创建收藏夹的用户上下文中，另一次是作为tweet的作者。

对于Peewee，我们使用[`Model.alias()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.alias)来为一个模型类命名，这样它就可以在一个查询中被引用两次:

```python
Owner = User.alias()
query = (Favorite
         .select(Favorite, Tweet.content, User.username, Owner.username)
         .join(Owner)  # Join favorite -> user (owner of favorite).
         .switch(Favorite)
         .join(Tweet)  # Join favorite -> tweet
         .join(User))   # Join tweet -> user
```

We can iterate over the results and access the joined values in the following way. Note how Peewee has resolved the fields from the various models we selected and reconstructed the model graph:

我们可以遍历结果并按以下方式访问联接的值。注意Peewee是如何从我们选择的各种模型中解析字段并重构模型图的:

```python
>>> for fav in query:
...     print(fav.user.username, 'liked', fav.tweet.content, 'by', fav.tweet.user.username)
...
huey liked whine by mickey
mickey liked purr by huey
zaizee liked meow by huey
zaizee liked purr by huey
```



## Subqueries 子查询

Peewee allows you to join on any table-like object, including subqueries or common table expressions (CTEs). To demonstrate joining on a subquery, let’s query for all users and their latest tweet.

Here is the SQL:

Peewee允许您连接任何类表对象，包括子查询或公共表表达式(CTEs)。为了演示子查询上的连接，让我们查询所有用户及其最新tweet。

下面是SQL语句:

```python
SELECT tweet.*, user.*
FROM tweet
INNER JOIN (
    SELECT latest.user_id, MAX(latest.timestamp) AS max_ts
    FROM tweet AS latest
    GROUP BY latest.user_id) AS latest_query
ON ((tweet.user_id = latest_query.user_id) AND (tweet.timestamp = latest_query.max_ts))
INNER JOIN user ON (tweet.user_id = user.id)
```

We’ll do this by creating a subquery which selects each user and the timestamp of their latest tweet. Then we can query the tweets table in the outer query and join on the user and timestamp combination from the subquery.

为此，我们将创建一个子查询，它选择每个用户及其最新tweet的时间戳。然后，我们可以在外部查询中查询tweets表，并从子查询中连接用户和时间戳组合。

```python
# Define our subquery first. We'll use an alias of the Tweet model, since
# we will be querying from the Tweet model directly in the outer query.
Latest = Tweet.alias()
latest_query = (Latest
                .select(Latest.user, fn.MAX(Latest.timestamp).alias('max_ts'))
                .group_by(Latest.user)
                .alias('latest_query'))

# Our join predicate will ensure that we match tweets based on their
# timestamp *and* user_id.
predicate = ((Tweet.user == latest_query.c.user_id) &
             (Tweet.timestamp == latest_query.c.max_ts))

# We put it all together, querying from tweet and joining on the subquery
# using the above predicate.
query = (Tweet
         .select(Tweet, User)  # Select all columns from tweet and user.
         .join(latest_query, on=predicate)  # Join tweet -> subquery.
         .join_from(Tweet, User))  # Join from tweet -> user.
```

Iterating over the query, we can see each user and their latest tweet.

通过迭代查询，我们可以看到每个用户和他们的最新tweet。

```python
>>> for tweet in query:
...     print(tweet.user.username, '->', tweet.content)
...
huey -> purr
mickey -> whine
```

There are a couple things you may not have seen before in the code we used to create the query in this section:

- We used [`join_from()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ModelSelect.join_from) to explicitly specify the join context. We wrote `.join_from(Tweet, User)`, which is equivalent to `.switch(Tweet).join(User)`.
- We referenced columns in the subquery using the magic `.c` attribute, for example `latest_query.c.max_ts`. The `.c` attribute is used to dynamically create column references.
- Instead of passing individual fields to `Tweet.select()`, we passed the `Tweet` and `User` models. This is shorthand for selecting all fields on the given model.

在本节创建查询的代码中，有一些东西你可能没有见过:

- 使用[`join_from()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ModelSelect.join_from)显式指定连接上下文。我们写了`join_from(Tweet,User)`，相当于` .switch(Tweet).join(User)`。
- 我们在子查询中使用`.c`属性来引用列，例如`latest_query.c.max_ts`。`.c`属性用于动态创建列引用。
- 我们传递了`Tweet`和`User`模型，而不是传递单独的字段给`Tweet.select()`。这是选择给定模型上所有字段的简写。



### Common-table Expressions 公共表表达式

In the previous section we joined on a subquery, but we could just as easily have used a [common-table expression (CTE)](http://docs.peewee-orm.com/en/latest/peewee/querying.html#cte). We will repeat the same query as before, listing users and their latest tweets, but this time we will do it using a CTE.

Here is the SQL:

在上一节中，我们连接了一个子查询，但是我们也可以轻松地使用[公共表表达式(CTE)](http://docs.peewee-orm.com/en/latest/peewee/querying.html#cte)。我们将重复与前面相同的查询，列出用户及其最新tweet，但这一次我们将使用CTE。

下面是SQL语句:

```python
WITH latest AS (
    SELECT user_id, MAX(timestamp) AS max_ts
    FROM tweet
    GROUP BY user_id)
SELECT tweet.*, user.*
FROM tweet
INNER JOIN latest
    ON ((latest.user_id = tweet.user_id) AND (latest.max_ts = tweet.timestamp))
INNER JOIN user
    ON (tweet.user_id = user.id)
```

This example looks very similar to the previous example with the subquery:

这个例子看起来和前面的子查询的例子非常相似:

```python
# Define our CTE first. We'll use an alias of the Tweet model, since
# we will be querying from the Tweet model directly in the main query.
Latest = Tweet.alias()
cte = (Latest
       .select(Latest.user, fn.MAX(Latest.timestamp).alias('max_ts'))
       .group_by(Latest.user)
       .cte('latest'))

# Our join predicate will ensure that we match tweets based on their
# timestamp *and* user_id.
predicate = ((Tweet.user == cte.c.user_id) &
             (Tweet.timestamp == cte.c.max_ts))

# We put it all together, querying from tweet and joining on the CTE
# using the above predicate.
query = (Tweet
         .select(Tweet, User)  # Select all columns from tweet and user.
         .join(cte, on=predicate)  # Join tweet -> CTE.
         .join_from(Tweet, User)  # Join from tweet -> user.
         .with_cte(cte))
```

We can iterate over the result-set, which consists of the latest tweets for each user:

我们可以迭代结果集，它包含每个用户的最新tweet:

```python
>>> for tweet in query:
...     print(tweet.user.username, '->', tweet.content)
...
huey -> purr
mickey -> whine
```

Note

For more information about using CTEs, including information on writing recursive CTEs, see the [Common Table Expressions](http://docs.peewee-orm.com/en/latest/peewee/querying.html#cte) section of the “Querying” document.

请注意

有关使用CTEs的更多信息，包括编写递归CTEs的信息，请参见“查询”文档的[公共表表达式](http://docs.peewee-orm.com/en/latest/peewee/querying.html#cte)一节。



## Multiple foreign-keys to the same Model

同一个模型的多个外键

When there are multiple foreign keys to the same model, it is good practice to explicitly specify which field you are joining on.

Referring back to the [example app’s models](http://docs.peewee-orm.com/en/latest/peewee/example.html#example-app-models), consider the *Relationship* model, which is used to denote when one user follows another. Here is the model definition:

当同一个模型有多个外键时，最好明确指定要连接的字段。

回到[示例应用程序的模型](http://docs.peewee-orm.com/en/latest/peewee/example.html#example-app-models)，考虑*Relationship*模型，它用于表示一个用户何时跟随另一个用户。
模型定义如下:

```python
class Relationship(BaseModel):
    from_user = ForeignKeyField(User, backref='relationships')
    to_user = ForeignKeyField(User, backref='related_to')

    class Meta:
        indexes = (
            # Specify a unique multi-column index on from/to-user.
            (('from_user', 'to_user'), True),
        )
```

Since there are two foreign keys to *User*, we should always specify which field we are using in a join.

For example, to determine which users I am following, I would write:

因为*User*有两个外键，所以我们应该指定在连接中使用哪个字段。

例如，为了确定我关注哪些用户，我可以这样写:

```python
(User
 .select()
 .join(Relationship, on=Relationship.to_user)
 .where(Relationship.from_user == charlie))
```

On the other hand, if I wanted to determine which users are following me, I would instead join on the *from_user* column and filter on the relationship’s *to_user*:

另一方面，如果我想确定哪些用户在关注我，我可以加入*from_user*列，并过滤关系的*to_user*:

```python
(User
 .select()
 .join(Relationship, on=Relationship.from_user)
 .where(Relationship.to_user == charlie))
```

## Joining on arbitrary fields 任意字段连接

If a foreign key does not exist between two tables you can still perform a join, but you must manually specify the join predicate.

In the following example, there is no explicit foreign-key between *User* and *ActivityLog*, but there is an implied relationship between the *ActivityLog.object_id* field and *User.id*. Rather than joining on a specific [`Field`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Field), we will join using an [`Expression`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Expression).

如果两个表之间不存在外键，您仍然可以执行联接，但必须手动指定联接谓词。

在下面的例子中，在*User*和*ActivityLog*之间没有显式的外键，但是在*ActivityLog之间有一个隐含的关系。
object_id*字段和*User.id*。
我们将使用[`Expression`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Expression)进行连接，而不是使用特定的[`Field`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Field)。

```python
user_log = (User
            .select(User, ActivityLog)
            .join(ActivityLog, on=(User.id == ActivityLog.object_id), attr='log')
            .where(
                (ActivityLog.activity_type == 'user_activity') &
                (User.username == 'charlie')))

for user in user_log:
    print(user.username, user.log.description)

#### Print something like ####
charlie logged in
charlie posted a tweet
charlie retweeted
charlie posted a tweet
charlie logged out
```

Note

Recall that we can control the attribute Peewee will assign the joined instance to by specifying the `attr` parameter in the `join()` method. In the previous example, we used the following *join*:

请注意

回想一下，我们可以通过在` join()`方法中指定`attr`参数来控制Peewee将分配给已连接实例的属性。
在前面的例子中，我们使用了以下*join*:

```python
join(ActivityLog, on=(User.id == ActivityLog.object_id), attr='log')
```

Then when iterating over the query, we were able to directly access the joined *ActivityLog* without incurring an additional query:

然后，当遍历查询时，我们能够直接访问已连接的 *ActivityLog*，而无需引发额外的查询:

```python
for user in user_log:
    print(user.username, user.log.description)
```

## Self-joins 自连接

Peewee supports constructing queries containing a self-join.

Peewee支持构造包含自连接的查询。

### Using model aliases 使用模型的别名

To join on the same model (table) twice, it is necessary to create a model alias to represent the second instance of the table in a query. Consider the following model:

为了在同一个模型(表)上连接两次，有必要在查询中创建一个模型别名来表示表的第二个实例。
考虑以下模型:

```python
class Category(Model):
    name = CharField()
    parent = ForeignKeyField('self', backref='children')
```

What if we wanted to query all categories whose parent category is *Electronics*. One way would be to perform a self-join:

如果我们想要查询父类别为*Electronics*的所有类别，该怎么办? 一种方法是执行自连接:

```python
Parent = Category.alias()
query = (Category
         .select()
         .join(Parent, on=(Category.parent == Parent.id))
         .where(Parent.name == 'Electronics'))
```

When performing a join that uses a [`ModelAlias`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ModelAlias), it is necessary to specify the join condition using the `on` keyword argument. In this case we are joining the category with its parent category.

当执行使用[`ModelAlias`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ModelAlias)的连接时，有必要使用`on`关键字参数指定连接条件。在本例中，我们将这个类别与它的父类别连接起来。

### Using subqueries 使用子查询

Another less common approach involves the use of subqueries. Here is another way we might construct a query to get all the categories whose parent category is *Electronics* using a subquery:

另一种不太常见的方法是使用子查询。这里有另一种方法，我们可以构造一个查询，以获得父类别是*Electronics*的所有类别，使用子查询:

```python
Parent = Category.alias()
join_query = Parent.select().where(Parent.name == 'Electronics')

# Subqueries used as JOINs need to have an alias.
join_query = join_query.alias('jq')

query = (Category
         .select()
         .join(join_query, on=(Category.parent == join_query.c.id)))
```

This will generate the following SQL query:

这将生成以下SQL查询:

```python
SELECT t1."id", t1."name", t1."parent_id"
FROM "category" AS t1
INNER JOIN (
  SELECT t2."id"
  FROM "category" AS t2
  WHERE (t2."name" = ?)) AS jq ON (t1."parent_id" = "jq"."id")
```

To access the `id` value from the subquery, we use the `.c` magic lookup which will generate the appropriate SQL expression:

要从子查询中访问`id`值，我们使用`.c `魔法查找，将生成适当的SQL表达式:

```python
Category.parent == join_query.c.id
# Becomes: (t1."parent_id" = "jq"."id")
```



## Implementing Many to Many 实现多对多

Peewee provides a field for representing many-to-many relationships, much like Django does. This feature was added due to many requests from users, but I strongly advocate against using it, since it conflates the idea of a field with a junction table and hidden joins. It’s just a nasty hack to provide convenient accessors.

To implement many-to-many **correctly** with peewee, you will therefore create the intermediary table yourself and query through it:

Peewee提供了一个表示多对多关系的字段，就像Django一样。
这个特性是由于用户的许多请求而添加的，但是我强烈反对使用它，因为它将字段的概念与连接表和隐藏连接合并在一起。
这只是一个提供方便访问器的恶意攻击。

为了正确的使用peewee实现多对多**，你需要自己创建中间表并通过它进行查询:

```python
class Student(Model):
    name = CharField()

class Course(Model):
    name = CharField()

class StudentCourse(Model):
    student = ForeignKeyField(Student)
    course = ForeignKeyField(Course)
```

To query, let’s say we want to find students who are enrolled in math class:

为了进行查询，假设我们想要找到参加数学课的学生:

```python
query = (Student
         .select()
         .join(StudentCourse)
         .join(Course)
         .where(Course.name == 'math'))
for student in query:
    print(student.name)
```

To query what classes a given student is enrolled in:

查询一个给定的学生注册的课程:

```python
courses = (Course
           .select()
           .join(StudentCourse)
           .join(Student)
           .where(Student.name == 'da vinci'))

for course in courses:
    print(course.name)
```

To efficiently iterate over a many-to-many relation, i.e., list all students and their respective courses, we will query the *through* model `StudentCourse` and *precompute* the Student and Course:

为了有效地迭代多对多关系，即列出所有的学生和他们各自的课程，我们将查询through模型`StudentCourse`并预先计算学生和课程:

```python
query = (StudentCourse
         .select(StudentCourse, Student, Course)
         .join(Course)
         .switch(StudentCourse)
         .join(Student)
         .order_by(Student.name))
```

To print a list of students and their courses you might do the following:

要打印学生和他们的课程的列表，你可以做以下工作:

```python
for student_course in query:
    print(student_course.student.name, '->', student_course.course.name)
```

Since we selected all fields from `Student` and `Course` in the *select* clause of the query, these foreign key traversals are “free” and we’ve done the whole iteration with just 1 query.

由于我们在查询的*select*子句中选择了`Student`和`Course`中的所有字段，这些外键遍历是“自由的”，我们只用一个查询就完成了整个迭代。



### ManyToManyField

The [`ManyToManyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField) provides a *field-like* API over many-to-many fields. For all but the simplest many-to-many situations, you’re better off using the standard peewee APIs. But, if your models are very simple and your querying needs are not very complex, [`ManyToManyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField) may work.

[`ManyToManyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField)提供了一个多对多字段的类*字段* API。除了最简单的多对多情况外，您最好使用标准的peewee api。
但是，如果您的模型非常简单，您的查询需求不是非常复杂，[`ManyToManyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField)可能会工作。

Modeling students and courses using [`ManyToManyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField):

使用[`ManyToManyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField)为学生和课程建模:

```python
from peewee import *

db = SqliteDatabase('school.db')

class BaseModel(Model):
    class Meta:
        database = db

class Student(BaseModel):
    name = CharField()

class Course(BaseModel):
    name = CharField()
    students = ManyToManyField(Student, backref='courses')

StudentCourse = Course.students.get_through_model()

db.create_tables([
    Student,
    Course,
    StudentCourse])

# Get all classes that "huey" is enrolled in:
huey = Student.get(Student.name == 'Huey')
for course in huey.courses.order_by(Course.name):
    print(course.name)

# Get all students in "English 101":
engl_101 = Course.get(Course.name == 'English 101')
for student in engl_101.students:
    print(student.name)

# When adding objects to a many-to-many relationship, we can pass
# in either a single model instance, a list of models, or even a
# query of models:
huey.courses.add(Course.select().where(Course.name.contains('English')))

engl_101.students.add(Student.get(Student.name == 'Mickey'))
engl_101.students.add([
    Student.get(Student.name == 'Charlie'),
    Student.get(Student.name == 'Zaizee')])

# The same rules apply for removing items from a many-to-many:
huey.courses.remove(Course.select().where(Course.name.startswith('CS')))

engl_101.students.remove(huey)

# Calling .clear() will remove all associated objects:
cs_150.students.clear()
```

Attention

Before many-to-many relationships can be added, the objects being referenced will need to be saved first. In order to create relationships in the many-to-many through table, Peewee needs to know the primary keys of the models being referenced.

> 注意
>
> 在添加多对多关系之前，需要先保存被引用的对象。为了在多对多through表中创建关系，Peewee需要知道所引用模型的主键。

Warning

It is **strongly recommended** that you do not attempt to subclass models containing [`ManyToManyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField) instances.

> 警告
>
> 强烈建议您不要尝试子类化包含[`ManyToManyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField)实例的模型。

A [`ManyToManyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField), despite its name, is not a field in the usual sense. Instead of being a column on a table, the many-to-many field covers the fact that behind-the-scenes there’s actually a separate table with two foreign-key pointers (the *through table*).

Therefore, when a subclass is created that inherits a many-to-many field, what actually needs to be inherited is the *through table*. Because of the potential for subtle bugs, Peewee does not attempt to automatically subclass the through model and modify its foreign-key pointers. As a result, many-to-many fields typically will not work with inheritance.

For more examples, see:

- [`ManyToManyField.add()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField.add)
- [`ManyToManyField.remove()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField.remove)
- [`ManyToManyField.clear()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField.clear)
- [`ManyToManyField.get_through_model()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField.get_through_model)



一个[`ManyToManyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField)，尽管它的名字，并不是一个通常意义上的字段。多对多字段并不是表上的列，它包含了这样一个事实:在幕后，实际上有一个单独的表，具有两个外键指针(*through表*)。

因此，当创建继承多对多字段的子类时，实际需要继承的是*through表*。由于潜在的细微错误，Peewee不尝试自动地子类化through模型并修改它的外键指针。因此，多对多字段通常不能用于继承。

更多的例子，见:

- [`ManyToManyField.add()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField.add)
- [`ManyToManyField.remove()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField.remove)
- [`ManyToManyField.clear()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField.clear)
- [`ManyToManyField.get_through_model()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ManyToManyField.get_through_model)



## Avoiding the N+1 problem 避免N+1问题

The *N+1 problem* refers to a situation where an application performs a query, then for each row of the result set, the application performs at least one other query (another way to conceptualize this is as a nested loop). In many cases, these *n* queries can be avoided through the use of a SQL join or subquery. The database itself may do a nested loop, but it will usually be more performant than doing *n* queries in your application code, which involves latency communicating with the database and may not take advantage of indices or other optimizations employed by the database when joining or executing a subquery.

Peewee provides several APIs for mitigating *N+1* query behavior. Recollecting the models used throughout this document, *User* and *Tweet*, this section will try to outline some common *N+1* scenarios, and how peewee can help you avoid them.

Attention

In some cases, N+1 queries will not result in a significant or measurable performance hit. It all depends on the data you are querying, the database you are using, and the latency involved in executing queries and retrieving results. As always when making optimizations, profile before and after to ensure the changes do what you expect them to.

*N+1问题*指的是这样一种情况：应用程序执行一个查询，然后对于结果集的每一行，应用程序至少执行另一个查询(另一种将其概念化为嵌套循环的方法)。在很多情况下，这些*n*查询可以通过使用SQL join或子查询来避免。数据库本身可能会做一个嵌套循环，但它通常会比在应用程序代码中执行*n*查询更有性能，这涉及到与数据库通信的延迟，并且在连接或执行子查询时可能不会利用数据库使用的索引或其他优化。

Peewee提供了几个api来减少*N+1*查询行为。回顾本文档中*User*和*Tweet*使用的模型，本节将尝试概述一些常见的*N+1*场景，以及peewee如何帮助您避免它们。

注意

在某些情况下，N+1个查询不会导致显著或可衡量的性能损失。这完全取决于您正在查询的数据、您正在使用的数据库以及执行查询和检索结果所涉及的延迟。与往常一样，在进行优化时，在前后进行概要分析，以确保更改按您的预期进行。



### List recent tweets 最近的微博列表

The twitter timeline displays a list of tweets from multiple users. In addition to the tweet’s content, the username of the tweet’s author is also displayed. The N+1 scenario here would be:

1. Fetch the 10 most recent tweets.
2. For each tweet, select the author (10 queries).

By selecting both tables and using a *join*, peewee makes it possible to accomplish this in a single query:

twitter时间线显示来自多个用户的tweet列表。除了tweet的内容之外，还显示了tweet作者的用户名。这里的N+1情形是:

1. 
获取最近的10条tweet。
2. 
对于每条推文，选择作者(10个查询)。

通过选择两个表并使用*join*， peewee可以在单个查询中完成:

```python
query = (Tweet
         .select(Tweet, User)  # Note that we are selecting both models.
         .join(User)  # Use an INNER join because every tweet has an author.
         .order_by(Tweet.id.desc())  # Get the most recent tweets.
         .limit(10))

for tweet in query:
    print(tweet.user.username, '-', tweet.message)
```

Without the join, accessing `tweet.user.username` would trigger a query to resolve the foreign key `tweet.user` and retrieve the associated user. But since we have selected and joined on `User`, peewee will automatically resolve the foreign-key for us.

Note

This technique is discussed in more detail in [Selecting from multiple sources](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#multiple-sources).

如果没有join，则访问`tweet.user.username`将触发一个查询来解析外键`tweet.user`，并检索关联的用户。但由于我们已经选择并加入了`User`，peewee将自动为我们解析外键。



请注意

这种技术在[从多个来源中选择](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#multiple-sources)中有更详细的讨论。



### List users and all their tweets 列出用户及其所有tweet

Let’s say you want to build a page that shows several users and all of their tweets. The N+1 scenario would be:

1. Fetch some users.
2. For each user, fetch their tweets.

This situation is similar to the previous example, but there is one important difference: when we selected tweets, they only have a single associated user, so we could directly assign the foreign key. The reverse is not true, however, as one user may have any number of tweets (or none at all).

Peewee provides an approach to avoiding *O(n)* queries in this situation. Fetch users first, then fetch all the tweets associated with those users. Once peewee has the big list of tweets, it will assign them out, matching them with the appropriate user. This method is usually faster but will involve a query for each table being selected.

假设您想构建一个页面，显示几个用户和他们的所有tweet。N+1的情形是:

1. 
获取一些用户。
2. 
对于每个用户，获取他们的tweet。

这种情况与前面的示例类似，但有一个重要的区别:当我们选择tweets时，它们只有一个关联的用户，因此我们可以直接分配外键。然而，反过来就不成立了，因为一个用户可能有任意数量的tweet(或者根本没有tweet)。

Peewee提供了一种在这种情况下避免*O(n)*查询的方法。首先获取用户，然后获取与这些用户关联的所有tweet。一旦peewee有了一个很大的推文列表，它就会把它们分配出去，匹配到合适的用户。这种方法通常更快，但需要对所选的每个表进行查询。



### Using prefetch 使用预取

peewee supports pre-fetching related data using sub-queries. This method requires the use of a special API, [`prefetch()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#prefetch). Prefetch, as its name implies, will eagerly load the appropriate tweets for the given users using subqueries. This means instead of *O(n)* queries for *n* rows, we will do *O(k)* queries for *k* tables.

Here is an example of how we might fetch several users and any tweets they created within the past week.

peewee支持使用子查询预取相关数据。这个方法需要使用特殊的API [`prefetch()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#prefetch)。顾名思义，Prefetch将使用子查询急切地为给定用户加载适当的tweet。这意味着我们将代替对*n*行进行*O(n)*查询，对*k*表进行*O(k)*查询。

下面是一个示例，说明我们如何获取几个用户和他们在过去一周内创建的任何tweet。

```python
week_ago = datetime.date.today() - datetime.timedelta(days=7)
users = User.select()
tweets = (Tweet
          .select()
          .where(Tweet.timestamp >= week_ago))

# This will perform two queries.
users_with_tweets = prefetch(users, tweets)

for user in users_with_tweets:
    print(user.username)
    for tweet in user.tweets:
        print('  ', tweet.message)
```

Note

Note that neither the `User` query, nor the `Tweet` query contained a JOIN clause. When using [`prefetch()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#prefetch) you do not need to specify the join.

[`prefetch()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#prefetch) can be used to query an arbitrary number of tables. Check the API documentation for more examples.

Some things to consider when using [`prefetch()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#prefetch):

- Foreign keys must exist between the models being prefetched.
- LIMIT works as you’d expect on the outer-most query, but may be difficult to implement correctly if trying to limit the size of the sub-selects.

请注意

注意，`User`查询和`Tweet`查询都不包含一个JOIN子句。当使用[`prefetch()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#prefetch)时，不需要指定联接。

[`prefetch()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#prefetch)可以查询任意数量的表。查看API文档以获取更多示例。

使用[`prefetch()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#prefetch):

- 被预取的模型之间必须存在外键。

- LIMIT如你所期望的那样在最外部的查询上工作，但是如果试图限制子选择的大小，可能很难正确实现。





http://docs.peewee-orm.com/en/latest/peewee/quickstart.html)