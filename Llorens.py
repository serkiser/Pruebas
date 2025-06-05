import requests
import json

# Obtencion de datos 

#Obtener nombre
print('Dime tu nombre:')
nombre = input()

#Obtener edad
while True:
    elo = input('Dime tu elo: ')
    
    try:
        elo = int(elo)  # Intenta convertir a entero
        
        if elo <= 0:  # Verifica si la edad es un número positivo mayor que 0
            print('La edad debe ser un número positivo mayor que 0.')
        else:
            break  # Edad válida, salimos del bucle
            
    except ValueError:  # Si no se pudo convertir a entero
        print('Por favor, introduce un número válido (ej: 25).')

#Obtener lugar de residencia
print('Dime donde vives:')
lugar = input()

# Haces la petición con esos parámetros
url = "https://fide-api.vercel.app/top_players/?limit=200&history=false"

response = requests.get(url)
data = response.json()


for i in data:
    jugador = i['name']
    elo_api = i['rating']
    elo_api = int(elo_api)
    if elo < elo_api:
        print(f"Tu elo es el mismo que el de {jugador} con un elo de {elo_api}")
    elif elo == elo_api:
        print(f"Tu elo es el mismo que el de {jugador} con un elo de {elo_api}")