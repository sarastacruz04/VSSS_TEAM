#Controlador fisico de actuadores de ruedas del robot Travesim
#Conecta con la API de Webots para inicializar los motores (left_motor y right_motor). Controla el tiempo de paso (timestep) y aplica la secuencia automática de prueba con protección contra fallos.
from controller import Robot
import time

# 1. Inicializamos como un Robot estándar (sin violar permisos de Webots)
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# 2. Conectamos con los motores
motor_izquierdo = robot.getDevice('left_motor')
motor_derecho = robot.getDevice('right_motor')

# Configuramos posición infinita para control por velocidad
motor_izquierdo.setPosition(float('inf'))
motor_derecho.setPosition(float('inf'))

print("--- CONTROLADOR DE MOTORES INICIADO ---")

tiempo_inicio = time.time()

# Punto 10 de la guía: Estructura try / finally para Comando Cero
try:
    while robot.step(timestep) != -1:
        transcurrido = time.time() - tiempo_inicio

        # Punto 9 de la guía: Secuencia de movimiento automática
        if transcurrido < 3.0:
            # 1. Avanzar (primeros 3 segundos)
            motor_izquierdo.setVelocity(5.0)
            motor_derecho.setVelocity(5.0)
        elif transcurrido < 6.0:
            # 2. Girar sobre su propio eje (siguientes 3 segundos)
            motor_izquierdo.setVelocity(-5.0)
            motor_derecho.setVelocity(5.0)
        else:
            # 3. Detenerse
            motor_izquierdo.setVelocity(0.0)
            motor_derecho.setVelocity(0.0)

finally:
    # Punto 6 y 10: Comando Cero garantizado (apaga motores si el script se detiene)
    motor_izquierdo.setVelocity(0.0)
    motor_derecho.setVelocity(0.0)
    print("--- COMANDO CERO APLICADO: MOTORES APAGADOS DE FORMA SEGURA ---")