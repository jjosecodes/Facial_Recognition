import tkinter as tk
from tkinter import ttk, messagebox
from main import register_face, recognize_faces
import threading
import cv2
from PIL import Image, ImageTk
import sqlite3
import sys
import io

class CameraFeed:
    def __init__(self, label):
        self.label = label
        self.is_running = False
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Unable to access camera")
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
            ("View Database", self.show_database_page),
            ("Exit", self.on_exit)
        ]
        for text, command in buttons:
            btn = ttk.Button(self.nav_frame, text=text, command=command)
            btn.pack(fill="x", pady=2)

        # Pages
        self.register_page = self.create_register_page()
        self.recognition_page = self.create_recognition_page()
        self.database_page = self.create_database_page()

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

        # Add log output area
        self.log_output = tk.Text(frame, wrap="word", height=20, width=40)
        self.log_output.pack(fill="both", expand=True, padx=10, pady=10)

        # Redirect stdout to log
        self.stdout_backup = sys.stdout
        sys.stdout = self.RedirectToWidget(self.log_output)

        start_btn = ttk.Button(frame, text="Start Recognition", command=self.recognize_faces_gui)
        start_btn.pack(pady=10)
        return frame

    def create_database_page(self):
        frame = ttk.Frame(self.content_frame)
        ttk.Label(frame, text="Database View", font=("Helvetica", 16)).pack(pady=10)

        self.database_tree = ttk.Treeview(frame, columns=("ID", "Name", "Timestamp"), show="headings")
        self.database_tree.heading("ID", text="ID")
        self.database_tree.heading("Name", text="Name")
        self.database_tree.heading("Timestamp", text="Last Attendance")
        self.database_tree.pack(fill="both", expand=True)

        refresh_btn = ttk.Button(frame, text="Refresh", command=self.refresh_database)
        refresh_btn.pack(pady=10)
        return frame

    def show_register_page(self):
        self.hide_all_pages()
        self.register_page.pack(fill="both", expand=True)

    def show_recognition_page(self):
        self.hide_all_pages()
        self.recognition_page.pack(fill="both", expand=True)

    def show_database_page(self):
        self.hide_all_pages()
        self.database_page.pack(fill="both", expand=True)
        self.refresh_database()

    def hide_all_pages(self):
        self.register_page.pack_forget()
        self.recognition_page.pack_forget()
        self.database_page.pack_forget()

    def register_face_gui(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name.")
            return
        self.camera_feed.stop()  # Stop camera feed during registration
        threading.Thread(target=self.run_register_face, args=(name,), daemon=True).start()

    def run_register_face(self, name):
        try:
            register_face(name)
            messagebox.showinfo("Success", f"Face registered successfully for {name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to register face: {str(e)}")
        finally:
            self.camera_feed.start()  # Restart camera feed after registration

    def recognize_faces_gui(self):
        self.camera_feed.stop()  # Stop camera feed during recognition
        threading.Thread(target=self.run_recognition, daemon=True).start()

    def run_recognition(self):
        try:
            recognize_faces()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.camera_feed.start()  # Restart camera feed after recognition

    def refresh_database(self):
        conn = sqlite3.connect("../database/attendance.db")
        cursor = conn.cursor()
        self.database_tree.delete(*self.database_tree.get_children())
        cursor.execute("SELECT id, name, timestamp FROM attendance ORDER BY id")
        for row in cursor.fetchall():
            self.database_tree.insert("", "end", values=row)
        conn.close()

    def on_exit(self):
        self.camera_feed.stop()
        sys.stdout = self.stdout_backup  # Restore original stdout
        self.destroy()

    class RedirectToWidget:
        def __init__(self, widget):
            self.widget = widget

        def write(self, text):
            self.widget.insert("end", text)
            self.widget.see("end")  # Auto-scroll to the end

        def flush(self):
            pass

if __name__ == "__main__":
    app = Application()
    app.camera_feed.start()
    app.mainloop()
