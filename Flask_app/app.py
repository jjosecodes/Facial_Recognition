from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configure SQLite database
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "attendance.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)

# Attendance Model
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Face(db.Model):
    __tablename__ = 'faces'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    embedding = db.Column(db.Text, nullable=False)
    photo = db.Column(db.String(255)) 

@app.route("/")
def dashboard():
    

    logs = Attendance.query.order_by(Attendance.timestamp.desc()).all()

    
    summary = db.session.query(
        Attendance.name, db.func.count(Attendance.name)
    ).group_by(Attendance.name).all()

    daily_summary = db.session.query(
        db.func.date(Attendance.timestamp),  
        db.func.count(Attendance.id)         #
    ).group_by(db.func.date(Attendance.timestamp)).all()

    
    heatmap_data = {str(date): count for date, count in daily_summary}

    return render_template("dashboard.html", logs=logs, summary=summary, heatmap_data=heatmap_data)

@app.route("/logs", methods=["GET", "POST"])
def logs():
    if request.method == "POST":
        name = request.form["name"]
        new_entry = Attendance(name=name)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for("logs"))

    logs = Attendance.query.order_by(Attendance.timestamp.desc()).all()
    return render_template("logs.html", logs=logs)

@app.route("/filter", methods=["POST"])
def filter_logs():
    date = request.form.get("date")
    name = request.form.get("name")

    query = Attendance.query
    if date:
        query = query.filter(db.func.date(Attendance.timestamp) == date)
    if name:
        query = query.filter(Attendance.name.ilike(f"%{name}%"))

    logs = query.order_by(Attendance.timestamp.desc()).all()
    return render_template("logs.html", logs=logs)

@app.route("/delete/<int:log_id>", methods=["POST"])
def delete_log(log_id):
    log = Attendance.query.get_or_404(log_id)
    db.session.delete(log)
    db.session.commit()
    return redirect(url_for("logs"))

@app.route("/employees")
def employees():
    # Fetch unique employee names
    employees = Face.query.order_by(Face.id).all()
    return render_template("employees.html", employees=employees)

@app.route("/employee/<string:name>")
def employee_logs(name):
    logs = Attendance.query.filter_by(name=name).order_by(Attendance.timestamp.desc()).all()
    return render_template("logs.html", logs=logs)


@app.route("/delete_face/<int:face_id>", methods=["POST"])
def delete_face(face_id):
    # Find the entry by id and delete it
    face = Face.query.get_or_404(face_id)
    db.session.delete(face)
    db.session.commit()
    return redirect(url_for("employees"))

if __name__ == "__main__":
    app.run(debug=True)
