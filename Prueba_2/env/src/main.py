# Crear una matriz de 10x10 con patrones definidos
def obtener_columnas(i):
    if i == 1:
        return list(range(2, 4)) + list(range(6, 8))
    elif i == 2 or i == 5:
        return list(range(1, 9))
    elif i in range(3, 5):
        return list(range(0, 10))
    elif i == 6:
        return list(range(2, 8))
    elif i == 7:
        return list(range(3, 7))
    elif i == 8:
        return list(range(4, 7))
    elif i == 9:
        return [5]
    else:
        return []

matriz = []
for i in range(10):
    columnas = obtener_columnas(i)
    fila = ['@' if j in columnas else '.' for j in range(10)]
    matriz.append(fila)

# Mostrar la matriz
for fila in matriz:
    print(" ".join(fila))