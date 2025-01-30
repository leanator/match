rm -rf *.gz; tar --exclude='venv' --exclude='.git' --exclude='__pycache__' --exclude='temporary.db' -czf project.tar.gz *

/mi_app
  ├── config.yaml        # Archivo de configuración (base de datos, nombre de app, etc.)
  ├── main.py            # Código principal para correr la app
  ├── models.py          # Definición de las tablas de la base de datos
  ├── migrations/        # Carpeta para los scripts de migración (en caso de que decidas hacer cambios)
  ├── data/              # Carpeta para los datos (JSON, backups)
  ├── requirements.txt   # Dependencias del proyecto
  ├── README.md          # Documentación del proyecto
  └── app.db             # Base de datos (si usas SQLite persistente)

# **Documentación del Diseño de la Aplicación**

## **1. Objetivo de la Aplicación**
La aplicación tiene como objetivo proporcionar una herramienta privada y personalizable para mejorar la comunicación entre parejas. Ofrecerá un sistema de preguntas y respuestas con la capacidad de generar coincidencias según las respuestas de los usuarios. A largo plazo, podrá integrar retos y desafíos, todo en un entorno discreto y fácil de usar.

## **2. Estructura General**
La app será híbrida, utilizando una base de datos en memoria para entornos de desarrollo y una base de datos persistente (archivo SQLite) cuando sea necesario. Se iniciará con un archivo JSON para configurar las preguntas y opciones, pero evolucionará a medida que se agreguen más funcionalidades, como la generación dinámica de preguntas a través de una API de IA.

### **Componentes principales de la app**:
- **Backend**: Gestionado con Flask para el manejo de rutas y la lógica.
- **Base de Datos**: SQLite en memoria para desarrollo y en archivo (`app.db`) para persistencia de datos.
- **Interfaz de Usuario**: Inicialmente una interfaz simple, posiblemente web (usando HTML/CSS y Flask), que se expandirá conforme avance el proyecto.

---

## **3. Requisitos Técnicos**
- **Lenguaje de desarrollo**: Python con Flask para la gestión del backend.
- **Base de Datos**: SQLite, utilizando una base de datos en memoria durante el desarrollo, y persistente en un archivo (`app.db`) en producción.
- **Configuración**: Se utilizará un archivo `config.yaml` para gestionar configuraciones generales (nombre de la app, idioma, base de datos).

---

## **4. Estructura de la Base de Datos**

### **Tablas principales:**
1. **`config`**: Almacena configuraciones globales de la app (por ejemplo, nombre de la app, idioma por defecto).
2. **`preguntas`**: Almacena las preguntas que los usuarios deben responder. Incluye atributos como texto, categoría, nivel de intensidad, etc.
3. **`opciones_respuesta`**: Define las opciones de respuesta disponibles para las preguntas (NO, TAL VEZ, SÍ).
4. **`estados`**: Almacena los diferentes estados de las preguntas y respuestas (activa, editada, eliminada).
5. **`respuestas`**: Almacena las respuestas de los usuarios a las preguntas, asociándolas con el usuario y la pregunta correspondiente.
6. **`coincidencias`**: Registra las coincidencias entre las respuestas de los usuarios. Una coincidencia se puede clasificar como plena, parcial o no coincidencia.
7. **`reportes`**: Permite a los usuarios reportar preguntas inapropiadas o incorrectas. También se incluyen sugerencias para reemplazar preguntas.
8. **`notificaciones`**: Almacena notificaciones para los usuarios relacionadas con cambios en sus respuestas o nuevas coincidencias.

### **Relaciones entre tablas:**
- **`preguntas`** y **`respuestas`**: Relacionadas por el ID de la pregunta y el ID del usuario.
- **`coincidencias`**: Relaciona las respuestas de los usuarios basándose en las coincidencias entre sus respuestas.
- **`reportes`**: Relacionado con las preguntas, permitiendo que los usuarios informen sobre problemas con las preguntas.

---

## **5. Flujos de Usuario**

### **Pantalla de Inicio**
- **Objetivo**: Mostrar la bienvenida y permitir el inicio de sesión.
- **Elementos**:
  - Título de la app
  - Botón de "Iniciar sesión"
  - Información breve sobre la app

### **Pantalla de Login**
- **Objetivo**: Permitir que el usuario ingrese sus credenciales.
- **Elementos**:
  - Campos de usuario y contraseña
  - Botón de "Entrar"
  - Opción de "Recuperar contraseña"

### **Pantalla Principal (Dashboard)**
- **Objetivo**: Ofrecer acceso a la funcionalidad principal de la app.
- **Elementos**:
  - Botón para responder preguntas
  - Botón para ver coincidencias
  - Menú de configuración

### **Pantalla de Responder Preguntas**
- **Objetivo**: Mostrar las preguntas y permitir que los usuarios respondan.
- **Elementos**:
  - Pregunta con opciones de respuesta: NO, TAL VEZ, SÍ
  - Barra de progreso de respuestas
  - Botón para avanzar a la siguiente pregunta

### **Pantalla de Coincidencias**
- **Objetivo**: Mostrar las coincidencias entre las respuestas de los usuarios.
- **Elementos**:
  - Coincidencias plenas
  - Coincidencias parciales
  - No coincidencias
  - Filtros por categoría o nivel

### **Pantalla de Configuración**
- **Objetivo**: Permitir que los usuarios ajusten su perfil y preferencias.
- **Elementos**:
  - Opciones para modificar el perfil
  - Vinculación con pareja
  - Preferencias de privacidad

---

## **6. Lógica de Preguntas y Respuestas**

### **Preguntas**
- Al iniciar la app, las preguntas se cargan desde el archivo `data.json` y se insertan en la base de datos.
- Cada pregunta tiene un texto, una categoría (como "Fantasías", "Juegos de rol"), y un nivel de intensidad (por ejemplo, "Suave", "Picante").
- Las preguntas pueden ser predefinidas o generadas dinámicamente más adelante.

### **Respuestas**
- Los usuarios responden las preguntas seleccionando una de las opciones disponibles: **NO**, **TAL VEZ**, **SÍ**.
- Las respuestas se almacenan en la base de datos junto con el ID del usuario y el ID de la pregunta.
- Se calcula la coincidencia de las respuestas entre los usuarios, clasificándolas como **plena**, **parcial**, o **no coincidencia**.

---

## **7. Generación de Nuevas Preguntas con IA**
A largo plazo, se integrará una funcionalidad que permitirá que los usuarios generen nuevas preguntas de manera dinámica utilizando una API de IA (como OpenAI). Estas preguntas generadas se almacenarán en la base de datos y estarán disponibles para que los usuarios las respondan.

---

## **8. Consideraciones de Seguridad y Privacidad**
- **Autenticación**: Los usuarios accederán con un nombre de usuario y contraseña. Se implementará una autenticación básica para garantizar la privacidad.
- **Almacenamiento de Datos**: Todos los datos (preguntas, respuestas, coincidencias) se almacenarán en la base de datos, y se manejará con privacidad.
- **Configuración de Privacidad**: Los usuarios podrán decidir qué respuestas o datos se comparten con su pareja.

---

## **9. Implementación y Desarrollo Futuro**

### **Primeros pasos de implementación**
1. Desarrollar la interfaz básica de usuario usando Flask.
2. Integrar la lógica de preguntas y respuestas en el backend.
3. Implementar el sistema de coincidencias basado en las respuestas.

### **Expansiones futuras**
1. Implementar generación automática de preguntas mediante la API de IA.
2. Crear un sistema de retroalimentación donde los usuarios puedan reportar preguntas inapropiadas o sugerir nuevas preguntas.
3. Mejorar la interfaz de usuario con opciones de personalización visual.

---

Este diseño cubre todos los aspectos clave de la aplicación, y ahora puedes usarlo como referencia para guiar el desarrollo de la app. Cuando estés listo para avanzar en la implementación, podemos seguir estructurando los pasos de desarrollo y revisando los detalles técnicos necesarios.

---
