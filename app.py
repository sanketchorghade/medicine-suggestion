from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = "medicaldatasore.db"


# ---------- DATABASE CONNECTION ----------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- HOME ----------
@app.route('/')
def home():
    return render_template('index.html')


# ---------- RECOMMENDATION API ----------
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    symptoms_input = data.get('symptoms', '').lower().strip()

    if not symptoms_input:
        return jsonify({'error': 'Please enter symptoms'}), 400

    symptom_list = [s.strip() for s in symptoms_input.split(',')]
    results = []

    conn = get_db_connection()
    cursor = conn.cursor()

    for symptom in symptom_list:
        cursor.execute("""
            SELECT symptom, condition, medicines, advice
            FROM doctor
            WHERE LOWER(symptom) LIKE ?
        """, (f"%{symptom}%",))

        record = cursor.fetchone()

        if record:
            results.append({
                "symptom": record["symptom"].title(),
                "condition": record["condition"],
                "medicines": record["medicines"].split(", "),
                "advice": record["advice"]
            })
        else:
            results.append({
                "symptom": symptom.title(),
                "condition": "Unknown",
                "medicines": ["Please consult a doctor"],
                "advice": "Your symptom requires professional medical evaluation."
            })

    conn.close()
    return jsonify({"results": results})


# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True, port=5000)
