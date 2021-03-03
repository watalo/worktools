import os
from bin import conf
from bin import pool
from tinydb import TinyDB


x = pool.Pool()
x.inflow.insert({'type': 'apple', 'count': 7})
x.finish.insert({'type': 'apple', 'count': 7})
x.plan.insert({'type': 'apple', 'count': 7})