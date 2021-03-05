#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@NAME		:proj.py
@TIME		:2021/02/27 03:19:43
@AUTHOR     :watalo
@VERSION	:0.0.1
'''
'''
项目分为3种：
1、流程项目
    属性：
    - 企业名称
    - 项目状态：['调查中'、'评议会'、'审查中'、'待上会'、'已获批']
    - 项目属性
        - 金额
        - 品种: []
        - 负责人
        - 完成时限

2、投放项目
    属性：
    - 企业名称
    - 品种:['表内'、'表外']
    - 金额
    - 起始日期
    - 到期日期
    - 收益率

3、计划项目
    属性：
    - 企业名称
    - 拜访进度
    - 营销方案
    - 完成时限

'''

from datetime import datetime

class Inflow(object):
    '''
    流程中的项目类，封装以下属性：
        - 企业名称
        - 项目状态
        - 项目属性：继承prod模块中的各种产品类

    '''
    def __init__(self, name, member):
        self.name = name
        self.member = member
        self.status = '新增'
        self.scheme = []
        
    def status_fresh(self, index):
        '''
        :description: 刷新项目状态，数据库中新增项目返回'调查中'
        :param {index}: 列表索引值--> [0, 4]
        :return: 5种状态之一
        '''
        status_list = ['调查中', '评议会', '审查中', '已上会', '已获批']
        # opt = input("项目目前处于什么进度（1-'调查中'、2-'评议会'、3-'审查中'、4-'待上会'、5-'已获批）:")
        if self.stauts == '新增':
            self.status = status_list[index]
        else:
            if index < status_list.index(self.status): 
                self.info_add('！！！流程回退，原因为【】')
            else:
                self.status = status_list[index]
   
    def scheme_add(self, prod_obj):
        self.scheme.append(prod_obj)
    
    def scheme_adjust(self, prod_obj_list):
        self.scheme = prod_obj_list

    def scheme_info(self):
        try:
            amount = 0
            description = ''
            for prod_obj in self.scheme:
                amount += prod_obj.amount
                description = '' + prod_obj.info()
            res = '{time}:综合授信{am}万元，其中{desc}。'.format(
                time = str(datetime.now())[:-7],
                am = amount,
                desc = description
            )
            return res
        except:
            return '{}:方案待定'.format(str(datetime.now())[:-7])    

    def info_add(self, description):
        self.info.append('{time}:{desc}'.format(
            time = str(datetime.now())[:-7], 
            desc = description
            ))

    def member_adjust(self, new_member):
        self.member = new_member
    
    def write_db(self):
        '''
        :description:将上述信息写入数据库
        :param {var}:None
        :return: 更新数据库
        '''
        pass

class Finish(object):
    '''
    已投放的项目类，封装以下属性：
        - 企业名称
        - 品种
        - 金额
        - 起始日期
        - 到期日期
        - 收益率
        - 备注：保证金多少
    '''
    def __init__(self, inflow_obj, prod_obj, info = None):
        self.amount = inflow_obj.name
        self.category = prod_obj.category
        self.starttime = prod_obj.starttime         
        self.endtime = prod_obj.endtime
        self.revenue_rate = prod_obj.revenue_rate
        self.info = info

    def write_db(self):
        '''
        :description:将上述信息写入数据库
        :param {var}:None
        :return: 更新数据库
        '''
        pass

class Plan(object):

    def __init__(self, name, progress, member, prod_obj_list, deadline) -> None:
        self.name = name
        self.progress = progress
        self.scheme = prod_obj_list
        self.deadline = deadline
        self.member = member


    def write_db(self):
        '''
        :description:将上述信息写入数据库
        :param {var}:None
        :return: 更新数据库
        '''
        pass

if __name__ == '__main__':
    pass