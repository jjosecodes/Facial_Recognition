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

### Getting Started

- Must have **Python 3.8+** installed on your system.
- Must have `cmake` installed on machine 
- Required Python libraries: `dlib`, `OpenCV`, `NumPy`, `SQLite`, `Flask`, `Tkinter`.
- Ensure you have a camera connected (or access to live video for testing).

#### Steps to install


### 1. Setting Up the Environment

Clone or Download the Project:
```bash
git clone <repository-url>
cd <repository_name>
```


### 2. Install CMake

Download and install `cmake` based on your platform:

- **Windows**:
  - Download the installer from [cmake.org](https://cmake.org/download/).
  - During installation, select the option to add CMake to the system PATH for all users.

- **macOS**:
  - Use the `.dmg` installer from the website or install via Homebrew:
    ```bash
    brew install cmake
    ```

- **Linux**:
  - Install CMake using your package manager:
    ```bash
    sudo apt-get install cmake
    ```


### 3. Install Necessary Libraries 


Once you have installed `CMake`, install the required Python libraries:

- Open a terminal or command prompt.
- Run the following command to install the necessary libraries:
  ```bash
  pip install -r requirements.txt
   ```





### Running the Tkinter GUI

1. **Launch the GUI**:
   - Navigate to the project's directory.
   - Run the following command:
     ```bash
     python gui.py
     ```

2. **Using the GUI**:
   - **Register Face**:
     - Enter the person's name.
     - Align your face with the camera feed.
     - Click "Register" to save the face embedding.
   - **Detect Face**:
     - Start live detection by clicking "Start Detection".
     - View the real-time recognition results.
   - **View Log**:
     - Access timestamps and registered names in the log

### Running the Flask Application

1. **Launch the Flask Server**:
   - Navigate to the flask_app directory.
   - Run the following command:
     ```bash
     python app.py
     ```

2. **Using the Flask Application**:
   - **Access the Web Interface**:
     - Open your web browser.
     - Navigate to the URL provided in the terminal (e.g., `http://127.0.0.1:5000/)

- **View Log**:
     - Access the "Log" section to view timestamps and registered entries in the database.
     - **Filter by Date**:
       - Use the date filter to narrow down logs by a specific date or date range.
     - **Filter by Face**:
       - Select a registered face from the dropdown or search by name to view logs related to that specific individual.
- **View Members**:
  - Section that shows the list of registered members where admin can delete members as needed