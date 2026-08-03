Semana1-tarea3
* protobuf empaqueta estructuras de datos complejas en binarios muy ligeros para que la comunicación entre el simulador y tu cerebro de Python ocurra sin retrasos (baja latencia).

Semana1-tarea4
* En la liga VSS, el estándar de comunicación se llama VSSProto, el cual utiliza Google Protocol Buffers para estructurar la información del partido. Imagina que el paquete de red es una carta sellada en un idioma cifrado; Protobuf es el diccionario oficial que nos permite abrir la carta y leer con precisión matemática:¿Exactamente en qué coordenada $(X, Y)$ está la pelota?¿Dónde está posicionado nuestro robot?¿Dónde están los robots del equipo contrario?Sin esta tarea, nuestro robot jugaría con los ojos vendados
* Crear una capa de abstracción en Python para que el software del robot no dependa directamente de cómo envía los datos Webots. Si el día de mañana la cámara de la cancha cambia su formato, solo modificamos el lector, pero nuestro código interno sigue recibiendo el mismo modelo de datos.

* En la arquitectura de Webots existen dos tipos de "cerebros" o entidades en código:Un controlador de Robot estándar: Es el cerebro del jugador. Solo tiene permiso para interactuar con sus propios sensores (cámaras, encoders) y actuadores (motores left_motor, right_motor). No puede ver el mundo desde arriba ni leer las coordenadas globales de la cancha.Un controlador de Supervisor: Es el equivalente al "árbitro" o al sistema de cámaras del estadio. Tiene privilegios de administrador para leer la posición absoluta $(X, Y, Z)$ de cualquier objeto en la simulación mediante funciones como getPosition() o getFromDef().

Semana1-tarea5/6
* Crear la estructura modular donde residirán las funciones de los 3 jugadores (Portero, Defensa y Atacante) y verificar que, por seguridad, si no hay órdenes activas, la estrategia devuelva Comando Cero (0.0, 0.0) para que ningún robot se mueva sin control.
