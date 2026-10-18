import mysql.connector
def get_db_connection():
 db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="chitra@123",
    database="Internship_and_job_allocation_system"
)

 return db