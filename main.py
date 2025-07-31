import sqlite3
import os
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_PATH = "auth_codes.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_codes (
                user_id INTEGER PRIMARY KEY,
                code TEXT
            )
        """)
        conn.commit()

def save_code(user_id, code):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO auth_codes (user_id, code)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET code=excluded.code
        """, (user_id, code))
        conn.commit()

def get_code(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT code FROM auth_codes WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        return row[0] if row else None

@app.route("/callback/<int:user_id>")
def callback(user_id):
    code = request.args.get("code")
    if not code:
        return "Missing code", 400

    save_code(user_id, code)
    print(f"[CALLBACK] user_id={user_id}, code={code}")
    return f"<h1>✅ Авторизация прошла</h1><p>user_id: {user_id}</p><p>code: {code}</p>", 200


@app.route("/get/<int:user_id>")
def get_user_code(user_id):
    code = get_code(user_id)
    return jsonify({
        "user_id": user_id,
        "code": code
    }), 200

@app.route("/healthz")
def healthz():
    return "OK", 200

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)