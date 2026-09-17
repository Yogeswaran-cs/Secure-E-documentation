import os
import hashlib
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import mysql.connector

app = Flask(__name__)
app.secret_key = 'securedocs_secret_key'

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Update with your MySQL password
    'database': 'securedocs'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s AND role = %s", (username, password, role))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']

            cursor.execute("INSERT INTO logins (user_identifier, user_role) VALUES (%s, %s)", (username, role))
            conn.commit()
            cursor.close()
            conn.close()

            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'verifier':
                return redirect(url_for('verifier_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid Credentials', 'danger')
            cursor.close()
            conn.close()

    return render_template('login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM documents ORDER BY timestamp DESC")
    documents = cursor.fetchall()

    cursor.execute("SELECT * FROM logins ORDER BY login_time DESC LIMIT 5")
    recent_logins = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('admin_dashboard.html', documents=documents, recent_logins=recent_logins)

@app.route('/admin/issue', methods=['GET', 'POST'])
def issue_document():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        recipient = request.form['recipient']
        file = request.files['file']

        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            file_hash = calculate_sha256(file_path)
            mock_tx_id = "0x" + uuid.uuid4().hex + uuid.uuid4().hex[:16]
            mock_time = datetime.now()

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM documents WHERE token = %s", (file_hash,))
            existing = cursor.fetchone()

            if existing:
                status = 'Duplicate'
            else:
                status = 'Verified'

            cursor.execute("""
                INSERT INTO documents (user_id, filename, token, status, blockchain_tx_id, blockchain_timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (recipient, file.filename, file_hash, status, mock_tx_id, mock_time))
            conn.commit()
            cursor.close()
            conn.close()

            flash('Document issued successfully!', 'success')
            return redirect(url_for('admin_dashboard'))

    return render_template('issue_document.html')

@app.route('/user/dashboard')
def user_dashboard():
    if session.get('role') != 'user':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM documents WHERE user_id = %s", (session['username'],))
    documents = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('user_dashboard.html', documents=documents)

@app.route('/verifier/dashboard')
def verifier_dashboard():
    if session.get('role') != 'verifier':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM documents ORDER BY timestamp DESC LIMIT 5")
    activities = cursor.fetchall()

    cursor.execute("SELECT * FROM logins WHERE user_role = 'verifier' ORDER BY login_time DESC LIMIT 5")
    history = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('verifier_dashboard.html', activities=activities, history=history)

@app.route('/document/<int:doc_id>')
def document_details(doc_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM documents WHERE id = %s", (doc_id,))
    doc = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('document_details.html', doc=doc)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)