import requests

lista_de_funciones = []

def variable_nombre(nombre):
    # Comprobar que cada palabra del nombre tiene solo letras
    nombre_compuesto = all(palabra.isalpha() for palabra in nombre.split())

    if not nombre_compuesto:
        return "Nombre inválido: solo se permiten letras y espacios"

    if nombre.isdigit():
        return "Nombre inválido: no puede ser solo números"

    return f"Nombre válido: {nombre}"

def variable_elo(elo):
        try:
            elo = int(elo)
            if elo <= 0:
                return "ELO debe ser un número positivo"
            return f"ELO válido: {elo}"
        except ValueError:
            return "ELO inválido: por favor, introduce un número válido (ej: 1500)"
            
            
            