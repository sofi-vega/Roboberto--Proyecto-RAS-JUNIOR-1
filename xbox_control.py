import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy

class XboxController(Node):
    def __init__(self):
        super().__init__('xbox_to_servo_node')
        
        self.joy_subscription = self.create_subscription(
            Joy,
            '/joy',
            self.joy_callback,
            10
        )
        
        self.publisher = self.create_publisher(Twist, '/pub', 10)
        
        # Posición inicial / original de los servos
        self.servo1 = 90.0
        self.servo2 = 90.0
        self.servo3 = 90.0
        self.servo4 = 90.0
        
        self.incremento = 10.0
        
        # Bandera de seguridad para evitar saltos infinitos
        self.control_libre = True

        self.get_logger().info('=============================================')
        self.get_logger().info('  ROBOBERTO - Xbox Full Control (10°)        ')
        self.get_logger().info('=============================================')
        self.get_logger().info('  Botón Y / Botón A     → Servo 1 (±10°)')
        self.get_logger().info('  Botón B / Botón X     → Servo 2 (±10°)')
        self.get_logger().info('  Gatillo RT / LT       → Servo 3 (±10°)')
        self.get_logger().info('  Cruceta ARRIBA        → RESET A 90°    ')
        self.get_logger().info('=============================================')

    def joy_callback(self, msg):
        # --- Lectura de Botones ---
        btn_a = msg.buttons[0]
        btn_b = msg.buttons[1]
        btn_x = msg.buttons[2]
        btn_y = msg.buttons[3]

        # --- Lectura de Gatillos ---
        gatillo_lt = 1 if msg.axes[2] < -0.5 else 0
        gatillo_rt = 1 if msg.axes[5] < -0.5 else 0

        # --- Lectura de la Cruceta (D-pad) ---
        # axes[7] es el eje vertical de la cruceta. 1.0 significa hacia arriba.
        cruceta_arriba = 1 if msg.axes[7] > 0.5 else 0

        # Verificamos si soltaste todos los botones, gatillos y la cruceta
        ningun_boton = (btn_a == 0 and btn_b == 0 and btn_x == 0 and btn_y == 0)
        ningun_gatillo = (gatillo_lt == 0 and gatillo_rt == 0)
        ninguna_cruceta = (cruceta_arriba == 0)

        if ningun_boton and ningun_gatillo and ninguna_cruceta:
            self.control_libre = True
            return

        # Si el sistema está libre para procesar un comando
        if self.control_libre:
            hubo_cambio = False

            # --- FUNCIÓN RESET (Cruceta Arriba) ---
            if cruceta_arriba == 1:
                self.servo1 = 90.0
                self.servo2 = 90.0
                self.servo3 = 90.0
                self.servo4 = 90.0
                self.control_libre = False
                self.enviar_comando()
                self.get_logger().info('¡Posición Original Restaurada (90°)!')
                return

            # --- SERVO 1 (Botones Y / A) ---
            if btn_y == 1:
                self.servo1 += self.incremento
                hubo_cambio = True
            elif btn_a == 1:
                self.servo1 -= self.incremento
                hubo_cambio = True

            # --- SERVO 2 (Botones B / X) ---
            if btn_b == 1:
                self.servo2 += self.incremento
                hubo_cambio = True
            elif btn_x == 1:
                self.servo2 -= self.incremento
                hubo_cambio = True

            # --- SERVO 3 (Gatillos RT / LT) ---
            if gatillo_rt == 1:
                self.servo3 += self.incremento
                hubo_cambio = True
            elif gatillo_lt == 1:
                self.servo3 -= self.incremento
                hubo_cambio = True

            if hubo_cambio:
                self.control_libre = False 
                
                # Mantener los límites de seguridad física de los motores (0 a 180)
                self.servo1 = max(0.0, min(180.0, self.servo1))
                self.servo2 = max(0.0, min(180.0, self.servo2))
                self.servo3 = max(0.0, min(180.0, self.servo3))
                
                self.enviar_comando()

    def enviar_comando(self):
        msg = Twist()
        msg.linear.x  = float(self.servo1)
        msg.linear.y  = float(self.servo2)
        msg.linear.z  = float(self.servo3)
        msg.angular.x = float(self.servo4)
        
        self.publisher.publish(msg)
        self.get_logger().info(
            f"Ángulos → [S1: {self.servo1:.1f}° | S2: {self.servo2:.1f}° | S3: {self.servo3:.1f}° | S4: {self.servo4:.1f}°]"
        )

def main(args=None):
    rclpy.init(args=args)
    node = XboxController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
