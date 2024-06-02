from flask import Flask, render_template
from tareas import asignar_tareas, imprimir_calendario, personas, espacios, dias

app = Flask(__name__)

@app.route('/')
def index():
    calendario = asignar_tareas(personas, espacios, dias)
    contador_tareas = {persona.nombre: len(persona.tareas_asignadas) for persona in personas}
    return render_template('index.html', calendario=calendario, espacios=espacios, contador_tareas=contador_tareas)

if __name__ == '__main__':
    app.run(debug=True)
