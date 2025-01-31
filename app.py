# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, g
import sqlite3
import json
import random

app = Flask(__name__)

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
    with app.app_context():  # Asegurar que la BD se inicializa en el contexto de Flask
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si la tabla 'preguntas' existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='preguntas';")
        table_exists = cursor.fetchone()

        # Si la tabla no existe, la creamos
        if not table_exists:
            cursor.execute("""
            CREATE TABLE preguntas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                texto TEXT NOT NULL,
                categoria TEXT NOT NULL,
                nivel TEXT NOT NULL,
                estado TEXT CHECK(estado IN ('activa', 'editada', 'eliminada')) DEFAULT 'activa',
                origen TEXT CHECK(origen IN ('predefinida', 'generada'))
            );
            """)

        # Verificar si la tabla está vacía
        cursor.execute("SELECT COUNT(*) FROM preguntas")
        if cursor.fetchone()[0] == 0:
            json_path = os.path.join("data", "questions_data.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as file:
                    preguntas_json = json.load(file).get("preguntas", [])

                for pregunta in preguntas_json:
                    cursor.execute(
                        "INSERT INTO preguntas (texto, categoria, nivel, estado, origen) VALUES (?, ?, ?, ?, ?)",
                        (pregunta["texto"], pregunta["categoria"], pregunta["nivel"], pregunta["estado"], "predefinida")
                    )

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




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Aquí puedes implementar la lógica de inicio de sesión
        # Por ahora solo redirigimos a '/questions'
        return redirect('/questions')
    return render_template('login.html')  # Renderiza un archivo login.html (puedes personalizarlo luego)

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db_connection', None)
    if db is not None:
        print("TRAZA: Cerrando conexión a la BD")
        db.close()


if __name__ == '__main__':
    # Inicializar la base de datos dentro del contexto de la app
    with app.app_context():
        initialize_db()
    app.run(debug=True)
