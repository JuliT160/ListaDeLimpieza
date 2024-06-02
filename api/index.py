from flask import Flask, render_template
from tareas import asignar_tareas, personas, espacios, dias

app = Flask(__name__)
app.template_folder = "C://Users//Usuario//source//cutl//templates"
app.static_folder = "C://Users//Usuario//source//cutl//static"

@app.route('/')
def index():
    print(app.template_folder)
    print(app.static_folder)
    try:
        calendario = asignar_tareas(personas, espacios, dias)
        contador_tareas = {persona.nombre: len(persona.tareas_asignadas) for persona in personas}
        return render_template('index.html', calendario=calendario, espacios=espacios, contador_tareas=contador_tareas)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
