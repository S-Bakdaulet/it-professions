from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Браузерден (GitHub Pages немесе local сайттан) сұраныстарды қабылдау үшін


# Базаны инициализациялау (егер таблица болмаса, құрады)
def init_db():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CourseRequests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            selected_course TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


init_db()


# Сайттағы формадан өтінім қабылдайтын маршрут (API endpoint)
@app.route('/api/apply', methods=['POST'])
def apply_course():
    data = request.json
    name = data.get('name')
    course = data.get('course')

    if not name or not course:
        return jsonify({'status': 'error', 'message': 'Барлық өрісті толтырыңыз!'}), 400

    # DBeaver-дегі my_database.db файлына деректі жазу
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO CourseRequests (student_name, selected_course) VALUES (?, ?)', (name, course))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': f'Рақмет, {name}! "{course}" курсына өтінішіңіз базаға сақталды!'})


if __name__ == '__main__':
    print("Python Server іске қосылды: http://127.0.0.1:5000")
    app.run(port=5000, debug=True)