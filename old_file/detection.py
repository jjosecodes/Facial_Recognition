import cv2
import dlib


# Load face detector
detector = dlib.get_frontal_face_detector()

def detect_faces():
    # Use the webcam
    # 1 - main camera, 3 - NDI camera from laptop
    video_stream = cv2.VideoCapture(0) 
    while True:
        ret, frame = video_stream.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        faces = detector(gray)  # Detect faces
        print(f"Number of faces detected: {len(faces)}")

        # Draw rectangles around face
        for face in faces:
            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow("Face Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_stream.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_faces()
    