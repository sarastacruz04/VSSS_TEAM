from controller import Robot
import struct
import sys


MAX_ROBOTS = 5
MAX_SPEED = 68.0
MESSAGE_FORMAT = "<I" + ("d" * MAX_ROBOTS) + ("d" * MAX_ROBOTS)
MESSAGE_SIZE = struct.calcsize(MESSAGE_FORMAT)


def clip(value):
    return max(-MAX_SPEED, min(MAX_SPEED, value))


def read_args():
    team_name = sys.argv[1].lower() if len(sys.argv) > 1 else "yellow"
    robot_number = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    return team_name, robot_number


team_name, robot_number = read_args()

robot = Robot()
timestep = int(robot.getBasicTimeStep())

receiver = robot.getDevice("robot_receiver")
if receiver is None:
    raise RuntimeError("No se encontro el receiver 'robot_receiver'")

receiver.setChannel(0 if team_name == "yellow" else 1)
receiver.enable(timestep)

left_motor = robot.getDevice("left_motor")
right_motor = robot.getDevice("right_motor")

left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

print(f"--- vss_robot_controller.py iniciado: {team_name} robot {robot_number} ---")

try:
    while robot.step(timestep) != -1:
        while receiver.getQueueLength() > 0:
            data = receiver.getBytes()
            receiver.nextPacket()

            if len(data) < MESSAGE_SIZE:
                continue

            unpacked = struct.unpack(MESSAGE_FORMAT, data[:MESSAGE_SIZE])
            left_speeds = unpacked[1:1 + MAX_ROBOTS]
            right_speeds = unpacked[1 + MAX_ROBOTS:1 + 2 * MAX_ROBOTS]

            left_motor.setVelocity(clip(left_speeds[robot_number]))
            right_motor.setVelocity(clip(right_speeds[robot_number]))
finally:
    left_motor.setVelocity(0.0)
    right_motor.setVelocity(0.0)
    print("--- comando cero aplicado en vss_robot_controller.py ---")
