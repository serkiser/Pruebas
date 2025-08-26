#Mi asistente personal

import time
import datetime

def saludo():
    print("Hola, soy tu asistente personal.")
    time.sleep(1)
    print("¿Cómo te llamas?")
    nombre = input("")
    print(f"Encantado de conocerte, {nombre}. ¿En qué puedo ayudarte hoy?")
    return 1

def hora_actual():
    ahora = datetime.datetime.now()
    hora = ahora.strftime("%H:%M:%S")
    print(f"La hora actual es {hora}")

# Guardamos el resultado de saludo()
respuesta = saludo()

# Y luego decidimos qué hacer
if respuesta == 1:
    hora_actual()
