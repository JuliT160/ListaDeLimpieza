from flask import Flask, render_template
from tareas import asignar_tareas, personas, espacios, dias

app = Flask(__name__)
app.template_folder = "../templates"
app.static_folder = "../static"

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
    print(app.template_folder)
    print(app.static_folder)
    try:
        calendario = asignar_tareas(personas, espacios, dias)
        contador_tareas = contar_tareas(calendario)
        return render_template('index.html', calendario=calendario, espacios=espacios, contador_tareas=contador_tareas)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
