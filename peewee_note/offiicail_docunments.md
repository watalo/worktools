# Quickstart

This document presents a brief, high-level overview of Peewee’s primary features. This guide will cover:

- [Model Definition](http://docs.peewee-orm.com/en/latest/peewee/quickstart.html#model-definition)
- [Storing data](http://docs.peewee-orm.com/en/latest/peewee/quickstart.html#storing-data)
- [Retrieving Data](http://docs.peewee-orm.com/en/latest/peewee/quickstart.html#retrieving-data)

Note

If you’d like something a bit more meaty, there is a thorough tutorial on [creating a “twitter”-style web app](http://docs.peewee-orm.com/en/latest/peewee/example.html#example-app) using peewee and the Flask framework. In the projects folder you can find more self-contained Peewee examples, like a [blog app](https://github.com/coleifer/peewee/tree/master/examples/blog).`examples/`

I **strongly** recommend opening an interactive shell session and running the code. That way you can get a feel for typing in queries.



## Model Definition

Model classes, fields and model instances all map to database concepts:

| Object         | Corresponds to…         |
| -------------- | ----------------------- |
| Model class    | Database table          |
| Field instance | Column on a table       |
| Model instance | Row in a database table |

When starting a project with peewee, it’s typically best to begin with your data model, by defining one or more [`Model`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model) classes:

```python
from peewee import *

db = SqliteDatabase('people.db')

class Person(Model):
    name = CharField()
    birthday = DateField()

    class Meta:
        database = db # This model uses the "people.db" database.
```

Note

Peewee will automatically infer the database table name from the name of the class. You can override the default name by specifying a attribute in the inner “Meta” class (alongside the attribute). To learn more about how Peewee generates table names, refer to the [Table Names](http://docs.peewee-orm.com/en/latest/peewee/models.html#table-names) section.`table_name``database`

Also note that we named our model instead of . This is a convention you should follow – even though the table will contain multiple people, we always name the class using the singular form.`Person``People`

There are lots of [field types](http://docs.peewee-orm.com/en/latest/peewee/models.html#fields) suitable for storing various types of data. Peewee handles converting between *pythonic* values those used by the database, so you can use Python types in your code without having to worry.

Things get interesting when we set up relationships between models using [foreign key relationships](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#relationships). This is simple with peewee:

```python
class Pet(Model):
    owner = ForeignKeyField(Person, backref='pets')
    name = CharField()
    animal_type = CharField()

    class Meta:
        database = db # this model uses the "people.db" database
```

Now that we have our models, let’s connect to the database. Although it’s not necessary to open the connection explicitly, it is good practice since it will reveal any errors with your database connection immediately, as opposed to some arbitrary time later when the first query is executed. It is also good to close the connection when you are done – for instance, a web app might open a connection when it receives a request, and close the connection when it sends the response.

```python
db.connect()
```

We’ll begin by creating the tables in the database that will store our data. This will create the tables with the appropriate columns, indexes, sequences, and foreign key constraints:

```
db.create_tables([Person, Pet])
```

## Storing data

Let’s begin by populating the database with some people. We will use the [`save()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.save) and [`create()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.create) methods to add and update people’s records.

```python
from datetime import date
uncle_bob = Person(name='Bob', birthday=date(1960, 1, 15))
uncle_bob.save() # bob is now stored in the database
# Returns: 1
```

Note

When you call [`save()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.save), the number of rows modified is returned.

You can also add a person by calling the [`create()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.create) method, which returns a model instance:

```python
grandma = Person.create(name='Grandma', birthday=date(1935, 3, 1))
herb = Person.create(name='Herb', birthday=date(1950, 5, 5))
```

To update a row, modify the model instance and call [`save()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.save) to persist the changes. Here we will change Grandma’s name and then save the changes in the database:

```python
grandma.name = 'Grandma L.'
grandma.save()  # Update grandma's name in the database.
# Returns: 1
```

Now we have stored 3 people in the database. Let’s give them some pets. Grandma doesn’t like animals in the house, so she won’t have any, but Herb is an animal lover:

```python
bob_kitty = Pet.create(owner=uncle_bob, name='Kitty', animal_type='cat')
herb_fido = Pet.create(owner=herb, name='Fido', animal_type='dog')
herb_mittens = Pet.create(owner=herb, name='Mittens', animal_type='cat')
herb_mittens_jr = Pet.create(owner=herb, name='Mittens Jr', animal_type='cat')
```

After a long full life, Mittens sickens and dies. We need to remove him from the database:

```python
herb_mittens.delete_instance() # he had a great life
# Returns: 1
```

Note

The return value of [`delete_instance()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.delete_instance) is the number of rows removed from the database.

Uncle Bob decides that too many animals have been dying at Herb’s house, so he adopts Fido:

```pthon
herb_fido.owner = uncle_bob
herb_fido.save()
```

## Retrieving Data

The real strength of our database is in how it allows us to retrieve data through *queries*. Relational databases are excellent for making ad-hoc queries.

### Getting single records

Let’s retrieve Grandma’s record from the database. To get a single record from the database, use :`Select.get()`

```
grandma = Person.select().where(Person.name == 'Grandma L.').get()
```

We can also use the equivalent shorthand [`Model.get()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get):

```
grandma = Person.get(Person.name == 'Grandma L.')
```

### Lists of records

Let’s list all the people in the database:

```python
for person in Person.select():
    print(person.name)

# prints:
# Bob
# Grandma L.
# Herb
```

Let’s list all the cats and their owner’s name:

```python
query = Pet.select().where(Pet.animal_type == 'cat')
for pet in query:
    print(pet.name, pet.owner.name)

# prints:
# Kitty Bob
# Mittens Jr Herb
```

Attention

There is a big problem with the previous query: because we are accessing and we did not select this relation in our original query, peewee will have to perform an additional query to retrieve the pet’s owner. This behavior is referred to as [N+1](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#nplusone) and it should generally be avoided.`pet.owner.name`

For an in-depth guide to working with relationships and joins, refer to the [Relationships and Joins](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#relationships) documentation.

We can avoid the extra queries by selecting both *Pet* and *Person*, and adding a *join*.

```python
query = (Pet
         .select(Pet, Person)
         .join(Person)
         .where(Pet.animal_type == 'cat'))

for pet in query:
    print(pet.name, pet.owner.name)

# prints:
# Kitty Bob
# Mittens Jr Herb
```

Let’s get all the pets owned by Bob:

```python
for pet in Pet.select().join(Person).where(Person.name == 'Bob'):
    print(pet.name)

# prints:
# Kitty
# Fido
```

We can do another cool thing here to get bob’s pets. Since we already have an object to represent Bob, we can do this instead:

```python
for pet in Pet.select().where(Pet.owner == uncle_bob):
    print(pet.name)
```

### Sorting

Let’s make sure these are sorted alphabetically by adding an clause:`order_by()`

```python
for pet in Pet.select().where(Pet.owner == uncle_bob).order_by(Pet.name):
    print(pet.name)

# prints:
# Fido
# Kitty
```

Let’s list all the people now, youngest to oldest:

```python
for person in Person.select().order_by(Person.birthday.desc()):
    print(person.name, person.birthday)

# prints:
# Bob 1960-01-15
# Herb 1950-05-05
# Grandma L. 1935-03-01
```

### Combining filter expressions

Peewee supports arbitrarily-nested expressions. Let’s get all the people whose birthday was either:

- before 1940 (grandma)
- after 1959 (bob)

```python
d1940 = date(1940, 1, 1)
d1960 = date(1960, 1, 1)
query = (Person
         .select()
         .where((Person.birthday < d1940) | (Person.birthday > d1960)))

for person in query:
    print(person.name, person.birthday)

# prints:
# Bob 1960-01-15
# Grandma L. 1935-03-01
```

Now let’s do the opposite. People whose birthday is between 1940 and 1960:

```python
query = (Person
         .select()
         .where(Person.birthday.between(d1940, d1960)))

for person in query:
    print(person.name, person.birthday)

# prints:
# Herb 1950-05-05
```

### Aggregates and Prefetch

Now let’s list all the people *and* how many pets they have:

```python
for person in Person.select():
    print(person.name, person.pets.count(), 'pets')

# prints:
# Bob 2 pets
# Grandma L. 0 pets
# Herb 1 pets
```

Once again we’ve run into a classic example of [N+1](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#nplusone) query behavior. In this case, we’re executing an additional query for every returned by the original ! We can avoid this by performing a *JOIN* and using a SQL function to aggregate the results.`Person``SELECT`

```python
query = (Person
         .select(Person, fn.COUNT(Pet.id).alias('pet_count'))
         .join(Pet, JOIN.LEFT_OUTER)  # include people without pets.
         .group_by(Person)
         .order_by(Person.name))

for person in query:
    # "pet_count" becomes an attribute on the returned model instances.
    print(person.name, person.pet_count, 'pets')

# prints:
# Bob 2 pets
# Grandma L. 0 pets
# Herb 1 pets
```

Note

Peewee provides a magical helper [`fn()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#fn), which can be used to call any SQL function. In the above example, would be translated into .`fn.COUNT(Pet.id).alias('pet_count')``COUNT(pet.id) AS pet_count`

Now let’s list all the people and the names of all their pets. As you may have guessed, this could easily turn into another [N+1](http://docs.peewee-orm.com/en/latest/peewee/relationships.html#nplusone) situation if we’re not careful.

Before diving into the code, consider how this example is different from the earlier example where we listed all the pets and their owner’s name. A pet can only have one owner, so when we performed the join from to , there was always going to be a single match. The situation is different when we are joining from to because a person may have zero pets or they may have several pets. Because we’re using a relational databases, if we were to do a join from to then every person with multiple pets would be repeated, once for each pet.`Pet``Person``Person``Pet``Person``Pet`

It would look like this:

```python
query = (Person
         .select(Person, Pet)
         .join(Pet, JOIN.LEFT_OUTER)
         .order_by(Person.name, Pet.name))
for person in query:
    # We need to check if they have a pet instance attached, since not all
    # people have pets.
    if hasattr(person, 'pet'):
        print(person.name, person.pet.name)
    else:
        print(person.name, 'no pets')

# prints:
# Bob Fido
# Bob Kitty
# Grandma L. no pets
# Herb Mittens Jr
```

Usually this type of duplication is undesirable. To accommodate the more common (and intuitive) workflow of listing a person and attaching **a list** of that person’s pets, we can use a special method called [`prefetch()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ModelSelect.prefetch):

```python
query = Person.select().order_by(Person.name).prefetch(Pet)
for person in query:
    print(person.name)
    for pet in person.pets:
        print('  *', pet.name)

# prints:
# Bob
#   * Kitty
#   * Fido
# Grandma L.
# Herb
#   * Mittens Jr
```

### SQL Functions

One last query. This will use a SQL function to find all people whose names start with either an upper or lower-case *G*:

```python
expression = fn.Lower(fn.Substr(Person.name, 1, 1)) == 'g'
for person in Person.select().where(expression):
    print(person.name)

# prints:
# Grandma L.
```

This is just the basics! You can make your queries as complex as you like. Check the documentation on [Querying](http://docs.peewee-orm.com/en/latest/peewee/querying.html#querying) for more info.

## Database

We’re done with our database, let’s close the connection:

```css
db.close()
```

In an actual application, there are some established patterns for how you would manage your database connection lifetime. For example, a web application will typically open a connection at start of request, and close the connection after generating the response. A [connection pool](http://docs.peewee-orm.com/en/latest/peewee/database.html#connection-pooling) can help eliminate latency associated with startup costs.

To learn about setting up your database, see the [Database](http://docs.peewee-orm.com/en/latest/peewee/database.html#database) documentation, which provides many examples. Peewee also supports [configuring the database at run-time](http://docs.peewee-orm.com/en/latest/peewee/database.html#deferring-initialization) as well as setting or changing the database at any time.

### Working with existing databases

If you already have a database, you can autogenerate peewee models using [pwiz, a model generator](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#pwiz). For instance, if I have a postgresql database named *charles_blog*, I might run:

```css
python -m pwiz -e postgresql charles_blog > blog_models.py
```

## What next?

That’s it for the quickstart. If you want to look at a full web-app, check out the [Example app](http://docs.peewee-orm.com/en/latest/peewee/example.html#example-app).