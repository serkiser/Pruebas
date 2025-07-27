import requests

# Obtención de datos personales
nombre = input('Dime tu nombre: ')

while True:
    try:
        elo = int(input('Dime tu ELO: '))
        if elo <= 0:
            print('ELO debe ser un número positivo.')
        else:
            break
    except ValueError:
        print('Por favor, introduce un número válido (ej: 1500).')

lugar = input('Dime donde vives: ')

# Obtención de datos de jugadores FIDE
url = "https://fide-api.vercel.app/top_players/?limit=200&history=false"
data = requests.get(url).json()

# Variables para comparación
jugador_mas_cercano_superior = None
jugador_mas_cercano_inferior = None
Lista_de_jugadores = []
for jugador in data:
    try:
        #Creamos la lista de jugadores y diferencia de elo
        
        elo_api = int(jugador['rating'])
        
       
        diferencia = abs(elo_api - elo)
        Lista_de_jugadores.append((jugador['name'],  elo_api, jugador.get('rank', 'N/A'), diferencia))
        
        
    except (KeyError, ValueError):
        continue  # Si hay error en los datos del jugador, pasamos al siguiente

Lista_de_jugadores.sort(key=lambda x: x[3])  # Ordenamos por la diferencia de ELO
if len(Lista_de_jugadores) > 1 and Lista_de_jugadores[0][3] == Lista_de_jugadores[1][3]:
    print("\nHay empate en la menor diferencia:")
    print(Lista_de_jugadores[0])
    print(Lista_de_jugadores[1])
else:
    print("\nSolo un jugador tiene la menor diferencia:")
    print(Lista_de_jugadores[0])