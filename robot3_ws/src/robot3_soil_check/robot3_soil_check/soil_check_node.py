# robot3_soil_check/soil_check_node.py

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32, Bool
import json
from datetime import datetime


def get_timestamp():
    """Return current time in HH:MM:SS format"""
    return datetime.now().strftime("%H:%M:%S")


class SoilCheckNode(Node):
    def __init__(self):
        super().__init__("soil_check_node")

        # ---------------------------------------------------------
        # AUTO MODE - starts enabled by default
        # ---------------------------------------------------------
        self.is_auto_enabled = True
        self.auto_interval_sec = 5  # default 5 seconds
        self.auto_timer = self.create_timer(self.auto_interval_sec, self.auto_check)

        # ---------------------------------------------------------
        # SUBSCRIPTIONS (UI manual + ESP response + settings)
        # ---------------------------------------------------------
        self.sub_ui = self.create_subscription(
            String,
            "/ui/check_soil_moisture",
            self.cb_ui_request,
            10
        )

        self.sub_interval = self.create_subscription(
            String,
            "/ui/settings_soil_interval",
            self.cb_update_interval,
            10
        )
        
        # Subscribe to soil mode changes (auto/manual)
        self.sub_mode = self.create_subscription(
            String,
            "/ui/soil_mode",
            self.cb_mode_change,
            10
        )

        self.sub_esp_soil = self.create_subscription(
            Float32,
            "/robot1/soil_moisture",
            self.cb_esp_response,
            10
        )

        # ---------------------------------------------------------
        # PUBLISHERS
        # ---------------------------------------------------------
        self.pub_esp = self.create_publisher(
            String,
            "/robot1/check_soil_moisture",
            10
        )

        self.pub_forward = self.create_publisher(
            Float32,
            "/robot1/soil_moisture",
            10
        )

        # Event to dashboard
        self.pub_dashboard = self.create_publisher(
            String,
            "/dashboard/soil_event",
            10
        )

        self.get_logger().info(
            f"[{get_timestamp()}] SoilCheckNode started with auto interval = {self.auto_interval_sec} sec (AUTO mode ON)"
        )

    # ---------------------------------------------------------
    # MODE CHANGE HANDLER (auto/manual)
    # ---------------------------------------------------------
    def cb_mode_change(self, msg: String):
        mode = msg.data.strip().lower()
        
        if mode == "auto":
            self.enable_auto_mode()
        elif mode == "manual":
            self.disable_auto_mode()
        else:
            self.get_logger().warn(f"[{get_timestamp()}] Unknown soil mode: {mode}")

    # ---------------------------------------------------------
    # ENABLE AUTO MODE
    # ---------------------------------------------------------
    def enable_auto_mode(self):
        if self.is_auto_enabled:
            return  # Already enabled
            
        self.is_auto_enabled = True
        self.get_logger().info(f"[{get_timestamp()}] Soil check: AUTO mode ENABLED")
        
        # Cancel existing timer and create new one
        if self.auto_timer:
            self.auto_timer.cancel()
        self.auto_timer = self.create_timer(self.auto_interval_sec, self.auto_check)

    # ---------------------------------------------------------
    # DISABLE AUTO MODE
    # ---------------------------------------------------------
    def disable_auto_mode(self):
        if not self.is_auto_enabled:
            return  # Already disabled
            
        self.is_auto_enabled = False
        self.get_logger().info(f"[{get_timestamp()}] Soil check: AUTO mode DISABLED")
        
        # Stop auto timer
        if self.auto_timer:
            self.auto_timer.cancel()
            self.auto_timer = None

    # ---------------------------------------------------------
    # AUTO SOIL CHECK (only runs when auto enabled)
    # ---------------------------------------------------------
    def auto_check(self):
        if not self.is_auto_enabled:
            return
            
        out = String()
        out.data = "check"
        self.pub_esp.publish(out)
        self.get_logger().info(f"[{get_timestamp()}] AUTO soil check triggered")

    # ---------------------------------------------------------
    # UPDATE AUTO INTERVAL FROM UI SETTINGS
    # ---------------------------------------------------------
    def cb_update_interval(self, msg: String):
        try:
            new_interval = int(msg.data)
            if new_interval <= 0:
                raise ValueError
        except:
            self.get_logger().warn(f"[{get_timestamp()}] Invalid interval received: {msg.data}")
            return

        self.auto_interval_sec = new_interval
        self.get_logger().info(
            f"[{get_timestamp()}] Updated auto soil-check interval to {self.auto_interval_sec} seconds"
        )

        # Reset timer ONLY if auto mode is currently running
        if self.is_auto_enabled and self.auto_timer:
            self.auto_timer.cancel()
            self.auto_timer = self.create_timer(self.auto_interval_sec, self.auto_check)

    # ---------------------------------------------------------
    # MANUAL UI REQUEST
    # ---------------------------------------------------------
    def cb_ui_request(self, msg: String):
        cmd = msg.data.strip()

        if cmd != "check":
            self.get_logger().warn(f"[{get_timestamp()}] Ignored UI command: {cmd}")
            return

        out = String()
        out.data = "check"
        self.pub_esp.publish(out)

        self.get_logger().info(f"[{get_timestamp()}] MANUAL soil check requested")

    # ---------------------------------------------------------
    # ESP32 RESPONSE
    # ---------------------------------------------------------
    def cb_esp_response(self, msg: Float32):
        value = float(msg.data)

        self.get_logger().info(f"[{get_timestamp()}] ESP32 → Soil moisture = {value:.1f}%")

        # Forward to SensorNode
        forward = Float32()
        forward.data = value
        self.pub_forward.publish(forward)

        # Send dashboard event
        event = {
            "moisture": value
        }
        out = String()
        out.data = json.dumps(event)
        self.pub_dashboard.publish(out)

        self.get_logger().info(f"[{get_timestamp()}] Sent soil_event → dashboard & UI")


# ==================================================================
# MAIN
# ==================================================================
def main():
    rclpy.init()
    node = SoilCheckNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()      