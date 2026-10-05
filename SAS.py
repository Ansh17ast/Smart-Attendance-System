import cv2
import face_recognition
import os
import sqlite3
import json
import logging
import numpy as np   # ✅ needed for np.ascontiguousarray
from datetime import datetime
# ---------- Logging ----------2
logging.basicConfig(
    filename='system.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ---------- Database ----------
def init_db(db_file="attendance.db"):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  timestamp TEXT NOT NULL,
                  status TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def mark_attendance(name, db_file="attendance.db"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute(
            "INSERT INTO attendance (name, timestamp, status) VALUES (?, ?, ?)",
            (name, timestamp, "Present")
        )
        conn.commit()
        conn.close()
        logging.info(f"Attendance marked for {name} at {timestamp}")
    except Exception as e:
        logging.error(f"Error marking attendance for {name}: {e}")

# ---------- Load Student Encodings ----------
def ensure_student_dir(image_folder="student_images"):
    if not os.path.exists(image_folder):
        os.makedirs(image_folder, exist_ok=True)
        logging.warning(f"Missing folder: {image_folder}")

def load_student_encodings(image_folder="student_images"):
    ensure_student_dir(image_folder)
    known_face_encodings = []
    known_face_names = []

    files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not files:
        logging.warning(f"No images found in {image_folder}.")
        return [], []

    for filename in files:
        image_path = os.path.join(image_folder, filename)
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_face_encodings.append(encodings[0])
                known_face_names.append(os.path.splitext(filename)[0])
                logging.info(f"Loaded face encoding for {filename}")
            else:
                logging.warning(f"No face found in {filename}")
        except Exception as e:
            logging.error(f"Error processing {filename}: {e}")

    return known_face_encodings, known_face_names

# ---------- Attendance Loop ----------
def take_attendance(known_encodings, known_names):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) if hasattr(cv2, 'CAP_DSHOW') else cv2.VideoCapture(0)
    if not cap.isOpened():
        logging.error("Failed to open webcam.")
        print("Error: Could not open webcam.")
        return

    marked_names = set()   # ✅ track already marked students

    print("Starting attendance... Press 'q' to stop.")
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            logging.error("Failed to capture video frame.")
            print("Failed to capture video.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame = np.ascontiguousarray(rgb_frame)

        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            label = "Unknown"
            if known_encodings:
                distances = face_recognition.face_distance(known_encodings, face_encoding)
                if len(distances) > 0:
                    best_idx = distances.argmin()
                    if distances[best_idx] <= 0.5:
                        name = known_names[best_idx]

                        if name not in marked_names:
                            mark_attendance(name)
                            marked_names.add(name)
                            print(f"Attendance marked for {name}")
                            label = f"{name} (✔)"   # ✅ first time
                        else:
                            label = f"{name} (Already Present)"  # ✅ show already marked
                    else:
                        logging.info("Unknown face detected.")
                else:
                    label = "Unknown"

            # Draw rectangle + label
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(frame, (left, bottom - 20), (right, bottom), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, label, (left + 4, bottom - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        cv2.imshow('Smart Attendance', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# ---------- FAQ Chatbot ----------
def load_faq_data(json_file="faq.json"):
    if not os.path.exists(json_file):
        default_faq = {
            "attendance": "at the start of class if you want to check the attendance you can check that on vtop.",
            "exam schedule": "Check the academic calendar for exam dates.",
            "leave policy": "Submit leave requests via the student portal at least 24 hours in advance.",
            "makeup exam": "Makeup exams require approval from the academic office.",
            "attendance report": "Attendance reports are available on the student portal."
        }
        with open(json_file, 'w') as f:
            json.dump(default_faq, f, indent=4)
        logging.info("Created default FAQ file.")
        return default_faq

    with open(json_file, 'r') as f:
        return json.load(f)

def get_faq_response(query, faq_data):
    q = query.lower()
    for keyword, response in faq_data.items():
        if keyword in q:
            return response
    return "Sorry, I don't understand your question. Try keywords like 'attendance', 'exam', or 'leave'."

def chatbot():
    faq_data = load_faq_data()
    print("FAQ Chatbot: Type your question (or 'exit' to quit)")
    while True:
        try:
            query = input("> ")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() == 'exit':
            break
        response = get_faq_response(query, faq_data)
        print(response)
        logging.info(f"Chatbot query: {query} | Response: {response}")

# ---------- Main ----------
def main():
    init_db()
    print("Smart Attendance System with FAQ Chatbot")
    print("1. Take Attendance")
    print("2. Chat with FAQ Bot")
    choice = input("Enter choice (1 or 2): ").strip()

    if choice == '1':
        known_encodings, known_names = load_student_encodings()
        if known_encodings:
            take_attendance(known_encodings, known_names)
        else:
            print("No student data found. Add face images to 'student_images' folder.")
            logging.warning("No student encodings found.")
    elif choice == '2':
        chatbot()
    else:
        print("Invalid choice.")
        logging.error(f"Invalid menu choice: {choice}")

    print("Session completed. Thank you.")

if __name__ == "__main__":
    main()