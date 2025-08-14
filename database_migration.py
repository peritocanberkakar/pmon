#!/usr/bin/env python3
"""
Database Migration Script for PMON v1.2.0
Handles schema changes for PING feature
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Migrate existing database to support PING features"""
    
    # Database file path
    db_path = Path("pmon.db")
    
    if not db_path.exists():
        print("Database file not found. Creating new database...")
        return
    
    print("Starting database migration...")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if new columns exist
        cursor.execute("PRAGMA table_info(service_definitions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'location' not in columns:
            print("Adding 'location' column to service_definitions...")
            cursor.execute("ALTER TABLE service_definitions ADD COLUMN location TEXT")
        
        if 'country' not in columns:
            print("Adding 'country' column to service_definitions...")
            cursor.execute("ALTER TABLE service_definitions ADD COLUMN country TEXT")
        
        if 'city' not in columns:
            print("Adding 'city' column to service_definitions...")
            cursor.execute("ALTER TABLE service_definitions ADD COLUMN city TEXT")
        
        if 'ping_location_id' not in columns:
            print("Adding 'ping_location_id' column to service_definitions...")
            cursor.execute("ALTER TABLE service_definitions ADD COLUMN ping_location_id INTEGER")
        
        # Check if ping_locations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ping_locations'")
        if not cursor.fetchone():
            print("Creating ping_locations table...")
            cursor.execute("""
                CREATE TABLE ping_locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    country TEXT,
                    city TEXT,
                    region TEXT,
                    isp TEXT,
                    ip_range TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        # Check if alert_channels table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alert_channels'")
        if not cursor.fetchone():
            print("Creating alert_channels table...")
            cursor.execute("""
                CREATE TABLE alert_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    channel_type TEXT NOT NULL,
                    config TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants (id)
                )
            """)
        
        # Check if alert_rules table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alert_rules'")
        if not cursor.fetchone():
            print("Creating alert_rules table...")
            cursor.execute("""
                CREATE TABLE alert_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    monitor_id INTEGER NOT NULL,
                    alert_channel_id INTEGER NOT NULL,
                    rule_type TEXT NOT NULL,
                    threshold INTEGER,
                    cooldown_minutes INTEGER DEFAULT 30,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants (id),
                    FOREIGN KEY (monitor_id) REFERENCES monitors (id),
                    FOREIGN KEY (alert_channel_id) REFERENCES alert_channels (id)
                )
            """)
        
        # Check if alert_history table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alert_history'")
        if not cursor.fetchone():
            print("Creating alert_history table...")
            cursor.execute("""
                CREATE TABLE alert_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    monitor_id INTEGER NOT NULL,
                    alert_rule_id INTEGER NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants (id),
                    FOREIGN KEY (monitor_id) REFERENCES monitors (id),
                    FOREIGN KEY (alert_rule_id) REFERENCES alert_rules (id)
                )
            """)
        
        # Check if monitors table has new statistics columns
        cursor.execute("PRAGMA table_info(monitors)")
        monitor_columns = [column[1] for column in cursor.fetchall()]
        
        if 'consecutive_failures' not in monitor_columns:
            print("Adding statistics columns to monitors...")
            cursor.execute("ALTER TABLE monitors ADD COLUMN consecutive_failures INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE monitors ADD COLUMN consecutive_successes INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE monitors ADD COLUMN total_checks INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE monitors ADD COLUMN total_failures INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE monitors ADD COLUMN uptime_percentage REAL DEFAULT 100.0")
            cursor.execute("ALTER TABLE monitors ADD COLUMN last_latency_ms INTEGER")
        
        # Commit changes
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
