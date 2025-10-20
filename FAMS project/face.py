"""
Face Attendance Management System (FAMS)
----------------------------------------
Features:
- DeepFace-based recognition (no Dlib)
- CustomTkinter GUI with 4 tabs (Register, Recognize, Dashboard, Dataset)
- MySQL integration via XAMPP
- Department input for registration
- Real-time logs, dashboard updates, and dataset management
"""

import cv2
import os
import numpy as np
import pandas as pd
from datetime import datetime
from deepface import DeepFace
import mysql.connector
import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import threading

# --------------------- DATABASE CONNECTION -----------------------
def connect_mysql():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Empty password for XAMPP
            database="attendance_db"
        )
        print("✅ Connected to MySQL")
        return conn
    except mysql.connector.Error as e:
        print("❌ MySQL Connection Error:", e)
        return None

# --------------------- GLOBAL PATHS -----------------------
TRAINING_PATH = r"C:\Users\DELL\OneDrive\Desktop\FAMS project\TrainingImage"
LABEL_PATH = r"C:\Users\DELL\OneDrive\Desktop\FAMS project\TrainingImageLabel"
os.makedirs(TRAINING_PATH, exist_ok=True)
os.makedirs(LABEL_PATH, exist_ok=True)

# --------------------- DATABASE FUNCTIONS -----------------------
def create_table():
    conn = connect_mysql()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50),
                department VARCHAR(50),
                time TIME,
                date DATE
            )
        """)
        conn.commit()
        conn.close()
        print("📦 Attendance table verified/created.")

# --------------------- UTILITY FUNCTIONS -----------------------
def log_message(textbox, msg):
    textbox.configure(state="normal")
    textbox.insert("end", msg + "\n")
    textbox.configure(state="disabled")
    textbox.see("end")
    print(msg)

# --------------------- LIVENESS DETECTION -----------------------
def detect_liveness(frame, previous_frame):
    if previous_frame is None:
        return True
    diff = cv2.absdiff(previous_frame, frame)
    non_zero = np.count_nonzero(diff)
    return non_zero > 20000  # crude motion threshold

# --------------------- FACE REGISTRATION -----------------------
def register_face(name, dept, textbox):
    if not name or not dept:
        messagebox.showwarning("Input Error", "Please enter both Name and Department.")
        return
    cam = cv2.VideoCapture(0)
    count = 0
    log_message(textbox, f"📸 Starting capture for {name} ({dept}) ...")

    while True:
        ret, frame = cam.read()
        if not ret:
            log_message(textbox, "⚠️ Failed to access camera.")
            break

        cv2.imshow("Registration", frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or count >= 30:
            break

        count += 1
        filename = f"{name}_{count}.jpg"
        path = os.path.join(TRAINING_PATH, filename)
        cv2.imwrite(path, frame)
        log_message(textbox, f"Saved {filename}")

    cam.release()
    cv2.destroyAllWindows()
    log_message(textbox, f"✅ Registration completed for {name}")

# --------------------- FACE RECOGNITION -----------------------
def recognize_faces(textbox):
    cam = cv2.VideoCapture(0)
    log_message(textbox, "🧠 Starting face recognition...")

    previous_frame = None
    recognized = set()

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        liveness_ok = detect_liveness(gray, previous_frame)
        previous_frame = gray.copy()

        if not liveness_ok:
            cv2.putText(frame, "⚠️ Liveness Check Failed", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            try:
                for img_name in os.listdir(TRAINING_PATH):
                    img_path = os.path.join(TRAINING_PATH, img_name)
                    result = DeepFace.verify(frame, img_path, model_name="VGG-Face", enforce_detection=False)
                    if result["verified"]:
                        name = img_name.split("_")[0]
                        if name not in recognized:
                            recognized.add(name)
                            now = datetime.now()
                            date = now.strftime("%Y-%m-%d")
                            time = now.strftime("%H:%M:%S")

                            conn = connect_mysql()
                            if conn:
                                cur = conn.cursor()
                                cur.execute(
                                    "INSERT INTO attendance (name, department, time, date) VALUES (%s, %s, %s, %s)",
                                    (name, "Unknown", time, date)
                                )
                                conn.commit()
                                conn.close()

                            log_message(textbox, f"🟢 Attendance marked for {name}")
                            cv2.putText(frame, f"Welcome {name}", (50, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                        break
            except Exception as e:
                log_message(textbox, f"⚠️ Error: {e}")

        cv2.imshow("Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
    log_message(textbox, "🔒 Recognition ended.")

# --------------------- DASHBOARD REFRESH -----------------------
def refresh_dashboard(tree):
    for item in tree.get_children():
        tree.delete(item)

    conn = connect_mysql()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM attendance ORDER BY id DESC")
        rows = cur.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        conn.close()

# --------------------- DATASET VIEW -----------------------
def load_dataset(tree):
    for item in tree.get_children():
        tree.delete(item)
    for img_name in os.listdir(TRAINING_PATH):
        tree.insert("", "end", values=(img_name,))

# --------------------- GUI -----------------------
def build_gui():
    app = ctk.CTk()
    app.title("Face Attendance Management System")
    app.geometry("1100x700")
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    tabview = ctk.CTkTabview(app)
    tabview.pack(fill="both", expand=True, padx=10, pady=10)

    tab_register = tabview.add("Register")
    tab_recognize = tabview.add("Recognize")
    tab_dashboard = tabview.add("Dashboard")
    tab_dataset = tabview.add("Dataset")

    # Register Tab
    name_entry = ctk.CTkEntry(tab_register, placeholder_text="Enter Student Name", width=300)
    dept_entry = ctk.CTkEntry(tab_register, placeholder_text="Enter Department", width=300)
    name_entry.pack(pady=10)
    dept_entry.pack(pady=10)

    log_text = ctk.CTkTextbox(tab_register, width=500, height=300)
    log_text.pack(pady=10)
    log_text.configure(state="disabled")

    ctk.CTkButton(tab_register, text="Capture Photos",
                  command=lambda: threading.Thread(target=register_face,
                                                   args=(name_entry.get(), dept_entry.get(), log_text)).start()).pack(pady=10)

    # Recognize Tab
    recog_log = ctk.CTkTextbox(tab_recognize, width=500, height=300)
    recog_log.pack(pady=20)
    recog_log.configure(state="disabled")
    ctk.CTkButton(tab_recognize, text="Start Recognition",
                  command=lambda: threading.Thread(target=recognize_faces, args=(recog_log,)).start()).pack(pady=10)

    # Dashboard Tab
    columns = ("ID", "Name", "Department", "Time", "Date")
    tree = ttk.Treeview(tab_dashboard, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True, pady=20)

    ctk.CTkButton(tab_dashboard, text="Refresh Dashboard",
                  command=lambda: refresh_dashboard(tree)).pack(pady=10)

    # Dataset Tab
    ds_tree = ttk.Treeview(tab_dataset, columns=("Image Name",), show="headings")
    ds_tree.heading("Image Name", text="Image Name")
    ds_tree.pack(fill="both", expand=True, pady=20)
    ctk.CTkButton(tab_dataset, text="Load Dataset",
                  command=lambda: load_dataset(ds_tree)).pack(pady=10)

    create_table()
    app.mainloop()

if __name__ == "__main__":
    build_gui()
