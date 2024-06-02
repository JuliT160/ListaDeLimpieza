from flask import Flask, render_template, request, redirect, url_for
from tareas import Persona, Espacio, asignar_tareas

app = Flask(__name__)
app.template_folder = "../templates"
app.static_folder = "../static"

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
    Espacio("Patio", frecuencia=["Lunes", "Miércoles", "Viernes"])
]

dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

def contar_tareas(calendario):
    contador_tareas = {}
    for dia, tareas in calendario.items():
        for espacio, persona in tareas.items():
            if persona:
                if persona in contador_tareas:
                    contador_tareas[persona] += 1
                else:
                    contador_tareas[persona] = 1
    return contador_tareas

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
        persona.no_disponibilidad = no_disponibilidad
        return redirect(url_for('ver_personas'))
    return render_template('modificar_persona.html', persona=persona, dias=dias)

@app.route('/agregar_persona', methods=['GET', 'POST'])
def agregar_persona():
    if request.method == 'POST':
        nombre = request.form['nombre']
        genero = request.form['genero']
        no_disponibilidad = request.form.getlist('no_disponibilidad')
        nueva_persona = Persona(nombre, genero, no_disponibilidad)
        personas.append(nueva_persona)
        return redirect(url_for('ver_personas'))
    return render_template('agregar_persona.html', dias=dias)

@app.route('/eliminar_persona/<nombre>')
def eliminar_persona(nombre):
    global personas
    personas = [p for p in personas if p.nombre != nombre]
    return redirect(url_for('ver_personas'))

@app.route('/generar_lista')
def generar_lista():
    calendario = asignar_tareas(personas, espacios, dias)
    contador_tareas = contar_tareas(calendario)
    return render_template('index.html', calendario=calendario, espacios=espacios, dias=dias, contador_tareas=contador_tareas)

if __name__ == '__main__':
    app.run(debug=True)
