# 🎯 Face Attendance Management System (FAMS)

An intelligent **AI-powered desktop application** that automates attendance tracking using **facial recognition** powered by **DeepFace** and **OpenCV**, combined with a secure and modern **CustomTkinter GUI** and **MySQL database** for reliable record storage.

---

## 📌 Overview

**Face Attendance Management System (FAMS)** is a Python-based attendance tracking solution that uses **facial recognition** to eliminate manual attendance marking and increase efficiency.  

Featuring both **automatic camera-based recognition** and **manual marking**, FAMS is designed for educational institutions, workplaces, and other organizations that need to maintain reliable attendance logs.

All data is stored in a **MySQL database** with automatic **CSV backups** for students and attendance records, and the app includes a **dark-themed admin dashboard** with export and management tools.

---

## 🧾 Features

- 🧍‍♂️ **Student Registration** – Capture live images and register students with **Enrollment ID**, **Name**, and **Department**.
- 🧠 **DeepFace Model Recognition (VGG-Face)** – Leverages AI-based face verification for accurate real-time facial recognition.
- 🕶️ **Liveness Detection** – Motion-based check to prevent spoofing using static images.
- ⚙️ **Admin Dashboard (Login Protected)** – View, refresh, export, and clear attendance data with admin credentials.
- ✍️ **Manual Attendance Tab** – Option to manually record attendance.
- 🖼️ **Dark-Themed CustomTkinter GUI** – Modern, responsive, and user-friendly interface.
- 💾 **Automatic CSV Sync**  
  - Student details stored at:  
    `C:\Users\DELL\Videos\Captures\FAMS project\Attendance\students_data.csv`
  - Attendance logs stored at:  
    `C:\Users\DELL\OneDrive\Desktop\FAMS project\StudentDetails\attendance_records.csv`
- 🗄️ **Database Integration (MySQL)** –  
  `students` table for student info and `attendance` table for attendance logs.
- 🧵 **Threaded Processing** – Preloads DeepFace in the background to keep the GUI smooth and responsive.

---

## 🧰 Tech Stack

| Component | Technology Used |
|------------|----------------|
| **Language** | Python 3 |
| **GUI Framework** | CustomTkinter |
| **Facial Recognition** | DeepFace (VGG-Face model) |
| **Image Processing** | OpenCV |
| **Database** | MySQL (via mysql-connector) |
| **Data Handling** | Pandas + CSV |
| **Utilities** | PIL, NumPy, Threading |

---

## 🚀 How It Works

1. **Register Student:**  
   - Capture webcam images and save them as `ENROLLMENT_NAME_count.jpg` in the folder.  
   - Automatically store student info in MySQL and update `students_data.csv`.

2. **Face Recognition:**  
   - When a student appears in front of the camera, their live frame is verified against stored images using **DeepFace.verify()**.  
   - Attendance is automatically stored in the MySQL `attendance` table and appended to `attendance_records.csv`.

3. **Manual Attendance:**  
   - Enter Enrollment ID and Name manually if face recognition fails or no camera is available.

4. **Admin Dashboard:**  
   - Login with admin credentials to manage attendance data.
   - Features: Refresh, Clear All Records, and Export Attendance to CSV.

---

## ⚙️ Configuration Details

### MySQL Database
Database: `attendance_db`  
Tables:
- **students** → Stores `enrollment`, `name`, `department`
- **attendance** → Logs attendance with `time` and `date`

### Default Admin Credentials
- **username**- `Shasidharkella18`
- **password**- `naidu@1977`

## 🧩 Folder Structure

FAMS Project/
│
├── TrainingImage/ # Captured student images
├── TrainingImageLabel/ # Reserved (future labels/models)
├── StudentDetails/ # stores student data & csv backups
├── Attendance/ # stores attendance logs & Student CSV backups
├── FAMS_Main.py # Main application file
└── requirements.txt # Python dependencies


---

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL Server (e.g., XAMPP or MySQL Workbench)
- Webcam access for face capture
- Dependencies:
pip install deepface opencv-python customtkinter mysql-connector-python pandas Pillow


---

## 💡 Key Highlights

- Real-time DeepFace verification (VGG-Face)
- Background model preloading (non-freezing GUI)
- Auto data backup in MySQL + CSV
- Rich dark mode GUI using CustomTkinter
- Step-by-step logs inside the GUI and console

---

## 💡 Future Improvements

- Replace `DeepFace.verify()` with face embedding comparison for faster recognition.
- Improve liveness detection using blink/eye movement analysis.
- Add facial model training cache for better accuracy.
- Add an attendance analytics dashboard (charts and reports).

---

## 🧱 Project Advantages

- Fully automated attendance process.  
- Database + CSV redundancy increases data reliability.  
- Secure, fast, scalable, and easy to use for institutions or workplaces.

---

## 🔐 License

This project is open-source under the **MIT License**.

---

## 👨‍💻 Author

**Developed by:** Kella Shasidhar  
📧 Email: [shasidharkella814@gmail.com]   
💼 LinkedIn: [shasidharkella](www.linkedin.com/in/shasidhar-kella-2087a1313)

---

## ❤️ Acknowledgments

Special thanks to DeepFace, OpenCV, and CustomTkinter open-source communities for enabling AI-based face recognition integration within Python.

---



