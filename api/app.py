from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, g
from tareas_mejoradas import Persona, Espacio, asignar_tareas_mejorado, contar_tareas_mejorado
from datetime import datetime
from dotenv import load_dotenv
import sqlite3
import json
import os

app = Flask(__name__)
app.template_folder = "../templates"
app.static_folder = "../static"
app.secret_key = os.getenv('SECRET_KEY')

# Configuración de la base de datos SQLite
DATABASE = 'tareas.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS personas
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       nombre TEXT,
                       genero TEXT,
                       no_disponibilidad TEXT)''')
        db.execute('''CREATE TABLE IF NOT EXISTS historial
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       fecha TEXT,
                       calendario TEXT,
                       contador_tareas TEXT)''')
        db.commit()

# Asegúrate de llamar a init_db() antes de ejecutar la aplicación
init_db()

# Declaracion y obtencion de datos necesarios
def get_personas():
    db = get_db()
    personas = db.execute('SELECT * FROM personas').fetchall()
    return [Persona(p['nombre'], p['genero'], set(json.loads(p['no_disponibilidad']))) for p in personas]

espacios = [
    Espacio("Baño Mujeres", "M"),
    Espacio("Baño Hombres", "H"),
    Espacio("Baño Mixto"),
    Espacio("Cocina Arriba"),
    Espacio("Cocina Abajo"),
    Espacio("Sala", frecuencia=["Lunes", "Miércoles", "Viernes"]),
    Espacio("Hall y Vereda", frecuencia=["Lunes", "Miércoles", "Viernes"]),
    Espacio("Patio", frecuencia=["Lunes", "Miércoles", "Viernes"]),
]

dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Rutas
@app.route('/')
def inicio():
    return render_template('inicio.html')

# Manejo de personas
@app.route('/ver_personas')
def ver_personas():
    personas = get_personas()
    return render_template('ver_personas.html', personas=personas)

@app.route('/modificar_persona/<nombre>', methods=['GET', 'POST'])
def modificar_persona(nombre):
    db = get_db()
    if request.method == 'POST':
        no_disponibilidad = json.dumps(list(request.form.getlist('no_disponibilidad')))
        db.execute('UPDATE personas SET no_disponibilidad = ? WHERE nombre = ?', (no_disponibilidad, nombre))
        db.commit()
        return redirect(url_for('ver_personas'))
    persona = db.execute('SELECT * FROM personas WHERE nombre = ?', (nombre,)).fetchone()
    return render_template('modificar_persona.html', persona=Persona(persona['nombre'], persona['genero'], set(json.loads(persona['no_disponibilidad']))), dias=dias)

@app.route('/agregar_persona', methods=['GET', 'POST'])
def agregar_persona():
    if request.method == 'POST':
        nombre = request.form['nombre']
        genero = request.form['genero']
        no_disponibilidad = json.dumps(list(request.form.getlist('no_disponibilidad')))
        db = get_db()
        db.execute('INSERT INTO personas (nombre, genero, no_disponibilidad) VALUES (?, ?, ?)',
                   (nombre, genero, no_disponibilidad))
        db.commit()
        return redirect(url_for('ver_personas'))
    return render_template('agregar_persona.html', dias=dias)

@app.route('/eliminar_persona/<nombre>')
def eliminar_persona(nombre):
    db = get_db()
    db.execute('DELETE FROM personas WHERE nombre = ?', (nombre,))
    db.commit()
    return redirect(url_for('ver_personas'))

#Manejo de historial
@app.route('/guardar_historial', methods=['POST'])
def guardar_historial():
    calendario = json.dumps(request.json['calendario'])
    contador_tareas = json.dumps(request.json['contador_tareas'])
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    db = get_db()
    db.execute('INSERT INTO historial (fecha, calendario, contador_tareas) VALUES (?, ?, ?)',
               (fecha, calendario, contador_tareas))
    db.commit()
    
    return jsonify({'message': 'Historial guardado correctamente'}), 200

@app.route('/obtener_ultimo_historial')
def obtener_ultimo_historial():
    db = get_db()
    ultimo_historial = db.execute('SELECT * FROM historial ORDER BY fecha DESC LIMIT 1').fetchone()
    
    if ultimo_historial:
        return jsonify({
            'fecha': ultimo_historial['fecha'],
            'calendario': json.loads(ultimo_historial['calendario']),
            'contador_tareas': json.loads(ultimo_historial['contador_tareas'])
        }), 200
    else:
        return jsonify({'message': 'No hay historial disponible'}), 404

@app.route('/ver_historial')
def ver_historial():
    db = get_db()
    historial = db.execute('SELECT * FROM historial ORDER BY fecha DESC LIMIT 10').fetchall()
    
    orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    historial_list = []
    for row in historial:
        calendario = json.loads(row['calendario'])
        calendario_ordenado = {dia: calendario[dia] for dia in orden_dias if dia in calendario}
        
        historial_list.append({
            'id': row['id'],
            'fecha': row['fecha'],
            'calendario': calendario_ordenado,
            'contador_tareas': json.loads(row['contador_tareas'])
        })
    
    return render_template('ver_historial.html', historial=historial_list)

#borrar historial completo
@app.route('/borrar_historial', methods=['POST'])
def borrar_historial():
    password = request.form.get('password')
    if password == os.getenv('ADMIN_PASSWORD'):
        db = get_db()
        db.execute('DELETE FROM historial')
        db.commit()
        flash('Historial borrado correctamente', 'success')
    else:
        flash('Contraseña incorrecta', 'danger')
    return redirect(url_for('ver_historial'))

#borrar historial individual
@app.route('/borrar_historial_individual/<int:id>', methods=['POST'])
def borrar_historial_individual(id):
    password = request.form.get('password')
    if password == os.getenv('ADMIN_PASSWORD'):
        db = get_db()
        db.execute('DELETE FROM historial WHERE id = ?', (id,))
        db.commit()
        flash('Entrada de historial borrada correctamente', 'success')
    else:
        flash('Contraseña incorrecta', 'danger')
    return redirect(url_for('ver_historial'))

@app.route('/editar_historial/<int:id>', methods=['GET', 'POST'])
def editar_historial(id):
    db = get_db()
    if request.method == 'POST':
        # Procesar los datos del formulario sino no funca
        form_data = request.form.to_dict()
        calendario = {}
        for key, value in form_data.items():
            dia, espacio = key.split('_', 1)
            if dia not in calendario:
                calendario[dia] = {}
            calendario[dia][espacio] = value

        calendario_json = json.dumps(calendario)
        contador_tareas = contar_tareas_mejorado(calendario)
        contador_tareas_json = json.dumps(contador_tareas)
        
        db.execute('UPDATE historial SET calendario = ?, contador_tareas = ? WHERE id = ?',
                   (calendario_json, contador_tareas_json, id))
        db.commit()
        flash('Historial actualizado correctamente', 'success')
        return redirect(url_for('ver_historial'))
    
    historial = db.execute('SELECT * FROM historial WHERE id = ?', (id,)).fetchone()
    if historial:
        calendario = json.loads(historial['calendario'])
        personas = get_personas()
        return render_template('editar_historial.html', 
                               id=id, 
                               calendario=calendario, 
                               personas=personas, 
                               espacios=espacios, 
                               dias=dias)
    else:
        flash('El historial no existe', 'danger')
        return redirect(url_for('ver_historial'))

# Generación de lista
@app.route('/generar_lista')
def generar_lista():
    personas = get_personas()
    # Reset tareas_asignadas for each person before generating the list
    for persona in personas:
        persona.tareas_asignadas = 0
    
    # Obtener el último historial
    db = get_db()
    ultimo_historial = db.execute('SELECT * FROM historial ORDER BY fecha DESC LIMIT 1').fetchone()
    
    if ultimo_historial:
        calendario_anterior = json.loads(ultimo_historial['calendario'])
        contador_tareas_anterior = json.loads(ultimo_historial['contador_tareas'])
    else:
        calendario_anterior = None
        contador_tareas_anterior = None
    
    calendario = asignar_tareas_mejorado(personas, espacios, dias, calendario_anterior, contador_tareas_anterior)
    contador_tareas = contar_tareas_mejorado(calendario)
    return render_template('index.html', calendario=calendario, espacios=espacios, dias=dias, contador_tareas=contador_tareas)

@app.route('/generar_calendario', methods=['POST'])
def generar_calendario():
    # Obtener el último historial de SQLite
    db = get_db()
    ultimo_historial = db.execute('SELECT * FROM historial ORDER BY fecha DESC LIMIT 1').fetchone()
    
    calendario_anterior = None
    contador_tareas_anterior = None
    if ultimo_historial:
        calendario_anterior = json.loads(ultimo_historial['calendario'])
        contador_tareas_anterior = json.loads(ultimo_historial['contador_tareas'])

    # Generar el nuevo calendario
    calendario = asignar_tareas_mejorado(get_personas(), espacios, dias, calendario_anterior, contador_tareas_anterior)
    contador_tareas = contar_tareas_mejorado(calendario)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
