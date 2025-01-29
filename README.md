tar --exclude='venv' -czf project.tar.gz *

/mi_app
  ├── config.yaml        # Archivo de configuración (base de datos, nombre de app, etc.)
  ├── main.py            # Código principal para correr la app
  ├── models.py          # Definición de las tablas de la base de datos
  ├── migrations/        # Carpeta para los scripts de migración (en caso de que decidas hacer cambios)
  ├── data/              # Carpeta para los datos (JSON, backups)
  ├── requirements.txt   # Dependencias del proyecto
  ├── README.md          # Documentación del proyecto
  └── app.db             # Base de datos (si usas SQLite persistente)
