import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


class ServoPublisher(Node):
    def __init__(self):
        super().__init__('servo_publisher')

        self.publisher = self.create_publisher(
            Int32,
            'servo_cmd',
            10
        )

        self.angle = 0
        self.timer = self.create_timer(1.0, self.publish_angle)

    def publish_angle(self):
        msg = Int32()
        msg.data = self.angle

        self.publisher.publish(msg)
        self.get_logger().info(f'Publicando angulo: {self.angle}')

        self.angle += 30

        if self.angle > 180:
            self.angle = 0


def main(args=None):
    rclpy.init(args=args)

    node = ServoPublisher()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()