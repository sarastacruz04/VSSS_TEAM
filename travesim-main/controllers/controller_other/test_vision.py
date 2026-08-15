import json
import socket


UDP_IP = "127.0.0.1"
UDP_PORT = 10002


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.settimeout(2.0)
sock.bind((UDP_IP, UDP_PORT))

print(f"Escuchando vision JSON en {UDP_IP}:{UDP_PORT}...")

try:
    while True:
        try:
            data, addr = sock.recvfrom(65535)
            env = json.loads(data.decode("utf-8"))

            ball = env["frame"]["ball"]
            yellow = env["frame"]["robots_yellow"]
            blue = env["frame"]["robots_blue"]

            print(
                f"step={env['step']} "
                f"ball=({ball['x']:.3f}, {ball['y']:.3f}) "
                f"yellow0=({yellow[0]['x']:.3f}, {yellow[0]['y']:.3f}) "
                f"blue0=({blue[0]['x']:.3f}, {blue[0]['y']:.3f}) "
                f"desde={addr}"
            )
        except socket.timeout:
            print("Esperando vision JSON... asegúrate de que Match3v3.wbt este en Play")
except KeyboardInterrupt:
    print("\nMonitoreo detenido.")
finally:
    sock.close()
