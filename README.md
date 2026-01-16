# Smart Attendance System (Face Recognition + FAQ Chatbot)

A Python-based Smart Attendance System that marks attendance automatically using real-time **face recognition** from a webcam.  
Attendance is stored in an **SQLite database** with timestamps and prevents duplicate marking.  
Also includes a simple **FAQ Chatbot** for common student queries.

---

##  Features
- Real-time face detection & recognition using webcam
- Marks attendance only once per person in a session
- Stores attendance in SQLite database (`attendance.db`)
- Saves logs in `system.log`
- Student face dataset support using `student_images/`
- FAQ chatbot using JSON keyword matching (`faq.json`)

---

##  Tech Stack
- Python
- OpenCV (cv2)
- face_recognition
- NumPy
- SQLite3
- JSON
- Logging

---

##  Project Structure
Smart_Attendance_System/
│── student_images/ # Add student face images here (jpg/png)
│── attendance.db # Auto-created database
│── faq.json # FAQ data file
│── system.log # Logs
│── main.py # Main project file

---

##  How to Run
1. Install required libraries:
```bash
pip install opencv-python face_recognition numpy

student_images/
student_images/Ansh.jpg
student_images/Rahul.png
 
Run the proect 
python main.py
