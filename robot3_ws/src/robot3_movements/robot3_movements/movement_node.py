import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from robot3_movements.movement_utils import get_command


class MovementNode(Node):
    def __init__(self):
        super().__init__("robot3_movement_node")

        # Publishers for robot1 and robot2
        self.pub_r1 = self.create_publisher(String, "/robot1/move_cmd", 10)
        self.pub_r2 = self.create_publisher(String, "/robot2/move_cmd", 10)

        # Subscription from UI (robot1 + robot2)
        self.sub_ui = self.create_subscription(
            String,
            "/ui/move_cmd",
            self.ui_callback,
            10
        )

        self.get_logger().info("MovementNode started — listening to /ui/move_cmd")

    # --------------------------------------------------------------
    # Receive UI command → publish to robot topics
    # --------------------------------------------------------------
    def ui_callback(self, msg: String):

        """
        Expected UI command format:
            "r1_up" / "r1_left" / "r1_stop"
            "r2_down" / "r2_right" / "r2_stop"
        """

        data = msg.data.strip()

        # Robot 1 command
        if data.startswith("r1_"):
            action = data.replace("r1_", "")
            cmd = get_command(action)

            out = String()
            out.data = cmd
            self.pub_r1.publish(out)

            self.get_logger().info(f"Robot1 → {cmd}")

        # Robot 2 command
        elif data.startswith("r2_"):
            action = data.replace("r2_", "")
            cmd = get_command(action)

            out = String()
            out.data = cmd
            self.pub_r2.publish(out)

            self.get_logger().info(f"Robot2 → {cmd}")


def main():
    rclpy.init()
    node = MovementNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
