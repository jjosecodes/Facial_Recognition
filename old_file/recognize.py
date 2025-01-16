import cv2
import dlib
import sqlite3
from datetime import datetime
import numpy as np

detector = dlib.get_frontal_face_detector()
embedder = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

# Load known face embeddings and names (for simplicity, hardcode for now)
known_embeddings = [...]  # Add known embeddings here
known_names = [...]       # Add corresponding names here

def recognize_and_log():
    conn = sqlite3.connect("../database/attendance.db")
    cursor = conn.cursor()

    video_stream = cv2.VideoCapture(0)
    while True:
        ret, frame = video_stream.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            shape = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")(gray, face)
            embedding = embedder.compute_face_descriptor(frame, shape)

            # Compare embedding with known embeddings
            matches = [np.linalg.norm(np.array(embedding) - np.array(known)) < 0.6 for known in known_embeddings]
            if any(matches):
                name = known_names[matches.index(True)]
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO attendance (name, timestamp) VALUES (?, ?)", (name, timestamp))
                conn.commit()
                print(f"Recognized {name}, logged at {timestamp}")

        cv2.imshow("Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_stream.release()
    cv2.destroyAllWindows()
    conn.close()

if __name__ == "__main__":
    recognize_and_log()
