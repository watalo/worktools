#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@NAME		:conf.py
@TIME		:2021/03/03 04:33:46
@AUTHOR     :watalo
@VERSION	:0.0.x
'''
'''
路径配置文件
'''


import os


db_path = os.getcwd() + '/project_pool/db/db.json'

def output_files_path(): 
    output_files_path = os.getcwd() + 'project/output'
    if os.path.exists(output_files_path):
        return output_files_path
    else:
        os.mkdir(output_files_path)
        return output_files_path

if __name__ == '__main__':
    output_files_path()
