from controller import Supervisor
import json
import math
import socket
import struct
import sys


MAX_ROBOTS = 5
MESSAGE_FORMAT = "<I" + ("d" * MAX_ROBOTS) + ("d" * MAX_ROBOTS)


def parse_args():
    args = sys.argv[1:]
    return {
        "robots_per_team": int(args[0]) if len(args) > 0 else 3,
        "yellow_port": int(args[4]) if len(args) > 4 else 20012,
        "blue_port": int(args[6]) if len(args) > 6 else 20013,
        "vision_address": args[7] if len(args) > 7 else "224.0.0.1",
        "vision_port": int(args[8]) if len(args) > 8 else 10002,
    }


def yaw_from_orientation(orientation):
    # Webots returns a 3x3 orientation matrix. For planar robots, yaw is the
    # angle of the robot local X axis projected on the field XY plane.
    return math.atan2(orientation[3], orientation[0])


def node_state(node, robot_id=None):
    position = node.getPosition()
    velocity = node.getVelocity()
    state = {
        "x": position[0],
        "y": position[1],
        "z": position[2],
        "vx": velocity[0],
        "vy": velocity[1],
        "vz": velocity[2],
    }

    if robot_id is not None:
        state["robot_id"] = robot_id
        state["orientation"] = yaw_from_orientation(node.getOrientation())

    return state


def find_node_by_name(supervisor, name):
    children = supervisor.getRoot().getField("children")

    for index in range(children.getCount()):
        node = children.getMFNode(index)
        name_field = node.getField("name")

        if name_field is not None and name_field.getSFString() == name:
            return node

    return None


def command_bytes(frame, commands):
    left = [0.0] * MAX_ROBOTS
    right = [0.0] * MAX_ROBOTS

    for robot_id, speeds in commands.items():
        if 0 <= robot_id < MAX_ROBOTS:
            left[robot_id] = speeds[0]
            right[robot_id] = speeds[1]

    return struct.pack(MESSAGE_FORMAT, frame, *left, *right)


def read_udp_commands(sock):
    commands = {}

    while True:
        try:
            data, _ = sock.recvfrom(65535)
        except BlockingIOError:
            break

        try:
            payload = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue

        for item in payload.get("commands", []):
            robot_id = int(item.get("robot_id", 0))
            left = float(item.get("left_wheel", 0.0))
            right = float(item.get("right_wheel", 0.0))
            commands[robot_id] = (left, right)

    return commands


config = parse_args()
supervisor = Supervisor()
timestep = int(supervisor.getBasicTimeStep())

yellow_emitter = supervisor.getDevice("yellow_team")
blue_emitter = supervisor.getDevice("blue_team")
yellow_emitter.setChannel(0)
blue_emitter.setChannel(1)

yellow_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
yellow_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
yellow_socket.bind(("127.0.0.1", config["yellow_port"]))
yellow_socket.setblocking(False)

blue_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
blue_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
blue_socket.bind(("127.0.0.1", config["blue_port"]))
blue_socket.setblocking(False)

vision_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ball = find_node_by_name(supervisor, "VssBall")
yellow_robots = [
    find_node_by_name(supervisor, f"YellowRobot{i}") for i in range(config["robots_per_team"])
]
blue_robots = [
    find_node_by_name(supervisor, f"BlueRobot{i}") for i in range(config["robots_per_team"])
]

if ball is None:
    raise RuntimeError("No se encontro el nodo VssBall")

if any(node is None for node in yellow_robots + blue_robots):
    raise RuntimeError("No se encontraron todos los robots por DEF/name")

frame = 0
last_yellow_commands = {}
last_blue_commands = {}

print("--- referee_controller.py iniciado ---")
print(f"Vision JSON: 127.0.0.1:{config['vision_port']}")
print(f"Yellow commands JSON: 127.0.0.1:{config['yellow_port']}")
print(f"Blue commands JSON: 127.0.0.1:{config['blue_port']}")

while supervisor.step(timestep) != -1:
    frame += 1

    new_yellow = read_udp_commands(yellow_socket)
    new_blue = read_udp_commands(blue_socket)

    if new_yellow:
        last_yellow_commands.update(new_yellow)
    if new_blue:
        last_blue_commands.update(new_blue)

    yellow_emitter.send(command_bytes(frame, last_yellow_commands))
    blue_emitter.send(command_bytes(frame, last_blue_commands))

    env = {
        "step": frame,
        "frame": {
            "ball": node_state(ball),
            "robots_yellow": [
                node_state(node, i) for i, node in enumerate(yellow_robots)
            ],
            "robots_blue": [
                node_state(node, i) for i, node in enumerate(blue_robots)
            ],
        },
        "field": {
            "width": 1.3,
            "length": 1.5,
            "goal_width": 0.4,
            "goal_depth": 0.1,
        },
    }

    vision_payload = json.dumps(env).encode("utf-8")

    vision_socket.sendto(
        vision_payload,
        ("127.0.0.1", config["vision_port"]),
    )
