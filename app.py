from flask import Flask, render_template, request, redirect, g, session
from auth import auth

import sqlite3
import json
import random

app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura"  # Cambiar por algo seguro en producción
app.register_blueprint(auth)

# Conexión a la base de datos (archivo temporal persistente durante la ejecución)
def get_db_connection():
    if 'db_connection' not in g:
        g.db_connection = sqlite3.connect('temporary.db', check_same_thread=False)  # BD persistente en ejecución
        g.db_connection.row_factory = sqlite3.Row
    return g.db_connection



# Cargar preguntas desde el archivo JSON
def load_questions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, texto, categoria, nivel, estado FROM preguntas")
    preguntas = [dict(row) for row in cursor.fetchall()]  # Convertimos sqlite3.Row a diccionario
    #conn.close()
    return preguntas


# Inicialización de la base de datos con app.app_context()
import os
import json
import os
def initialize_db():
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()

        # Crear la tabla de usuarios si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
        """)

        # Crear la tabla de preguntas si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS preguntas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT NOT NULL,
            categoria TEXT NOT NULL,
            nivel TEXT NOT NULL,
            estado TEXT CHECK(estado IN ('activa', 'editada', 'eliminada')) DEFAULT 'activa',
            origen TEXT CHECK(origen IN ('predefinida', 'generada'))
        );
        """)

        # Crear la tabla de respuestas si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS respuestas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pregunta_id INTEGER,
            usuario_id INTEGER,
            texto TEXT NOT NULL,
            valor INTEGER NOT NULL,
            FOREIGN KEY (pregunta_id) REFERENCES preguntas(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
        """)

        conn.commit()






# Ruta para la página de inicio
@app.route('/')
def home():
    return render_template('index.html')

# Ruta para mostrar preguntas y respuestas
@app.route('/questions', methods=["GET", "POST"])
def questions():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("TRAZA: Entro a questions")

    if request.method == "POST":
        print("TRAZA: Entro a questions - POST")
        usuario_id = random.randint(1, 1000)

        preguntas = load_questions()
        print("TRAZA: Preguntas cargadas:", preguntas)

        for pregunta in preguntas:
            if "id" not in pregunta:
                print("TRAZA: ERROR: Pregunta sin ID:", pregunta)
                continue

            respuesta = request.form.get(f"respuesta_{pregunta['id']}")
            if respuesta:
                valor_respuesta = 0 if respuesta == "NO" else 1 if respuesta == "TAL VEZ" else 2
                cursor.execute("INSERT INTO respuestas (pregunta_id, usuario_id, texto, valor) VALUES (?, ?, ?, ?)",
                               (pregunta['id'], usuario_id, respuesta, valor_respuesta))

        conn.commit()

        cursor.execute("SELECT * FROM respuestas")
        respuestas_guardadas = [dict(row) for row in cursor.fetchall()] 
        
        print("TRAZA: Respuestas guardadas:", respuestas_guardadas)

        return redirect('/results')

    cursor.execute("SELECT id, texto FROM preguntas")
    preguntas = cursor.fetchall()
    conn.close()
    return render_template('questions.html', preguntas=preguntas)








# Ruta para mostrar resultados (coincidencias)
@app.route('/results')
def results():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener los distintos usuarios que han respondido
    cursor.execute("SELECT DISTINCT usuario_id FROM respuestas")
    usuarios = [row['usuario_id'] for row in cursor.fetchall()]

    if len(usuarios) < 2:
        print("TRAZA: Menos de 2 usuarios con respuestas. No se pueden calcular coincidencias.")
        return render_template('results.html', coincidencias=0, porcentaje=0, mensaje="Esperando respuestas de otro usuario")

    usuario_1, usuario_2 = usuarios[:2]  # Tomamos los dos primeros usuarios con respuestas
    print(f"Comparando respuestas de usuarios: {usuario_1} vs {usuario_2}")

    # Obtener respuestas para ambos usuarios
    cursor.execute("SELECT pregunta_id, valor FROM respuestas WHERE usuario_id = ?", (usuario_1,))
    respuestas_usuario_1 = {row['pregunta_id']: row['valor'] for row in cursor.fetchall()}

    cursor.execute("SELECT pregunta_id, valor FROM respuestas WHERE usuario_id = ?", (usuario_2,))
    respuestas_usuario_2 = {row['pregunta_id']: row['valor'] for row in cursor.fetchall()}

    print(f"Respuestas usuario {usuario_1}: {respuestas_usuario_1}")
    print(f"Respuestas usuario {usuario_2}: {respuestas_usuario_2}")

    # Comparación de respuestas
    coincidencias = sum(1 for q_id in respuestas_usuario_1 if respuestas_usuario_1[q_id] == respuestas_usuario_2.get(q_id))
    
    total_preguntas = len(respuestas_usuario_1)
    porcentaje = (coincidencias / total_preguntas) * 100 if total_preguntas > 0 else 0

    conn.close()
    return render_template('results.html', coincidencias=coincidencias, porcentaje=porcentaje, mensaje="")







@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db_connection', None)
    if db is not None:
        print("TRAZA: Cerrando conexión a la BD")
        db.close()

import hashlib

def crear_usuario_prueba():
    conn = get_db_connection()
    cursor = conn.cursor()

    nombre = "admin"
    password = "123456"
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    try:
        cursor.execute("INSERT INTO usuarios (nombre, password_hash) VALUES (?, ?)", (nombre, password_hash))
        conn.commit()
        print("Usuario de prueba creado: admin / 123456")
    except sqlite3.IntegrityError:
        print("El usuario ya existe.")
    finally:
        conn.close()

# Llamar esta función al inicio para crear el usuario
with app.app_context():
    crear_usuario_prueba()


if __name__ == '__main__':
    # Inicializar la base de datos dentro del contexto de la app
    with app.app_context():
        initialize_db()
    app.run(debug=True)
