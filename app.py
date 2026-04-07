from flask import Flask, request, jsonify
from database import get_db_connection
from models import create_tables

app = Flask(__name__)

# ---------------- ROLE CHECK ----------------
def require_roles(allowed_roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user_role = request.headers.get('role')
            user_email = request.headers.get('email')

            if not user_role:
                return jsonify({"error": "Role header is required"}), 400

            if user_role not in allowed_roles:
                return jsonify({"error": "Permission denied"}), 403

            # Check if user is active
            if user_email:
                conn = get_db_connection()
                user = conn.execute(
                    "SELECT * FROM users WHERE email=? AND role=?",
                    (user_email, user_role)
                ).fetchone()
                conn.close()

                if user and user['status'] == 'inactive':
                    return jsonify({"error": "Your account is inactive. Contact admin."}), 403

            return func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

# ---------------- HOME ----------------
@app.route('/')
def home():
    return "FinSight backend is running successfully!"

# ---------------- USER APIs ----------------
@app.route('/users', methods=['POST'])
@require_roles(['admin'])
def add_user():
    data = request.json

    name = data.get('name')
    email = data.get('email')
    role = data.get('role')
    status = data.get('status', 'active')

    if not name or not email or not role:
        return jsonify({"error": "Required fields are missing"}), 400

    if role not in ['admin', 'analyst', 'viewer']:
        return jsonify({"error": "Role must be admin, analyst, or viewer"}), 400

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO users (name, email, role, status) VALUES (?, ?, ?, ?)",
        (name, email, role, status)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "User added successfully"}), 201

@app.route('/users', methods=['GET'])
@require_roles(['admin'])
def fetch_users():
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()

    return jsonify([dict(user) for user in users])

# UPDATE USER STATUS
@app.route('/users/<int:user_id>', methods=['PUT'])
@require_roles(['admin'])
def update_user(user_id):
    data = request.json
    status = data.get('status')

    if status not in ['active', 'inactive']:
        return jsonify({"error": "Status must be active or inactive"}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    conn.execute(
        "UPDATE users SET status=? WHERE id=?",
        (status, user_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "User status updated successfully"})

# ---------------- RECORD APIs ----------------
@app.route('/records', methods=['POST'])
@require_roles(['admin'])
def add_record():
    data = request.json

    user_id = data.get('user_id')
    amount = data.get('amount')
    record_type = data.get('type')
    category = data.get('category')
    date = data.get('date')
    note = data.get('note')

    if not user_id or not amount or not record_type:
        return jsonify({"error": "Required fields are missing"}), 400

    if amount <= 0:
        return jsonify({"error": "Amount must be greater than zero"}), 400

    if record_type not in ['income', 'expense']:
        return jsonify({"error": "Type must be income or expense"}), 400

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO records (user_id, amount, type, category, date, note) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, amount, record_type, category, date, note)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Record added successfully"}), 201

@app.route('/records', methods=['GET'])
@require_roles(['admin', 'analyst', 'viewer'])
def fetch_records():
    record_type = request.args.get('type')
    category = request.args.get('category')
    date = request.args.get('date')

    query = "SELECT * FROM records WHERE 1=1"
    params = []

    if record_type:
        query += " AND type=?"
        params.append(record_type)

    if category:
        query += " AND category=?"
        params.append(category)

    if date:
        query += " AND date=?"
        params.append(date)

    conn = get_db_connection()
    records = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([dict(rec) for rec in records])

# UPDATE RECORD
@app.route('/records/<int:record_id>', methods=['PUT'])
@require_roles(['admin'])
def update_record(record_id):
    data = request.json

    amount = data.get('amount')
    record_type = data.get('type')
    category = data.get('category')
    date = data.get('date')
    note = data.get('note')

    if not amount or not record_type:
        return jsonify({"error": "Amount and type are required"}), 400

    if amount <= 0:
        return jsonify({"error": "Amount must be greater than zero"}), 400

    if record_type not in ['income', 'expense']:
        return jsonify({"error": "Type must be income or expense"}), 400

    conn = get_db_connection()
    record = conn.execute("SELECT * FROM records WHERE id=?", (record_id,)).fetchone()
    if not record:
        conn.close()
        return jsonify({"error": "Record not found"}), 404

    conn.execute("""
        UPDATE records
        SET amount=?, type=?, category=?, date=?, note=?
        WHERE id=?
    """, (amount, record_type, category, date, note, record_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Record updated successfully"})

# DELETE RECORD
@app.route('/records/<int:record_id>', methods=['DELETE'])
@require_roles(['admin'])
def delete_record(record_id):
    conn = get_db_connection()
    record = conn.execute("SELECT * FROM records WHERE id=?", (record_id,)).fetchone()
    if not record:
        conn.close()
        return jsonify({"error": "Record not found"}), 404

    conn.execute("DELETE FROM records WHERE id=?", (record_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Record deleted successfully"})

# ---------------- DASHBOARD APIs ----------------
@app.route('/dashboard/summary', methods=['GET'])
@require_roles(['admin', 'analyst', 'viewer'])
def get_summary():
    conn = get_db_connection()

    income = conn.execute(
        "SELECT SUM(amount) FROM records WHERE type='income'"
    ).fetchone()[0]

    expense = conn.execute(
        "SELECT SUM(amount) FROM records WHERE type='expense'"
    ).fetchone()[0]

    conn.close()

    income = income if income else 0
    expense = expense if expense else 0

    return jsonify({
        "total_income": income,
        "total_expense": expense,
        "net_balance": income - expense
    })

@app.route('/dashboard/category', methods=['GET'])
@require_roles(['admin', 'analyst', 'viewer'])
def get_category_summary():
    conn = get_db_connection()

    data = conn.execute("""
        SELECT category, SUM(amount) as total
        FROM records
        GROUP BY category
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in data])

@app.route('/dashboard/recent', methods=['GET'])
@require_roles(['admin', 'analyst', 'viewer'])
def get_recent_activity():
    conn = get_db_connection()

    data = conn.execute("""
        SELECT * FROM records
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in data])

# TRENDS API
@app.route('/dashboard/trends', methods=['GET'])
@require_roles(['admin', 'analyst'])
def get_trends():
    conn = get_db_connection()

    data = conn.execute("""
        SELECT substr(date, 1, 7) as month,
               SUM(CASE WHEN type='income' THEN amount ELSE 0 END) as income,
               SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as expense
        FROM records
        GROUP BY month
        ORDER BY month
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in data])

# ---------------- MAIN ----------------
if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
