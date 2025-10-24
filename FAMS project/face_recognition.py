"""
Face Attendance Management System (FAMS) - Updated
-------------------------------------------------

- Added Enrollment ID to registration
- Admin-only dashboard (username/password)
- added Manual Attendance tab
- DeepFace preload in background to avoid blocking GUI
- Saves registration images as: ENROLLMENT_NAME_count.jpg
- Stores students in `students` table and attendance in `attendance` table
- Dark themed CustomTkinter GUI
- Step-by-step GUI logs and console output
"""

import os
import cv2
import time
import threading
import numpy as np
from datetime import datetime
from PIL import Image
import mysql.connector
from deepface import DeepFace        # requires DeepFace installed  
DeepFace.build_model("VGG-Face")
import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
import pandas as pd
import csv


def admin_attendance_window():
    """Admin panel window showing attendance records in ascending order with refresh."""
    win = tk.Toplevel()
    win.title("Admin Attendance Panel")
    win.geometry("900x500")

    # --- Treeview for Attendance ---
    global tree
    columns = ("ID", "Enrollment", "Name", "Department", "Time", "Date")
    tree = ttk.Treeview(win, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=130, anchor="center")

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # --- Buttons ---
    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    refresh_btn = tk.Button(btn_frame, text="🔄 Refresh Attendance", command=view_attendance)
    refresh_btn.grid(row=0, column=0, padx=10)

    export_btn = tk.Button(btn_frame, text="💾 Export to CSV", command=lambda: export_attendance_to_csv(tree))
    export_btn.grid(row=0, column=1, padx=10)

    # Load initial data
    view_attendance()


def view_attendance():
    """Load attendance into the admin Treeview (ascending order)."""
    for i in tree.get_children():
        tree.delete(i)

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="attendance_db"
        )
        query = "SELECT * FROM attendance ORDER BY id ASC"
        df = pd.read_sql(query, conn)
        conn.close()

        # Fill Treeview in ascending order
        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))

    except Exception as e:
        print(f"❌ Error loading attendance: {e}")


def export_attendance_to_csv(tree):
    """Export current attendance view to a CSV file (for backup)."""
    import csv
    from tkinter import filedialog, messagebox

    try:
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Write headers
            writer.writerow(["ID", "Enrollment", "Name", "Department", "Time", "Date"])
            # Write rows
            for row_id in tree.get_children():
                row = tree.item(row_id)["values"]
                writer.writerow(row)
        messagebox.showinfo("Export Complete", f"✅ Attendance exported to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"❌ Failed to export attendance: {e}")


# ----------------------------- CONFIG -----------------------------
# Paths (use raw strings for Windows paths)
TRAINING_PATH = r"C:\Users\DELL\OneDrive\Desktop\FAMS project\TrainingImage"
LABEL_PATH = r"C:\Users\DELL\OneDrive\Desktop\FAMS project\TrainingImageLabel"
os.makedirs(TRAINING_PATH, exist_ok=True)
os.makedirs(LABEL_PATH, exist_ok=True)

# Admin credentials (from your original code)
ADMIN_USERNAME = "Shasidhar18"
ADMIN_PASSWORD = "Naidu@1977"

# MySQL / XAMPP config
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # empty as you specified
    "database": "attendance_db"
}

# DeepFace model name (VGG-Face used here; change if you prefer)
DEEPFACE_MODEL_NAME = "VGG-Face"

# ------------------------ DATABASE HELPERS ------------------------
def connect_mysql():
    """Connect to MySQL and return connection (or None)."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✅ Connected to MySQL")
        return conn
    except Exception as e:
        print("❌ MySQL Connection Error:", e)
        return None

def ensure_db_tables():
    """Create necessary tables if they don't exist: students and attendance."""
    conn = connect_mysql()
    if not conn:
        print("⚠️ Skipping table creation because DB connection failed.")
        return
    cur = conn.cursor()
    # Students table: store enrollment, name, department, registration datetime
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            enrollment INT(11) UNIQUE,
            name VARCHAR(200),
            department VARCHAR(200),
            time TIME DEFAULT CURRENT_TIMESTAMP,
            date DATE DEFAULT CURRENT_TIMESTAMP
        );
    """)
    # Attendance table: store enrollment, name, department, time, date
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            enrollment INT(11),
            name VARCHAR(200),
            department VARCHAR(200),
            time TIME DEFAULT CURTIME(),
            date DATE DEFAULT CURDATE()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("📦 Database tables ensured (students, attendance).")

# ------------------------ LOGGING UTIL ----------------------------
def gui_log(textbox, message):
    """Append message to GUI textbox and also print to console."""
    try:
        textbox.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        textbox.insert("end", f"[{timestamp}] {message}\n")
        textbox.configure(state="disabled")
        textbox.see("end")
    except Exception:
        pass
    print(message)

# ------------------------ CSV AUTO-UPDATE  ------------------------
STUDENTS_CSV = r"C:\Users\DELL\Videos\Captures\FAMS project\Attendance\students_data.csv"
ATTENDANCE_CSV = r"C:\Users\DELL\OneDrive\Desktop\FAMS project\StudentDetails\attendance_records.csv"

def append_student_to_csv(enrollment, name, department):
    """Append new student info to CSV when registered."""
    file_exists = os.path.isfile(STUDENTS_CSV)
    with open(STUDENTS_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # write header only if file didn't exist
        if not file_exists:
            writer.writerow(["Enrollment", "Name", "Department", "Date_Registered", "Time_Registered"])
        now = datetime.now()
        writer.writerow([enrollment, name, department, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")])

def append_attendance_to_csv(enrollment, name, department, date_str, time_str):
    """Append attendance record to CSV every time attendance is marked."""
    file_exists = os.path.isfile(ATTENDANCE_CSV)
    with open(ATTENDANCE_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Enrollment", "Name", "Department", "Date", "Time"])
        writer.writerow([enrollment, name, department, date_str, time_str])

# ------------------------ DEEPFACE PRELOAD ------------------------
MODEL_CACHE = {"model": None}
def preload_deepface_model(log_box=None):
    """Load DeepFace model in a background thread to avoid blocking GUI.
       This will download weights first time if required."""
    def _load():
        try:
            msg = "🔄 Preloading DeepFace model (this may download weights - first run only)..."
            if log_box: gui_log(log_box, msg)
            else: print(msg)
            model = DeepFace.build_model(DEEPFACE_MODEL_NAME)
            MODEL_CACHE["model"] = model
            msg2 = f"✅ DeepFace model '{DEEPFACE_MODEL_NAME}' loaded."
            if log_box: gui_log(log_box, msg2)
            else: print(msg2)
        except Exception as ex:
            err = f"❌ DeepFace preload failed: {ex}"
            if log_box: gui_log(log_box, err)
            else: print(err)
    t = threading.Thread(target=_load, daemon=True)
    t.start()

# ------------------------ LIVENESS (SIMPLE) -----------------------
def detect_liveness(prev_gray, cur_gray):
    """Simple motion-based liveness: compare frame difference."""
    if prev_gray is None:
        return True
    diff = cv2.absdiff(prev_gray, cur_gray)
    nz = np.count_nonzero(diff)
    # tuned threshold - adjust according to lighting/camera
    return nz > 10000

# ------------------------ REGISTRATION ---------------------------
def register_student(enrollment, name, department, log_box):
    """Capture images from camera and save, and save student to DB."""
    if not enrollment or not name or not department:
        messagebox.showwarning("Input required", "Please enter Enrollment ID, Name and Department.")
        return

    # Save student record to DB (or update if exists)
    conn = connect_mysql()
    if conn:
        cur = conn.cursor()
        now = datetime.now()
        try:
            # Try insert; if duplicate, update name/department
            cur.execute("INSERT INTO students (enrollment, name, department) VALUES (%s,%s,%s)",
                        (enrollment, name, department))
            conn.commit()
            append_student_to_csv(enrollment, name, department)
            gui_log(log_box, f"📁 Student added to CSV backup: {enrollment}, {name}")

            gui_log(log_box, f"🗂️ Student record inserted: {enrollment}, {name}, {department}")
        except mysql.connector.IntegrityError:
            cur.execute("UPDATE students SET name=%s, department=%s WHERE enrollment=%s",
                        (name, department, enrollment))
            conn.commit()
            append_student_to_csv(enrollment, name, department)
            gui_log(log_box, f"📁 Student added to CSV backup: {enrollment}, {name}")

            gui_log(log_box, f"♻️ Student record updated: {enrollment}, {name}, {department}")
        except Exception as e:
            gui_log(log_box, f"❌ DB error while saving student: {e}")
        finally:
            cur.close()
            conn.close()
    else:
        gui_log(log_box, "⚠️ DB unavailable; continuing to save images locally.")

    # Camera capture
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        gui_log(log_box, "❌ Cannot open camera.")
        return

    gui_log(log_box, f"📸 Starting capture for {enrollment} - {name} ... Press 'q' to stop early.")
    count = 0
    prev = None
    saved = 0
    while saved < 40:  # capture up to 40 images
        ret, frame = cam.read()
        if not ret:
            gui_log(log_box, "⚠️ Frame read failed, aborting.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        live = detect_liveness(prev, gray)
        prev = gray.copy()

        display_frame = frame.copy()
        msg = "Liveness OK" if live else "Liveness FAIL"
        color = (0,255,0) if live else (0,0,255)
        cv2.putText(display_frame, msg, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("Register - Press 'q' to stop", display_frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            gui_log(log_box, "⏹️ Capture stopped by user.")
            break

        # Save every nth frame to avoid duplicate near-same images
        if count % 4 == 0:
            fname = f"{enrollment}_{name}_{saved+1}.jpg"
            fpath = os.path.join(TRAINING_PATH, fname)
            cv2.imwrite(fpath, frame)
            gui_log(log_box, f"Saved image: {fname}")
            saved += 1

        count += 1

    cam.release()
    cv2.destroyAllWindows()
    gui_log(log_box, f"✅ Registration complete: {enrollment} ({name}). {saved} images saved.")

# ------------------------ RECOGNITION -----------------------------
def recognize_loop(log_box):
    """Run recognition loop. Uses DeepFace.verify between live frame and each stored image.
       Marks attendance for first matched enrollment for which verify returns True."""
    # Ensure model is loaded (wait briefly if model in background)
    if MODEL_CACHE["model"] is None:
        gui_log(log_box, "⏳ Waiting for DeepFace model to load (first-run download may be in progress)...")
        # Wait up to 120s
        waited = 0
        while MODEL_CACHE["model"] is None and waited < 120:
            time.sleep(1)
            waited += 1
        if MODEL_CACHE["model"] is None:
            gui_log(log_box, "❌ Model not loaded; abort recognition.")
            return

    model = MODEL_CACHE["model"]
    gui_log(log_box, "🧠 Starting recognition. Press 'q' to stop.")

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        gui_log(log_box, "❌ Cannot open camera for recognition.")
        return

    prev_gray = None
    recognized_set = set()  # avoid duplicate marks in same session

    try:
        while True:
            ret, frame = cam.read()
            if not ret:
                gui_log(log_box, "⚠️ Failed to read camera frame.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            live = detect_liveness(prev_gray, gray)
            prev_gray = gray.copy()

            if not live:
                cv2.putText(frame, "⚠️ Liveness fail - move slightly", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
            else:
                # iterate stored images and verify
                for img_name in os.listdir(TRAINING_PATH):
                    img_path = os.path.join(TRAINING_PATH, img_name)
                    # DeepFace.verify accepts numpy array (frame) and image path
                    try:
                        # enforce_detection False to avoid exceptions if face not detected in either
                        res = DeepFace.verify(frame, img_path, model_name=DEEPFACE_MODEL_NAME, enforce_detection=False)
                        if res.get("verified", False):
                            # parse enrollment and name from filename: enrollment_name_x.jpg
                            parts = img_name.split("_")
                            if len(parts) >= 2:
                                enrollment_found = parts[0]
                                name_found = parts[1]
                            else:
                                enrollment_found = img_name
                                name_found = img_name

                            if enrollment_found not in recognized_set:
                                recognized_set.add(enrollment_found)
                                now = datetime.now()
                                date_str = now.strftime("%Y-%m-%d")
                                time_str = now.strftime("%H:%M:%S")

                                # attempt to find department from students table
                                department_val = "Unknown"
                                conn = connect_mysql()
                                if conn:
                                    cur = conn.cursor()
                                    try:
                                        cur.execute("SELECT department FROM students WHERE enrollment=%s", (enrollment_found,))
                                        r = cur.fetchone()
                                        if r:
                                            department_val = r[0]
                                    except Exception:
                                        department_val = "Unknown"
                                    finally:
                                        cur.close()
                                        conn.close()

                                # mark attendance in DB
                                conn2 = connect_mysql()
                                if conn2:
                                    cur2 = conn2.cursor()
                                    try:
                                        cur2.execute("INSERT INTO attendance (enrollment, name, department, time, date) VALUES (%s,%s,%s,%s,%s)",
                                                     (enrollment_found, name_found, department_val, time_str, date_str))
                                        conn2.commit()
                                        gui_log(log_box, f"🟢 Marked attendance: {enrollment_found} - {name_found} ({department_val})")
                                        append_attendance_to_csv(enrollment_found, name_found, department_val, date_str, time_str)
                                        gui_log(log_box, "💾 Attendance record backed up to CSV.")

                                    except Exception as e:
                                        gui_log(log_box, f"❌ Attendance DB insert failed: {e}")
                                    finally:
                                        cur2.close()
                                        conn2.close()
                                else:
                                    gui_log(log_box, "⚠️ Could not connect to DB to save attendance. Logged only locally.")
                            # annotate and break (we matched one image)
                            cv2.putText(frame, f"{name_found} ({enrollment_found})", (10,70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
                            break
                    except Exception as e:
                        # ignore verification errors but log occasionally
                        gui_log(log_box, f"⚠️ Verify error for {img_name}: {e}")
            cv2.imshow("Recognition - press 'q' to stop", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                gui_log(log_box, "⏹️ Recognition stopped by user.")
                break
    finally:
        cam.release()
        cv2.destroyAllWindows()
        gui_log(log_box, "🔒 Recognition ended.")

# ------------------------ MANUAL ATTENDANCE ----------------------
def manual_attendance_mark(enroll, name, dept, log_box):
    """Mark attendance manually — only for registered students."""
    if not enroll or not name:
        messagebox.showwarning("Input Error", "Please enter Enrollment and Name.")
        return

    conn = connect_mysql()
    if not conn:
        gui_log(log_box, "⚠️ DB unavailable; could not save manual attendance.")
        return

    cur = conn.cursor()
    try:
        # ✅ Verify student exists
        cur.execute("SELECT name, department FROM students WHERE enrollment = %s", (enroll,))
        student = cur.fetchone()

        if student is None:
            messagebox.showerror("Error", "Enrollment not found in registered students.")
            gui_log(log_box, f"❌ Unregistered enrollment: {enroll}")
            return

        # Use DB data, not free-typed values
        name_found, dept_found = student
        now = datetime.now()
        cur.execute("""
            INSERT INTO attendance (enrollment, name, department, time, date)
            VALUES (%s, %s, %s, %s, %s)
        """, (enroll, name_found, dept_found, now.strftime("%H:%M:%S"), now.strftime("%Y-%m-%d")))
        conn.commit()
        append_attendance_to_csv(enroll, name_found, dept_found, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"))
        gui_log(log_box, "💾 Manual attendance backed up to CSV.")


        gui_log(log_box, f"📝 Manual attendance marked: {enroll} - {name_found} ({dept_found})")
        messagebox.showinfo("Success", "Manual attendance recorded.")
    except Exception as e:
        gui_log(log_box, f"❌ Error saving manual attendance: {e}")
        messagebox.showerror("Error", f"Failed to save manual attendance: {e}")
    finally:
        cur.close()
        conn.close()


# ------------------------ DASHBOARD UI ---------------------------
def open_admin_dashboard(parent, log_box):
    """Open an admin login dialog and if correct, show the dashboard in a new window."""
    def try_login():
        u = user_var.get().strip()
        p = pass_var.get().strip()
        if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
            login_win.destroy()
            show_dashboard_window(parent, log_box)
        else:
            messagebox.showerror("Login failed", "Invalid admin credentials.")

    login_win = ctk.CTkToplevel(parent)
    login_win.title("Admin Login")
    login_win.geometry("360x200")
    login_win.grab_set()

    ctk.CTkLabel(login_win, text="Admin Login", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(10,5))
    frm = ctk.CTkFrame(login_win)
    frm.pack(padx=10, pady=10, fill="both", expand=True)

    ctk.CTkLabel(frm, text="Username").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    user_var = ctk.StringVar()
    user_entry = ctk.CTkEntry(frm, textvariable=user_var)
    user_entry.grid(row=0, column=1, padx=10, pady=5)

    ctk.CTkLabel(frm, text="Password").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    pass_var = ctk.StringVar()
    pass_entry = ctk.CTkEntry(frm, textvariable=pass_var, show="*")
    pass_entry.grid(row=1, column=1, padx=10, pady=5)

    ctk.CTkButton(login_win, text="Login", command=try_login).pack(pady=10)

def show_dashboard_window(parent, log_box):
    """Show the admin dashboard window with attendance table and controls."""
    dash = ctk.CTkToplevel(parent)
    dash.title("Admin Dashboard - Attendance")
    dash.geometry("900x600")

    # Treeview for attendance
    columns = ("id", "enrollment", "name", "department", "time", "date")
    tree = ttk.Treeview(dash, columns=columns, show="headings")
    tree.heading("id", text="ID")
    tree.heading("enrollment", text="Enrollment")
    tree.heading("name", text="Name")
    tree.heading("department", text="Department")
    tree.heading("time", text="Time")
    tree.heading("date", text="Date")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Buttons
    btn_frame = ctk.CTkFrame(dash)
    btn_frame.pack(fill="x", padx=10, pady=(0,10))

    def refresh():
        for r in tree.get_children():
            tree.delete(r)
        conn = connect_mysql()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute("SELECT id, enrollment, name, department, time, date FROM attendance ORDER BY id ASC")
                for row in cur.fetchall():
                    tree.insert("", "end", values=row)
                gui_log(log_box, "🔁 Dashboard refreshed.")
            except Exception as e:
                gui_log(log_box, f"❌ Failed to load attendance: {e}")
            finally:
                cur.close()
                conn.close()
        else:
            gui_log(log_box, "⚠️ DB unavailable; cannot refresh dashboard.")

    def clear_attendance():
        if messagebox.askyesno("Confirm", "This will delete all attendance records. Continue?"):
            conn = connect_mysql()
            if conn:
                cur = conn.cursor()
                try:
                    cur.execute("DELETE FROM attendance")
                    conn.commit()
                    refresh()
                    gui_log(log_box, "🧹 All attendance records cleared.")
                except Exception as e:
                    gui_log(log_box, f"❌ Failed to clear attendance: {e}")
                finally:
                    cur.close()
                    conn.close()
            else:
                gui_log(log_box, "⚠️ DB unavailable; cannot clear records.")

    ctk.CTkButton(btn_frame, text="Refresh", command=refresh).pack(side="left", padx=8)
    ctk.CTkButton(btn_frame, text="Clear All Attendance", command=clear_attendance).pack(side="left", padx=8)

    refresh()

# ------------------------ GUI BUILD ------------------------------
def build_gui():
    """Main GUI layout using CustomTkinter with tabbed interface."""
    ensure_db_tables()  # ensure DB tables before GUI

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    app = ctk.CTk()
    app.title("FAMS — Face Attendance Management System")
    app.geometry("1200x750")

    header = ctk.CTkFrame(app)
    header.pack(fill="x", padx=12, pady=8)
    ctk.CTkLabel(header, text="FAMS — Face Attendance System", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", padx=12)
    # Admin Dashboard button (requires login)
    ctk.CTkButton(header, text="Open Admin Dashboard", command=lambda: open_admin_dashboard(app, log_box)).pack(side="right", padx=12)

    # Tabview
    tabview = ctk.CTkTabview(app, width=1100)
    tabview.pack(expand=True, fill="both", padx=12, pady=(4,12))

    # Register Tab -------------------------------------------------
    tab_register = tabview.add("Register")
    reg_frame = ctk.CTkFrame(tab_register)
    reg_frame.pack(fill="both", expand=True, padx=16, pady=12)

    left_reg = ctk.CTkFrame(reg_frame)
    left_reg.pack(side="left", fill="y", padx=(8,12), pady=8)

    ctk.CTkLabel(left_reg, text="Enrollment ID").pack(anchor="w", padx=8, pady=(8,2))
    enroll_var = ctk.StringVar()
    enroll_entry = ctk.CTkEntry(left_reg, textvariable=enroll_var, width=300)
    enroll_entry.pack(padx=8, pady=(0,8))

    ctk.CTkLabel(left_reg, text="Student Name").pack(anchor="w", padx=8, pady=(8,2))
    name_var = ctk.StringVar()
    name_entry = ctk.CTkEntry(left_reg, textvariable=name_var, width=300)
    name_entry.pack(padx=8, pady=(0,8))

    ctk.CTkLabel(left_reg, text="Department").pack(anchor="w", padx=8, pady=(8,2))
    dept_var = ctk.StringVar()
    dept_entry = ctk.CTkEntry(left_reg, textvariable=dept_var, width=300)
    dept_entry.pack(padx=8, pady=(0,12))

    # Capture button
    def on_register_click():
        e = enroll_var.get().strip()
        n = name_var.get().strip()
        d = dept_var.get().strip()
        if not e or not n or not d:
            messagebox.showwarning("Missing data", "Please fill Enrollment ID, Name and Department.")
            return
        # run registration in separate thread so GUI doesn't freeze
        threading.Thread(target=register_student, args=(e, n, d, log_box), daemon=True).start()

    ctk.CTkButton(left_reg, text="Capture Photos & Register", command=on_register_click).pack(pady=(6,12))

    # Right side: logs
    right_reg = ctk.CTkFrame(reg_frame)
    right_reg.pack(side="left", fill="both", expand=True, padx=(12,8), pady=8)
    ctk.CTkLabel(right_reg, text="Logs").pack(anchor="nw", padx=8, pady=(6,2))
    global log_box  # define globally for access in other functions
    log_box = ctk.CTkTextbox(right_reg, width=700, height=420)
    log_box.pack(padx=8, pady=(0,8))
    log_box.configure(state="disabled")

    # Preload model in background
    preload_deepface_model(log_box)

    # Recognition Tab -----------------------------------------------
    tab_recog = tabview.add("Recognition")
    recog_frame = ctk.CTkFrame(tab_recog)
    recog_frame.pack(fill="both", expand=True, padx=12, pady=12)

    ctk.CTkLabel(recog_frame, text="Recognition", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(8,6))
    recog_log_box = ctk.CTkTextbox(recog_frame, width=1000, height=320)
    recog_log_box.pack(pady=(6,12))
    recog_log_box.configure(state="disabled")

    def start_recognition():
        threading.Thread(target=recognize_loop, args=(recog_log_box,), daemon=True).start()

    ctk.CTkButton(recog_frame, text="Start Recognition (Camera)", command=start_recognition).pack()

    # Manual Attendance Tab ---------------------------------------
    tab_manual = tabview.add("Manual Attendance")
    man_frame = ctk.CTkFrame(tab_manual)
    man_frame.pack(fill="both", expand=True, padx=12, pady=12)

    left_man = ctk.CTkFrame(man_frame)
    left_man.pack(side="left", fill="y", padx=(8,12), pady=8)

    ctk.CTkLabel(left_man, text="Enrollment ID").pack(anchor="w", padx=8, pady=(8,2))
    man_enroll_var = ctk.StringVar()
    man_enroll = ctk.CTkEntry(left_man, textvariable=man_enroll_var, width=280)
    man_enroll.pack(padx=8, pady=(0,8))

    ctk.CTkLabel(left_man, text="Name").pack(anchor="w", padx=8, pady=(8,2))
    man_name_var = ctk.StringVar()
    man_name = ctk.CTkEntry(left_man, textvariable=man_name_var, width=280)
    man_name.pack(padx=8, pady=(0,8))

    ctk.CTkLabel(left_man, text="Department").pack(anchor="w", padx=8, pady=(8,2))
    man_dept_var = ctk.StringVar()
    man_dept = ctk.CTkEntry(left_man, textvariable=man_dept_var, width=280)
    man_dept.pack(padx=8, pady=(0,12))

    def on_manual_mark():
        e = man_enroll_var.get().strip()
        n = man_name_var.get().strip()
        d = man_dept_var.get().strip()
        if not e or not n:
            messagebox.showwarning("Missing data", "Please provide enrollment and name.")
            return
        manual_attendance_mark(e, n, d, log_box)
        # Clear fields
        man_enroll_var.set("")
        man_name_var.set("")
        man_dept_var.set("")

    ctk.CTkButton(left_man, text="Mark Manual Attendance", command=on_manual_mark).pack(pady=(6,12))


    # Footer: quick tips
    footer = ctk.CTkFrame(app)
    footer.pack(fill="x", padx=12, pady=6)
    ctk.CTkLabel(footer, text="Tip: On first DeepFace run weights will be downloaded (~500MB). Recognition will start after preload completes.", text_color="gray").pack(side="left", padx=8)

    app.mainloop()



# ------------------------ ENTRYPOINT -----------------------------
if __name__ == "__main__":
    build_gui()

