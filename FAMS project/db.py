# reset_ids.py
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",    # your password if any
    database="attendance_db"
)
cur = conn.cursor()

cur.execute("TRUNCATE TABLE attendance;")  # deletes all records and resets ID
cur.execute("TRUNCATE TABLE students;")    # optional — if you also want to reset students
conn.commit()

print("✅ Tables cleared and AUTO_INCREMENT reset to 1.")
cur.close()
conn.close()

