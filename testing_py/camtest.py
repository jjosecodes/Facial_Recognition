import cv2

video_stream = cv2.VideoCapture(0)

while True:
    ret, frame = video_stream.read()
    if not ret:
        print("Failed to capture video.")   
        break

    cv2.imshow("Test Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_stream.release()
cv2.destroyAllWindows()
