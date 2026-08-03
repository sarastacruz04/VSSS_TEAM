#Modelo de Datos/Estado del Mundo 
#Define las clases inmutables Position(x, y) y WorldState(robot_pos, ball_pos) usando @dataclass(frozen=True). 
from dataclasses import dataclass

@dataclass(frozen=True)
class Position:
    x: float
    y: float

@dataclass(frozen=True)
class WorldState:
    robot_pos: Position
    ball_pos: Position