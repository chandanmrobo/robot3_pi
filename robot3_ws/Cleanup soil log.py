#!/usr/bin/env python3
"""
Soil Log Cleanup Script

Your soil_log.json has 172 identical readings (all 30.0%) taken every 50ms.
This script will reduce it to a more reasonable sample rate.

Options:
1. Keep 1 reading per minute (~17 entries)
2. Keep first, middle, and last (~3 entries)
3. Keep all (no change)
"""

import json
import os

SOIL_LOG_PATH = os.path.expanduser("~/robot3_ws/src/robot3_dashboard/robot3_dashboard/storage/soil_log.json")
BACKUP_PATH = os.path.expanduser("~/robot3_ws/src/robot3_dashboard/robot3_dashboard/storage/soil_log_backup.json")

# # Or use the uploaded file for testing
# SOIL_LOG_PATH = "/mnt/user-data/uploads/soil_log.json"

def load_soil_data():
    """Load soil log data"""
    try:
        with open(SOIL_LOG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None

def clean_soil_log():
    """Clean up excessive soil log entries"""
    
    print("=" * 80)
    print("Soil Log Cleanup Tool")
    print("=" * 80)
    
    # Load data
    data = load_soil_data()
    if not data:
        return
    
    print(f"\n📊 Current Status:")
    print(f"   Total entries: {len(data)}")
    print(f"   Unique values: {set(r['moisture'] for r in data)}")
    print(f"   Date range: {data[0]['timestamp']} to {data[-1]['timestamp']}")
    
    # Analyze
    all_same = len(set(r['moisture'] for r in data)) == 1
    if all_same:
        print(f"   ⚠️  All {len(data)} readings are identical: {data[0]['moisture']}%")
    
    print(f"\n🔧 Cleanup Options:")
    print(f"   1. Keep 1 per minute (~17 entries) - Recommended")
    print(f"   2. Keep first and last only (2 entries) - Minimal")
    print(f"   3. Keep 10 samples evenly distributed (10 entries)")
    print(f"   4. Exit without changes")
    
    choice = input("\nEnter your choice (1/2/3/4): ").strip()
    
    if choice == "1":
        # Keep 1 per minute (roughly every 10 readings)
        step = max(1, len(data) // 17)
        cleaned = [data[i] for i in range(0, len(data), step)]
        print(f"\n✅ Keeping 1 reading per minute")
        
    elif choice == "2":
        # Keep first and last
        cleaned = [data[0], data[-1]]
        print(f"\n✅ Keeping first and last only")
        
    elif choice == "3":
        # Keep 10 evenly distributed
        step = max(1, len(data) // 10)
        cleaned = [data[i] for i in range(0, len(data), step)][:10]
        print(f"\n✅ Keeping 10 evenly distributed samples")
        
    else:
        print("\n❌ No changes made")
        return
    
    # Show results
    print(f"\n📊 Cleanup Results:")
    print(f"   Original entries: {len(data)}")
    print(f"   Cleaned entries: {len(cleaned)}")
    print(f"   Removed: {len(data) - len(cleaned)} entries")
    print(f"   Space saved: ~{100 * (len(data) - len(cleaned)) / len(data):.1f}%")
    
    # Save
    print(f"\n💾 Saving cleaned data...")
    
    # Create backup
    try:
        with open(BACKUP_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"   ✅ Backup saved: {BACKUP_PATH}")
    except Exception as e:
        print(f"   ⚠️  Backup failed: {e}")
    
    # Save cleaned data
    try:
        with open(SOIL_LOG_PATH, 'w') as f:
            json.dump(cleaned, f, indent=2)
        print(f"   ✅ Cleaned data saved: {SOIL_LOG_PATH}")
    except Exception as e:
        print(f"   ❌ Save failed: {e}")
        return
    
    print(f"\n✅ Done!")
    print(f"\nℹ️  Note: This only cleans the log file.")
    print(f"   To prevent this in the future, reduce the logging frequency in your code.")
    print(f"   Change from: self.timer = self.create_timer(0.05, ...)")
    print(f"   To:          self.timer = self.create_timer(300.0, ...)  # 5 minutes")

if __name__ == "__main__":
    print("""
⚠️  WARNING: Update the SOIL_LOG_PATH variable to match your system!

Current path: ~/robot3_ws/src/robot3_dashboard/robot3_dashboard/storage/soil_log.json

If your path is different, edit line 15 of this script.
    """)
    
    proceed = input("Press Enter to continue or Ctrl+C to exit: ")
    clean_soil_log()