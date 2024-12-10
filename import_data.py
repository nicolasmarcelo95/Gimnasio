import sqlite3
import pandas as pd

# Leer el archivo Excel
excel_data = pd.read_excel('Datos_prueba.xlsx')

# Conexión a SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Insertar datos en la base de datos
for index, row in excel_data.iterrows():
    # Validar que los campos requeridos no estén vacíos
    if pd.isna(row['fecha_nacimiento']) or pd.isna(row['edad']) or pd.isna(row['direccion']):
        print(f"Fila {index + 1} ignorada: Datos incompletos")
        continue  # Saltar esta fila

    try:
        cursor.execute(
            """
            INSERT INTO usuarios (rut_completo, nombre, paterno, materno, fecha_nacimiento, edad, direccion, tipo_vecino, tiene_membresia)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row['rut_completo'],
                row['nombre'],
                row['paterno'],
                row['materno'],
                str(row['fecha_nacimiento']),  # Convertir la fecha a cadena
                int(row['edad']),
                row['direccion'],
                row['tipo_vecino'],
                row['tiene_membresia']
            )
        )
    except sqlite3.IntegrityError:
        print(f"El RUT {row['rut_completo']} ya está en la base de datos.")

# Confirmar cambios y cerrar conexión
conn.commit()
conn.close()

print("Datos importados con éxito desde Excel")