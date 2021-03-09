import sqlite3



class Main():

    def __init__(self, db_path):
        self.con = sqlite3.connect('example.db')
        self.cur = self.con.cursor()

    def create_table(self, tabel_name, *args, **kwargs):
        sql_srcipts = 'CREATE TABlE {table_name}({})'.format(tabel_name, args)
        self.cur.execute(sql_srcipts)
 

con = sqlite3.connect('example.db')
cur = con.cursor()


# 使用函数定义SQL语句命令，让语句简单化
cur.execute()

    cur.execute('''SELECT * FROM tablename''')
    res = cur.fetchall()

    cur.execute("DELETE from tablename WHERE ID=11083041")
    res = cur.fetchall()

    def insert(table_name,condition):
        
        return 
# 明天学习sqlite语法，https://www.runoob.com/sqlite/sqlite-where-clause.html        


    print(res)