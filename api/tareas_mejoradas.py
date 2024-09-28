import random
from collections import defaultdict
from typing import List, Dict

class Persona:
    def __init__(self, nombre: str, genero: str, no_disponibilidad: List[str]):
        self.nombre = nombre
        self.genero = genero
        self.no_disponibilidad = set(no_disponibilidad)
        self.tareas_asignadas = 0
        self.espacios_asignados = defaultdict(int)  # Nuevo: para contar asignaciones por espacio

class Espacio:
    def __init__(self, nombre: str, genero_preferido: str = None, frecuencia: List[str] = None):
        self.nombre = nombre
        self.genero_preferido = genero_preferido
        self.frecuencia = set(frecuencia) if frecuencia else set()

def asignar_tareas_mejorado(personas: List[Persona], espacios: List[Espacio], dias: List[str], calendario_anterior: Dict[str, Dict[str, str]] = None, contador_tareas_anterior: Dict[str, int] = None) -> Dict[str, Dict[str, str]]:
    calendario = {dia: {espacio.nombre: "" for espacio in espacios} for dia in dias}
    personas_disponibles = defaultdict(list)

    # Reiniciar contadores de espacios asignados
    for persona in personas:
        persona.espacios_asignados.clear()

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
                # Ajustar la selección basada en el historial y asignaciones previas
                if calendario_anterior and contador_tareas_anterior:
                    persona_anterior = calendario_anterior.get(dia, {}).get(espacio.nombre)
                    if persona_anterior:
                        candidatos = [p for p in candidatos if p.nombre != persona_anterior]

                # Filtrar candidatos que ya han sido asignados a este espacio esta semana
                candidatos = [p for p in candidatos if p.espacios_asignados[espacio.nombre] == 0]

                if not candidatos:
                    # Si no hay candidatos sin asignaciones previas, seleccionar entre todos
                    candidatos = personas_disponibles[dia]

                # Select candidates with the minimum number of assigned tasks
                min_tasks = min(p.tareas_asignadas for p in candidatos)
                candidatos_min = [p for p in candidatos if p.tareas_asignadas == min_tasks]
                
                # Randomly select from the candidates with the minimum number of tasks
                persona_elegida = random.choice(candidatos_min)
                calendario[dia][espacio.nombre] = persona_elegida.nombre
                persona_elegida.tareas_asignadas += 1
                persona_elegida.espacios_asignados[espacio.nombre] += 1
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