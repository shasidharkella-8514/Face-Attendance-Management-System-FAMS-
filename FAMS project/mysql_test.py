import mysql.connector

def connect_mysql():
    """Connect to MySQL database (adjust credentials)."""
    return mysql.connector.connect(
        host="localhost",
        user="root",        # your MySQL username
        password="",        # your MySQL password
        database="attendance_db"  # your database name
    )

def show_attendance():
    """Fetch and display attendance in ascending order by ID."""
    conn = connect_mysql()
    cur = conn.cursor()

    cur.execute("SELECT id, enrollment, name, department, time, date FROM attendance ORDER BY id ASC")
    records = cur.fetchall()

    print("🧾 Attendance Records (Oldest → Latest):\n")
    for row in records:
        print(f"ID: {row[0]}, Enrollment: {row[1]}, Name: {row[2]}, Department: {row[3]}, Time: {row[4]}, Date: {row[5]}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    show_attendance()




