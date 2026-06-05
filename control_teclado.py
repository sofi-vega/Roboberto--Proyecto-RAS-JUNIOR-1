import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import tty
import termios

# Mapeo de teclas modificado: (Servo1, Servo2, Servo3, Servo4)
# Indica el incremento o decremento en grados por cada pulsación
KEYMAP = {
    'w': ( 10.0,   0.0,   0.0,   0.0),   # Servo 1 +
    's': (-10.0,   0.0,   0.0,   0.0),   # Servo 1 -
    'a': (  0.0, -10.0,   0.0,   0.0),   # Servo 2 -
    'd': (  0.0,  10.0,   0.0,   0.0),   # Servo 2 +
    'q': (  0.0,   0.0, -10.0,   0.0),   # Servo 3 -
    'e': (  0.0,   0.0,  10.0,   0.0),   # Servo 3 +
    'z': (  0.0,   0.0,   0.0, -10.0),   # Servo 4 -
    'c': (  0.0,   0.0,   0.0,  10.0),   # Servo 4 +
}

def get_key():
    """Lee una tecla sin necesidad de presionar Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key

class KeyboardController(Node):
    def __init__(self):
        super().__init__('keyboard_controller')
        self.publisher = self.create_publisher(Twist, '/pub', 10)
        
        # Posición inicial de los 4 servos (Centro)
        self.servo1 = 90.0
        self.servo2 = 90.0
        self.servo3 = 90.0
        self.servo4 = 90.0
        
        self.get_logger().info('Nodo de teclado listo.')
        self.print_help()

    def print_help(self):
        print("""
=============================================
  ROBOBERTO - Control Teclado (Modo Grados)
=============================================
  W/S   → Servo 1  (±10°)
  A/D   → Servo 2  (±10°)
  Q/E   → Servo 3  (±10°)
  Z/C   → Servo 4  (±10°)
  SPACE → Reiniciar todo a 90°
  ESC   → Salir
=============================================
        """)

    def run(self):
        while rclpy.ok():
            key = get_key()

            if key == '\x1b':  # ESC para salir
                self.get_logger().info('Saliendo...')
                break

            # Si se presiona espacio, se restablecen los valores centrales
            if key == ' ':
                self.servo1 = 90.0
                self.servo2 = 90.0
                self.servo3 = 90.0
                self.servo4 = 90.0
                self.publicar_angulos(key)
                continue

            if key in KEYMAP:
                inc_s1, inc_s2, inc_s3, inc_s4 = KEYMAP[key]
                
                # Aplicamos los incrementos acumulativos
                self.servo1 += inc_s1
                self.servo2 += inc_s2
                self.servo3 += inc_s3
                self.servo4 += inc_s4

                # Limitamos los valores entre 0.0 y 180.0 para proteger los motores
                self.servo1 = max(0.0, min(180.0, self.servo1))
                self.servo2 = max(0.0, min(180.0, self.servo2))
                self.servo3 = max(0.0, min(180.0, self.servo3))
                self.servo4 = max(0.0, min(180.0, self.servo4))

                self.publicar_angulos(key)

    def publicar_angulos(self, key):
        """Construye el mensaje Twist y lo publica."""
        msg = Twist()
        msg.linear.x  = float(self.servo1)
        msg.linear.y  = float(self.servo2)
        msg.linear.z  = float(self.servo3)
        msg.angular.x = float(self.servo4)

        self.publisher.publish(msg)
        
        display_key = 'SPACE' if key == ' ' else key
        self.get_logger().info(
            f"Tecla '{display_key}' → [{self.servo1:.1f}°, {self.servo2:.1f}°, {self.servo3:.1f}°, {self.servo4:.1f}°]"
        )

def main(args=None):
    rclpy.init(args=args)
    node = KeyboardController()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
