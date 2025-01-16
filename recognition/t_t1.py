import tkinter as tk
from tkinter import ttk, messagebox
from maintest import register_face, get_known_faces
import threading
import cv2
from PIL import Image, ImageTk
import numpy as np
import sqlite3
import os
from datetime import datetime
import dlib

# Load Dlib models
detector = dlib.get_frontal_face_detector()
embedder = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")
shape_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")


class CameraFeed:
    def __init__(self, label):
        self.label = label
        self.is_running = False
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Unable to access the camera")
            return
        self.is_running = True
        self.update_feed()

    def update_feed(self):
        if self.is_running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.label.imgtk = imgtk
                self.label.configure(image=imgtk)
                self.label.after(10, self.update_feed)
            else:
                messagebox.showerror("Error", "Failed to capture frame")
                self.stop()

    def stop(self):
        if self.cap:
            self.is_running = False
            self.cap.release()
            self.label.configure(image="")


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Face Recognition Attendance System")
        self.geometry("1024x768")

        self.names, self.embeddings, self.photos = get_known_faces()
        self.default_image_path = "./NoFedImage/default.jpg"
        self.waiting_image_path = "./NoFedImage/waiting.jpg"
        self.unrecognized_image_path = "./NoFedImage/unrecognized.jpg"
        self.recognition_running = False
        self.recognition_thread = None
        self.setup_ui()

    def setup_ui(self):
        # Frames
        self.nav_frame = ttk.Frame(self, padding="5")
        self.nav_frame.pack(side="left", fill="y", padx=5, pady=5)

        self.camera_frame = ttk.Frame(self, padding="5")
        self.camera_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.content_frame = ttk.Frame(self, padding="5")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Camera feed
        self.camera_label = ttk.Label(self.camera_frame)
        self.camera_label.pack(fill="both", expand=True)
        self.camera_feed = CameraFeed(self.camera_label)

        # Navigation buttons
        buttons = [
            ("Register Face", self.show_register_page),
            ("Recognition Mode", self.show_recognition_page),
            ("Exit", self.on_exit),
        ]
        for text, command in buttons:
            btn = ttk.Button(self.nav_frame, text=text, command=command)
            btn.pack(fill="x", pady=2)

        # Pages
        self.register_page = self.create_register_page()
        self.recognition_page = self.create_recognition_page()

        # Show default page
        self.show_register_page()

    def create_register_page(self):
        frame = ttk.Frame(self.content_frame)
        ttk.Label(frame, text="Register Face", font=("Helvetica", 16)).pack(pady=10)

        name_label = ttk.Label(frame, text="Enter Name:")
        name_label.pack(pady=5)
        self.name_entry = ttk.Entry(frame)
        self.name_entry.pack(pady=5)

        register_btn = ttk.Button(frame, text="Register", command=self.register_face_gui)
        register_btn.pack(pady=10)
        return frame

    def create_recognition_page(self):
        frame = ttk.Frame(self.content_frame)
        ttk.Label(frame, text="Recognition Mode", font=("Helvetica", 16)).pack(pady=10)

        # Display recognized image
        self.recognized_image_label = ttk.Label(frame)
        self.recognized_image_label.pack(pady=10)

        # Display right-side status (Access Granted, Unauthorized, etc.)
        self.recognized_status_label = ttk.Label(frame, text="", font=("Helvetica", 14))
        self.recognized_status_label.pack(pady=10)

        # Recognition button
        self.recognition_button = ttk.Button(frame, text="Start Recognition", command=self.toggle_recognition)
        self.recognition_button.pack(pady=10)

        # Set initial "waiting" image
        self.set_image(self.waiting_image_path)
        return frame

    def set_image(self, image_path):
        try:
            image = Image.open(image_path).resize((150, 200))
            photo = ImageTk.PhotoImage(image)
            self.recognized_image_label.config(image=photo)
            self.recognized_image_label.image = photo
        except Exception as e:
            print(f"[DEBUG] Error setting image: {str(e)}")

    def set_status(self, status_text, status_color):
        self.recognized_status_label.config(text=status_text, foreground=status_color)

    def show_register_page(self):
        self.hide_all_pages()
        self.register_page.pack(fill="both", expand=True)

    def show_recognition_page(self):
        self.hide_all_pages()
        self.recognition_page.pack(fill="both", expand=True)

    def hide_all_pages(self):
        self.register_page.pack_forget()
        self.recognition_page.pack_forget()

    def register_face_gui(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name.")
            return

        threading.Thread(target=self.run_register_face, args=(name,), daemon=True).start()

    def run_register_face(self, name):
        if not self.camera_feed.cap or not self.camera_feed.cap.isOpened():
            messagebox.showerror("Error", "Camera is not running.")
            return

        try:
            print("[DEBUG] Starting registration...")
            ret, frame = self.camera_feed.cap.read()
            if not ret:
                print("[DEBUG] Failed to capture frame for registration.")
                messagebox.showerror("Error", "Failed to capture frame for registration.")
                return

            # Process the captured frame for registration
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            if not faces:
                print("[DEBUG] No faces detected during registration.")
                messagebox.showerror("Error", "No face detected. Please try again.")
                return

            for face in faces:
                shape = shape_predictor(gray, face)
                embedding = embedder.compute_face_descriptor(frame, shape)

                # Save the captured image and embedding to the database
                photo_path = f"./photos/{name}.jpg"
                cv2.imwrite(photo_path, frame)

                conn = sqlite3.connect("../database/attendance.db")
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO faces (name, embedding, photo) VALUES (?, ?, ?)",
                    (name, ','.join(map(str, embedding)), photo_path),
                )
                conn.commit()
                conn.close()

                print(f"[DEBUG] Successfully registered face for {name}.")
                messagebox.showinfo("Success", f"Face registered successfully for {name}")
                return
        except Exception as e:
            print(f"[DEBUG] Error during registration: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def toggle_recognition(self):
        if self.recognition_running:
            # Stop recognition
            self.recognition_running = False
            self.recognition_button.config(text="Start Recognition")
            print("[DEBUG] Recognition stopped.")
            
            # Reset the UI to waiting screen
            self.set_image(self.waiting_image_path)  # Reset to the waiting image
            self.set_status("", "")  # Clear the status
        else:
            # Start recognition
            self.names, self.embeddings, self.photos = get_known_faces()  # Refresh data
            self.recognition_running = True
            self.recognition_button.config(text="Stop Recognition")
            self.recognition_thread = threading.Thread(target=self.run_recognition, daemon=True)
            self.recognition_thread.start()
            print("[DEBUG] Recognition started.")


    def run_recognition(self):
        if not self.names:
            messagebox.showerror("Error", "No faces registered. Please register faces first.")
            return

        while self.recognition_running:
            ret, frame = self.camera_feed.cap.read()
            if not ret:
                print("[DEBUG] Camera feed error.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            if not faces:
                # No faces detected, reset to waiting screen
                self.set_image(self.waiting_image_path)
                self.set_status("", "")  # Clear the status
                continue

            recognized = False
            for face in faces:
                shape = shape_predictor(gray, face)
                embedding = embedder.compute_face_descriptor(frame, shape)

                matches = [np.linalg.norm(np.array(embedding) - np.array(known)) < 0.6 for known in self.embeddings]
                if any(matches):
                    recognized = True
                    name = self.names[matches.index(True)]
                    photo_path = self.photos[matches.index(True)]
                    recognized_image_path = photo_path if os.path.exists(photo_path) else self.default_image_path

                    print(f"[DEBUG] Recognized: {name}")
                    self.set_image(recognized_image_path)
                    self.set_status(f"Access Granted\nName: {name}", "green")
                    break  # Exit after recognizing a face

            if not recognized:
                # Unrecognized face
                self.set_image(self.unrecognized_image_path)
                self.set_status("Unauthorized", "red")

        # If the loop exits (e.g., on stop), reset to waiting screen
        self.set_image(self.waiting_image_path)
        self.set_status("", "")
        print("[DEBUG] Recognition thread exiting.")


    def on_exit(self):
        self.camera_feed.stop()
        self.recognition_running = False
        self.destroy()


if __name__ == "__main__":
    app = Application()
    app.camera_feed.start()
    app.mainloop()
