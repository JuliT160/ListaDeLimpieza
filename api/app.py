from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from tareas_mejoradas import Persona, Espacio, asignar_tareas_mejorado, contar_tareas_mejorado
from datetime import datetime
import sqlite3
import json

app = Flask(__name__)
app.template_folder = "../templates"
app.static_folder = "../static"
app.secret_key = 'Trenque769'

# Configuración de la base de datos SQLite
DATABASE = 'tareas.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS historial
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       fecha TEXT,
                       calendario TEXT,
                       contador_tareas TEXT)''')
        db.commit()

# Asegúrate de llamar a init_db() antes de ejecutar la aplicación
init_db()

personas = [
    Persona("Julieta", "M", []),
    Persona("Iara", "M", []),
    Persona("Benjamin", "H", []),
    Persona("Nahuel", "H", []),
    Persona("Tobias", "H", []),
    Persona("Fermin", "H", []),
    Persona("Magali", "M", []),
    Persona("Belen", "M", []),
    Persona("Josefina", "M", []),
    Persona("Emilia", "M", []),
    Persona("Valentina", "M", []),
    Persona("Juan", "H", []),
    Persona("Nicolas", "H", []),
    Persona("Sebastian", "H", []),
    Persona("Lucia", "M", []),
    Persona("Zoe", "M", []),
    Persona("Julian", "H", []),
    Persona("Mateo", "H", []),
    Persona("Mirko", "H", []),
]

espacios = [
    Espacio("Baño Mujeres", "M"),
    Espacio("Baño Hombres", "H"),
    Espacio("Baño Mixto"),
    Espacio("Cocina Arriba"),
    Espacio("Cocina Abajo"),
    Espacio("Sala", frecuencia=["Lunes", "Miércoles", "Viernes"]),
    Espacio("Hall y Vereda", frecuencia=["Lunes", "Miércoles", "Viernes"]),
    Espacio("Patio", frecuencia=["Lunes", "Miércoles", "Viernes"]),
    #Espacio("Patio2", frecuencia=["Lunes", "Miércoles", "Viernes"]),
]

dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/ver_personas')
def ver_personas():
    return render_template('ver_personas.html', personas=personas)

@app.route('/modificar_persona/<nombre>', methods=['GET', 'POST'])
def modificar_persona(nombre):
    persona = next((p for p in personas if p.nombre == nombre), None)
    if request.method == 'POST':
        no_disponibilidad = request.form.getlist('no_disponibilidad')
        persona.no_disponibilidad = set(no_disponibilidad)  # Use a set instead of a list
        return redirect(url_for('ver_personas'))
    return render_template('modificar_persona.html', persona=persona, dias=dias)

@app.route('/agregar_persona', methods=['GET', 'POST'])
def agregar_persona():
    if request.method == 'POST':
        nombre = request.form['nombre']
        genero = request.form['genero']
        no_disponibilidad = set(request.form.getlist('no_disponibilidad'))  # Use a set instead of a list
        nueva_persona = Persona(nombre, genero, no_disponibilidad)
        personas.append(nueva_persona)
        return redirect(url_for('ver_personas'))
    return render_template('agregar_persona.html', dias=dias)

@app.route('/eliminar_persona/<nombre>')
def eliminar_persona(nombre):
    global personas
    personas = [p for p in personas if p.nombre != nombre]
    return redirect(url_for('ver_personas'))

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
    
    calendario = asignar_tareas_mejorado(personas, espacios, dias, calendario_anterior, contador_tareas_anterior)
    contador_tareas = contar_tareas_mejorado(calendario)
    return render_template('index.html', calendario=calendario, espacios=espacios, dias=dias, contador_tareas=contador_tareas)



# Modifica la función generar_lista para usar el historial
@app.route('/generar_lista')
def generar_lista():
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


@app.route('/ver_historial')
def ver_historial():
    db = get_db()
    historial = db.execute('SELECT * FROM historial ORDER BY fecha DESC LIMIT 10').fetchall()
    
    # Definimos el orden correcto de los días
    orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    historial_list = []
    for row in historial:
        calendario = json.loads(row['calendario'])
        # Ordenamos el calendario para cada entrada del historial
        calendario_ordenado = {dia: calendario[dia] for dia in orden_dias if dia in calendario}
        
        historial_list.append({
            'fecha': row['fecha'],
            'calendario': calendario_ordenado,
            'contador_tareas': json.loads(row['contador_tareas'])
        })
    
    return render_template('ver_historial.html', historial=historial_list)


@app.route('/borrar_historial', methods=['POST'])
def borrar_historial():
    password = request.form.get('password')
    if password == 'Trenque769':
        db = get_db()
        db.execute('DELETE FROM historial')
        db.commit()
        flash('Historial borrado correctamente', 'success')
    else:
        flash('Contraseña incorrecta', 'danger')
    return redirect(url_for('ver_historial'))


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
    calendario = asignar_tareas_mejorado(personas, espacios, dias, calendario_anterior, contador_tareas_anterior)
    contador_tareas = contar_tareas_mejorado(calendario)

@app.route('/borrar_historial_individual/<int:id>', methods=['POST'])
def borrar_historial_individual(id):
    db = get_db()
    db.execute('DELETE FROM historial WHERE id = ?', (id,))
    db.commit()
    flash('Entrada de historial borrada correctamente', 'success')
    return redirect(url_for('ver_historial'))

@app.route('/modificar_historial_individual/<int:id>', methods=['GET'])
def modificar_historial_individual(id):
    db = get_db()
    historial = db.execute('SELECT * FROM historial WHERE id = ?', (id,)).fetchone()
    
    if historial:
        return render_template('modificar_historial.html', historial={
            'id': historial['id'],
            'calendario': json.loads(historial['calendario']),
            'contador_tareas': json.loads(historial['contador_tareas'])
        })
    else:
        flash('El historial no existe', 'danger')
        return redirect(url_for('ver_historial'))

@app.route('/guardar_modificacion_historial/<int:id>', methods=['POST'])
def guardar_modificacion_historial(id):
    calendario = request.form['calendario']
    contador_tareas = request.form['contador_tareas']
    
    db = get_db()
    db.execute('UPDATE historial SET calendario = ?, contador_tareas = ? WHERE id = ?',
               (calendario, contador_tareas, id))
    db.commit()
    
    flash('Historial actualizado correctamente', 'success')
    return redirect(url_for('ver_historial'))


if __name__ == '__main__':
    app.run(debug=True)