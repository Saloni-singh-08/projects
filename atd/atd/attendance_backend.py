# Backend - Flask + SQLite (Fixed and Improved)
from flask import Flask, request, jsonify
import sqlite3
import base64
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = 'attendance.db'
IMAGE_DIR = 'images'

os.makedirs(IMAGE_DIR, exist_ok=True)

# Initialize DB with fixed structure
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empId TEXT NOT NULL,
            imagePath TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            timestamp TEXT NOT NULL
        )''')
        conn.commit()

init_db()

@app.route('/mark-attendance', methods=['POST'])
def mark_attendance():
    try:
        data = request.get_json()
        empId = data.get('empId')
        image_data = data.get('image')
        location = data.get('location')

        if not empId or not image_data or not location:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        image_base64 = image_data.split(",")[-1]
        latitude = location.get('latitude')
        longitude = location.get('longitude')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        image_filename = f"{empId}_{timestamp.replace(' ', '_').replace(':', '-')}.png"
        image_path = os.path.join(IMAGE_DIR, image_filename)
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_base64))

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO attendance (empId, imagePath, latitude, longitude, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (empId, image_path, latitude, longitude, timestamp))
            conn.commit()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/get-attendance', methods=['GET'])
def get_attendance():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, empId, imagePath, latitude, longitude, timestamp FROM attendance")
            rows = cursor.fetchall()

        records = []
        for row in rows:
            image_base64 = ""
            if os.path.exists(row[2]):
                with open(row[2], "rb") as f:
                    image_base64 = "data:image/png;base64," + base64.b64encode(f.read()).decode('utf-8')

            records.append({
                "id": row[0],
                "empId": row[1],
                "image": image_base64,
                "location": {"latitude": row[3], "longitude": row[4]},
                "timestamp": row[5]
            })

        return jsonify({"records": records})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
