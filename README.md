Software Equipo VSSS - []
Entorno de trabajo:
Versión de Python: [Ej: 3.11.4]

Simulador: Webots

Dependencias manejadas en entorno virtual (.venv)

Comandos útiles:
Para activar el entorno en Windows: .\.venv\Scripts\Activate.ps1

Para instalar dependencias si cambiamos de PC: pip install -r requirements.txt

¿Por qué hacemos la IA en Python y no en C++?
Python nos permite procesar matrices de datos, tomar decisiones lógicas y ajustar la estrategia en milisegundos sin perder tiempo en compilaciones complejas. La regla de oro del proyecto es: El computador Host (donde corre la IA) usa 100% Python. C++ se reserva únicamente para el microcontrolador físico (ESP32/STM32) en la fase final de hardware.

Cinemática Diferencial y Bitácora de Signos
Nuestros robots utilizan tracción diferencial (dos ruedas independientes). Para controlar su movimiento no enviamos órdenes complejas como "avanzar a 2 m/s", sino velocidades angulares individuales a la rueda izquierda ($v_{izq}$) y derecha ($v_{der}$):
Avanzar: $v_{izq} > 0$ y $v_{der} > 0$ (ambas ruedas giran en el mismo sentido hacia adelante).
Retroceder: $v_{izq} < 0$ y $v_{der} < 0$.
Rotación sobre su propio eje: $v_{izq}$ y $v_{der}$ con igual magnitud pero signos opuestos (ej. $-5.0$ y $+5.0$).

Fail-safe: Comando Cero y la Cláusula try / finally
En robótica autónoma, si el código de la PC sufre un colapso (crash), los motores pueden quedarse girando a la última velocidad recibida, haciendo que el robot choque violentamente.Lógica implementada: Envolvimos el bucle principal en un bloque try / finally. Sin importar cómo muera el script (cancelación con Ctrl+C, error de código o pausa en el simulador), Python garantiza la ejecución del bloque finally, enviando automáticamente las velocidades $(0.0, 0.0)$ a los motores.

Desacoplamiento Arquitectónico (Patrón de Capas)
En lugar de que la estrategia envíe órdenes directamente a las ruedas, creamos el modelo WorldState. Si en el futuro cambiamos la cámara física de la cancha o el simulador Webots, el código de la estrategia en strategy.py no cambiará en absoluto. Solo cambiará la capa de red que llena la clase WorldState.


Socket-UDP
* Si UDP es el "método de envío" (el megáfono), un Socket es el mecanismo en código que te permite abrir la oreja o la puerta para escuchar.
* UDP: Es un protocolo de comunicación ultrarrápido sin confirmación ("Envía y olvida"), ideal para sistemas en tiempo real como robótica o streaming.
Puerto: Es el número de canal por el que viaja un tipo específico de datos (ej. puerto 10002 para las posiciones de la cancha).
Socket UDP: Es la herramienta de código en Python que abre la puerta de ese puerto para enviar o recibir esos paquetes de datos veloces.


DESAFIOS Y SOLUCIONES
Incompatibilidad de permisos Supervisor vs Robot (Error: ignoring illegal call...)	
-> Se intentó llamar a getPosition() desde un nodo Robot estándar. Webots prohíbe a un jugador actuar como administrador del mundo.	
-> Reestructuramos el código: mantuvimos a controller_wheels.py como un Robot puro y pasamos la lectura de posición al módulo de red/visión independiente.

Bloqueo de compilación C++ en Windows (WARNING: Starts <generic> controller)
-> El simulador exigía compilar controladores C++ con la herramienta Linux make, inexistente nativamente en Windows PowerShell.	
-> Aplicamos el dictamen Python-First: evitamos compilar C++ en el Host y abrimos sockets UDP puros en Python sin depender de binarios externos.

Terminal congelada en escucha de red (Socket bloqueante en recvfrom)
-> La función sock.recvfrom() pausaba todo el programa indefinidamente hasta recibir un paquete UDP de la red.	
-> Añadimos un tiempo límite de espera mediante sock.settimeout(1.0). Esto volvió al socket no-bloqueante, permitiendo imprimir la telemetría periódicamente.



  
