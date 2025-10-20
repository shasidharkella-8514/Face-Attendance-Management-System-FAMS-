import mysql.connector

def connect_mysql():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # change if you have different username
        password="",          # add password if set
        database="attendance_db"       # replace with your DB name
    )

def cleanup_database():
    conn = connect_mysql()
    cur = conn.cursor()

    print("🧹 Cleaning up demo data...")
    try:
        # remove demo users
        cur.execute("DELETE FROM students WHERE name = 'John Doe';")
        # optional: start completely fresh
        # cur.execute("TRUNCATE TABLE students;")
        # cur.execute("TRUNCATE TABLE attendance;")
        conn.commit()
        print("✅ Cleanup complete!")
    except Exception as e:
        print("⚠️ Error:", e)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    cleanup_database()



