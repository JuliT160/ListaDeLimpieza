import random
from collections import defaultdict
from tareas_mejoradas import Persona, Espacio, asignar_tareas_mejorado, contar_tareas_mejorado
import matplotlib.pyplot as plt

# Define the data (same as in your original code)
def create_personas():
    return [
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
]

dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

def generate_random_unavailability(dias):
    num_unavailable = random.randint(0, 3)  # 0 to 3 unavailable days
    return random.sample(dias, num_unavailable)

def run_distribution_test(num_iterations=1000000):
    total_tasks = defaultdict(int)
    all_counts = []

    for _ in range(num_iterations):
        personas = create_personas()
        # Generate random unavailability for each person
        for persona in personas:
            persona.no_disponibilidad = generate_random_unavailability(dias)

        calendario = asignar_tareas_mejorado(personas, espacios, dias)
        contador_tareas = contar_tareas_mejorado(calendario)
        
        for persona, count in contador_tareas.items():
            total_tasks[persona] += count
        
        all_counts.append(list(contador_tareas.values()))

    # Calculate average tasks per person
    avg_tasks = {persona: total / num_iterations for persona, total in total_tasks.items()}

    # Calculate standard deviation
    std_dev = {persona: (sum((count - avg_tasks[persona])**2 for count in counts) / num_iterations)**0.5 
               for persona, counts in zip(avg_tasks.keys(), zip(*all_counts))}

    return avg_tasks, std_dev

def print_results(avg_tasks, std_dev):
    print(f"Results after {num_iterations} iterations:")
    print("\nAverage tasks per person:")
    for persona, avg in sorted(avg_tasks.items(), key=lambda x: x[1], reverse=True):
        print(f"{persona}: {avg:.2f} ± {std_dev[persona]:.2f}")

    print(f"\nOverall average: {sum(avg_tasks.values()) / len(avg_tasks):.2f}")
    print(f"Standard deviation of averages: {(sum((avg - sum(avg_tasks.values()) / len(avg_tasks))**2 for avg in avg_tasks.values()) / len(avg_tasks))**0.5:.2f}")

def plot_results(avg_tasks, std_dev):
    fig, ax = plt.subplots(figsize=(12, 6))
    
    personas = list(avg_tasks.keys())
    averages = list(avg_tasks.values())
    errors = list(std_dev.values())

    ax.bar(personas, averages, yerr=errors, capsize=5)
    ax.set_ylabel('Average number of tasks')
    ax.set_title(f'Task Distribution over {num_iterations} iterations')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('task_distribution.png')
    print("Plot saved as 'task_distribution.png'")

if __name__ == "__main__":
    num_iterations = 100
    avg_tasks, std_dev = run_distribution_test(num_iterations)
    print_results(avg_tasks, std_dev)
    plot_results(avg_tasks, std_dev)