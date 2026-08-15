import json
import socket
import time


VISION_IP = "127.0.0.1"
VISION_PORT = 10002

TEAM_IP = "127.0.0.1"
YELLOW_TEAM_PORT = 20012
BLUE_TEAM_PORT = 20013

BLUE_GOALKEEPER_ID = 0
BLUE_GOALKEEPER_X = -0.71
GOALKEEPER_Y_MIN = -0.30
GOALKEEPER_Y_MAX = 0.30

# Si el robot se mueve al lado contrario, cambia este valor a -1.0.
FORWARD_Y_SIGN = 1.0

MAX_SPEED = 2.0
KP_Y = 7.0
STOP_Y_ERROR = 0.025


def clamp(value, lower, upper):
    return max(lower, min(upper, value))


def send_commands(sock, port, commands):
    payload = {
        "commands": [
            {
                "robot_id": robot_id,
                "left_wheel": left_wheel,
                "right_wheel": right_wheel,
            }
            for robot_id, left_wheel, right_wheel in commands
        ]
    }
    sock.sendto(json.dumps(payload).encode("utf-8"), (TEAM_IP, port))


def stop_all(sock):
    stopped = [(0, 0.0, 0.0), (1, 0.0, 0.0), (2, 0.0, 0.0)]
    send_commands(sock, YELLOW_TEAM_PORT, stopped)
    send_commands(sock, BLUE_TEAM_PORT, stopped)


def goalkeeper_target_y(ball):
    return clamp(ball["y"], GOALKEEPER_Y_MIN, GOALKEEPER_Y_MAX)


def goalkeeper_speed(current_y, target_y):
    error_y = target_y - current_y

    if abs(error_y) < STOP_Y_ERROR:
        return 0.0, error_y

    speed = FORWARD_Y_SIGN * KP_Y * error_y
    return clamp(speed, -MAX_SPEED, MAX_SPEED), error_y


vision_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
vision_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
vision_sock.settimeout(0.25)
vision_sock.bind((VISION_IP, VISION_PORT))

command_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("--- main_team.py iniciado ---")
print(f"Leyendo vision en {VISION_IP}:{VISION_PORT}")
print(f"Enviando comandos al azul en {TEAM_IP}:{BLUE_TEAM_PORT}")
print("Rol activo: BlueRobot0=portero sobre un solo eje")
print(
    f"BlueRobot0 mantiene x aprox {BLUE_GOALKEEPER_X:.2f}; "
    f"solo corrige y entre {GOALKEEPER_Y_MIN:.2f} y {GOALKEEPER_Y_MAX:.2f}"
)
print(f"FORWARD_Y_SIGN={FORWARD_Y_SIGN}")

try:
    while True:
        try:
            data, _ = vision_sock.recvfrom(65535)
            world = json.loads(data.decode("utf-8"))
        except socket.timeout:
            print("Sin vision reciente: comando cero")
            stop_all(command_sock)
            continue

        ball = world["frame"]["ball"]
        blue0 = world["frame"]["robots_blue"][BLUE_GOALKEEPER_ID]

        target_y = goalkeeper_target_y(ball)
        speed, error_y = goalkeeper_speed(blue0["y"], target_y)

        send_commands(
            command_sock,
            YELLOW_TEAM_PORT,
            [
                (0, 0.0, 0.0),
                (1, 0.0, 0.0),
                (2, 0.0, 0.0),
            ],
        )
        send_commands(
            command_sock,
            BLUE_TEAM_PORT,
            [
                (0, speed, speed),
                (1, 0.0, 0.0),
                (2, 0.0, 0.0),
            ],
        )

        print(
            f"ball_y={ball['y']:.2f} "
            f"B0=({blue0['x']:.2f},{blue0['y']:.2f}) "
            f"target_y={target_y:.2f} "
            f"error_y={error_y:.3f} "
            f"cmd=({speed:.2f},{speed:.2f})"
        )

        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nDeteniendo robots")
finally:
    stop_all(command_sock)
    vision_sock.close()
    command_sock.close()
