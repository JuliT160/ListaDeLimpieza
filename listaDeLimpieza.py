import random

# Clases para representar las personas y los espacios
class Persona:
    def __init__(self, nombre, genero, no_disponibilidad):
        self.nombre = nombre
        self.genero = genero
        self.no_disponibilidad = no_disponibilidad  # Lista de días no disponibles
        self.tareas_asignadas = {}  # Día: Espacio

class Espacio:
    def __init__(self, nombre, restriccion_genero=None, frecuencia="diaria"):
        self.nombre = nombre
        self.restriccion_genero = restriccion_genero  # None, "M", o "H"
        self.frecuencia = frecuencia  # "diaria" o ["Lunes", "Miércoles", "Viernes"]

# Función para determinar si una persona puede limpiar un espacio en un día específico
def puede_limpiarp(calendario, persona, dia):
    dias_semana = list(calendario.keys())
    dia_idx = dias_semana.index(dia)
    dia_anterior = dias_semana[dia_idx - 1] if dia_idx > 0 else None

    if dia_anterior and dia_anterior in persona.tareas_asignadas:
        return False  # No puede limpiar dos días seguidos

    return True

# Función para asignar las tareas de limpieza
def asignar_tareas(personas, espacios, dias):
    calendario = {dia: {espacio.nombre: None for espacio in espacios if espacio.frecuencia == "diaria" or dia in espacio.frecuencia} for dia in dias}
    contador_tareas = {p: 0 for p in personas}  # Contador de tareas asignadas a cada persona

    for dia in dias:
        for espacio in [e for e in espacios if e.frecuencia == "diaria" or dia in e.frecuencia]:
            disponibles = [p for p in personas if dia not in p.no_disponibilidad and (espacio.restriccion_genero is None or p.genero == espacio.restriccion_genero) and p.nombre not in calendario[dia].values()]
            posibles = [p for p in disponibles if puede_limpiarp(calendario, p, dia) and espacio.nombre not in p.tareas_asignadas.values()]

            # Ordena las personas por el número de tareas asignadas
            posibles.sort(key=lambda p: contador_tareas[p])

            if posibles:
                elegido = posibles[0]  # Elige la persona con menos tareas asignadas
                calendario[dia][espacio.nombre] = elegido.nombre
                elegido.tareas_asignadas[dia] = espacio.nombre
                contador_tareas[elegido] += 1  # Incrementa el contador de tareas asignadas a la persona

            else:
                # En caso de que no haya nadie disponible, intentamos asignar a alguien sin considerar la restricción de dos días seguidos
                if disponibles:
                    elegido = random.choice(disponibles)
                    calendario[dia][espacio.nombre] = elegido.nombre
                    elegido.tareas_asignadas[dia] = espacio.nombre

    return calendario

# Función para imprimir el calendario de tareas
def imprimir_calendario(calendario, espacios, dias):
    # Calcula la longitud máxima del nombre de los espacios para alinear la tabla
    max_nombre_espacio = len(max(espacios, key=lambda x: len(x.nombre)).nombre)

    # Imprime la fila superior de la tabla
    print(" " * 4 + " ".join(espacio.nombre.ljust(max_nombre_espacio) for espacio in espacios))
    print(" " * 4 + " " + "-" * (max_nombre_espacio * len(espacios) + len(espacios) - 1))

    for dia in dias:
        print(f"{dia.ljust(9)} |", end="")
        for espacio in espacios:
            persona = calendario[dia].get(espacio.nombre, "")
            print(f" {persona.ljust(max_nombre_espacio)} |", end="")
        print()

# Datos de entrada
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

# Ejecutar la asignación
calendario = asignar_tareas(personas, espacios, dias)

# Mostrar el resultado
"""for dia, tareas in calendario.items():
    print(f"{dia}:")
    for espacio, persona in tareas.items():
        print(f"  {espacio}: {persona}")"""

imprimir_calendario(calendario, espacios, dias)

# Mostrar los nombres de las personas con la cantidad de veces que limpia en la semana
for persona in personas:
    print(f"{persona.nombre}: {len(persona.tareas_asignadas)}")
