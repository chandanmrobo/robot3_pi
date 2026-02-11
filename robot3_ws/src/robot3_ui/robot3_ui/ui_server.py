#!/usr/bin/env python3

import os
import json
import asyncio
import logging
import time
from datetime import datetime
from fractions import Fraction
from threading import Thread, Lock

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import CompressedImage
from robot3_msgs.msg import BatteryStatus, DHT11, SoilMoisture

from flask import Flask, send_from_directory
from flask_socketio import SocketIO

# WebRTC
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from av import VideoFrame
import cv2
import numpy as np

# Dashboard API
from robot3_dashboard.dashboard_api import dashboard_api


# ============================================================
# LOGGING
# ============================================================
LOG_FILE = os.path.expanduser("~/robot3_ws/ui_log.txt")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

handler = logging.FileHandler(LOG_FILE, mode='a')
handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))

ui_logger = logging.getLogger("ui_server")
ui_logger.setLevel(logging.INFO)
ui_logger.addHandler(handler)
ui_logger.addHandler(logging.StreamHandler())


# ============================================================
# FLASK + SOCKET.IO
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_BUILD_DIR = os.path.join(BASE_DIR, "ui_build")

app = Flask(__name__, static_folder=UI_BUILD_DIR, static_url_path="")
app.register_blueprint(dashboard_api)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


# ============================================================
# WEBRTC VIDEO TRACK (Thread-Safe)
# ============================================================
class CameraVideoTrack(MediaStreamTrack):
    """WebRTC video track with thread-safe frame pushing"""
    kind = "video"
    
    def __init__(self):
        super().__init__()
        self._latest_frame = None
        self._frame_lock = Lock()
        self._pts = 0
        self._frame_rate = 30  # FPS
    
    async def recv(self):
        """Called by aiortc to get next frame"""
        with self._frame_lock:
            frame = self._latest_frame
        
        if frame is None:
            # Return black frame if no data yet
            black = np.zeros((480, 640, 3), dtype=np.uint8)
            vf = VideoFrame.from_ndarray(black, format="bgr24")
        else:
            vf = VideoFrame.from_ndarray(frame, format="bgr24")
        
        # Proper timestamp
        self._pts += 1
        vf.pts = self._pts
        vf.time_base = Fraction(1, self._frame_rate)
        
        return vf
    
    def push_frame(self, frame: np.ndarray):
        """Thread-safe frame update from ROS callback"""
        with self._frame_lock:
            self._latest_frame = frame


# ============================================================
# WEBRTC GLOBALS
# ============================================================
camera_track = CameraVideoTrack()
active_pcs = {}
pc_lock = Lock()
webrtc_loop = None
webrtc_loop_thread = None


def start_webrtc_loop():
    """Start persistent event loop for WebRTC peer connections"""
    global webrtc_loop
    
    webrtc_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(webrtc_loop)
    
    try:
        webrtc_loop.run_forever()
    finally:
        webrtc_loop.close()


@socketio.on("webrtc_offer")
def handle_webrtc_offer(offer):
    """Handle WebRTC offer from React UI"""
    ui_logger.info("📡 Received WebRTC offer")
    
    async def process_offer():
        global active_pcs, camera_track
        
        try:
            # Create peer connection
            pc = RTCPeerConnection()
            
            # Store PC
            with pc_lock:
                if "main" in active_pcs:
                    try:
                        await active_pcs["main"].close()
                    except:
                        pass
                active_pcs["main"] = pc
            
            # Set remote description FIRST
            await pc.setRemoteDescription(
                RTCSessionDescription(sdp=offer["sdp"], type=offer["type"])
            )
            ui_logger.info("✅ Remote description set")
            
            # Handle transceivers properly
            transceivers = pc.getTransceivers()
            video_transceiver = None
            
            for t in transceivers:
                if t.kind == "video":
                    video_transceiver = t
                    break
            
            if video_transceiver:
                # ⭐ FIX: Change direction to sendonly and replace track
                video_transceiver.direction = "sendonly"
                video_transceiver.sender.replaceTrack(camera_track)
                ui_logger.info("📹 Camera track replaced, direction set to sendonly")
            else:
                # Add new track (creates new transceiver)
                pc.addTrack(camera_track)
                ui_logger.info("📹 Camera track added")
            
            # Create answer
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            
            ui_logger.info("✅ Answer created")
            
            # Return answer to main thread
            return {
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type
            }
            
        except Exception as e:
            ui_logger.error(f"❌ WebRTC error: {e}")
            import traceback
            ui_logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    # Schedule coroutine in persistent event loop
    future = asyncio.run_coroutine_threadsafe(process_offer(), webrtc_loop)
    
    # Wait for result (with timeout)
    try:
        result = future.result(timeout=5.0)
        
        if "error" in result:
            socketio.emit("webrtc_error", result)
            ui_logger.error(f"❌ WebRTC negotiation failed: {result['error']}")
        else:
            socketio.emit("webrtc_answer", result)
            ui_logger.info("✅ WebRTC answer sent to client")
            
    except Exception as e:
        ui_logger.error(f"❌ WebRTC negotiation error: {e}")
        socketio.emit("webrtc_error", {"error": str(e)})


# ============================================================
# ROS UI BRIDGE (Camera Subscription)
# ============================================================
class UIBridge(Node):
    def __init__(self):
        super().__init__("robot3_ui_server")
        ui_logger.info("🤖 UIBridge started")
        
        # Camera subscription
        self.create_subscription(
            CompressedImage,
            "/robot2/camera/image_raw/compressed",
            self.cb_camera,
            10
        )
        
        # Battery subscriptions
        self.create_subscription(BatteryStatus, "/robot1/battery_status", self.cb_batt_r1, 10)
        self.create_subscription(BatteryStatus, "/robot2/battery_status", self.cb_batt_r2, 10)
        
        # Sensor subscriptions
        self.create_subscription(DHT11, "/robot1/dht11_status", self.cb_dht, 10)
        self.create_subscription(SoilMoisture, "/robot1/soil_status", self.cb_soil, 10)
        
        # Detection subscriptions
        self.create_subscription(String, "/ui/plant_detection", self.cb_plant, 10)
        self.create_subscription(String, "/ui/bird_detection", self.cb_bird, 10)
        
        # Dashboard events
        self.create_subscription(String, "/dashboard/seed_event", self.cb_seed_event, 10)
        self.create_subscription(String, "/dashboard/soil_event", self.cb_soil_event, 10)
        
        # Publishers
        self.pub_move = self.create_publisher(String, "/ui/move_cmd", 10)
        self.pub_seed = self.create_publisher(String, "/ui/seed_cmd", 10)
        self.pub_soil_check = self.create_publisher(String, "/ui/check_soil_moisture", 10)
        self.pub_detection_mode = self.create_publisher(String, "/ui/detection_mode", 10)
        self.pub_seed_gap = self.create_publisher(String, "/ui/settings_seed_gap", 10)
        self.pub_soil_interval = self.create_publisher(String, "/ui/settings_soil_interval", 10)
        self.pub_wifi = self.create_publisher(String, "/ui/settings_wifi", 10)
        
        # ⭐ NEW: Mode control publishers
        self.pub_soil_mode = self.create_publisher(String, "/ui/soil_mode", 10)
        self.pub_seed_mode = self.create_publisher(String, "/ui/seed_cmd", 10)  # seed mode uses same topic as commands
        
        self.frame_count = 0
        ui_logger.info("✅ All topics connected")
    
    def cb_camera(self, msg: CompressedImage):
        """Receive camera frames and push to WebRTC"""
        try:
            # Decode JPEG
            np_arr = np.frombuffer(msg.data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                camera_track.push_frame(frame)
                
                # Log every 30 frames
                self.frame_count += 1
                if self.frame_count % 30 == 0:
                    self.get_logger().info(f"📹 Frames: {self.frame_count}")
                    
        except Exception as e:
            self.get_logger().error(f"Camera error: {e}")
    
    # ROS → Socket.IO callbacks
    def cb_batt_r1(self, msg):
        socketio.emit("robot1_battery", {
            "voltage": float(msg.voltage),
            "percent": float(msg.percent),
            "low_flag": bool(msg.low_flag)
        })
    
    def cb_batt_r2(self, msg):
        socketio.emit("robot2_battery", {
            "voltage": float(msg.voltage),
            "percent": float(msg.percent),
            "low_flag": bool(msg.low_flag)
        })
    
    def cb_dht(self, msg):
        socketio.emit("robot1_dht", {
            "temperature": float(msg.temperature),
            "humidity": float(msg.humidity)
        })
    
    def cb_soil(self, msg):
        socketio.emit("robot1_soil", {"moisture": float(msg.moisture)})
    
    def cb_plant(self, msg):
        socketio.emit("plant_detection", {"disease": msg.data})
    
    def cb_bird(self, msg):
        socketio.emit("bird_detection", {"bird": msg.data})
    
    def cb_seed_event(self, msg):
        try:
            data = json.loads(msg.data)
        except:
            data = {"count": 1, "totalCount": 0}
        socketio.emit("seed_event", data)
    
    def cb_soil_event(self, msg):
        try:
            data = json.loads(msg.data)
        except:
            data = {"moisture": 0}
        socketio.emit("soil_event", data)
    
    def _pub_str(self, publisher, data):
        msg = String()
        msg.data = str(data)
        publisher.publish(msg)
    
    def send_move_cmd(self, cmd):
        self._pub_str(self.pub_move, cmd)
    
    def send_seed_cmd(self, cmd):
        self._pub_str(self.pub_seed, cmd)
    
    def send_soil_check(self):
        self._pub_str(self.pub_soil_check, "check")
    
    def send_detection_mode(self, mode):
        self._pub_str(self.pub_detection_mode, mode)
    
    def send_seed_gap(self, gap):
        self._pub_str(self.pub_seed_gap, gap)
    
    def send_soil_interval(self, interval):
        self._pub_str(self.pub_soil_interval, interval)
    
    def send_wifi_settings(self, ssid, password):
        payload = json.dumps({"ssid": ssid, "password": password})
        self._pub_str(self.pub_wifi, payload)
    
    # ⭐ NEW: Mode control methods
    def send_soil_mode(self, mode):
        self._pub_str(self.pub_soil_mode, mode)
    
    def send_seed_mode(self, mode):
        # Send seed_mode_auto or seed_mode_manual
        self._pub_str(self.pub_seed_mode, f"seed_mode_{mode}")


# ============================================================
# SOCKET.IO HANDLERS (UI → ROS)
# ============================================================
@socketio.on("move_cmd")
def handle_move(data):
    node.send_move_cmd(data)

@socketio.on("seed_cmd")
def handle_seed(data):
    node.send_seed_cmd(data)

@socketio.on("soil_check")
def handle_soil_check(data):
    node.send_soil_check()

@socketio.on("detection_mode")
def handle_detection_mode(data):
    node.send_detection_mode(data.get("mode", "plant"))

@socketio.on("settings_seed_gap")
def handle_seed_gap(data):
    node.send_seed_gap(data.get("gap", 5))

@socketio.on("settings_soil_interval")
def handle_soil_interval(data):
    node.send_soil_interval(data.get("interval", 5))

@socketio.on("settings_wifi")
def handle_wifi(data):
    node.send_wifi_settings(data.get("ssid", ""), data.get("password", ""))

# ⭐ NEW: Mode control handlers
@socketio.on("soil_mode")
def handle_soil_mode(data):
    node.send_soil_mode(data)

@socketio.on("seed_mode")
def handle_seed_mode(data):
    node.send_seed_mode(data)


# ============================================================
# SERVE REACT UI
# ============================================================
@app.route("/")
def serve_index():
    return send_from_directory(UI_BUILD_DIR, "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    candidate = os.path.join(UI_BUILD_DIR, filename)
    if os.path.exists(candidate):
        return send_from_directory(UI_BUILD_DIR, filename)
    
    assets = os.path.join(UI_BUILD_DIR, "assets", filename)
    if os.path.exists(assets):
        return send_from_directory(os.path.join(UI_BUILD_DIR, "assets"), filename)
    
    return send_from_directory(UI_BUILD_DIR, "index.html")


# ============================================================
# MAIN
# ============================================================
def main(args=None):
    global node, webrtc_loop, webrtc_loop_thread
    
    ui_logger.info("=" * 60)
    ui_logger.info("🚀 Robot3 UI Server (WebRTC Fixed)")
    ui_logger.info("=" * 60)
    
    rclpy.init(args=args)
    node = UIBridge()
    
    # Start persistent WebRTC event loop in background thread
    webrtc_loop_thread = Thread(target=start_webrtc_loop, daemon=True)
    webrtc_loop_thread.start()
    ui_logger.info("✅ WebRTC event loop started")
    
    # Wait for loop to initialize
    time.sleep(0.5)
    
    # ROS in background thread
    ros_thread = Thread(target=rclpy.spin, args=(node,), daemon=True)
    ros_thread.start()
    
    ui_logger.info(f"📂 UI: {UI_BUILD_DIR}")
    ui_logger.info("🌐 http://0.0.0.0:5000")
    ui_logger.info(f"📝 Logs: {LOG_FILE}")
    
    try:
        socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
    finally:
        ui_logger.info("🛑 Shutting down")
        
        # Cleanup WebRTC
        if webrtc_loop and webrtc_loop.is_running():
            webrtc_loop.call_soon_threadsafe(webrtc_loop.stop)
        
        with pc_lock:
            for pc in active_pcs.values():
                try:
                    if webrtc_loop:
                        future = asyncio.run_coroutine_threadsafe(pc.close(), webrtc_loop)
                        future.result(timeout=2.0)
                except:
                    pass
        
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()