from flask import Flask, request, jsonify
import sqlite3
import re  # Necesario para usar expresiones regulares
from datetime import datetime #Para calcular la edad en base la fecha de nacimiento
import os

app = Flask(__name__)

# Función para validar el formato del RUT
def validar_rut_formato(rut):
    # Expresión regular para el formato 1234567-8 o 12345678-9
    patron = r'^\d{7,8}-[0-9Kk]$'
    return re.match(patron, rut) is not None

# Función para conectar a la base de datos
def connect_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Permite devolver filas como diccionarios
    return conn

# Función para determinar beneficios según las condicionantes exactas
def calcular_beneficios(usuario):
    beneficios = []

    # Evaluar condicionantes
    cumple_1 = usuario['edad'] >= 65
    cumple_2 = usuario['tipo_vecino'].upper() == "VECINO"
    cumple_3 = usuario['Tiene_membresia'].upper() == "SI"
    cumple_4 = 22 <= usuario['edad'] <= 49
    cumple_5 = 50 <= usuario['edad'] <= 64

    # Asignar beneficios basados en combinaciones específicas
    if cumple_1 and not cumple_2 and not cumple_3:  # Solo 1)
        beneficios = ["1 semana gratis al mes"]
    elif not cumple_1 and cumple_2 and not cumple_3:  # Solo 2)
        beneficios = ["2 bebidas isotónicas"]
    elif not cumple_1 and not cumple_2 and cumple_3:  # Solo 3)
        beneficios = ["3 bebidas isotónicas"]
    elif not cumple_2 and not cumple_3 and cumple_4:  # Solo 4)
        beneficios = ["Sin beneficios"]
    elif not cumple_2 and not cumple_3 and cumple_5:  # Solo 5)
        beneficios = ["1 bebida isotónica"]
    elif cumple_1 and cumple_2 and not cumple_3:  # 1) y 2)
        beneficios = ["2 semanas gratis al mes y 1 bebida isotónica"]
    elif cumple_1 and not cumple_2 and cumple_3:  # 1) y 3)
        beneficios = ["1 semana gratis al mes y 2 bebidas isotónicas"]
    elif not cumple_1 and cumple_2 and cumple_3:  # 2) y 3)
        beneficios = ["1 semana gratis al mes y 1 bebidas isotónicas"]
    elif cumple_1 and cumple_2 and cumple_3:  # 1), 2) y 3)
        beneficios = ["2 semanas gratis al mes y 4 bebidas isotónicas"]
    else: beneficios = "Sin beneficios"

    return beneficios

@app.route('/')
def home():
    return "Bienvenido al portal del gimnasio"



# Endpoint 1: Listar todos los usuarios
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios')
    rows = cursor.fetchall()
    conn.close()

    usuarios = [dict(row) for row in rows]  # Convertir filas a diccionarios
    return jsonify(usuarios)

# Endpoint 2: Validar un usuario por RUT
@app.route('/usuarios/<rut>', methods=['GET'])
def validar_usuario(rut):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE rut_completo = ?', (rut,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify(dict(row))
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404

@app.route('/usuarios/<rut>/validar', methods=['POST'])
def validar_usuario_por_documentos(rut):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE rut_completo = ?', (rut,))
    usuario = cursor.fetchone()

    if not usuario:
        # Caso 1: RUT no está registrado
        return jsonify({"mensaje": "El RUT no está inscrito en la base de datos. ¿Desea inscribirse?"}), 404

    usuario = dict(usuario)

    # Caso 2: Usuario ya validado
    if usuario['validado'] == "SI":
        beneficios = calcular_beneficios(usuario)
        return jsonify({"mensaje": "Usuario ya validado. Mostrando beneficios.", "beneficios": beneficios}), 200

    # Caso 3: Usuario no validado, verificar documentos
    data = request.json
    if not data.get('documento_identidad') or not data.get('documento_direccion'):
        return jsonify({"error": "Faltan documentos para validar"}), 400

    # Simular validación de documentos
    if data['documento_identidad']['rut'] == rut:
        if data['documento_direccion']['direccion'] == usuario['direccion']:
            # Validación exitosa: Actualizar la columna validado a "SI"
            cursor.execute('UPDATE usuarios SET validado = ? WHERE rut_completo = ?', ("SI", rut))
            conn.commit()
            beneficios = calcular_beneficios(usuario)
            conn.close()
            return jsonify({"mensaje": "Validación exitosa. Mostrando beneficios.", "beneficios": beneficios}), 200
        else:
            # Direcciones no coinciden
            beneficios = calcular_beneficios(usuario)
            conn.close()
            return jsonify({
                "mensaje": "Dirección incorrecta. Por favor actualizarla con el personal. Validación parcial.",
                "beneficios": beneficios
            }), 200
    else:
        # RUT en documentos no coincide con el RUT ingresado
        conn.close()
        return jsonify({"error": "El RUT de los documentos no coincide con el ingresado"}), 400



# Endpoint 3: Agregar un nuevo usuario
@app.route('/usuarios', methods=['POST'])
def agregar_usuario():
    data = request.json

    # Validación de datos obligatorios
    if (not data.get('nombre') or 
        not data.get('paterno') or not data.get('materno')  or 
        not data.get('direccion')):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    # Validar el formato del RUT
    if not validar_rut_formato(data.get('rut_completo', '')):
        return jsonify({"error": "El RUT ingresado no tiene un formato válido"}), 400
    
     # Validar el formato de fecha_nacimiento
    try:
        fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d')  # Asignar la fecha_nacimiento
    except (KeyError, ValueError):
        return jsonify({"error": "El campo 'fecha_nacimiento' debe tener el formato 'año-mes-día' (YYYY-MM-DD)"}), 400 
    
    # Validar el valor de tipo_vecino
    if data.get('tipo_vecino', '').upper() not in ['VECINO', 'NO VECINO']:
        return jsonify({"error": "El campo 'tipo_vecino' debe ser 'VECINO' o 'NO VECINO'"}), 400

    # Calcular la edad automáticamente
    today = datetime.today()
    edad = today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

    # Validación de valores permitidos en Tiene_membresia
    if data.get('Tiene_membresia').upper() not in ["SI", "NO"]:
        return jsonify({"error": "El campo 'Tiene_membresia' debe ser 'SI' o 'NO'"}), 400  
    

        
    # Inicializar la conexión fuera del try 
    conn = None  
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO usuarios (rut_completo, nombre, paterno, materno, fecha_nacimiento, edad, direccion, tipo_vecino, Tiene_membresia)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['rut_completo'],
            data['nombre'],
            data['paterno'],
            data['materno'],
            data['fecha_nacimiento'],  # Directamente del JSON
            edad,  # Usamos la edad calculada aquí
            data['direccion'],
            data['tipo_vecino'].upper(),  # Convertimos a mayúsculas
            data['Tiene_membresia'].upper()  # Convertimos a mayúsculas
        ))
        conn.commit()
        conn.close()
        return jsonify({"mensaje": "Usuario agregado con éxito"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "El RUT ya está registrado"}), 400
    finally:
        if conn:
            conn.close()  # Cerrar siempre la conexión    



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


