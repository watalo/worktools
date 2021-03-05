from . import prod
from . import proj
from . import conf
from tinydb import TinyDB, Query
# from openpyxl import Workbook
'''
数据写入读取的汇总池类：
属性：
    TinyDB中的三张表：
        - 流程项目
        - 投放项目
        - 计划项目
方法：
    - 增加条目 
    - 删除条目
    - 修改条目
    - 查询条目
    - 输出
'''



class Pool(object):

    def __init__(self):
        self.db = TinyDB(conf.db_path)
        self.inflow = self.db.table('流程项目')
        self.finish = self.db.table('投放项目')
        self.plan = self.db.table('计划项目')

    def insert(self, proj_obj, catagery):
        if catagery == 'inflow':
            self.inflow.insert({
                '企业名称' : proj_obj.name,
                '主办人' : proj_obj.member,
                '状态' : proj_obj.status,
                '方案' : proj_obj.scheme_info,
                '备注' : proj_obj.info,
            })
        elif catagery == 'finish':
            pass
        elif catagery == 'plan':
            pass

    def desert(self):
        pass

    def adjust(self):
        pass

    def search(self):
        pass

    def output(self):
        pass
    



