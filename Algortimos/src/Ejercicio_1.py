import math

while True:
    valor_uno = input("Introduce el primer valor:")
    valor_dos = input("Introduce el segundo valor:")

    if valor_uno != valor_dos:
        print("OK")
        break
    else:
        print("No puedens ser iguales")
    
if valor_uno > valor_dos:
        print (f"El {valor_uno} es mayor que {valor_dos}")
else:
         print (f"El {valor_dos} es mayor que {valor_uno}")

