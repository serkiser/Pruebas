import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Constantes
G = 6.67430e-11  # Constante gravitacional
dt = 1000        # Paso de tiempo (segundos)

# Masas (kg)
m_planet = 5.972e24  # Tierra
m_object = 1000      # Satélite

# Posiciones iniciales (metros)
planet_pos = np.array([0.0, 0.0])
object_pos = np.array([6.371e6, 0.0])  # Radio terrestre

# Velocidad inicial (m/s) - Órbita circular
object_vel = np.array([0.0, 7.7e3])  # ~7.7 km/s

# Almacenar trayectoria
trajectory = [object_pos.copy()]

# Simulación (1000 pasos)
for _ in range(1000):
    r_vector = planet_pos - object_pos
    r = np.linalg.norm(r_vector)
    
    # Evitar división por cero (si el objeto cae al planeta)
    if r < 1e5:  # Si está muy cerca, detener la simulación
        break
    
    # Fuerza gravitacional
    force_magnitude = G * (m_planet * m_object) / (r**2)
    force_direction = r_vector / r
    force = force_magnitude * force_direction
    
    # Aceleración y movimiento
    acceleration = force / m_object
    object_vel += acceleration * dt
    object_pos += object_vel * dt
    
    trajectory.append(object_pos.copy())

# Convertir a array de NumPy
trajectory = np.array(trajectory)

# Configurar gráfico
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_title("Simulación de Gravedad")
ax.set_xlim(-1.5e7, 1.5e7)
ax.set_ylim(-1.5e7, 1.5e7)

# Dibujar planeta y objeto
planet, = ax.plot(planet_pos[0], planet_pos[1], 'bo', markersize=20, label="Planeta")
orbit, = ax.plot([], [], 'r-', label="Trayectoria")
object_point, = ax.plot([], [], 'ro', label="Objeto")

# Función de inicialización
def init():
    orbit.set_data([], [])
    object_point.set_data([], [])
    return orbit, object_point

# Función de actualización (con protección contra frames vacíos)
def update(frame):
    if frame == 0:
        return init()
    
    # Extraer coordenadas hasta el frame actual
    x = trajectory[:frame+1, 0]  # frame+1 para incluir el punto actual
    y = trajectory[:frame+1, 1]
    
    orbit.set_data(x, y)
    
    # Solo actualizar si hay datos
    if len(x) > 0:
        object_point.set_data([x[-1]], [y[-1]])
    
    return orbit, object_point

# Crear animación (ajustar frames al tamaño de trajectory)
ani = FuncAnimation(
    fig, update, frames=len(trajectory),
    init_func=init, blit=True, interval=50, repeat=False
)

plt.legend()
plt.grid()
plt.show()