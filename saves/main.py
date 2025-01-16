import cv2
import dlib
import sqlite3
import numpy as np
from datetime import datetime
import time

# Load models with error handling
detector = dlib.get_frontal_face_detector()
try:
    embedder = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")
    shape_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    print("Models loaded successfully.")
except Exception as e:
    print(f"Error loading models: {e}")
    exit()

def create_tables():
    """
    Create necessary tables in the SQLite database.
    This ensures that the required tables exist before any operations.
    """
    conn = sqlite3.connect("../database/attendance.db")
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                embedding TEXT NOT NULL,
                photo TEXT  
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()
    finally:
        conn.close()

# Call the function to ensure tables are created
create_tables()

def get_known_faces():
    """
    Fetch all known face embeddings and their associated names from the database.
    Returns:
        - names (list): List of names of registered individuals.
        - embeddings (list): List of numpy arrays containing face embeddings.
    """
    conn = sqlite3.connect("../database/attendance.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name, embedding FROM faces")
        data = cursor.fetchall()
        # Extract names and embeddings, converting the latter from string to numpy array
        names = [row[0] for row in data]
        embeddings = [np.array(row[1].split(','), dtype=float) for row in data]
        return names, embeddings
    finally:
        conn.close()

def register_face(name=None):
    """
    Register a new face by capturing from the webcam, extracting the face embedding,
    and saving the name and embedding in the database.
    """
    if name is None:
        name = input("Enter the person's name: ")
    video_stream = cv2.VideoCapture(0)

    if not video_stream.isOpened():
        print("Error: Camera not initialized!")
        return

    print("Camera initialized. Position yourself. Capturing in 4 seconds...")
    time.sleep(4)

    conn = sqlite3.connect("../database/attendance.db")
    try:
        cursor = conn.cursor()
        while True:
            ret, frame = video_stream.read()
            if not ret:
                print("Error: Failed to retrieve frame from camera.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            for face in faces:
                shape = shape_predictor(gray, face)
                embedding = embedder.compute_face_descriptor(frame, shape)
                cursor.execute("INSERT INTO faces (name, embedding) VALUES (?, ?)", 
                            (name, ','.join(map(str, embedding))))
                conn.commit()
                print(f"Registered {name} successfully!")
                return

            cv2.imshow("Register Face", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        video_stream.release()
        conn.close()
        cv2.destroyAllWindows()

def recognize_faces():
    """
    Recognize faces in real-time from the webcam, comparing with known embeddings
    and logging attendance if a match is found.
    """
    names, known_embeddings = get_known_faces()
    if not names:
        print("No faces registered in the database. Please register faces first.")
        return

    video_stream = cv2.VideoCapture(0)
    if not video_stream.isOpened():
        print("Error: Camera not initialized!")
        return

    conn = sqlite3.connect("../database/attendance.db")
    try:
        cursor = conn.cursor()
        while True:
            ret, frame = video_stream.read()
            if not ret:
                print("Error: Unable to read frames from the camera.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            for face in faces:
                shape = shape_predictor(gray, face)
                embedding = embedder.compute_face_descriptor(frame, shape)

                matches = [np.linalg.norm(np.array(embedding) - np.array(known)) < 0.6 
                            for known in known_embeddings]
                if any(matches):
                    name = names[matches.index(True)]
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("INSERT INTO attendance (name, timestamp) VALUES (?, ?)", 
                                (name, timestamp))
                    conn.commit()
                    print(f"Recognized {name} at {timestamp}")

            cv2.imshow("Recognition", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        video_stream.release()
        conn.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Face Recognition Attendance System")
    print("=================================")
    
    while True:
        print("\nOptions:")
        print("r - Register a new face")
        print("a - Start attendance recognition")
        print("q - Quit the application")
        
        mode = input("\nEnter your choice: ").lower()
        
        if mode == 'r':
            register_face()
        elif mode == 'a':
            recognize_faces()
        elif mode == 'q':
            print("Exiting application...")
            break
        else:
            print("Invalid option. Please try again.")
