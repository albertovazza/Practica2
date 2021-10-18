# !/usr/bin/env python3

import socket
import sys
import threading
import datetime
import pickle

BUFFER_SIZE =  1024
l = 0
posicioneslib =  []
identificadores = []
coordX = ['A','B','C']
coordY = ['1','2','3']
tablero = []
finJuego = False
listaconexiones = []
winner = ""
inicio = datetime.datetime.now()
fin = ""


def imprimirTablero():
    espacio = "    "
    for i in range(0, 4*l - 3):
        espacio += "_"

    col ="    A   B   C"
    if(l == 5):
        col += "   D   E"
    print(col)

    for i in range(0, l):
        print( i + 1, end='   ')
        for j in range(0, l):
            dato = " " if (tablero[i][j] == "") else tablero[i][j]
            barra = " | " if (j < l - 1) else "  "
            print(dato + barra,end='')
        if i < l - 1:
            print("\n" + espacio)
    print("\n")



def InicializarTablero( dif ):
    tablero.clear()
    for i in range ( 0, dif):
        aux = []
        for j in range ( 0, dif):
            aux.append( '' )
        tablero.append(aux)



def ServirPorSiempre(socketTcp, numeroConexiones):
    try:
        while True:
            client_conn, client_addr = socketTcp.accept()
            print("Conectado a", client_addr)

            print("Esperando la dificultad de juego ... ")
            dif = client_conn.recv(BUFFER_SIZE)
            print ("Recibido, la dificultad es: ", dif,"   de : ", client_addr)

            global l
            if( l == 0):
                inicio = datetime.datetime.now()
                if( int( dif ) == 1 ):
                    l = 3
                else:
                    l = 5
                    coordX.append('D')
                    coordX.append('E')
                    coordY.append('4')
                    coordY.append('5')
                posicioneslib.clear()
                for i in range (1, l * l + 1):
                    posicioneslib.append(i)

                for i in range(1, l + 1):
                    identificadores.append(str(i))

                InicializarTablero( l )
            listaconexiones.append(client_conn)
            identificador = identificadores[ len(listaconexiones) - 1 ]
            thread_read = threading.Thread(target=RecibirTiros, args=[client_conn, client_addr, identificador])
            thread_read.start()
            gestion_conexiones()
    except Exception as e:
        print(e)




def gestion_conexiones():
    for conn in listaconexiones:
        if conn.fileno() == -1:
            listaconexiones.remove(conn)
    print("hilos activos:", threading.active_count())
    print("enum", threading.enumerate())
    print("conexiones: ", len(listaconexiones))
    print(listaconexiones)



def VerificarTiro( tiroCliente, identificador):
    coordenadas = tiroCliente.split(',')
    if( len(coordenadas) == 2 ):
        if( set(coordenadas[0]).issubset(set(coordX)) and coordenadas[0] != '' and
            set(coordenadas[1]).issubset(set(coordY)) and coordenadas[1] != ''):
                return AsignarCoordenadas( int( coordenadas[1] ) - 1, ord( coordenadas[0] ) - 65 , l,  identificador)

    return False



def AsignarCoordenadas(x, y, l, identificador):
    if( tablero[x][y] == ''):
        tablero[x][y] = identificador
        posicion = y + 1 + l * x
        if( posicion in posicioneslib ):
            posicioneslib.remove(posicion)
        return True
    return False



def VerificarTablero(x, y, identificador):
    simbolo = identificador
    lineaCompletada = True
    print( posicioneslib )
    #Compara horizontalmente
    for j in range (0, l):
        if( tablero[x][j] != simbolo ):
            lineaCompletada = False
            break

    #Compara verticalmente
    if(not lineaCompletada):
        lineaCompletada = True
        for i in range (0, l):
            if( tablero[i][y] != simbolo ):
                lineaCompletada = False
                break

    #Diagonalmente
    if(not lineaCompletada and x == y):
        lineaCompletada = True
        for i in range (0, l):
            if( tablero[i][i] != simbolo ):
                lineaCompletada = False
                break

    if(not lineaCompletada and (x + y) == (l - 1)):
        lineaCompletada = True
        for i in range (0, l):
            if( tablero[i][l - 1 - i] != simbolo ):
                lineaCompletada = False
                break

    if(not lineaCompletada and len(posicioneslib) >  0):
        return False

    global winner
    if( not lineaCompletada):
        winner = "-1"
        return True
    winner = identificador
    return True



def EnviarTableroAClientes(finJuego = False):
    i = 0
    for conn in listaconexiones:
        dato = []
        dato = tablero.copy()
        if( finJuego ):
            dato.append('Fin del juego ')
            if( winner == "-1" ):
                dato.append( "El juego ha terminado en empate" )
            elif( winner == identificadores[i] ):
                dato.append( "Victoria. Haz ganado!!" )
            else:
                dato.append( "Haz perdido" )
            print(inicio)
            fin = str( datetime.datetime.now() - inicio )
            dato.append("Duracion de la partida: " + fin)
            i += 1
        else:
            dato.append( finJuego )
        print(dato)
        conn.sendall(pickle.dumps(dato))



def RecibirTiros(conn, addr, identificador):
    try:
        cur_thread = threading.current_thread()
        finJuego = False
        while not finJuego:
            dato = []
            dato = tablero.copy()
            dato.append(finJuego)
            EnviarTableroAClientes()
            print("Esperando tiro del cliente ", addr)
            tiroCliente = conn.recv(BUFFER_SIZE)
            if ( VerificarTiro( pickle.loads(tiroCliente), identificador)):
                coordenadas = pickle.loads(tiroCliente).split(',')
                finJuego = VerificarTablero(int( coordenadas[1] ) - 1, ord( coordenadas[0] ) - 65, identificador)
        EnviarTableroAClientes(finJuego)
    except Exception as e:
        print(e)
    finally:
        print(conn)
        print(listaconexiones)
        listaconexiones.remove(conn)
        print(listaconexiones)
        conn.close()
        if( len(listaconexiones) == 0):
            tablero.clear()
            global l
            l = 0



host, port, numConn = sys.argv[1:4]

if len(sys.argv) != 4:
    print("orden:", sys.argv[0], "<host> <puerto> <num_connections>")
    sys.exit(1)

serveraddr = (host, int(port))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketServidor:
    socketServidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socketServidor.bind(serveraddr)
    socketServidor.listen(int(numConn))
    print("El servidor TCP está disponible y en espera de solicitudes")

    ServirPorSiempre(socketServidor, int(numConn))
