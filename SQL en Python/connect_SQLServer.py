import pyodbc

conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL server};'
'Server = DESKTOP-OA06KFP;'
'Database=Northwind;'
'UID=DESKTOP-OA06KFP\Diego;')

cursor = conn.cursor();
cursor.execute('select * from Orders')

for row in cursor:
    print (row)