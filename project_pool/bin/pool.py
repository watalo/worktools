from . import prod
from . import proj
from . import conf
from tinydb import TinyDB, Query
from openpyxl import Workbook


class Pool(object):

    def __init__(self):
        self.db = TinyDB(conf.db_path)
        self.inflow = self.db.table('流程项目')
        self.finish = self.db.table('投放项目')
        self.plan = self.db.table('计划项目')



    def Inflow():
        pass


