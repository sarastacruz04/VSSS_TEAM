import socket
import struct

UDP_IP = "224.0.0.1"
UDP_PORT = 10002

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Configuramos un tiempo límite de 2 segundos para que no se quede bloqueado eternamente
sock.settimeout(2.0)
sock.bind(('', UDP_PORT))

group = socket.inet_aton(UDP_IP)
mreq = struct.pack("4sL", group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print(f"Escuchando datos de visión en {UDP_IP}:{UDP_PORT}...")

try:
    while True:
        try:
            data, addr = sock.recvfrom(65535)
            print(f"¡Paquete recibido! Tamaño: {len(data)} bytes")
        except socket.timeout:
            print("Esperando paquetes de la cancha... (asegúrate de que Webots esté corriendo con Play)")
except KeyboardInterrupt:
    print("\nMonitoreo detenido.")
    sock.close()
