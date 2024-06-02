from flask import Flask, render_template
from tareas import Persona, Espacio, asignar_tareas

app = Flask(__name__)

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
def index():
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
        Persona("Alejo", "H", []),
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

    calendario = asignar_tareas(personas, espacios, dias)
    contador_tareas = contar_tareas(calendario)
    return render_template('index.html', calendario=calendario, espacios=espacios, dias=dias, contador_tareas=contador_tareas)

if __name__ == '__main__':
    app.run(debug=True)