#!/usr/bin/env python3

import socket
import datetime
import threading
import pickle
import os


HOST = ""  # The server's hostname or IP address
PORT = 0  # The port used by the server
buffer_size = 1024
tablero = []
s = 0
finJuego = False

HOST = input("Ingresa la direccion ip del servidor: ")

while (True):
    puerto = input("Ingresa el puerto: ")
    if (puerto.isdigit()):
        if (int(puerto) > 1023):
            PORT = int(puerto)
            break
    input("Puerto Incorrecto... Intenta de nuevo ")



def imprimirTablero(aux):
    global s
    if s == 0:
        s = aux
    else:
        return
    os.system("clear")
    print("")

    espacio = "    "

    for i in range(0, 4 * l - 3):
        espacio += "_"

    col = "    A   B   C"
    if (l == 5):
        col += "   D   E"
    print(col)
    s = 0

    for i in range(0, l):
        print(i + 1, end='   ')
        for j in range(0, l):
            dato = " " if (tablero[i][j] == "") else tablero[i][j]
            barra = " | " if (j < l - 1) else "  "
            print(dato + barra, end='')
        if i < l - 1:
            print("\n" + espacio)
    print("\n")




def VerificarTiro(tiroC, l, tablero):
    coordenadas = tiroC.split(',')
    if (len(coordenadas) == 2):
        if (set(coordenadas[0]).issubset(set(coordX)) and coordenadas[0] != '' and coordY.count(
                coordenadas[1]) and coordenadas[1] != ''):
            if (tablero[int(coordenadas[1]) - 1][ord(coordenadas[0]) - 65] == ''):
                return True
            else:
                Mostrar(
                    "La casilla ya esta ocupada, seleccione otra.")
                return False

    Mostrar("Formato incorrecto, intente de nuevo.")
    return False




def Mostrar(mensaje):
    input(mensaje)




def EnviarCoord(conn, dato):
    while (not finJuego):
        imprimirTablero(2)
        tiroC = input("Ingresa la celda donde desea tirar (letra,numero) : \n")

        if (finJuego):
            break

        if (VerificarTiro(tiroC, l, datoRec)):
            conn.sendall(pickle.dumps(tiroC))


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketCliente:
    socketCliente.connect((HOST, PORT))
    while (True):
        dif = input("Selecciona la dificultad \n 1.- Principiante \n 2.- Avanzado\n Opcion : ")
        if (dif.isdigit()):
            if (0 < int(dif) < 3):
                coordX = ['A', 'B', 'C']
                coordY = ['1', '2', '3']

                if (int(dif) == 1):
                    l = 3
                else:
                    l = 5
                    coordX.append('D')
                    coordX.append('E')
                    coordY.append('4')
                    coordY.append('5')

                print("Enviando dificultad ...")
                socketCliente.sendall(str.encode(dif))
                break
        input("Dificultad no valida, intenta de nuevo.")

    print("Esperando tablero de la partida...")
    datoRec = pickle.loads(socketCliente.recv(buffer_size))
    tablero = datoRec
    thread_read = threading.Thread(target=EnviarCoord, args=[socketCliente, datoRec])
    thread_read.start()

    while (not finJuego):
        imprimirTablero(1)
        print("\nIngresa la celda donde desea tirar (letra,numero) : ")
        datoRec = pickle.loads(socketCliente.recv(buffer_size))
        tablero = datoRec
        if (datoRec[l] == 'Fin del juego'):
            finJuego = True
            break

    os.system("clear")
    imprimirTablero(1)
    print(datoRec[l + 1])
    print(datoRec[l + 2])
    print("Pulsa enter para continuar ... ")
