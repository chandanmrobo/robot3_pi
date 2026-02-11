#!/usr/bin/env python3
"""
FILE: dashboard_api.py
LOCATION: ~/robot3_ws/src/robot3_dashboard/robot3_dashboard/dashboard_api.py

REST API endpoint for React UI dashboard charts.
GET /api/dashboard?range=daily|monthly|yearly

FIXED VERSION - Handles null values properly
"""

import os
import json
from flask import Blueprint, request, jsonify
from datetime import datetime


# ============================================================
# FLASK BLUEPRINT
# ============================================================
dashboard_api = Blueprint("dashboard_api", __name__)


# ============================================================
# FILE PATHS
# ============================================================
BASE_DIR = os.path.dirname(__file__)
STORAGE_DIR = os.path.join(BASE_DIR, "storage")

SENSOR_FILE = os.path.join(STORAGE_DIR, "sensor_log.json")
SEED_FILE = os.path.join(STORAGE_DIR, "seed_log.json")
SOIL_FILE = os.path.join(STORAGE_DIR, "soil_log.json")


# ============================================================
# HELPERS
# ============================================================
def ensure_storage_exists():
    """Create storage directory and initialize empty JSON files if needed"""
    os.makedirs(STORAGE_DIR, exist_ok=True)
    
    for filepath in [SENSOR_FILE, SEED_FILE, SOIL_FILE]:
        if not os.path.exists(filepath):
            with open(filepath, "w") as f:
                json.dump([], f)
            print(f"✅ Created: {filepath}")


def load_json(path):
    """Load JSON array from file, return [] if error."""
    try:
        if not os.path.exists(path):
            print(f"⚠️ File not found: {path}")
            return []
        
        with open(path, "r") as f:
            data = json.load(f)
            
        # Validate it's a list
        if not isinstance(data, list):
            print(f"⚠️ Invalid format in {path}, expected array")
            return []
            
        return data
        
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON decode error in {path}: {e}")
        return []
    except Exception as e:
        print(f"⚠️ Error loading {path}: {e}")
        return []


def filter_by_range(data, range_type):
    """
    Filter data array by time range.
    
    Args:
        data: List of dicts with "timestamp" key (ISO format)
        range_type: "daily", "monthly", or "yearly"
    
    Returns:
        Filtered list
    """
    if not data:
        return []
    
    now = datetime.now()
    today = now.date()
    
    filtered = []
    
    for item in data:
        # Skip if no timestamp
        if "timestamp" not in item:
            continue
            
        try:
            # Handle both ISO format and other formats
            ts_str = item["timestamp"]
            
            # Try parsing ISO format first
            try:
                ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
            except:
                # Fallback to other formats
                ts = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S.%f")
                
        except Exception as e:
            print(f"⚠️ Invalid timestamp: {item.get('timestamp')} - {e}")
            continue
        
        # Filter by range
        if range_type == "daily":
            if ts.date() == today:
                filtered.append(item)
        
        elif range_type == "monthly":
            if ts.year == now.year and ts.month == now.month:
                filtered.append(item)
        
        elif range_type == "yearly":
            if ts.year == now.year:
                filtered.append(item)
    
    return filtered


# ============================================================
# API ENDPOINT
# ============================================================
@dashboard_api.route("/api/dashboard", methods=["GET"])
def get_dashboard_data():
    """
    GET /api/dashboard?range=daily|monthly|yearly
    
    Returns:
        JSON with sensorData, seedData, stats
    """
    
    try:
        # Ensure storage exists
        ensure_storage_exists()
        
        # Parse range parameter
        range_type = request.args.get("range", "daily")
        
        if range_type not in ["daily", "monthly", "yearly"]:
            return jsonify({"error": "Invalid range parameter"}), 400
        
        print(f"📊 Dashboard API called: range={range_type}")
        
        # Load data from files
        sensor_data = load_json(SENSOR_FILE)
        seed_data = load_json(SEED_FILE)
        
        print(f"📂 Loaded {len(sensor_data)} sensor records, {len(seed_data)} seed records")
        
        # Apply time filters
        sensor_filtered = filter_by_range(sensor_data, range_type)
        seed_filtered = filter_by_range(seed_data, range_type)
        
        print(f"✅ Filtered to {len(sensor_filtered)} sensor, {len(seed_filtered)} seed records")
        
        # Calculate stats with safety checks
        avg_temp = 0.0
        avg_hum = 0.0
        avg_moist = 0.0
        total_seeds = 0
        
        # ============================================================
        # CRITICAL FIX: Filter out null/None values
        # ============================================================
        # Sensor stats (only if data exists)
        if sensor_filtered:
            # Calculate averages safely - FILTER OUT NULL VALUES
            # Changed from: if "temperature" in d
            # To: if "temperature" in d and d["temperature"] is not None
            temps = [d["temperature"] for d in sensor_filtered 
                     if "temperature" in d and d["temperature"] is not None]
            hums = [d["humidity"] for d in sensor_filtered 
                    if "humidity" in d and d["humidity"] is not None]
            moists = [d["moisture"] for d in sensor_filtered 
                      if "moisture" in d and d["moisture"] is not None]
            
            if temps:
                avg_temp = sum(temps) / len(temps)
            if hums:
                avg_hum = sum(hums) / len(hums)
            if moists:
                avg_moist = sum(moists) / len(moists)
        
        # Seed stats (only if data exists)
        if seed_filtered:
            # Sum all seed counts
            counts = [d.get("count", 0) for d in seed_filtered if "count" in d]
            total_seeds = sum(counts)
        
        stats = {
            "avgTemp": round(avg_temp, 1),
            "avgHumidity": round(avg_hum, 1),
            "avgMoisture": round(avg_moist, 1),
            "totalSeeds": total_seeds
        }
        
        print(f"📈 Stats calculated: {stats}")
        
        # Return JSON response
        return jsonify({
            "range": range_type,
            "sensorData": sensor_filtered,
            "seedData": seed_filtered,
            "stats": stats
        })
        
    except Exception as e:
        # Log error and return 500
        print(f"❌ Dashboard API error: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


# ============================================================
# HEALTH CHECK ENDPOINT
# ============================================================
@dashboard_api.route("/api/dashboard/health", methods=["GET"])
def health_check():
    """Check if storage files are accessible"""
    
    ensure_storage_exists()
    
    status = {
        "storage_dir": STORAGE_DIR,
        "files": {
            "sensor_log": os.path.exists(SENSOR_FILE),
            "seed_log": os.path.exists(SEED_FILE),
            "soil_log": os.path.exists(SOIL_FILE)
        }
    }
    
    return jsonify(status)