import sqlite3

# Conexión a SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Consultar datos
cursor.execute('SELECT * FROM usuarios LIMIT 10')
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
