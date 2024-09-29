from flask import Flask, render_template, request, redirect, url_for
from tareas_mejoradas import Persona, Espacio, asignar_tareas_mejorado, contar_tareas_mejorado
from firebase_config import db
from datetime import datetime
from firebase_admin import firestore
from flask import jsonify, flash

app = Flask(__name__)
app.template_folder = "../templates"
app.static_folder = "../static"
app.secret_key = 'Trenque769' 
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
    calendario = request.json['calendario']
    contador_tareas = request.json['contador_tareas']
    
    historial = {
        'fecha': datetime.now(),
        'calendario': calendario,
        'contador_tareas': contador_tareas
    }
    
    db.collection('historial').add(historial)
    
    return jsonify({'message': 'Historial guardado correctamente'}), 200

@app.route('/obtener_ultimo_historial')
def obtener_ultimo_historial():
    ultimo_historial = db.collection('historial').order_by('fecha', direction=firestore.Query.DESCENDING).limit(1).get()
    
    if len(ultimo_historial) > 0:
        return jsonify(ultimo_historial[0].to_dict()), 200
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
    ultimo_historial = db.collection('historial').order_by('fecha', direction=firestore.Query.DESCENDING).limit(1).get()
    
    if len(ultimo_historial) > 0:
        historial = ultimo_historial[0].to_dict()
        calendario_anterior = historial['calendario']
        contador_tareas_anterior = historial['contador_tareas']
    else:
        calendario_anterior = None
        contador_tareas_anterior = None
    
    calendario = asignar_tareas_mejorado(personas, espacios, dias, calendario_anterior, contador_tareas_anterior)
    contador_tareas = contar_tareas_mejorado(calendario)
    return render_template('index.html', calendario=calendario, espacios=espacios, dias=dias, contador_tareas=contador_tareas)


@app.route('/ver_historial')
def ver_historial():
    historial = db.collection('historial').order_by('fecha', direction=firestore.Query.DESCENDING).limit(10).get()
    
    historial_list = []
    for doc in historial:
        data = doc.to_dict()
        data['fecha'] = data['fecha'].strftime("%Y-%m-%d %H:%M:%S")
        historial_list.append(data)
    
    return render_template('ver_historial.html', historial=historial_list)


@app.route('/borrar_historial', methods=['POST'])
def borrar_historial():
    password = request.form.get('password')
    if password == 'Trenque769':
        # Borrar todo el historial
        docs = db.collection('historial').get()
        for doc in docs:
            doc.reference.delete()
        flash('Historial borrado correctamente', 'success')
    else:
        flash('Contraseña incorrecta', 'danger')
    return redirect(url_for('ver_historial'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)