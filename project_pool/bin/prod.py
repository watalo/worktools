#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@NAME		:prod.py
@TIME		:2021/02/28 23:02:04
@AUTHOR     :watalo
@VERSION	:0.0.x
'''
'''
产品类，封装各种产品的属性
    -贷款
    -银票
    -保函
    ...
'''

class Loans(object):
    '''
    表内贷款
    '''
    
    def __init__(self, amount, start_time = None, end_time = None, revenue_rate = None):
        '''
        :description: 
        :param {amount}: 字面，如下
        :param {start_time}:
        :param {end_time}:
        :param {revenue_rate}:
        :param {info}:
        :return:
        '''
        self.amount = amount
        self.start_time = start_time
        self.end_time = end_time
        self.revenue_rate = revenue_rate

    def length(self):
        return self.end_time - self.start_time
    
    def float_rate(self):
        base_rate_dict = {1:0.0365, 3:0.0385, 5:0.0435}
        if self.length() <= 365:
            return 100*((self.revenue_rate/base_rate_dict[1]) - 1)
        if self.length() >= 365 and self.length() <= 365*3:
            return 100*((self.revenue_rate/base_rate_dict[3]) - 1)
        if self.length() >= 365*5:
            return 100*((self.revenue_rate/base_rate_dict[5]) - 1)
        else:
            pass
    
    def amount_adjust(self, new_amount):
        self.amount = new_amount

    def info(self):
        res = '贷款额度{}万元'.format(self.amount)
        return res

class Notes(object):
    '''
    银行承兑汇票
    '''
    def __init__(self, amount, start_time, end_time, revenue_rate, bargain):
        '''
        :description: 
        :param {amount}: 字面，如下
        :param {start_time}:
        :param {end_time}:
        :param {revenue_rate}:
        :param {bargain}:
        :return:
        '''
        self.amount = amount
        self.start_time = start_time
        self.end_time = end_time
        self.revenue_rate = revenue_rate
        self.bargain = bargain

    def bargain_rate(self):
        return self.bargain / self.amount

    def info(self):
        res = '银票总额{}，形成保证金存款{}'.format(self.amount, self.bargain)
        return res


class Letters(object):
    '''
    保函
    '''
    def __init__(self, amount, start_time, end_time, revenue_rate, bargain):
        '''
        :description: 
        :param {amount}: 字面，如下
        :param {start_time}:
        :param {end_time}:
        :param {revenue_rate}:
        :param {bargaain}:
        :return:
        '''
        self.amount = amount
        self.start_time = start_time
        self.end_time = end_time
        self.revenue_rate = revenue_rate
        self.bargain = bargain

    def bargain_rate(self):
        return self.bargain / self.amount

if __name__ == '__main__':
    xx = Loans(1000)
    print(xx.info())