# Face Recognition and Classification System

This project is a comprehensive system for face recognition and classification. It includes features for detecting faces, registering individuals, and logging their appearance with timestamps. The system is implemented using Python, SQLite, Tkinter, and Flask.

## Features

1. **Face Detection and Classification**:
   - Detects faces in live images or video.
   - Classifies whether a person is registered in the database.

2. **Registration**:
   - Stores a person's name and face embedding in an SQLite database.

3. **Logging**:
   - Tracks and timestamps the appearance of individuals.

## How to Use

### Prerequisites

- **Python 3.8+** installed on your system.
- Required Python libraries: `dlib`, `OpenCV`, `NumPy`, `SQLite`, `Flask`, `Tkinter`.
- Ensure you have a camera connected (or access to live video for testing).

Install the necessary libraries:

```bash
pip install dlib opencv-python numpy flask
