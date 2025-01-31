from flask import Blueprint, request, session, redirect, url_for, flash, render_template
import sqlite3
import hashlib

auth = Blueprint('auth', __name__)

def get_db_connection():  # Define a function to establish a database connection
    conn = sqlite3.connect('database.db')  # Create a connection to the SQLite database file 'database.db'
    conn.row_factory = sqlite3.Row  # Set the row factory to return rows as dictionary-like objects
    return conn  # Return the database connection objectdef get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        password = request.form['password']
        password_hash = hash_password(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO usuarios (nombre, password_hash) VALUES (?, ?)", (nombre, password_hash))
            conn.commit()
            flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for('auth.login'))
        except sqlite3.IntegrityError:
            flash("El usuario ya existe.", "danger")
        finally:
            conn.close()

    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        password = request.form.get('password')

        if not nombre or not password:
            flash("Debes ingresar usuario y contraseña.", "danger")
            return redirect(url_for('auth.login'))

        password_hash = hash_password(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE nombre = ? AND password_hash = ?", (nombre, password_hash))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['usuario_id'] = user['id']
            session['nombre'] = user['nombre']
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for('questions'))
        else:
            flash("Credenciales incorrectas.", "danger")
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth.route('/logout')  # Define a route for the logout function at the URL endpoint '/logout'
def logout():  # Define the logout function
    session.clear()  # Clear all data from the session, effectively logging the user out
    flash("Has cerrado sesión.", "info")  # Flash a message to the user indicating they have logged out
    return redirect(url_for('auth.login'))  # Redirect the user to the login page after logout
    session.clear()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for('auth.login'))
from flask import Blueprint, request, session, redirect, url_for, flash, render_template  # Import necessary Flask modules for web routing, session management, and rendering templates
import sqlite3  # Import the SQLite module for database interactions
import hashlib  # Import the hashlib module for hashing passwords

auth = Blueprint('auth', __name__)  # Create a Blueprint named 'auth' for authentication-related routes

def get_db_connection():  # Define a function to establish a database connection
    conn = sqlite3.connect('database.db')  # Create a connection to the SQLite database file 'database.db'
    conn.row_factory = sqlite3.Row  # Set the row factory to return rows as dictionary-like objects
    return conn  # Return the database connection object

def hash_password(password):  # Define a function to hash passwords
    return hashlib.sha256(password.encode()).hexdigest()  # Hash the given password using SHA-256 and return the hexadecimal digest

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        password = request.form['password']
        password_hash = hash_password(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Asegurarnos de que el nombre de usuario sea único
            cursor.execute("SELECT * FROM usuarios WHERE nombre = ?", (nombre,))
            existing_user = cursor.fetchone()
            if existing_user:
                flash("El usuario ya existe.", "danger")
                return redirect(url_for('auth.register'))

            # Guardar el nuevo usuario
            cursor.execute("INSERT INTO usuarios (nombre, password_hash) VALUES (?, ?)", (nombre, password_hash))
            conn.commit()
            flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for('auth.login'))
        except sqlite3.IntegrityError:
            flash("Hubo un error al registrar el usuario.", "danger")
        finally:
            conn.close()

    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        password = request.form.get('password')

        if not nombre or not password:
            flash("Debes ingresar usuario y contraseña.", "danger")
            return redirect(url_for('auth.login'))  # Redirigir para evitar mostrar el mensaje antes de la interacción

        password_hash = hash_password(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE nombre = ? AND password_hash = ?", (nombre, password_hash))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['usuario_id'] = user['id']
            session['nombre'] = user['nombre']
            flash("Inicio de sesión exitoso.", "success")  # Solo se muestra si las credenciales son correctas
            return redirect(url_for('questions'))
        else:
            flash("Credenciales incorrectas.", "danger")  # Solo se muestra si las credenciales son incorrectas
            return redirect(url_for('auth.login'))

    return render_template('login.html')  # Solo renderiza el formulario si el método es GET




@auth.route('/logout')  # Define a route for the logout function at the URL endpoint '/logout'
def logout():  # Define the logout function
    session.clear()  # Clear all data from the session, effectively logging the user out
    flash("Has cerrado sesión.", "info")  # Flash a message to the user indicating they have logged out
    return redirect(url_for('auth.login'))  # Redirect the user to the login page after logout