# Smart Attendance System

[![CI](https://github.com/Ansh17ast/Smart-Attendance-System/actions/workflows/ci.yml/badge.svg)](https://github.com/Ansh17ast/Smart-Attendance-System/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python)](requirements.txt)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?logo=opencv)](requirements.txt)
[![Database](https://img.shields.io/badge/SQLite-Transactional%20Storage-003B57?logo=sqlite)](requirements.txt)

An automated biometric attendance management system built with Python, OpenCV, and dlib's 128-dimensional face embedding pipeline. Automates classroom and workplace attendance verification directly through live video feeds with in-session deduplication, SQLite persistence, and an integrated student FAQ assistant.

---

## ⚡ Key Highlights & Architecture

- **Real-Time Facial Feature Extraction:** Utilizes Histogram of Oriented Gradients (HOG) face detection and deep residual metric learning to generate 128-dimensional facial embeddings.
- **Euclidean Vector Matching:** Compares incoming webcam frames against pre-enrolled student facial vectors using Euclidean distance metrics (threshold $\le 0.5$) for reliable identity matching.
- **Transactional In-Session Deduplication:** Prevents multiple attendance submissions for the same individual within a single session via memory tracking and SQLite transactions.
- **Automated Logging & Recovery:** Full audit trail written to `system.log` recording enrollment status, recognition attempts, and database queries.
- **Rule-Based Student FAQ Bot:** Integrated student query assistant answering routine academic and attendance policy questions.
- **Privacy by Design:** Biometric image datasets and live attendance database files are strictly isolated from version control via `.gitignore`.

---

## System Pipeline

```
 +-----------------------------------------------------------------------------------+
 |                             Live Webcam Frame (OpenCV)                            |
 +-----------------------------------------+-----------------------------------------+
                                           |
                                           v
 +-----------------------------------------------------------------------------------+
 |                  Color Conversion (BGR -> RGB) & Memory Alignment                 |
 +-----------------------------------------+-----------------------------------------+
                                           |
                                           v
 +-----------------------------------------------------------------------------------+
 |                     HOG Face Detection & 128D Vector Extraction                   |
 +-----------------------------------------+-----------------------------------------+
                                           |
                                           v
 +-----------------------------------------------------------------------------------+
 |              Euclidean Distance Comparison vs Enrolled Vectors (<= 0.5)           |
 +-----------------------------------------+-----------------------------------------+
                                           |
                   +-----------------------+-----------------------+
                   | Recognized                                    | Unknown
                   v                                               v
 +-----------------------------------+           +-----------------------------------+
 | In-Memory Session Deduplication   |           | Bounding Box: Unknown (Logged)    |
 +-----------------+-----------------+           +-----------------------------------+
                   | New in Session
                   v
 +-----------------------------------+
 | Commit to SQLite (`attendance.db`)|
 +-----------------------------------+
```

---

## Repository Structure

```
Smart-Attendance-System/
├── .github/
│   └── workflows/
│       └── ci.yml             # Automated CI workflow
├── student_images/            # Enrolled student face portraits (git-ignored for privacy)
│   └── .gitkeep               # Directory placeholder
├── tests/
│   └── test_attendance.py     # Automated unit tests (database, deduplication, FAQ bot)
├── .gitignore                 # Excludes biometric photos, databases, logs, and venvs
├── FAQ.json                   # Knowledge base for student query assistant
├── README.md                  # System documentation
├── requirements.txt           # Project dependencies
└── SAS.py                     # Core application entrypoint
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Webcam / video capture device
- C++ Build Tools & CMake (required for building `dlib` on Windows)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Ansh17ast/Smart-Attendance-System.git
   cd Smart-Attendance-System
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Linux/macOS:
   source .venv/bin/activate
   ```

3. Install project dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

> **Note for Windows Users:** Installing `face-recognition` requires `dlib`. If pip fails to build the wheel, install CMake (`pip install cmake`) and ensure Visual Studio C++ Build Tools are installed on your machine.

---

## Usage

### 1. Enrolling Students
Place clear headshot photos (`.jpg`, `.jpeg`, or `.png`) of authorized students in the `student_images/` directory. The filename (without extension) is used as the student's identifier:
```
student_images/
├── Ansh_Thakur.jpg
└── Jane_Doe.png
```

### 2. Running the System
Launch the main application:
```bash
python SAS.py
```

The interactive menu will display:
```
Smart Attendance System with FAQ Chatbot
1. Take Attendance
2. Chat with FAQ Bot
Enter choice (1 or 2):
```
- Select **`1`** to start the video attendance stream. Press **`q`** to safely close the webcam window.
- Select **`2`** to interact with the FAQ assistant. Type **`exit`** to return.

---

## Running Automated Tests

Run the unit test suite covering database schema initialization, transactional insertions, and FAQ intent matching:
```bash
python -m unittest discover -s tests
```

Or using `pytest`:
```bash
pytest -v tests/
```

---

## Privacy & Security Considerations

Biometric face images and attendance logs represent sensitive student data. This repository adheres to the following privacy standards:
- **No Biometric Data in Version Control:** `student_images/*.jpg` and other image formats are excluded via `.gitignore`. Only a blank `.gitkeep` is tracked.
- **Isolated SQLite Storage:** Local runtime databases (`attendance.db`) and audit logs (`system.log`) are strictly excluded from commits.

---

## License

This project is licensed under the [MIT License](LICENSE).
