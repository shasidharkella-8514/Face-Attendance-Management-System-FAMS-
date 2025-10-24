import mysql.connector
import pandas as pd

# ✅ Connect to your MySQL database
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # update if your MySQL has a password
        database="attendance_db"
    )

    if conn.is_connected():
        print("✅ Connected to MySQL Database\n")

        # --- View Students Table ---
        print("🎓 STUDENTS TABLE DATA:")
        students_df = pd.read_sql("SELECT * FROM students", conn)
        print(students_df.to_string(index=False))  # pretty print

        print("\n--------------------------------------------\n")

        # --- View Attendance Table ---
        print("🕒 ATTENDANCE TABLE DATA:")
        attendance_df = pd.read_sql("SELECT * FROM attendance ORDER BY id ASC", conn)
        print(attendance_df.to_string(index=False))

        conn.close()
        print("\n🔒 Connection closed.")

except Exception as e:
    print(f"❌ Error: {e}")

students_df.to_csv("students_data.csv", index=False)
attendance_df.to_csv("attendance_data.csv", index=False)
print("📁 Exported both tables to CSV files in your folder.")


