#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
年金账单从文件名生成清单（xlsx）
@NAME		:annuity.py
@TIME		:2021/02/23 17:18:59
@AUTHOR     :watalo
@VERSION	:0.0.x
'''
from openpyxl import Workbook
import os

class Stat:
    def __init__(self, dir):
        self.source_path = dir

    def search(self):
        opt = []
        for home, dirs, files in os.walk(self.source_path):
            for filename in files:
                all = filename.split('-')
                opt.append(all)
        return opt

    def mkxlsx(self):
        wb = Workbook()
        ws = wb.active
        ws.title = '年金账单'
        i = 1
        for var_list in self.search():
            ws.append([i, var_list[0], var_list[1], var_list[2].split('.')[0]])
            i = i+1 
        wb.save('年金账单明细.xlsx')


if __name__ == '__main__':
    XF = Stat('C:/Users/watalo/Desktop/兴发年金账单')
    XF.mkxlsx()
    