#!/usr/bin/env python3
"""
Data Cleaning Script for Sensor Logs

This script will:
1. Load sensor_log.json
2. Remove or fix records with null values
3. Save the cleaned version

Usage:
    python3 clean_sensor_data.py
"""

import json
import os
from datetime import datetime

# File paths - adjust these to match your actual paths
SENSOR_LOG_PATH = os.path.expanduser("~/robot3_ws/src/robot3_dashboard/robot3_dashboard/storage/sensor_log.json")
BACKUP_PATH = os.path.expanduser("~/robot3_ws/src/robot3_dashboard/robot3_dashboard/storage/sensor_log_backup.json")


def clean_sensor_data(input_file, output_file, backup_file):
    """
    Clean sensor data by handling null values
    
    Options:
    1. Remove records with any null values
    2. Replace null with default values
    """
    
    print(f"📂 Loading data from: {input_file}")
    
    # Load existing data
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {input_file}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return
    
    print(f"📊 Total records: {len(data)}")
    
    # Create backup
    print(f"💾 Creating backup at: {backup_file}")
    with open(backup_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Analyze data
    records_with_nulls = 0
    null_temps = 0
    null_hums = 0
    null_moists = 0
    
    for record in data:
        has_null = False
        if record.get("temperature") is None:
            null_temps += 1
            has_null = True
        if record.get("humidity") is None:
            null_hums += 1
            has_null = True
        if record.get("moisture") is None:
            null_moists += 1
            has_null = True
        
        if has_null:
            records_with_nulls += 1
    
    print(f"\n📈 Data Analysis:")
    print(f"  Records with null values: {records_with_nulls}/{len(data)}")
    print(f"  Null temperatures: {null_temps}")
    print(f"  Null humidity: {null_hums}")
    print(f"  Null moisture: {null_moists}")
    
    # Ask user what to do
    print(f"\n🔧 Cleaning Options:")
    print(f"  1. Remove all records with any null values (removes {records_with_nulls} records)")
    print(f"  2. Replace nulls with default values (temp=25.0, humidity=60.0, moisture=30.0)")
    print(f"  3. Exit without changes")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    cleaned_data = []
    
    if choice == "1":
        # Option 1: Remove records with nulls
        print("\n🗑️  Removing records with null values...")
        for record in data:
            if (record.get("temperature") is not None and 
                record.get("humidity") is not None and 
                record.get("moisture") is not None):
                cleaned_data.append(record)
        
        print(f"✅ Removed {len(data) - len(cleaned_data)} records")
        
    elif choice == "2":
        # Option 2: Replace nulls with defaults
        print("\n🔄 Replacing null values with defaults...")
        for record in data:
            cleaned_record = record.copy()
            if cleaned_record.get("temperature") is None:
                cleaned_record["temperature"] = 25.0
            if cleaned_record.get("humidity") is None:
                cleaned_record["humidity"] = 60.0
            if cleaned_record.get("moisture") is None:
                cleaned_record["moisture"] = 30.0
            cleaned_data.append(cleaned_record)
        
        print(f"✅ Fixed {records_with_nulls} records")
        
    else:
        print("❌ Exiting without changes")
        return
    
    # Save cleaned data
    print(f"\n💾 Saving cleaned data to: {output_file}")
    with open(output_file, 'w') as f:
        json.dump(cleaned_data, f, indent=2)
    
    print(f"\n✅ Done!")
    print(f"📊 Final statistics:")
    print(f"  Original records: {len(data)}")
    print(f"  Cleaned records: {len(cleaned_data)}")
    print(f"  Backup saved at: {backup_file}")


if __name__ == "__main__":
    print("=" * 60)
    print("Sensor Data Cleaning Script")
    print("=" * 60)
    
    # Check if file exists
    if not os.path.exists(SENSOR_LOG_PATH):
        print(f"\n❌ Error: File not found at {SENSOR_LOG_PATH}")
        print("\nPlease update SENSOR_LOG_PATH in this script to match your actual file location.")
        print("\nExample paths:")
        print("  ~/robot3_ws/src/robot3_dashboard/robot3_dashboard/storage/sensor_log.json")
        print("  /home/chandan/robot3_ws/src/robot3_dashboard/robot3_dashboard/storage/sensor_log.json")
        exit(1)
    
    clean_sensor_data(SENSOR_LOG_PATH, SENSOR_LOG_PATH, BACKUP_PATH)