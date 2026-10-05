import os
import sys
import sqlite3
import tempfile
import unittest
from unittest.mock import MagicMock

# Gracefully stub hardware-dependent computer vision modules if not installed in headless test/CI environments
for mod in ("face_recognition", "cv2", "numpy"):
    if mod not in sys.modules:
        try:
            __import__(mod)
        except ImportError:
            sys.modules[mod] = MagicMock()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from SAS import init_db, mark_attendance, load_faq_data, get_faq_response

class TestSmartAttendanceSystem(unittest.TestCase):

    def test_database_initialization(self):
        """Verify attendance table schema is created properly."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            temp_db = tf.name

        try:
            init_db(temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attendance'")
            table = cursor.fetchone()
            conn.close()
            self.assertIsNotNone(table, "Table 'attendance' should be created")
        finally:
            if os.path.exists(temp_db):
                os.remove(temp_db)

    def test_mark_attendance(self):
        """Verify attendance records can be inserted and queried."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            temp_db = tf.name

        try:
            init_db(temp_db)
            mark_attendance("TestStudent", db_file=temp_db)

            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT name, status FROM attendance WHERE name = ?", ("TestStudent",))
            row = cursor.fetchone()
            conn.close()

            self.assertIsNotNone(row)
            self.assertEqual(row[0], "TestStudent")
            self.assertEqual(row[1], "Present")
        finally:
            if os.path.exists(temp_db):
                os.remove(temp_db)

    def test_faq_response_matching(self):
        """Verify keyword matching for FAQ chatbot queries."""
        faq_data = {
            "attendance": "Check your attendance on the student portal.",
            "exam schedule": "Check the academic calendar for exam dates.",
            "leave policy": "Submit leave requests at least 24 hours in advance."
        }

        # Direct keyword query
        resp1 = get_faq_response("when is the exam schedule released?", faq_data)
        self.assertEqual(resp1, "Check the academic calendar for exam dates.")

        # Substring query
        resp2 = get_faq_response("I have a question about attendance criteria", faq_data)
        self.assertEqual(resp2, "Check your attendance on the student portal.")

        # Unrecognized query fallback
        resp3 = get_faq_response("what is the cafeteria menu?", faq_data)
        self.assertIn("Sorry, I don't understand", resp3)

if __name__ == "__main__":
    unittest.main()
