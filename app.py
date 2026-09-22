import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Браузерден (GitHub Pages немесе локальді сайттан) сұраныстарды қабылдау үшін CORS қосу
CORS(app)

DB_NAME = 'my_database.db'


def init_db():
    """Деректер базасын инициализациялау және кестені құру/жаңарту"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Негізгі кестені құру
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CourseRequests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            phone TEXT,
            selected_course TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Егер бұрыннан бар кестеде 'phone' бағанасы болмаса, оны автоматты түрде қосу
    cursor.execute("PRAGMA table_info(CourseRequests);")
    columns = [column[1] for column in cursor.fetchall()]
    if 'phone' not in columns:
        cursor.execute("ALTER TABLE CourseRequests ADD COLUMN phone TEXT;")

    conn.commit()
    conn.close()


# Сервер іске қосылғанда базаны дайындау
init_db()


@app.route('/api/apply', methods=['POST'])
def apply_course():
    """Сайттағы формадан өтінім қабылдайтын API маршруты"""
    try:
        # JSON немесе Form data түрінде келген деректерді қабылдау
        data = request.get_json(silent=True) or request.form

        name = data.get('name') or data.get('student_name')
        phone = data.get('phone', 'Көрсетілмеген')
        course = data.get('course') or data.get('selected_course')

        # Валидация: аты мен курсы міндетті түрдe болуы керек
        if not name or not course:
            return jsonify({
                'status': 'error',
                'message': 'Барлық өрістерді толтырыңыз!'
            }), 400

        # SQLite базасына деректерді сақтау (DBeaver-ден көруге болады)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO CourseRequests (student_name, phone, selected_course)
            VALUES (?, ?, ?)
        ''', (name, phone, course))
        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': f'Рахмет, {name}! "{course}" курсына өтінішіңіз базаға сәтті сақталды.'
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Серверлік қате орын алды: {str(e)}'
        }), 500


@app.route('/api/requests', methods=['GET'])
def get_requests():
    """Базадағы барлық өтінімдерді қарауға арналған көмекші маршрут"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, student_name, phone, selected_course, created_at FROM CourseRequests ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                'id': row[0],
                'student_name': row[1],
                'phone': row[2],
                'selected_course': row[3],
                'created_at': row[4]
            })

        return jsonify({'status': 'success', 'data': result}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    print("Python Server іске қосылды: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
