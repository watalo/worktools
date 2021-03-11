#%%
from peewee import *
from datetime import date

database = 'pools.db'

db = SqliteDatabase(database)

class BaseModel(Model):
    class Meta:
        database = db

class Project(BaseModel):
    corption_name = CharField()
    menber = CharField()
    stutas = CharField()
    notional_amount = FloatField()
    exposure_amount = FloatField()
    used_ntl_amount = FloatField()
    used_esp_amount = FloatField()
    blns_ntl_amount = FloatField()
    blns_esp_amount = FloatField()
    start_date = DateField()
    end_date = DateField()


class Product(BaseModel):
    scheme = ForeignKeyField(Project, backref='products')
    catagory = CharField()
    notional_amount = FloatField()
    exposure_amount = FloatField()
    deposits_amount = FloatField()
    start_date = DateField()
    end_date = DateField()

db.connect()
db.create_tables([Project, Product])
#%%
dyg = Project.create(
    corption_name = '东阳光',
    menber = '吴然',
    stutas = '营销中',
    notional_amount = 0,
    exposure_amount = 0,
    used_ntl_amount = 0,
    used_esp_amount = 0,
    blns_ntl_amount = 0,
    blns_esp_amount = 0,
    start_date = date(2021, 2, 10),
    end_date = date(2021, 6, 30),
)
dyg.save()
#%%
dyg.stutas = '已上报'
dyg.save()

def get_pifu(proj_obj, na, ea, start_date, end_date):
    proj_obj.stutas = '已批未投'
    proj_obj.notional_amount = na
    proj_obj.exposure_amount = ea
    proj_obj.start_date = start_date
    proj_obj.end_date = end_date
    proj_obj.save()


get_pifu(dyg, 15000, 9000, date(2021, 3, 13), date(2021, 9, 22))

#%%
inflow_proj = Project.select().where(Project.stutas == '已批未投')
for proj in inflow_proj:
    print(proj.corption_name)
# dyg_loans = Product.create(
#     scheme = dyg,
#     catagory = '流贷',
#     notional_amount = 9000,
#     exposure_amount = 9000,
#     deposits_amount = 2000,
#     start_date = DateField(2021, 3, 2),
#     end_date = DateField(2022, 3, 19)
# )




# %%
db.close()
# %%
