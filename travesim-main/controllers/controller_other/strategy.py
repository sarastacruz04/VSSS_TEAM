# Controlador de estrategia del robot Travesim
#Contiene los esqueletos de los 3 roles del partido (role_keeper, role_defender, role_attacker). Retornan las velocidades para cada rueda.
from model import WorldState

# Punto 6 de la guía: Funciones de rol que devuelven velocidades (v_izq, v_der)

def role_keeper(state: WorldState) -> tuple[float, float]:
    """Lógica inicial del Portero. Retorna (v_izq, v_der)"""
    # Por seguridad, inicia en Comando Cero
    return (0.0, 0.0)

def role_defender(state: WorldState) -> tuple[float, float]:
    """Lógica inicial del Defensa. Retorna (v_izq, v_der)"""
    return (0.0, 0.0)

def role_attacker(state: WorldState) -> tuple[float, float]:
    """Lógica inicial del Atacante. Retorna (v_izq, v_der)"""
    return (0.0, 0.0)

def compute_strategy(state: WorldState) -> dict:
    """
    Calcula los comandos para todo el equipo.
    Garantiza que la salida sea un mapa estructurado de velocidades.
    """
    return {
        "robot_0": role_keeper(state),
        "robot_1": role_defender(state),
        "robot_2": role_attacker(state)
    }