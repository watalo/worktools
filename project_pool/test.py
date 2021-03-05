from bin import conf, pool, prod, proj
x = prod.Loans(9000)
print(x.info())
pj = proj.Inflow('东阳光', '杨佳琪')
pj.scheme_add(x)
print(pj.scheme_info())

