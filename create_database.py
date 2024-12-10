import sqlite3

# Conexión a SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear la tabla Usuarios
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rut_completo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    paterno TEXT,
    materno TEXT,
    fecha_nacimiento TEXT,
    edad INTEGER,
    direccion TEXT,
    tipo_vecino TEXT,
    Tiene_membresia TEXT
)
''')

print("Tabla creada con éxito")
conn.close()
