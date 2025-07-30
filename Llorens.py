import requests

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
            
def variable_donde_vives(lugar):
    lugar_compuesto = all(palabra.isalpha() for palabra in lugar.split())

    if not lugar_compuesto:
        return "Lugar inválido: solo se permiten letras y espacios"

    if lugar.isdigit():
        return "Lugar inválido: no puede ser solo números"

    return f"Lugar válido: {lugar}"

def api_jugadores(elo):  
    import requests  # asegúrate de que está al inicio
    url = "https://fide-api.vercel.app/top_players/?limit=200&history=false"
    data = requests.get(url).json()

    Lista_de_jugadores = []
    for jugador in data:
        try:
            elo_api = int(jugador['rating'])
            diferencia = abs(elo_api - elo)
            Lista_de_jugadores.append((jugador['name'], elo_api, jugador.get('rank', 'N/A'), diferencia))
        except (KeyError, ValueError):
            continue

    Lista_de_jugadores.sort(key=lambda x: x[3])
    
    if len(Lista_de_jugadores) > 1 and Lista_de_jugadores[0][3] == Lista_de_jugadores[1][3]:
        return f"Empate:\n1. {Lista_de_jugadores[0][0]} ({Lista_de_jugadores[0][1]})\n2. {Lista_de_jugadores[1][0]} ({Lista_de_jugadores[1][1]})"
    else:
        jugador = Lista_de_jugadores[0]
        return f"Jugador más cercano: {jugador[0]} (ELO {jugador[1]})"

