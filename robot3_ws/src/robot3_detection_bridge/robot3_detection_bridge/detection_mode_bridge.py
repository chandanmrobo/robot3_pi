#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class DetectionModeBridge(Node):
    """
    Separate minimal bridge:
      UI → /ui/detection_mode
      Robot2 ← /robot2/detection_mode
    """

    def __init__(self):
        super().__init__("detection_mode_bridge")

        self.get_logger().info("Detection Mode Bridge started")

        # Subscribe to UI mode (plant / bird)
        self.sub_ui_mode = self.create_subscription(
            String,
            "/ui/detection_mode",
            self.cb_ui_mode,
            10
        )

        # Publish to robot_2
        self.pub_robot2_mode = self.create_publisher(
            String,
            "/robot2/detection_mode",
            10
        )

    # -------------------------------------------------

    def cb_ui_mode(self, msg: String):
        mode = msg.data.strip()

        # Validate mode
        if mode not in ("plant", "bird"):
            self.get_logger().warn(f"Invalid detection mode received: {mode}")
            return

        # Log and forward
        self.get_logger().info(f"Forwarding mode to robot2: {mode}")

        out_msg = String()
        out_msg.data = mode
        self.pub_robot2_mode.publish(out_msg)

# -----------------------------------------------------

def main(args=None):
    rclpy.init(args=args)
    node = DetectionModeBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
