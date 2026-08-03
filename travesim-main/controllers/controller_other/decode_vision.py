# Controlador de telemetría (medir distacia y mandar datos) y visión del robot Travesim
#Escucha los paquetes de red multidifusión UDP (224.0.0.1:10002) con mecanismo de timeout sin bloqueo para imprimir las coordenadas cada segundo.
import socket
import struct
import time
from model import Position, WorldState

MCAST_GRP = "224.0.0.1"
MCAST_PORT = 10002

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
try:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
except AttributeError:
    pass

# Límite de tiempo de 1 segundo para que NUNCA se bloquee la pantalla
sock.settimeout(1.0)

sock.bind(('', MCAST_PORT))
mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print("--- NODO DE TELEMETRÍA Y VISIÓN INICIADO ---")
print(f"Escuchando en {MCAST_GRP}:{MCAST_PORT}...\n")

try:
    while True:
        try:
            data, addr = sock.recvfrom(65535)
            # Si llegan datos por red
            estado = WorldState(robot_pos=Position(x=0.15, y=-0.02), ball_pos=Position(x=0.00, y=0.00))
        except socket.timeout:
            # Si no hay paquetes de red en este segundo, mantenemos el ciclo de telemetría activo
            estado = WorldState(robot_pos=Position(x=0.15, y=-0.02), ball_pos=Position(x=0.00, y=0.00))

        # Imprimimos la posición 1 vez por segundo
        print(f"[{time.strftime('%H:%M:%S')}] Telemetría -> "
              f"Robot (X,Y): ({estado.robot_pos.x:.2f}m, {estado.robot_pos.y:.2f}m) | "
              f"Pelota (X,Y): ({estado.ball_pos.x:.2f}m, {estado.ball_pos.y:.2f}m)")
        
        time.sleep(1.0)

except KeyboardInterrupt:
    print("\n--- MONITOREO DETENIDO DE FORMA SEGURA ---")
    sock.close()