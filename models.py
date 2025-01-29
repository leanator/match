import sqlite3

def crear_tablas(conn):
    cursor = conn.cursor()

    # Crear tabla de preguntas
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

    # Crear tabla de respuestas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS respuestas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        pregunta_id INTEGER NOT NULL,
        respuesta_id INTEGER NOT NULL,
        estado TEXT CHECK(estado IN ('activa', 'editada')) DEFAULT 'activa',
        fecha_respuesta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
        FOREIGN KEY (pregunta_id) REFERENCES preguntas(id) ON DELETE CASCADE,
        FOREIGN KEY (respuesta_id) REFERENCES opciones_respuesta(id)
    );
    """)

    # Añadir más tablas como las de coincidencias, reportes, etc.

    conn.commit()

# Conectar a la BD y crear tablas
conn = sqlite3.connect('app.db')  # O ':memory:' si es en memoria
crear_tablas(conn)
conn.close()
