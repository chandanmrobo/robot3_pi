#!/usr/bin/env python3
"""
FILE: dashboard_node.py
LOCATION: ~/robot3_ws/src/robot3_dashboard/robot3_dashboard/dashboard_node.py

Dashboard data logger - Subscribes to ROS events and saves to JSON files
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from robot3_msgs.msg import DHT11
import json
import os
import logging
from datetime import datetime


# ============================================================
# LOGGING SETUP
# ============================================================
LOG_FILE = os.path.expanduser("~/robot3_ws/dashboard_log.txt")

log_handler = logging.FileHandler(LOG_FILE, mode='a')
log_handler.setFormatter(
    logging.Formatter('[%(asctime)s] [DASHBOARD] %(message)s')
)

dashboard_logger = logging.getLogger("dashboard_node")
dashboard_logger.setLevel(logging.INFO)
dashboard_logger.addHandler(log_handler)
dashboard_logger.addHandler(logging.StreamHandler())


# ============================================================
# DASHBOARD NODE
# ============================================================
class DashboardNode(Node):
    def __init__(self):
        super().__init__("dashboard_node")
        
        # ----------------------------------------------------
        # STORAGE PATHS (ONLY 3 FILES!)
        # ----------------------------------------------------
        storage_dir = os.path.join(os.path.dirname(__file__), "storage")
        os.makedirs(storage_dir, exist_ok=True)
        
        self.sensor_log_path = os.path.join(storage_dir, "sensor_log.json")
        self.seed_log_path = os.path.join(storage_dir, "seed_log.json")
        self.soil_log_path = os.path.join(storage_dir, "soil_log.json")
        
        # Initialize files
        self._ensure_file(self.sensor_log_path)
        self._ensure_file(self.seed_log_path)
        self._ensure_file(self.soil_log_path)
        
        # ----------------------------------------------------
        # SUBSCRIPTIONS
        # ----------------------------------------------------
        
        # Cache DHT11 readings (don't log continuously)
        self.create_subscription(
            DHT11, "/robot1/dht11_status", self.cb_dht_cache, 10
        )
        
        # Log seed dispense events
        self.create_subscription(
            String, "/dashboard/seed_event", self.cb_seed_event, 10
        )
        
        # Log soil check events
        self.create_subscription(
            String, "/dashboard/soil_event", self.cb_soil_event, 10
        )
        
        # ----------------------------------------------------
        # SENSOR CACHE
        # ----------------------------------------------------
        self.latest_temp = 0.0
        self.latest_hum = 0.0
        
        dashboard_logger.info("✅ DashboardNode started")
        dashboard_logger.info(f"📂 Storage: {storage_dir}")
        dashboard_logger.info("📝 Logging to 3 files only:")
        dashboard_logger.info(f"   - {os.path.basename(self.sensor_log_path)}")
        dashboard_logger.info(f"   - {os.path.basename(self.seed_log_path)}")
        dashboard_logger.info(f"   - {os.path.basename(self.soil_log_path)}")
    
    # --------------------------------------------------------
    # FILE HELPERS
    # --------------------------------------------------------
    def _ensure_file(self, path):
        """Create empty JSON array if file doesn't exist."""
        if not os.path.exists(path):
            with open(path, "w") as f:
                json.dump([], f)
            dashboard_logger.info(f"✅ Created: {os.path.basename(path)}")
    
    def _append_log(self, path, entry):
        """
        Append entry to JSON file (thread-safe).
        
        Format: Always an array of objects
        """
        try:
            # Read existing data
            with open(path, "r") as f:
                data = json.load(f)
            
            # Validate it's a list
            if not isinstance(data, list):
                dashboard_logger.error(f"❌ Invalid format in {path}, resetting to []")
                data = []
            
            # Append new entry
            data.append(entry)
            
            # Keep only last 10,000 records to prevent file bloat
            if len(data) > 10000:
                data = data[-10000:]
                dashboard_logger.info(f"🗑️ Trimmed {os.path.basename(path)} to 10k records")
            
            # Write back
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            dashboard_logger.error(f"❌ Failed to append to {path}: {e}")
            return False
    
    # --------------------------------------------------------
    # DHT11 CACHE (NO LOGGING - just store latest values)
    # --------------------------------------------------------
    def cb_dht_cache(self, msg: DHT11):
        """
        Cache latest sensor values.
        These get saved ONLY when a soil check happens.
        """
        self.latest_temp = float(msg.temperature)
        self.latest_hum = float(msg.humidity)
        # No logging here - just cache
    
    # --------------------------------------------------------
    # SEED EVENT (LOG ONCE PER DISPENSE)
    # --------------------------------------------------------
    def cb_seed_event(self, msg: String):
        """
        Log seed dispense events.
        
        Expected format from backend:
        {
            "count": 1,
            "totalCount": 42,
            "mode": "auto" or "manual"
        }
        """
        try:
            data = json.loads(msg.data)
        except:
            dashboard_logger.error("❌ Invalid seed event JSON")
            return
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "count": data.get("count", 1),
            "totalCount": data.get("totalCount", 0),
            "mode": data.get("mode", "manual")
        }
        
        success = self._append_log(self.seed_log_path, entry)
        
        if success:
            dashboard_logger.info(
                f"🌱 Seed logged: +{entry['count']} ({entry['mode']}) → total={entry['totalCount']}"
            )
    
    # --------------------------------------------------------
    # SOIL EVENT (LOG SENSOR SNAPSHOT + SOIL READING)
    # --------------------------------------------------------
    def cb_soil_event(self, msg: String):
        """
        Log soil check event.
        
        This saves TWO things:
        1. Soil moisture reading → soil_log.json
        2. Environmental snapshot (temp+hum+soil) → sensor_log.json
        
        Expected format from backend:
        {
            "moisture": 45.2
        }
        """
        try:
            data = json.loads(msg.data)
            moisture = data.get("moisture", 0)
        except:
            dashboard_logger.error("❌ Invalid soil event JSON")
            return
        
        timestamp = datetime.now().isoformat()
        
        # ✅ 1. Log soil check event
        soil_entry = {
            "timestamp": timestamp,
            "moisture": float(moisture)
        }
        self._append_log(self.soil_log_path, soil_entry)
        
        # ✅ 2. Log environmental snapshot (temp + hum + soil combined)
        sensor_entry = {
            "timestamp": timestamp,
            "temperature": self.latest_temp,
            "humidity": self.latest_hum,
            "moisture": float(moisture)
        }
        self._append_log(self.sensor_log_path, sensor_entry)
        
        dashboard_logger.info(
            f"💧 Soil check: {moisture:.1f}% | Snapshot saved (T={self.latest_temp:.1f}°C, H={self.latest_hum:.1f}%)"
        )


# ============================================================
# MAIN
# ============================================================
def main():
    rclpy.init()
    node = DashboardNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        dashboard_logger.info("🛑 DashboardNode shutting down")
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()