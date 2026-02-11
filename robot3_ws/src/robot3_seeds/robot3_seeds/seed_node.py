# robot3_seeds/seed_node.py

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
import json
from datetime import datetime


def get_timestamp():
    """Return current time in HH:MM:SS format"""
    return datetime.now().strftime("%H:%M:%S")


class SeedNode(Node):
    def __init__(self):
        super().__init__("robot3_seed_node")

        # ---------------------------------------------------------
        # INTERNAL COUNTERS
        # ---------------------------------------------------------
        self.total_seed_count = 0

        # AUTO MODE - starts disabled
        self.is_auto_enabled = False
        self.seed_gap_sec = 5  # default (React default 5 cm → 5 sec)
        self.auto_timer = None

        # ---------------------------------------------------------
        # SUBSCRIPTIONS
        # ---------------------------------------------------------

        # Manual Seed Commands from UI
        self.sub_ui = self.create_subscription(
            String, "/ui/seed_cmd", self.ui_callback, 10
        )

        # React Settings – seed gap update
        self.sub_gap = self.create_subscription(
            String, "/ui/settings_seed_gap", self.cb_update_gap, 10
        )

        # ---------------------------------------------------------
        # PUBLISHERS
        # ---------------------------------------------------------

        # Hardware seed command to ESP32
        self.pub_seed = self.create_publisher(
            String, "/robot1/seed_cmd", 10
        )

        # Dashboard event publisher
        self.pub_dashboard = self.create_publisher(
            String, "/dashboard/seed_event", 10
        )

        self.get_logger().info(
            f"[{get_timestamp()}] SeedNode started – auto disabled, default gap = {self.seed_gap_sec}s"
        )

    # ---------------------------------------------------------
    # UPDATE SEED GAP (AUTO DISPENSE INTERVAL)
    # ---------------------------------------------------------
    def cb_update_gap(self, msg: String):
        try:
            new_gap = int(msg.data)
            if new_gap <= 0:
                raise ValueError
        except:
            self.get_logger().warn(f"[{get_timestamp()}] Invalid seed gap received: {msg.data}")
            return

        self.seed_gap_sec = new_gap
        self.get_logger().info(f"[{get_timestamp()}] Updated AUTO seed gap to {self.seed_gap_sec} sec")

        # Reset auto timer ONLY if auto mode is currently running
        if self.is_auto_enabled and self.auto_timer:
            self.auto_timer.cancel()
            self.auto_timer = self.create_timer(self.seed_gap_sec, self.auto_dispense)

    # ---------------------------------------------------------
    # UI → SEED COMMAND HANDLER (manual + mode switching)
    # ---------------------------------------------------------
    def ui_callback(self, msg: String):
        action = msg.data.strip()

        # -----------------------------------------------------
        # HANDLE MODE SWITCHING
        # -----------------------------------------------------
        if action == "seed_mode_auto":
            self.enable_auto_mode()
            return

        if action == "seed_mode_manual":
            self.disable_auto_mode()
            return

        # -----------------------------------------------------
        # HANDLE MANUAL DISPENSE (works independent of settings)
        # -----------------------------------------------------
        if action == "seed_dispense_once":
            self.do_dispense(manual=True)
            return

        # -----------------------------------------------------
        # FORWARD OTHER COMMANDS
        # -----------------------------------------------------
        out = String()
        out.data = action
        self.pub_seed.publish(out)

        self.get_logger().info(f"[{get_timestamp()}] SeedNode: UI action '{action}' forwarded")

    # ---------------------------------------------------------
    # AUTO MODE ENABLE / DISABLE
    # ---------------------------------------------------------
    def enable_auto_mode(self):
        if self.is_auto_enabled:
            return  # Already enabled
            
        self.is_auto_enabled = True
        self.get_logger().info(f"[{get_timestamp()}] SeedNode: AUTO mode ENABLED")

        # Cancel any existing timer
        if self.auto_timer:
            self.auto_timer.cancel()

        # Start new auto timer
        self.auto_timer = self.create_timer(self.seed_gap_sec, self.auto_dispense)

    def disable_auto_mode(self):
        if not self.is_auto_enabled:
            return  # Already disabled
            
        self.is_auto_enabled = False
        self.get_logger().info(f"[{get_timestamp()}] SeedNode: AUTO mode DISABLED")

        # Stop auto timer
        if self.auto_timer:
            self.auto_timer.cancel()
            self.auto_timer = None

    # ---------------------------------------------------------
    # AUTO DISPENSE CALLBACK (only runs when auto enabled)
    # ---------------------------------------------------------
    def auto_dispense(self):
        if not self.is_auto_enabled:
            return

        self.do_dispense(manual=False)

    # ---------------------------------------------------------
    # DO DISPENSE (manual or auto)
    # ---------------------------------------------------------
    def do_dispense(self, manual: bool):
        # Send to ESP32
        out = String()
        out.data = "dispense_once"
        self.pub_seed.publish(out)

        # Update total count
        self.total_seed_count += 1

        # Prepare dashboard event
        event = {
            "count": 1,
            "totalCount": self.total_seed_count,
            "mode": "manual" if manual else "auto"
        }

        msg = String()
        msg.data = json.dumps(event)
        self.pub_dashboard.publish(msg)

        mode_txt = "MANUAL" if manual else "AUTO"
        self.get_logger().info(
            f"[{get_timestamp()}] {mode_txt} seed dispense → total = {self.total_seed_count}"
        )


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    rclpy.init()
    node = SeedNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()