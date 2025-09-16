import os
from functools import wraps

import werkzeug.security
from flask import Flask, session, abort, redirect, render_template, request, flash, g, url_for
import sqlite3
import uuid
import json

from secure_session import CustomSessionInterface

app = Flask(__name__)
app.session_interface = CustomSessionInterface()
app.config["DATABASE"] = "db.sqlite"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(db):
    db = g.pop('db', None)

    if db is not None:
        db.close()

app.teardown_appcontext(close_db)

def get_user_by_name(db, username):
    user = db.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    return user

def get_user_by_id(db, id):
    user = db.execute(
        "SELECT * FROM users WHERE id = ?", (id,)
    ).fetchone()
    return user

def get_current_user():
    user_id = session.get("user_id")
    if user_id is None: return None
    return get_user_by_id(get_db(), user_id)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("You must be logged in to see this page.", category="warning")
            return redirect(url_for('login_view'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def homepage():
    return render_template("home.html", current_user=get_current_user())

@app.route("/login", methods=("GET",))
def login_view():
    return render_template("login.html", current_user=get_current_user())

@app.route("/login", methods=("POST",))
def do_login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    db = get_db()
    login_failed = False
    user = get_user_by_name(db, username)
    if user is None:
        login_failed = True
    elif not werkzeug.security.check_password_hash(user['password_hash'], password):
        login_failed = True

    if not login_failed:
        session["user_id"] = user['id']
        session["is_admin"] = False
        flash("Login successful.", category="message")
        return redirect(url_for("homepage"))
    else:
        flash("Login failed.", category="error")
        return render_template("login.html", current_user=get_current_user())

@app.route("/logout", methods=("POST",))
@login_required
def logout():
    session.clear()
    flash("Logged out.", category="message")
    return redirect("homepage")

@app.route("/register", methods=("GET",))
def register_view():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def do_register():
    username = request.form.get('username', '').strip()
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    accept_terms = request.form.get('accept_terms')
    db = get_db()

    # Basic validation
    if not username or not password or not confirm_password:
        flash('All fields are required.', 'error')
        return redirect(url_for('register_view'))

    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('register_view'))

    if not accept_terms:
        flash('You must agree to the Terms and Conditions.', 'error')
        return redirect(url_for('register_view'))

    if get_user_by_name(db, username) is not None:
        flash('Username already exists.', 'error')
        return redirect(url_for('register_view'))

    # Hash password and create user
    user_id = str(uuid.uuid4())
    hashed_pw = werkzeug.security.generate_password_hash(password)
    db.execute("INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)", (user_id, username, hashed_pw))
    db.commit()

    flash('Registration successful. You may now log in.', 'success')
    return redirect(url_for('login_view'))

@app.route("/models", methods=("GET",))
@login_required
def model_overview():
    db = get_db()
    result = db.execute("SELECT * FROM models")
    models = result.fetchall()
    return render_template('model-overview.html', models=models, current_user=get_current_user())

@app.route('/models/new')
@login_required
def new_model_form():
    return render_template('new-model-form.html', current_user=get_current_user())

@app.route('/models', methods=['POST'])
@login_required
def save_model():
    brand = request.form.get('brand')
    model_name = request.form.get('model_name')
    model_number = request.form.get('model_number')
    capacity = request.form.get('capacity')

    if not (brand and model_name and model_number and capacity):
        flash('All fields are required.', 'error')
        return redirect(url_for('new_model_form'))

    db = get_db()
    try:
        model_id = str(uuid.uuid4())
        db.execute(
            """
                INSERT INTO models (id, brand, model_name, model_number, capacity)
                VALUES (:id, :brand, :model_name, :model_number, :capacity)
            """,
            {
                'id': model_id,
                'brand': brand,
                'model_name': model_name,
                'model_number': model_number,
                'capacity': int(capacity, 10)
            }
        )
        db.commit()
        flash('Model saved successfully.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error saving model: {str(e)}', 'error')

    return redirect(url_for('model_overview'))

@app.route("/tapes", methods=("GET",))
@login_required
def tapes_overview():
    db = get_db()
    result = db.execute("""
        SELECT tapes.id, tapes.serial_number, tapes.status, tapes.location,
               models.brand as brand_name, models.model_name as model_name
        FROM tapes
        JOIN models ON tapes.model_id = models.id
    """)
    tapes = result.fetchall()
    return render_template('tapes-overview.html', tapes=tapes, current_user=get_current_user())

@app.route('/tapes/new')
@login_required
def new_tape_form():
    db = get_db()
    models_result = db.execute("SELECT id, brand, model_name FROM models")
    models = models_result.fetchall()
    return render_template('new-tape-form.html', models=models, current_user=get_current_user())

@app.route('/tapes', methods=['POST'])
@login_required
def save_tape():
    model_id = request.form.get('model_id')
    serial_number = request.form.get('serial_number')
    status = request.form.get('status')
    location = request.form.get('location')

    if not all([model_id, serial_number, status, location]):
        flash('All fields are required.', 'error')
        return redirect(url_for('new_tape_form'))

    tape_id = str(uuid.uuid4())
    db = get_db()
    try:
        db.execute("""
            INSERT INTO tapes (id, model_id, serial_number, status, location)
            VALUES (:id, :model_id, :serial_number, :status, :location)
        """, {
            'id': tape_id,
            'model_id': model_id,
            'serial_number': serial_number,
            'status': status,
            'location': location
        })
        db.commit()
        flash('Tape created successfully.', 'success')
    except Exception as e:
        db.rollback()
        flash("There was an error saving the tape.", category="error")

    return redirect(url_for('tapes_overview'))

@app.route('/tapes/<tape_id>/edit')
@login_required
def edit_tape_form(tape_id):
    db = get_db()
    tape = db.execute("SELECT * FROM tapes WHERE id = :id", {'id': tape_id}).fetchone()
    if not tape:
        flash('Tape not found.', 'error')
        return redirect(url_for('tapes_overview'))

    return render_template('edit-tape.html', tape=tape, statuses=["AVAILABLE", "IN_USE", "DECOMMISSIONED"], current_user=get_current_user())

@app.route('/tapes/<tape_id>', methods=['POST'])
@login_required
def update_tape(tape_id):
    status = request.form.get('status')
    location = request.form.get('location')

    if not all([status, location]):
        flash('All fields are required.', 'error')
        return redirect(url_for('edit_tape_form', tape_id=tape_id))

    db = get_db()
    try:
        db.execute("""
            UPDATE tapes SET status = :status, location = :location WHERE id = :id
        """, {
            'id': tape_id,
            'status': status,
            'location': location
        })
        db.commit()
        flash('Tape updated successfully.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Failed to update the tape :(', 'error')

    return redirect(url_for('tapes_overview'))

@app.route("/get-flag")
@login_required
def get_session():
    if not session["is_admin"]:
        abort(401)
    flag_path = os.getenv("FLAG_PATH", "flag/flag.txt")
    with open(flag_path) as f:
        return f.read()

@app.route("/legal")
def get_terms_and_conditions():
    return render_template("terms-and-conditions.html")

@app.route("/health")
def healthcheck():
    healthy = True
    try:
        db = get_db()
        query_result = db.execute("SELECT 1").fetchone()
        if query_result is None or query_result[0] != 1:
            healthy = False
    except:
        healthy = False

    if not healthy:
        status_code = 503
    else:
        status_code = 200
    result = {"healthy": healthy}
    response = app.response_class(
        response=json.dumps(result),
        status=status_code,
        mimetype='application/json'
    )
    return response




def init_db():
    with app.app_context():
        db = get_db()
        with open('db/schema.sql') as f:
            db.executescript(f.read())

if __name__ == "__main__":
    init_db()
    app.run()
