#1、新增授信项目
from bin import pool, prod, proj
# 项目的基本要素
# name = '宜昌东阳光药业股份有限公司'
# member = '杨佳琪'
# # 贷款产品的要素
# pd = prod.Loans(9000)
# pd2 = prod.Loans(4000)
# pd3 = prod.Notes(3000,1500)
# pj = proj.Inflow(name, member)
# pj.scheme_add(pd)
# pj.scheme_add(pd2)
# pj.scheme_add(pd3)
# print(pj.scheme_info())


pool = pool.Pool()
# pool.insert(pj, 'inflow')
# pj.status_fresh(3)
for i in pool.inflow.all():
    print(i)
