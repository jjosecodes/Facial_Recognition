import cv2
import dlib
import sqlite3
import numpy as np
from datetime import datetime
import time

# Load models
detector = dlib.get_frontal_face_detector()
embedder = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")
# facial landmarks
shape_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
# IF MODELS ARE NO LOADING ONLY 
try:
    embedder = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")
    shape_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    print("Models loaded successfully.")
except Exception as e:
    print(f"Error loading models: {e}")
    exit()
# Database connection
conn = sqlite3.connect("../database/attendance.db")
cursor = conn.cursor()

# Ensure tables exist
def create_tables():
    """
    Create necessary tables in the SQLite database.
    This ensures that the required tables exist before any operations.
    """
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            embedding TEXT NOT NULL,
            photo TEXT  -- Path to the stored photo
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


# Call the function to ensure tables are created
create_tables()

def get_known_faces():
    """
    Fetch all known face embeddings and their associated names from the database.
    Returns:
        - names (list): List of names of registered individuals.
        - embeddings (list): List of numpy arrays containing face embeddings.
    """
    cursor.execute("SELECT name, embedding FROM faces")
    data = cursor.fetchall()
    # Extract names and embeddings, converting the latter from string to numpy array
    names = [row[0] for row in data]
    embeddings = [np.array(row[1].split(','), dtype=float) for row in data]
    return names, embeddings

def register_face():
    """
    Register a new face by capturing from the webcam, extracting the face embedding,
    and saving the name and embedding in the database.
    """
    
    name = input("Enter the person's name: ")  # Get the name of the person to register
    video_stream = cv2.VideoCapture(0)  # Open the webcam

    if not video_stream.isOpened():
        print("Error: Camera not initialized!")
        return
    print("Camera initialized. Position yourself. Capturing in 4 seconds...")
    time.sleep(4) 
    while True:
        ret, frame = video_stream.read()
        if not ret:
            print("Error: Failed to retrieve frame from camera.")
            break

        # Debugging: Check if the feed is working
        print("Camera feed is active.")

        # Convert frame to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)  # Detect faces in the frame

        for face in faces:
            # Extract facial landmarks
            shape = shape_predictor(gray, face)
            # Generate face embedding
            embedding = embedder.compute_face_descriptor(frame, shape)
            # Insert name and embedding into the database
            cursor.execute("INSERT INTO faces (name, embedding) VALUES (?, ?)", 
                        (name, ','.join(map(str, embedding))))
            conn.commit()  # Commit the changes to the database
            print(f"Registered {name} successfully!")
            video_stream.release()
            cv2.destroyAllWindows()
            return

        # Display the webcam feed during registration
        cv2.imshow("Register Face", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit if 'q' is pressed
            break

    video_stream.release()
    cv2.destroyAllWindows()





def recognize_faces():
    """
    Recognize faces in real-time from the webcam, comparing with known embeddings
    and logging attendance if a match is found.
    """
    names, known_embeddings = get_known_faces()  # Fetch known embeddings and names
    video_stream = cv2.VideoCapture(0)  # Open the webcam

    while True:
        ret, frame = video_stream.read()
        if not ret:
            print("Error: Unable to read frames from the camera.")
        else:
            print("Frame captured successfully.")

        # Convert frame to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)  # Detect faces in the frame

        for face in faces:
            # Extract facial landmarks
            shape = shape_predictor(gray, face)
            # Generate face embedding
            embedding = embedder.compute_face_descriptor(frame, shape)

            # Compare the embedding with known embeddings
            matches = [np.linalg.norm(np.array(embedding) - np.array(known)) < 0.6 for known in known_embeddings]
            if any(matches):
                name = names[matches.index(True)]  # Get the matched name
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current timestamp
                # Log the recognized face in the attendance table
                cursor.execute("INSERT INTO attendance (name, timestamp) VALUES (?, ?)", (name, timestamp))
                conn.commit()
                print(f"Recognized {name} at {timestamp}")

        # Display the webcam feed during recognition
        cv2.imshow("Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit if 'q' is pressed
            break

    video_stream.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":


    """
    Main function to prompt the user for an action:
    - 'r': Register a new face
    - 'a': Start real-time face recognition and attendance logging
    - 'q': Quit the application
    """

    while True:
        mode = input("Enter 'r' to register a face, 'a' for attendance recognition, or 'q' to quit: ")
        if mode == 'r':
            register_face()  # Call the register function
        elif mode == 'a':
            recognize_faces()  # Call the recognition function
        elif mode == 'q':
            break  # Exit the application

# Close the database connection when the application exits
conn.close()
