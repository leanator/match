# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, g, session, url_for, flash
from auth import auth

import sqlite3
import json
from flask import Flask, request, session, g, redirect, render_template

# Inicializar la aplicación Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Clave secreta para la sesión

# Función para inicializar la base de datos
def inicializar_bd():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Crear la tabla usuarios si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            partner_id INTEGER,
            FOREIGN KEY (partner_id) REFERENCES usuarios(id)
        )
    """)
    print("TRAZA: Tabla usuarios creada o ya existe.")

    # Crear la tabla respuestas si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS respuestas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pregunta_id INTEGER NOT NULL,
            valor INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)
    print("TRAZA: Tabla respuestas creada o ya existe.")

    # Crear la tabla preguntas si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preguntas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT NOT NULL,
            categoria TEXT NOT NULL,
            nivel TEXT NOT NULL,
            estado TEXT NOT NULL
        )
    """)
    print("TRAZA: Tabla preguntas creada o ya existe.")

    # Asegurarnos de que la base de datos y tablas están correctamente creadas
    conn.commit()
    conn.close()
    print("TRAZA: Base de datos e inicialización completadas.")
    
import sqlite3
import json
import random

# Inicializar la aplicación Flask
app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura"  # Cambiar por algo seguro en producción
app.register_blueprint(auth)  # Registrar el blueprint de autenticación

# Función para obtener el texto de una pregunta por su ID
def get_question_text(pregunta_id):
    print("TRAZA: buscando texto para pregunta ID", pregunta_id)  # Trazas para ver qué ID se está pasando
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT texto FROM preguntas WHERE id = ?", (pregunta_id,))
    pregunta = cursor.fetchone()
    print("TRAZA: pregunta encontrada", pregunta)  # Verifica qué pregunta estamos obteniendo
    conn.close()
    return pregunta['texto'] if pregunta else None


# Conexión a la base de datos (archivo temporal persistente durante la ejecución)
def get_db_connection():
    db_path = 'database.db'

    if not os.path.exists(db_path):  # Verificamos si el archivo de la base de datos existe
        # Si no existe, creamos la base de datos
        print("TRAZA: La base de datos no existe. Creando 'database.db'.")
        initialize_db()  # Llamamos a la función para inicializar la base de datos

    if 'db_connection' not in g:
        g.db_connection = sqlite3.connect(db_path, check_same_thread=False)  # Conectamos a la base de datos
        g.db_connection.row_factory = sqlite3.Row  # Esto permite acceder a las columnas por nombre
    return g.db_connection



# Cargar preguntas desde el archivo JSON
def load_questions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, texto, categoria, nivel, estado FROM preguntas")
    preguntas = [dict(row) for row in cursor.fetchall()]  # Convertimos sqlite3.Row a diccionario
    #conn.close()
    return preguntas


import sqlite3
import json
import os

# Función para inicializar la base de datos
def initialize_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Crear la tabla usuarios si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            partner_id INTEGER,
            FOREIGN KEY (partner_id) REFERENCES usuarios(id)
        )
    """)

    # Crear la tabla respuestas si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS respuestas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pregunta_id INTEGER NOT NULL,
            valor INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    # Crear la tabla preguntas si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preguntas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT NOT NULL,
            categoria TEXT NOT NULL,
            nivel TEXT NOT NULL,
            estado TEXT NOT NULL
        )
    """)

    # Asegurarnos de que la base de datos y tablas están correctamente creadas
    conn.commit()
    conn.close()
    print("TRAZA: Base de datos e inicialización completadas.")


# Función para cargar preguntas desde un archivo JSON
def cargar_preguntas_desde_json():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    with open('data/questions_data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        preguntas = data['preguntas']

        for pregunta in preguntas:
            texto = pregunta['texto']
            categoria = pregunta['categoria']
            nivel = pregunta['nivel']
            estado = pregunta['estado']

            # Verificar si la pregunta ya existe en la base de datos
            cursor.execute("SELECT COUNT(*) FROM preguntas WHERE texto = ?", (texto,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO preguntas (texto, categoria, nivel, estado)
                    VALUES (?, ?, ?, ?)
                """, (texto, categoria, nivel, estado))
                print(f"TRAZA: Pregunta insertada: {texto}")
            else:
                print(f"TRAZA: Pregunta ya existe: {texto}")

    conn.commit()
    conn.close()
    print("TRAZA: Preguntas cargadas desde JSON.")




# Ruta para la página de inicio
@app.route('/')
def home():
    return render_template('index.html')

# Ruta para mostrar preguntas y respuestas
@app.route('/questions', methods=['GET', 'POST'])
def questions():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    usuario_id = session.get('usuario_id')

    # Obtener las preguntas que aún no han sido respondidas por el usuario
    cursor.execute("""
        SELECT id, texto FROM preguntas
        WHERE id NOT IN (SELECT pregunta_id FROM respuestas WHERE usuario_id = ?)
        ORDER BY id ASC
        LIMIT 1
    """, (usuario_id,))
    
    pregunta = cursor.fetchone()
    print(f"TRAZA: Pregunta obtenida: {pregunta}")

    # Obtener el total de preguntas
    cursor.execute("SELECT COUNT(*) FROM preguntas")
    total_preguntas = cursor.fetchone()[0]

    # Obtener cuántas preguntas ha respondido el usuario
    cursor.execute("SELECT COUNT(*) FROM respuestas WHERE usuario_id = ?", (usuario_id,))
    preguntas_respuestas = cursor.fetchone()[0]

    # Calcular las preguntas pendientes
    preguntas_pendientes = total_preguntas - preguntas_respuestas

    if request.method == "POST":
        if pregunta:  # Si hay una pregunta para mostrar
            respuesta = request.form.get("respuesta")
            print(f"TRAZA: Respuesta recibida: {respuesta}")
            if respuesta:
                valor_respuesta = 0 if respuesta == "NO" else 1 if respuesta == "TAL VEZ" else 2
                cursor.execute("""
                    INSERT INTO respuestas (pregunta_id, usuario_id, valor)
                    VALUES (?, ?, ?)
                """, (pregunta[0], usuario_id, valor_respuesta))
                conn.commit()
                print(f"TRAZA: Respuesta insertada: pregunta_id={pregunta[0]}, usuario_id={usuario_id}, valor={valor_respuesta}")

            # Obtener la siguiente pregunta
            cursor.execute("""
                SELECT id, texto FROM preguntas
                WHERE id NOT IN (SELECT pregunta_id FROM respuestas WHERE usuario_id = ?)
                ORDER BY id ASC
                LIMIT 1
            """, (usuario_id,))
            pregunta = cursor.fetchone()
            print(f"TRAZA: Siguiente pregunta obtenida: {pregunta}")

    conn.close()

    if not pregunta:
        return redirect('/results')

    return render_template('questions.html', pregunta=pregunta, total_preguntas=total_preguntas, preguntas_respuestas=preguntas_respuestas, preguntas_pendientes=preguntas_pendientes)

# Ruta para mostrar los resultados
@app.route('/results', methods=["GET"])
def results():
    print("TRAZA: Método recibido:", request.method)  # Esto debería ser GET
    
    if request.method == "GET":
        print("TRAZA: Procesando solicitud GET en /results")

        usuario_id = session.get('usuario_id')
        if not usuario_id:
            return redirect(url_for('auth.login'))

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Verificar si el usuario tiene un partner asignado
        cursor.execute("SELECT partner_id FROM usuarios WHERE id = ?", (usuario_id,))
        partner_id = cursor.fetchone()[0]
        if not partner_id:
            print("TRAZA: El usuario no tiene un partner asignado. Redirigiendo a /find_partner")
            return redirect(url_for('find_partner'))

        print(f"TRAZA: usuario_id es {usuario_id}, partner_id es {partner_id}")

        # Obtener respuestas de ambos usuarios
        cursor.execute("SELECT pregunta_id, valor FROM respuestas WHERE usuario_id = ?", (usuario_id,))
        respuestas_usuario_1 = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("SELECT pregunta_id, valor FROM respuestas WHERE usuario_id = ?", (partner_id,))
        respuestas_usuario_2 = {row[0]: row[1] for row in cursor.fetchall()}

        # Verificar que las respuestas se están recuperando correctamente
        print("TRAZA: Respuestas Usuario 1:", respuestas_usuario_1)
        print("TRAZA: Respuestas Usuario 2:", respuestas_usuario_2)

        # Inicializar contadores para cada tipo de coincidencia
        coincidencias_plenas = []
        coincidencias_parciales = []
        no_coincidencias = []

        # Comparar las respuestas
        for pregunta_id, valor_1 in respuestas_usuario_1.items():
            valor_2 = respuestas_usuario_2.get(pregunta_id)
            if valor_2 is not None:
                if valor_1 == valor_2:
                    coincidencias_plenas.append(pregunta_id)
                elif abs(valor_1 - valor_2) == 1:
                    coincidencias_parciales.append(pregunta_id)
                else:
                    no_coincidencias.append(pregunta_id)

        # Obtener los textos de las preguntas para mostrar en los resultados
        coincidencias_plenas_texto = []
        coincidencias_parciales_texto = []
        no_coincidencias_texto = []

        for pregunta_id in coincidencias_plenas:
            cursor.execute("SELECT texto FROM preguntas WHERE id = ?", (pregunta_id,))
            coincidencias_plenas_texto.append(cursor.fetchone()[0])

        for pregunta_id in coincidencias_parciales:
            cursor.execute("SELECT texto FROM preguntas WHERE id = ?", (pregunta_id,))
            coincidencias_parciales_texto.append(cursor.fetchone()[0])

        for pregunta_id in no_coincidencias:
            cursor.execute("SELECT texto FROM preguntas WHERE id = ?", (pregunta_id,))
            no_coincidencias_texto.append(cursor.fetchone()[0])

        conn.close()

        return render_template('results.html', 
                               coincidencias_plenas=coincidencias_plenas_texto, 
                               coincidencias_parciales=coincidencias_parciales_texto, 
                               no_coincidencias=no_coincidencias_texto)











@app.route('/find_partner', methods=['GET', 'POST'])
def find_partner():
    if request.method == 'POST':
        partner_name = request.form['partner_name']
        usuario_id = session.get('usuario_id')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Buscar el partner por nombre
        cursor.execute("SELECT id FROM usuarios WHERE nombre = ?", (partner_name,))
        partner = cursor.fetchone()

        if partner:
            # Mostrar pantalla de confirmación
            conn.close()
            return render_template('confirm_partner.html', partner_name=partner_name, partner_id=partner[0])
        else:
            conn.close()
            flash("No se encontró ningún usuario con ese nombre.", "danger")
    
    return render_template('find_partner.html')

@app.route('/confirm_partner', methods=['POST'])
def confirm_partner():
    partner_id = request.form['partner_id']
    usuario_id = session.get('usuario_id')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Asignar el partner al usuario y viceversa
    cursor.execute("UPDATE usuarios SET partner_id = ? WHERE id = ?", (partner_id, usuario_id))
    cursor.execute("UPDATE usuarios SET partner_id = ? WHERE id = ?", (usuario_id, partner_id))
    conn.commit()
    conn.close()

    # Mostrar mensaje de confirmación y redirigir a /results
    flash("Emparejamiento confirmado correctamente.", "success")
    return redirect(url_for('results'))




# Cerrar la conexión a la base de datos al finalizar el contexto de la aplicación
@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db_connection', None)
    if db is not None:
        print("TRAZA: Cerrando conexión a la BD")
        db.close()

import sqlite3
import hashlib


def crear_usuario_prueba():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    nombre = "admin"
    password = "123456"
    partner = None
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Verificar si el usuario ya existe
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE nombre = ?", (nombre,))
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (nombre, password_hash, partner_id) VALUES (?, ?, ?)", (nombre, password_hash, partner))
        conn.commit()
        print("Usuario de prueba creado: admin / 123456")
    else:
        print("El usuario de prueba ya existe.")
    
    conn.close()

if __name__ == '__main__':
    # Inicializar la base de datos dentro del contexto de la app
    with app.app_context():
        initialize_db()
        cargar_preguntas_desde_json()
        crear_usuario_prueba()

    app.run(debug=True, host='0.0.0.0', port=5000)

