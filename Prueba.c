#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef struct {
    int pulsador;  // 0 (OFF) o 1 (ON)
    int SR;        // 0 (Reset) o 1 (Set)
} ControlPLC;

// Función para la Versión 1 (Entrada Manual)
void version_manual() {
    printf("\n=== MODO MANUAL === (Ingresa 0 o 1)\n");
    for (int i = 0; i <= 10; i++) {
        ControlPLC sistema;
        
        printf("Iteración %2d: Estado del pulsador (0/1): ", i);
        scanf("%d", &sistema.pulsador);
        
        // Validación
        if (sistema.pulsador != 0 && sistema.pulsador != 1) {
            printf("Entrada no válida. Se asigna 0.\n");
            sistema.pulsador = 0;
        }
        
        sistema.SR = (sistema.pulsador == 1) ? 1 : 0;
        printf("-> Pulsador = %d, SR = %d\n", sistema.pulsador, sistema.SR);
    }
}

// Función para la Versión 2 (Lógica con Memoria)
void version_memoria() {
    printf("\n=== MODO MEMORIA === (SR mantiene estado hasta reset)\n");
    srand(time(0));
    int estado_SR = 0;  // Memoria del SR

    for (int i = 0; i <= 10; i++) {
        ControlPLC sistema;
        sistema.pulsador = rand() % 2;  // Aleatorio 0/1

        // Lógica: Pulsador=1 activa SR; reset si i es par
        if (sistema.pulsador == 1) {
            estado_SR = 1;
        } 
        else if (i % 2 == 0) {
            estado_SR = 0;
        }
        
        sistema.SR = estado_SR;
        printf("Iteración %2d: Pulsador = %d, SR = %d\n", i, sistema.pulsador, sistema.SR);
    }
}

int main() {
    int opcion;
    
    printf("Elije una versión:\n");
    printf("1. Modo Manual (Entrada por teclado)\n");
    printf("2. Modo Memoria (SR con estado persistente)\n");
    printf("Opción: ");
    scanf("%d", &opcion);

    switch (opcion) {
        case 1:
            version_manual();
            break;
        case 2:
            version_memoria();
            break;
        default:
            printf("Opción no válida. Saliendo.\n");
    }
    
    return 0;
}