import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle

# Parámetros físicos
k = 8.988e9  # Constante de Coulomb (N·m²/C²)
q1 = 20e-5    # Carga de la primera bola (C)
q2 = -20e-5   # Carga de la segunda bola (C)
m1 = 5.0     # Masa de la primera bola (kg)
m2 = 5.0     # Masa de la segunda bola (kg)
radius = 0.3 # Radio de las bolas (m)
d_initial = 4 # Distancia inicial entre centros (m)

# Coeficientes de comportamiento
coeficiente_restitucion = 0.3  # 0.0 = inelástico total, 1.0 = elástico
factor_friccion = 0.98         # 1.0 = sin fricción, <1.0 = fricción

# Posiciones iniciales (centros)
x1, y1 = -d_initial/2, 0
x2, y2 = d_initial/2, 0

# Velocidades iniciales
v1x, v1y = 0, 0.5
v2x, v2y = 0, -0.5

# Configuración de la gráfica
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(-5, 5)
ax.set_ylim(-2, 2)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Simulación de Cargas con Colisiones Inelásticas')

# Crear las bolas
bola1 = Circle((x1, y1), radius, color='red', alpha=0.7, label=f'Carga: {q1}C')
bola2 = Circle((x2, y2), radius, color='blue', alpha=0.7, label=f'Carga: {q2}C')
ax.add_patch(bola1)
ax.add_patch(bola2)
ax.legend()

# Texto para información
info_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)

# Parámetros de simulación
dt = 0.05  # Paso de tiempo (s)
t_max = 15  # Tiempo máximo (s)
frames = int(t_max / dt)

def check_collision():
    dx = x2 - x1
    dy = y2 - y1
    distance = np.sqrt(dx**2 + dy**2)
    return distance <= 2 * radius

def resolve_collision():
    global v1x, v1y, v2x, v2y
    
    # Vector normal de colisión
    nx = (x2 - x1) / (2 * radius)
    ny = (y2 - y1) / (2 * radius)
    
    # Velocidades relativas
    vrelx = v2x - v1x
    vrely = v2y - v1y
    
    # Producto punto (velocidad relativa en dirección normal)
    dot_product = vrelx * nx + vrely * ny
    
    # Impulso con pérdida de energía (inelástico)
    J = (1 + coeficiente_restitucion) * (m1 * m2) / (m1 + m2) * dot_product
    
    # Aplicar impulso (frenado)
    v1x += J * nx / m1
    v1y += J * ny / m1
    v2x -= J * nx / m2
    v2y -= J * ny / m2

def update(frame):
    global x1, y1, x2, y2, v1x, v1y, v2x, v2y
    
    # Calcular distancia entre centros
    dx = x2 - x1
    dy = y2 - y1
    r = np.sqrt(dx**2 + dy**2)
    
    # Ley de Coulomb (solo si no están en contacto)
    if r > 2 * radius:
        F = k * q1 * q2 / r**2
        Fx = F * dx/r
        Fy = F * dy/r
    else:
        Fx, Fy = 0, 0
    
    # Aceleraciones
    a1x, a1y = -Fx/m1, -Fy/m1
    a2x, a2y = Fx/m2, Fy/m2
    
    # Actualizar velocidades
    v1x += a1x * dt
    v1y += a1y * dt
    v2x += a2x * dt
    v2y += a2y * dt
    
    # Aplicar fricción (opcional, para frenado continuo)
    v1x *= factor_friccion
    v1y *= factor_friccion
    v2x *= factor_friccion
    v2y *= factor_friccion
    
    # Actualizar posiciones
    x1 += v1x * dt
    y1 += v1y * dt
    x2 += v2x * dt
    y2 += v2y * dt
    
    # Detección y respuesta de colisiones
    if check_collision():
        # Corregir posición para evitar solapamiento
        overlap = 2 * radius - r
        x1 -= overlap * dx/r * 0.5
        y1 -= overlap * dy/r * 0.5
        x2 += overlap * dx/r * 0.5
        y2 += overlap * dy/r * 0.5
        
        resolve_collision()
    
    # Actualizar gráficos
    bola1.center = (x1, y1)
    bola2.center = (x2, y2)
    info_text.set_text(f'Tiempo: {frame*dt:.2f}s\nDistancia: {r:.2f}m\nVelocidad: {np.sqrt(v1x**2 + v1y**2):.2f}m/s')
    
    return bola1, bola2, info_text

# Crear animación
ani = FuncAnimation(fig, update, frames=frames, interval=dt*1000, blit=True)

plt.show()