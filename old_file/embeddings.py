import cv2
import dlib
import sqlite3
import numpy as np

# Load models
detector = dlib.get_frontal_face_detector()
embedder = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")
shape_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Function to register a new face
def register_face():
    conn = sqlite3.connect("database/attendance.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
    ''')

    name = input("Enter the person's name: ")
    video_stream = cv2.VideoCapture(0)

    while True:
        ret, frame = video_stream.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            shape = shape_predictor(gray, face)
            embedding = embedder.compute_face_descriptor(frame, shape)

            # Save to database
            cursor.execute("INSERT INTO faces (name, embedding) VALUES (?, ?)", 
                            (name, ','.join(map(str, embedding))))
            conn.commit()
            print(f"Registered {name} successfully!")
            video_stream.release()
            cv2.destroyAllWindows()
            return

        cv2.imshow("Register Face", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_stream.release()
    cv2.destroyAllWindows()
    conn.close()

if __name__ == "__main__":
    register_face()
