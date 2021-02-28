#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@NAME		:prod.py
@TIME		:2021/02/28 23:02:04
@AUTHOR     :watalo
@VERSION	:0.0.x
'''

class Loans(object):
    '''
    表内贷款
    '''
    
    def __init__(self, amount, start_time, end_time, interest_rate, info):
        '''
        :description: 
        :param {amount}: 字面，如下
        :param {start_time}:
        :param {end_time}:
        :param {interest_rate}:
        :param {info}:
        :return:
        '''
        self.amount = amount
        self.start_time = start_time
        self.end_time = end_time
        self.interest_rate = interest_rate
        self.info = info

    def length(self):
        return self.end_time - self.start_time
    
    def float_rate(self):
        base_rate_dict = {1:0.0365, 3:0.0385, 5:0.0435}
        if self.length() <= 365:
            return 100*((self.interest_rate/base_rate_dict[1]) - 1)
        if self.length() >= 365 and self.length() <= 365*3:
            return 100*((self.interest_rate/base_rate_dict[3]) - 1)
        if self.length() >= 365*5:
            return 100*((self.interest_rate/base_rate_dict[5]) - 1)
        else:
            pass
    
    def amount_adjust(self, amount):
        pass

class Notes(object):
    '''
    银行承兑汇票
    '''
    def __init__(self, var):
        '''
        :description:
        :param {var}:
        :return:
        '''
        self.var = var
        pass

class Letters(object):
    '''
    :description:
    '''
    def __init__(self, var):
        '''
        :description:
        :param {var}:
        :return:
        '''
        self.var = var
        pass


if __name__ == '__main__':
    pass