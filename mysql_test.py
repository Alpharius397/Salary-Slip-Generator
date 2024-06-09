import mysql.connector as mysql

mydb = mysql.connect(
  host="localhost",
  user="root",
  password="08222004",
  port="3306"
)

print(mydb)