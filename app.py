from flask import Flask, render_template, request, redirect, g
import sqlite3
import json

app = Flask(__name__)

# Conexión a la base de datos (archivo temporal persistente durante la ejecución)
def get_db_connection():
    if not hasattr(g, 'db_connection'):
        g.db_connection = sqlite3.connect('temporary.db')  # Usar archivo temporal para mantener la BD
        g.db_connection.row_factory = sqlite3.Row
        
        # Imprimir el identificador único de la conexión para verificar si es la misma en cada solicitud
        db_id = id(g.db_connection)
        print(f"Conexión a la base de datos creada. ID único de la conexión: {db_id}")
    
    return g.db_connection

# Cargar preguntas desde el archivo JSON
def load_questions():
    with open('data/questions_data.json', 'r', encoding='utf-8') as file:
        return json.load(file)["preguntas"]

# Inicializar la base de datos y las tablas
def initialize_db():
    # Asegurarnos de estar dentro del contexto de la app
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()

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

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS respuestas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pregunta_id INTEGER,
            texto TEXT NOT NULL,
            valor INTEGER NOT NULL,
            FOREIGN KEY (pregunta_id) REFERENCES preguntas(id)
        );
        """)

        # Insertar preguntas y respuestas desde el JSON si la tabla está vacía
        cursor.execute("SELECT COUNT(*) FROM preguntas")
        if cursor.fetchone()[0] == 0:
            questions = load_questions()
            for pregunta in questions:
                cursor.execute("INSERT INTO preguntas (texto, categoria, nivel, estado) VALUES (?, ?, ?, ?)",
                               (pregunta["texto"], pregunta["categoria"], pregunta["nivel"], pregunta["estado"]))
                pregunta_id = cursor.lastrowid  # Obtener el ID de la pregunta insertada
                
                for respuesta in pregunta["respuestas"]:
                    cursor.execute("INSERT INTO respuestas (pregunta_id, texto, valor) VALUES (?, ?, ?)",
                                   (pregunta_id, respuesta["texto"], respuesta["valor"]))

        conn.commit()

        # Verificar la creación de las tablas y los registros
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\nTablas en la base de datos:")
        for table in tables:
            table_name = table[0]
            print(f"\nRegistros de la tabla '{table_name}':")
            cursor.execute(f"SELECT * FROM {table_name}")
            records = cursor.fetchall()
            for record in records:
                print(dict(record))  # Imprimir los registros como un diccionario para mejor lectura

# Inicializar la base de datos una vez al principio, pero dentro del contexto de la app
initialize_db()

# Rutas de Flask
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    # Aquí iría la lógica de login, por ahora solo redirige
    return redirect('/questions')

@app.route('/questions')
def questions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, texto FROM preguntas")
    preguntas = cursor.fetchall()
    conn.close()
    return render_template('questions.html', preguntas=preguntas)

if __name__ == '__main__':
    app.run(debug=True)
