# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, g, session, url_for, flash
from auth import auth

import sqlite3
import json
import random

app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura"  # Cambiar por algo seguro en producción
app.register_blueprint(auth)

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
@app.route('/questions', methods=["GET", "POST"])
def questions():
    conn = get_db_connection()
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
            respuesta = request.form.get(f"respuesta_{pregunta['id']}")
            if respuesta:
                valor_respuesta = 0 if respuesta == "NO" else 1 if respuesta == "TAL VEZ" else 2
                cursor.execute("""
                    INSERT INTO respuestas (pregunta_id, usuario_id, texto, valor)
                    VALUES (?, ?, ?, ?)
                """, (pregunta['id'], usuario_id, respuesta, valor_respuesta))
                conn.commit()

            # Obtener la siguiente pregunta
            return redirect(url_for('questions'))

        else:  # Si no hay más preguntas, redirigir a los resultados
            return redirect('/results')

    # Si hay una pregunta pendiente, mostrarla
    if pregunta:
        conn.close()
        return render_template('questions.html', pregunta=pregunta, total_preguntas=total_preguntas, preguntas_respuestas=preguntas_respuestas, preguntas_pendientes=preguntas_pendientes)

    # Si no hay preguntas pendientes, redirigir a los resultados
    conn.close()
    return redirect('/results')





@app.route('/results', methods=["GET"])
def results():
    print("TRAZA: Método recibido:", request.method)  # Esto debería ser GET
    
    if request.method == "GET":
        print("TRAZA: Procesando solicitud GET en /results")

        # Aquí podemos usar una variable de sesión para determinar qué usuario está buscando los resultados
        # Por ejemplo, lo asignamos manualmente para este ejemplo
        partner_id = 1  # Simula que estamos buscando la comparativa para el usuario con ID 1
        print(f"TRAZA: partner_id es {partner_id}")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Obtener respuestas de ambos usuarios
        cursor.execute("SELECT pregunta_id, valor FROM respuestas WHERE usuario_id = ?", (partner_id,))
        respuestas_usuario_1 = {row['pregunta_id']: row['valor'] for row in cursor.fetchall()}

        cursor.execute("SELECT pregunta_id, valor FROM respuestas WHERE usuario_id != ?", (partner_id,))
        respuestas_usuario_2 = {row['pregunta_id']: row['valor'] for row in cursor.fetchall()}

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
            pregunta_texto = get_question_text(pregunta_id)

            print(f"TRAZA: Comparando pregunta ID {pregunta_id}, Texto: {pregunta_texto}, Valor usuario 1: {valor_1}, Valor usuario 2: {valor_2}")

            if valor_1 == 2 and valor_2 == 2:
                coincidencias_plenas.append(pregunta_texto)  # Añadir el texto de la pregunta
            elif (valor_1 == 2 and valor_2 == 1) or (valor_1 == 1 and valor_2 == 2):
                coincidencias_parciales.append(pregunta_texto)  # Añadir el texto de la pregunta
            elif valor_1 == 0 or valor_2 == 0:
                no_coincidencias.append(pregunta_texto)  # Añadir el texto de la pregunta

        conn.close()

        print(f"TRAZA: Coincidencias Plenas: {coincidencias_plenas}")
        print(f"TRAZA: Coincidencias Parciales: {coincidencias_parciales}")
        print(f"TRAZA: No Coincidencias: {no_coincidencias}")

        return render_template('results.html', 
                               coincidencias_plenas=coincidencias_plenas, 
                               coincidencias_parciales=coincidencias_parciales,
                               no_coincidencias=no_coincidencias)

    # GET: Mostrar la página de resultados
    print("TRAZA: Método GET - Mostrando resultados.")
    return render_template('results.html')











@app.route('/find_partner', methods=["GET", "POST"])
def find_partner():
    if request.method == 'POST':
        partner_name = request.form['partner_name']
        
        # Verificar si el nombre ingresado coincide con algún usuario en la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM usuarios WHERE nombre = ?", (partner_name,))
        partner = cursor.fetchone()
        conn.close()

        if partner:
            # Si hay coincidencia, mostrar mensaje de confirmación
            return render_template('confirm_partner.html', partner_name=partner_name, partner_id=partner['id'])
        else:
            flash("No se encontró ningún usuario con ese nombre.", "danger")
    
    return render_template('find_partner.html')




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
    partner = None
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    try:
        cursor.execute("INSERT INTO usuarios (nombre, password_hash, partner_id) VALUES (?, ?,?)", (nombre, password_hash,partner))
        conn.commit()
        print("Usuario de prueba creado: admin / 123456")
    except sqlite3.IntegrityError:
        print("El usuario ya existe.")
    finally:
        conn.close()

if __name__ == '__main__':
    # Inicializar la base de datos dentro del contexto de la app
    with app.app_context():
        initialize_db()
        cargar_preguntas_desde_json()
        crear_usuario_prueba()

    app.run(debug=True, host='0.0.0.0', port=5000)


