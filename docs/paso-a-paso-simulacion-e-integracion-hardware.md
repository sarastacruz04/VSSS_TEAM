# Paso a paso para simulacion completa e integracion con hardware

Repositorio estudiado:

```text
C:\Users\monic\OneDrive\Documents\ChatGPT\Robotica\Repositorio\VSSS_TEAM
```

## 0. Idea general del sistema

El proyecto no debe mezclar estrategia, simulacion y hardware en un solo archivo. La arquitectura correcta es por capas:

```text
Vision simulada o real
        |
        v
WorldState
        |
        v
Estrategia
        |
        v
Control diferencial
        |
        v
Transporte de comandos
        |--------------------|
        v                    v
Simulacion Webots       Robot fisico
```

La estrategia debe trabajar siempre con el mismo `WorldState`, sin importar si las posiciones vienen de Webots o de una camara real.

## 1. Que ya existe en el repositorio

### Documentacion del equipo

- `README.md`: define Python como lenguaje principal para la IA, Webots como simulador, uso de entorno virtual y fail-safe con comando cero.
- `README-week.md`: explica Protobuf, VSSProto, diferencia entre controlador Robot y Supervisor, y necesidad de una capa de abstraccion.

### Simulador

- `travesim-main/worlds/RobotDev.wbt`: mundo para probar un robot.
- `travesim-main/worlds/Match3v3.wbt`: mundo base para partido 3v3.
- `travesim-main/worlds/Match5v5.wbt`: mundo base para partido 5v5.

### Controladores

- `travesim-main/controllers/controller_wheels/controller_wheels.py`: prueba local de motores.
- `travesim-main/controllers/controller_other/model.py`: modelo inicial `Position` y `WorldState`.
- `travesim-main/controllers/controller_other/strategy.py`: esqueletos de roles: portero, defensa y atacante.
- `travesim-main/controllers/controller_other/decode_vision.py`: escucha UDP multicast, pero todavia no decodifica Protobuf real.
- `travesim-main/controllers/vss_robot_controller/vss_robot_controller.cpp`: controlador Webots que recibe velocidades por radio y las aplica a motores.
- `travesim-main/controllers/referee_controller/referee_controller.cpp`: supervisor que lee posiciones del mundo, publica vision y recibe comandos.

### Protobuf

Los mensajes estan en:

```text
travesim-main/controllers/referee_controller/adapters/proto/simulation/
```

Archivos importantes:

- `common.proto`: define `Ball`, `Robot`, `Field`, `Frame`.
- `packet.proto`: define `Environment`, que es el paquete de vision.
- `command.proto`: define `Command` y `Commands`, que son los comandos de ruedas.
- `replacement.proto`: define reposicionamiento de bola y robots.

## 2. Fase A - Preparar el entorno

### Paso A1: Instalar Webots

Instalar Webots en Windows desde la pagina oficial de Cyberbotics.

Despues verificar que abre normalmente.

### Paso A2: Abrir el proyecto

Carpeta base:

```powershell
cd "C:\Users\monic\OneDrive\Documents\ChatGPT\Robotica\Repositorio\VSSS_TEAM\travesim-main"
```

### Paso A3: Crear entorno Python del equipo

Desde la raiz del repo `VSSS_TEAM`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install protobuf
```

Mas adelante pueden agregar:

```powershell
pip freeze > requirements.txt
```

## 3. Fase B - Probar simulacion minima

### Paso B1: Abrir mundo de desarrollo

Abrir:

```text
travesim-main/worlds/RobotDev.wbt
```

Este mundo sirve para comprobar que Webots reconoce el robot, los motores y el controlador Python `controller_wheels`.

### Paso B2: Ejecutar Play

En Webots:

1. Abrir `RobotDev.wbt`.
2. Presionar Play.
3. Verificar que el robot avanza, gira y se detiene.

Segun `docs/wheel_signs.md`:

```text
left = 5.0,  right = 5.0   -> avanza
left = -5.0, right = -5.0  -> retrocede
left = -5.0, right = 5.0   -> gira izquierda
left = 5.0,  right = -5.0  -> gira derecha
```

### Paso B3: Validar fail-safe

Detener el controlador o pausar Webots.

El controlador debe enviar:

```text
left = 0.0
right = 0.0
```

Esto ya esta implementado en `controller_wheels.py` con `try/finally`.

## 4. Fase C - Preparar Match3v3

### Paso C1: Abrir mundo de partido

Abrir:

```text
travesim-main/worlds/Match3v3.wbt
```

### Paso C2: Corregir robot amarillo 0

En el archivo `Match3v3.wbt`, el primer robot amarillo aparece con:

```text
controller "controller_wheels"
```

Para una simulacion completa, ese robot debe usar el mismo controlador que los demas:

```text
controller "vss_robot_controller"
robotNumber 0
```

Motivo:

- `controller_wheels` solo ejecuta una secuencia fija de prueba.
- `vss_robot_controller` recibe comandos desde el supervisor/referee.

### Paso C3: Confirmar que todos los robots tengan identificador

Cada robot debe tener:

```text
teamName "yellow" o "blue"
robotNumber 0, 1 o 2
```

El supervisor los identifica como:

```text
YellowRobot0
YellowRobot1
YellowRobot2
BlueRobot0
BlueRobot1
BlueRobot2
VssBall
```

## 5. Fase D - Entender vision simulada

En Webots no se procesa imagen con OpenCV para la simulacion inicial.

TraveSim hace esto:

```text
Supervisor Webots
  -> lee posicion real de bola y robots
  -> arma Environment protobuf
  -> lo envia por UDP multicast
```

Canal de vision:

```text
IP: 224.0.0.1
Puerto: 10002
Mensaje: fira_message.sim_to_ref.Environment
```

El mensaje `Environment` contiene:

```text
step
frame.ball
frame.robots_yellow[]
frame.robots_blue[]
field
goals_blue
goals_yellow
```

Cada robot trae:

```text
robot_id
x
y
orientation
vx
vy
vorientation
```

La bola trae:

```text
x
y
z
vx
vy
vz
```

## 6. Fase E - Generar Protobuf para Python

El repo tiene los `.proto`, pero no tiene los archivos Python generados `*_pb2.py`.

### Paso E1: Instalar herramienta de compilacion Protobuf

En el entorno virtual:

```powershell
pip install grpcio-tools protobuf
```

### Paso E2: Generar archivos Python

Desde:

```powershell
cd "C:\Users\monic\OneDrive\Documents\ChatGPT\Robotica\Repositorio\VSSS_TEAM\travesim-main\controllers\referee_controller\adapters\proto\simulation"
```

Ejecutar:

```powershell
python -m grpc_tools.protoc -I. --python_out=..\..\..\..\..\..\generated_proto common.proto command.proto replacement.proto packet.proto
```

Si la carpeta no existe, crearla antes:

```powershell
mkdir ..\..\..\..\..\..\generated_proto
```

Resultado esperado:

```text
generated_proto/
  common_pb2.py
  command_pb2.py
  replacement_pb2.py
  packet_pb2.py
```

## 7. Fase F - Implementar cliente de vision real

El archivo actual `decode_vision.py` escucha paquetes, pero usa datos falsos. Hay que convertirlo en un cliente real.

### Paso F1: Crear `vision_client.py`

Ubicacion recomendada:

```text
travesim-main/controllers/controller_other/vision_client.py
```

Debe hacer:

1. Abrir socket UDP multicast.
2. Recibir bytes.
3. Decodificar `Environment`.
4. Convertirlo a `WorldState`.

Pseudocodigo:

```python
import socket
import struct
from generated_proto import packet_pb2

class VisionClient:
    def __init__(self, ip="224.0.0.1", port=10002):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(0.1)
        self.sock.bind(("", port))

        group = socket.inet_aton(ip)
        mreq = struct.pack("4sL", group, socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def receive(self):
        data, _ = self.sock.recvfrom(65535)
        env = packet_pb2.Environment()
        env.ParseFromString(data)
        return env
```

### Paso F2: Convertir `Environment` a `WorldState`

Actualizar `model.py` para soportar bola, equipos y orientacion.

Modelo recomendado:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class BallState:
    x: float
    y: float
    vx: float
    vy: float

@dataclass(frozen=True)
class RobotState:
    robot_id: int
    x: float
    y: float
    theta: float
    vx: float
    vy: float

@dataclass(frozen=True)
class WorldState:
    step: int
    ball: BallState
    yellow: list[RobotState]
    blue: list[RobotState]
```

Mapper:

```python
def env_to_world(env):
    ball = env.frame.ball

    return WorldState(
        step=env.step,
        ball=BallState(ball.x, ball.y, ball.vx, ball.vy),
        yellow=[
            RobotState(r.robot_id, r.x, r.y, r.orientation, r.vx, r.vy)
            for r in env.frame.robots_yellow
        ],
        blue=[
            RobotState(r.robot_id, r.x, r.y, r.orientation, r.vx, r.vy)
            for r in env.frame.robots_blue
        ],
    )
```

### Paso F3: Probar vision

Con Webots corriendo en Play:

```powershell
python travesim-main\controllers\controller_other\vision_client.py
```

Resultado esperado:

```text
step=123 ball=(0.02, -0.01) yellow0=(0.15, 0.00)
```

Si no llegan paquetes:

- Verificar que Webots este en Play.
- Verificar que el mundo tenga `VssReferee`.
- Verificar firewall de Windows.
- Verificar puerto `10002`.

## 8. Fase G - Enviar comandos a la simulacion

TraveSim recibe comandos por equipo:

```text
Yellow Team: 127.0.0.1:20012
Blue Team:   127.0.0.1:20013
```

El mensaje esperado es:

```text
Packet
  cmd
    robot_commands[]
      id
      yellowteam
      wheel_left
      wheel_right
```

### Paso G1: Crear sender de comandos

Ubicacion recomendada:

```text
travesim-main/controllers/controller_other/team_sender.py
```

Pseudocodigo:

```python
import socket
from generated_proto import packet_pb2

class TeamSender:
    def __init__(self, yellow=True):
        self.yellow = yellow
        self.port = 20012 if yellow else 20013
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, commands):
        packet = packet_pb2.Packet()

        for robot_id, left, right in commands:
            cmd = packet.cmd.robot_commands.add()
            cmd.id = robot_id
            cmd.yellowteam = self.yellow
            cmd.wheel_left = left
            cmd.wheel_right = right

        self.sock.sendto(packet.SerializeToString(), ("127.0.0.1", self.port))
```

### Paso G2: Probar comando fijo

Enviar al robot 0:

```python
sender.send([(0, 5.0, 5.0)])
```

Resultado esperado:

- Robot 0 avanza.

Luego probar:

```python
sender.send([(0, -5.0, 5.0)])
```

Resultado esperado:

- Robot 0 gira a la izquierda.

## 9. Fase H - Crear primer ciclo completo

El primer ciclo completo debe hacer esto:

```text
recibir vision
  -> construir WorldState
  -> calcular comando
  -> enviar comando
  -> repetir
```

Archivo recomendado:

```text
travesim-main/controllers/controller_other/main_team.py
```

Pseudocodigo:

```python
vision = VisionClient()
sender = TeamSender(yellow=True)

try:
    while True:
        world = vision.get_latest()

        if world is None:
            sender.send([(0, 0.0, 0.0), (1, 0.0, 0.0), (2, 0.0, 0.0)])
            continue

        commands = compute_strategy(world)
        sender.send(commands)

finally:
    sender.send([(0, 0.0, 0.0), (1, 0.0, 0.0), (2, 0.0, 0.0)])
```

## 10. Fase I - Estrategia inicial

No empiecen con estrategia compleja. Empiecen con un atacante que va al balon.

### Paso I1: Calcular angulo al balon

```python
import math

def normalize_angle(angle):
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle

def go_to_ball(robot, ball):
    dx = ball.x - robot.x
    dy = ball.y - robot.y

    target = math.atan2(dy, dx)
    error = normalize_angle(target - robot.theta)

    base = 4.0
    turn = 8.0 * error

    left = base - turn
    right = base + turn

    return clamp(left), clamp(right)
```

### Paso I2: Limitar velocidades

El controlador C++ limita internamente a `68 rad/s`, pero para pruebas usen valores pequenos:

```python
MAX_SPEED = 8.0

def clamp(v):
    return max(-MAX_SPEED, min(MAX_SPEED, v))
```

### Paso I3: Asignar roles

Primera version:

```text
robot 0 -> arquero
robot 1 -> defensa
robot 2 -> atacante
```

Comportamiento minimo:

- Arquero: moverse sobre una linea cerca del arco propio siguiendo `ball.y`.
- Defensa: ubicarse entre bola y arco propio.
- Atacante: ir al balon.

## 11. Fase J - Pruebas de simulacion

Orden de pruebas:

1. `RobotDev`: probar signos de ruedas.
2. `Match3v3`: comprobar que vision recibe paquetes.
3. `Match3v3`: mandar comando fijo a un robot.
4. `Match3v3`: mandar comando cero a los 3 robots.
5. `Match3v3`: atacante va al balon.
6. `Match3v3`: defensa mantiene posicion.
7. `Match3v3`: arquero sigue la bola en Y.
8. Probar perdida de vision.
9. Probar cambio de lado.
10. Probar velocidades bajas, medias y altas.

Cada prueba debe registrarse con:

```text
fecha
mundo usado
robot probado
resultado esperado
resultado observado
error
solucion
```

## 12. Fase K - Preparar integracion con hardware real

Cuando la simulacion funcione, no cambien la estrategia. Cambien solo la salida de comandos.

```text
SimulationSender -> manda Packet protobuf a 127.0.0.1:20012/20013
HardwareSender   -> manda JSON/Serial/Wi-Fi al microcontrolador
```

La estrategia debe devolver siempre:

```text
robot_id
left_wheel
right_wheel
```

## 13. Contrato con el equipo de hardware

Antes de conectar nada, acuerden este contrato.

### Comando desde software hacia robot

```json
{
  "robot_id": 0,
  "left_wheel": 0.35,
  "right_wheel": 0.35,
  "timestamp_ms": 123456,
  "command_id": 88
}
```

### Respuesta desde robot hacia software

```json
{
  "robot_id": 0,
  "connected": true,
  "battery_v": 7.4,
  "last_command_id": 88,
  "error": null
}
```

### Decisiones que deben cerrar con hardware

- Medio de comunicacion: Serial USB, Wi-Fi UDP, Bluetooth o ESP-NOW.
- Unidad de comando: rad/s, RPM, PWM o porcentaje.
- Rango permitido: por ejemplo `-1.0` a `1.0`, o `-255` a `255`.
- Frecuencia de envio: recomendado 20 Hz a 50 Hz.
- Timeout de seguridad: recomendado 300 ms a 500 ms.
- Que hace el robot si pierde comunicacion: detener motores.

## 14. Fase L - Vision real

En competencia real el flujo cambia:

```text
Camara superior
  -> calibracion
  -> deteccion de colores/tags
  -> coordenadas en metros
  -> WorldState
```

Pero la estrategia no cambia.

Para la vision real necesitaran:

- Camara cenital a mas de 2 m.
- Calibracion de perspectiva.
- Deteccion de bola naranja.
- Deteccion de color de equipo: amarillo o azul.
- Deteccion de color individual del robot.
- Calculo de orientacion `theta`.
- Filtro para ruido y perdida temporal.

## 15. Orden final de construccion

Este es el orden recomendado para avanzar sin enredarse:

1. Probar `RobotDev.wbt` con `controller_wheels.py`.
2. Probar `Match3v3.wbt`.
3. Cambiar robot amarillo 0 a `vss_robot_controller`.
4. Generar `*_pb2.py` desde los `.proto`.
5. Implementar `VisionClient`.
6. Imprimir bola y robots desde vision real de TraveSim.
7. Implementar `TeamSender`.
8. Enviar comando fijo a un robot.
9. Crear `main_team.py`.
10. Conectar vision, estrategia y sender.
11. Implementar atacante `go_to_ball`.
12. Agregar defensa y arquero.
13. Agregar fail-safe si no hay vision.
14. Agregar limites de velocidad y aceleracion.
15. Registrar pruebas.
16. Cambiar `SimulationSender` por `HardwareSender`.
17. Probar hardware sin bola: stop, avanzar, girar, detener.
18. Probar hardware con vision real.
19. Calibrar diferencias entre simulacion y realidad.
20. Hacer prueba completa de partido.

## 16. Reparto para 3 integrantes de software

### Integrante 1 - Vision y estado del mundo

- Generar Protobuf Python.
- Implementar `VisionClient`.
- Convertir `Environment` a `WorldState`.
- Manejar perdida de vision.

### Integrante 2 - Estrategia y control

- Implementar `go_to_ball`.
- Implementar arquero.
- Implementar defensa.
- Limitar velocidades.
- Evitar faltas de area segun reglamento.

### Integrante 3 - Comunicacion e integracion

- Implementar `TeamSender`.
- Implementar `SimulationSender`.
- Definir contrato con hardware.
- Implementar `HardwareSender`.
- Crear pruebas y bitacora.

## 17. Resultado esperado

Al terminar la simulacion completa deben poder decir:

```text
Webots publica vision.
Nuestro Python lee Environment protobuf.
Nuestro Python construye WorldState.
La estrategia calcula ruedas.
Nuestro Python envia Packet protobuf al puerto del equipo.
Los robots se mueven en Match3v3.
Si se pierde vision o se detiene el programa, los robots paran.
```

Al terminar la integracion real deben poder decir:

```text
La camara real llena el mismo WorldState.
La estrategia es la misma que en simulacion.
El sender de hardware convierte ruedas a comandos del microcontrolador.
El robot fisico se detiene si pierde comunicacion.
El comportamiento real fue calibrado contra la simulacion.
```

