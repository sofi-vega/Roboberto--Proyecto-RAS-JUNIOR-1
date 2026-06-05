import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial


class ESP32Bridge(Node):
    def __init__(self):
        super().__init__('node_connection')

        # Parámetros del puerto serial
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 9600)

        port = self.get_parameter('port').value
        baudrate = self.get_parameter('baudrate').value

        self.get_logger().info(f'Conectando con ESP32 en {port} a {baudrate} baudios')

        # Conexión serial con la ESP32
        self.esp32 = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=0.1
        )

        # Suscriptor al tópico /pub
        self.subscription = self.create_subscription(
            Twist,
            '/pub',
            self.callback,
            10
        )

        self.get_logger().info('Nodo listo. Esperando mensajes en /pub')

    def callback(self, msg):
        # Leer datos del mensaje Twist
        servo_1 = msg.linear.x
        servo_2 = msg.linear.y
        servo_3 = msg.linear.z
        servo_4 = msg.angular.x

        self.get_logger().info(f'servo_1: {servo_1}')
        self.get_logger().info(f'servo_2: {servo_2}')
        self.get_logger().info(f'servo_3: {servo_3}')
        self.get_logger().info(f'servo_4: {servo_4}')

        # Mensaje que se manda a la ESP32 por serial
        message = f"{servo_1},{servo_2},{servo_3},{servo_4}\n"

        self.esp32.write(message.encode('utf-8'))


def main(args=None):
    rclpy.init(args=args)

    node = ESP32Bridge()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.esp32.close()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()