from . import prod
from . import proj
from . import conf
from tinydb import Tinydb, Query


class Pool(object):

    def __init__(self, ):
        self.db = Tinydb(conf.db_path)
        