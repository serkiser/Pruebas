import math

while True:
    
    ## Creamos un Array
    Lista_numeros = []

    ## Ponemos los numeros
    A = input("Introduce el valor A:")
    B = input("Introduce el valor B:")
    C = input("Introduce el valor C:")

    Lista_numeros.append(A)
    Lista_numeros.append(B)
    Lista_numeros.append(C)

    ## Compuebro que todos son diferentes
    for i in range (len(Lista_numeros)):
        if i != {i+1}:
            break
    


if A > B:
    if A > C:
        print (f"{A} es mayor que {B} y {C}")

if B > A:
    if B > C:
        print (f"{B} es mayor que {A} y {C}")
    else:
        print (f"{C} es mayor que {A} y {B}")   
    