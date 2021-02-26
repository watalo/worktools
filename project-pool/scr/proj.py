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

import tinydb
from datetime import date

class Inflow(object):

    def __init__(self, name):
        self.name = name
        self.status()
        self.scheme()

    def status(self):
        status_list = ['调查中', '评议会', '审查中', '待上会', '已获批']
        opt = input("项目目前处于什么进度（1-'调查中'、2-'评议会'、3-'审查中'、4-'待上会'、5-'已获批）:")
        

    def scheme(self):

        
    




if __name__ == '__main__':
    xx = Inflow('HEC')
    