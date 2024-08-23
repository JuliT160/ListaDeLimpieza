import random
from collections import defaultdict
from typing import List, Dict

class Persona:
    def __init__(self, nombre: str, genero: str, no_disponibilidad: List[str]):
        self.nombre = nombre
        self.genero = genero
        self.no_disponibilidad = set(no_disponibilidad)
        self.tareas_asignadas = 0

class Espacio:
    def __init__(self, nombre: str, genero_preferido: str = None, frecuencia: List[str] = None):
        self.nombre = nombre
        self.genero_preferido = genero_preferido
        self.frecuencia = set(frecuencia) if frecuencia else set()

def asignar_tareas_mejorado(personas: List[Persona], espacios: List[Espacio], dias: List[str]) -> Dict[str, Dict[str, str]]:
    calendario = {dia: {espacio.nombre: "" for espacio in espacios} for dia in dias}
    personas_disponibles = defaultdict(list)

    # Crear listas de personas disponibles por día
    for dia in dias:
        for persona in personas:
            if dia not in persona.no_disponibilidad:
                personas_disponibles[dia].append(persona)

    # Asignar tareas
    for dia in dias:
        for espacio in espacios:
            if espacio.frecuencia and dia not in espacio.frecuencia:
                continue

            candidatos = [p for p in personas_disponibles[dia] if p.genero == espacio.genero_preferido] if espacio.genero_preferido else personas_disponibles[dia]
            
            if not candidatos:
                candidatos = personas_disponibles[dia]

            if candidatos:
                # Select candidates with the minimum number of assigned tasks
                min_tasks = min(p.tareas_asignadas for p in candidatos)
                candidatos_min = [p for p in candidatos if p.tareas_asignadas == min_tasks]
                
                # Randomly select from the candidates with the minimum number of tasks
                persona_elegida = random.choice(candidatos_min)
                calendario[dia][espacio.nombre] = persona_elegida.nombre
                persona_elegida.tareas_asignadas += 1
                personas_disponibles[dia].remove(persona_elegida)

    return calendario

def contar_tareas_mejorado(calendario: Dict[str, Dict[str, str]]) -> Dict[str, int]:
    contador = defaultdict(int)
    for dia in calendario:
        for espacio in calendario[dia]:
            persona = calendario[dia][espacio]
            if persona:
                contador[persona] += 1
    return dict(contador)