#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class DetectionBridge(Node):
    def __init__(self):
        super().__init__("robot3_detection_bridge")

        self.get_logger().info("Robot3 Detection Bridge Started")

        # ------------------------------------------------------
        # SUBSCRIBE to Robot 2 detection topics
        # (replace topic names with your actual Robot2 topics)
        # ------------------------------------------------------
        self.sub_plant = self.create_subscription(
            String,
            "/robot2/plant_disease",
            self.cb_plant,
            10
        )

        self.sub_bird = self.create_subscription(
            String,
            "/robot2/bird_status",
            self.cb_bird,
            10
        )

        # ------------------------------------------------------
        # PUBLISH to UI server (ui_server.py listens here)
        # ------------------------------------------------------
        self.pub_ui_plant = self.create_publisher(
            String,
            "/ui/plant_detection",
            10
        )

        self.pub_ui_bird = self.create_publisher(
            String,
            "/ui/bird_detection",
            10
        )

    # ----------------------------------------------------------
    # ROBOT 2 → ROBOT 3 CALLBACKS
    # ----------------------------------------------------------
    def cb_plant(self, msg: String):
        """Forward plant disease result to UI server."""
        out = String()
        out.data = msg.data
        self.pub_ui_plant.publish(out)

        self.get_logger().info(f"Forwarded PLANT detection: {msg.data}")

    def cb_bird(self, msg: String):
        """Forward bird/crow detection result to UI server."""
        out = String()
        out.data = msg.data
        self.pub_ui_bird.publish(out)

        self.get_logger().info(f"Forwarded BIRD detection: {msg.data}")


def main(args=None):
    rclpy.init(args=args)
    node = DetectionBridge()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
