# Roboberto--Proyecto-RAS-JUNIOR-1

Sistema completo para controlar un brazo robótico de tres servomotores usando **ROS 2**, una **ESP32** y un **mando Xbox 360**. El proyecto permite operar el brazo mediante teclado o joystick con control incremental por grados.

---

## Tabla de contenidos

1. [Instalación rápida](#instalación-rápida)
2. [Introducción](#introducción)
3. [Estructura del proyecto](#estructura-del-proyecto)
4. [Cómo ejecutarlo](#cómo-ejecutarlo)

   * [Modo teclado](#modo-teclado)
   * [Modo Xbox](#modo-xbox)
5. [Flujo del código](#flujo-del-código)
6. [Equipo](#equipo)
7. [Licencia](#licencia)

---

## Instalación rápida

**1. Clonar el repositorio:**

```bash
git clone https://github.com/usuario/robotic_arm_ras.git
cd robotic_arm_ras
```

**2. Instalar dependencias ROS 2:**

```bash
sudo apt install ros-jazzy-desktop ros-jazzy-joy
pip install pyserial
```

**3. Compilar el workspace:**

```bash
colcon build
source install/setup.bash
```

**4. Conectar la ESP32** al puerto `/dev/ttyUSB0` con el firmware correspondiente cargado.

---

## Introducción

Este proyecto implementa el control completo de un brazo robótico de 3 DOF mediante la integración de **ROS 2 Jazzy** y una **ESP32**. A través de nodos Python y comunicación serial, se controlan tres servomotores: base, hombro y codo.

El sistema incluye **dos modos de operación**:

* **Modo teclado** — control incremental por ángulos (±10°) usando las teclas `W A S D Q E`.
* **Modo Xbox** — control con mando Xbox 360 mapeando botones y gatillos a incrementos de ±10°.

**Tecnologías utilizadas:**

| Capa         | Tecnología                               |
| ------------ | ---------------------------------------- |
| Middleware   | ROS 2 Jazzy                              |
| Control      | Python 3 (`rclpy`, `pyserial`)           |
| Mensajes     | `geometry_msgs/Twist`, `sensor_msgs/Joy` |
| Hardware     | ESP32 + 3 servomotores                   |
| Comunicación | Serial USB (9600 baudios)                |

---

## Estructura del proyecto

```text
robotic_arm_ras/
├── connect.py               # Nodo puente ROS 2 a ESP32 (serial)
├── control_teclado.py       # Nodo controlador por teclado
├── servo_publisher.py       # Publicador de prueba (barrido 0°-180°)
└── xbox_control.py          # Nodo controlador por mando Xbox
```

### `connect.py` — Puente ROS 2 / ESP32

Nodo `node_connection` que se suscribe al tópico `/pub` y reenvía los ángulos de los 3 servos a la ESP32 por serial en el formato:

```text
servo1,servo2,servo3\n
```

Parámetros configurables:

| Parámetro  | Default        |
| ---------- | -------------- |
| `port`     | `/dev/ttyUSB0` |
| `baudrate` | `9600`         |

---

### `control_teclado.py` — Modo Teclado

Nodo `keyboard_controller` que captura teclas y publica incrementos en el tópico `/pub` como `geometry_msgs/Twist`.

| Tecla     | Acción            |
| --------- | ----------------- |
| `W` / `S` | Servo 1 ±10°      |
| `A` / `D` | Servo 2 ±10°      |
| `Q` / `E` | Servo 3 ±10°      |
| `SPACE`   | Reset todos a 90° |
| `ESC`     | Salir             |

Todos los ángulos se limitan al rango `[0°, 180°]` para proteger los motores.

---

### `xbox_control.py` — Modo Xbox

Nodo `xbox_to_servo_node` que lee mensajes del tópico `/joy` y controla los servos con el mando Xbox 360.

| Control             | Acción              |
| ------------------- | ------------------- |
| Botón `Y` / `A`     | Servo 1 +10° / -10° |
| Botón `B` / `X`     | Servo 2 +10° / -10° |
| Gatillo `RT` / `LT` | Servo 3 +10° / -10° |
| Cruceta ↑           | Reset todos a 90°   |

Usa una bandera `control_libre` para evitar saltos continuos mientras el botón está presionado.

---

### `servo_publisher.py` — Test Publisher

Nodo de prueba que publica un barrido automático de ángulos (`0° - 180°` en pasos de 30°) en el tópico `servo_cmd` cada segundo.

---

## Cómo ejecutarlo

### Modo teclado

Abre **dos terminales** y ejecuta:

```bash
# Terminal 1 — Puente serial con la ESP32
ros2 run robotic_arm_ras connect

# Terminal 2 — Control por teclado
ros2 run robotic_arm_ras control_teclado
```

### Modo Xbox

Conecta el mando Xbox y abre **tres terminales**:

```bash
# Terminal 1 — Puente serial con la ESP32
ros2 run robotic_arm_ras connect

# Terminal 2 — Driver del joystick
ros2 run joy joy_node

# Terminal 3 — Control Xbox
ros2 run robotic_arm_ras xbox_control
```

---

## Flujo del código

```text
[Teclado / Mando Xbox]
        │
        ▼
[Nodo ROS 2: control_teclado.py / xbox_control.py]
   Publica geometry_msgs/Twist en /pub
   con servo1=linear.x, servo2=linear.y,
       servo3=linear.z
        │
        ▼
[Nodo ROS 2: connect.py]
   Se suscribe a /pub
   Serializa → "s1,s2,s3\n"
   Envía por USB serial
        │
        ▼
[ESP32]
   Parsea la cadena
   Escribe ángulos en los servos
```

---

## Equipo

| Nombre                 | Programa               | Correo                                                                        |
| ---------------------- | ---------------------- | ----------------------------------------------------------------------------- |
| Dylan Felipe Granados  | Ingeniería Mecatrónica | [dylan-granados@javeriana.edu.co](mailto:dylan-granados@javeriana.edu.co)     |
| David Santiago Meneses | Ingeniería Mecatrónica | [Menesesdsantiago@javeriana.edu.co](mailto:Menesesdsantiago@javeriana.edu.co) |
| Sofia Vega Sanchez     | Ingeniería Mecatrónica | [sm_vega@javeriana.edu.co](mailto:sm_vega@javeriana.edu.co)                   |

---

## Licencia

Este proyecto se distribuye bajo los términos de la licencia especificada en el archivo `LICENSE` ubicado en la raíz del repositorio.
