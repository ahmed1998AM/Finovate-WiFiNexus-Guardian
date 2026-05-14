"""
Database Manager - Handles local data storage using SQLite
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class DatabaseManager:
    """Manages SQLite database for local data storage"""
    
    def __init__(self):
        self.db_path = None
        self.conn = None
        self.cursor = None
        
    def initialize(self, db_name: str = "wifinexus.db") -> bool:
        """Initialize database connection and create tables"""
        try:
            # Create database directory
            db_dir = Path(__file__).parent.parent / "database"
            db_dir.mkdir(exist_ok=True)
            
            self.db_path = db_dir / db_name
            
            # Connect to database
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # Create tables
            self._create_tables()
            
            return True
        except Exception as e:
            print(f"Database initialization error: {e}")
            return False
    
    def _create_tables(self):
        """Create necessary database tables"""
        
        # Network scans table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ssid TEXT,
                bssid TEXT,
                signal_strength INTEGER,
                channel INTEGER,
                frequency TEXT,
                encryption TEXT,
                adapter_name TEXT
            )
        ''')
        
        # Connected devices table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS connected_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detection_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                mac_address TEXT,
                ip_address TEXT,
                vendor TEXT,
                first_seen DATETIME,
                last_seen DATETIME,
                is_active BOOLEAN
            )
        ''')
        
        # Performance logs table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                download_speed REAL,
                upload_speed REAL,
                latency REAL,
                packet_loss REAL,
                jitter REAL,
                network_id TEXT
            )
        ''')
        
        # Security events table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT,
                severity TEXT,
                description TEXT,
                source_mac TEXT,
                details TEXT
            )
        ''')
        
        # AI recommendations table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                recommendation_type TEXT,
                health_score INTEGER,
                issues TEXT,
                suggestions TEXT,
                applied BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Application settings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def save_network_scan(self, scan_data: Dict) -> int:
        """Save a network scan result"""
        try:
            self.cursor.execute('''
                INSERT INTO network_scans 
                (ssid, bssid, signal_strength, channel, frequency, encryption, adapter_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                scan_data.get('ssid'),
                scan_data.get('bssid'),
                scan_data.get('signal_strength'),
                scan_data.get('channel'),
                scan_data.get('frequency'),
                scan_data.get('encryption'),
                scan_data.get('adapter_name')
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error saving network scan: {e}")
            return -1
    
    def save_connected_device(self, device_data: Dict) -> int:
        """Save detected device information"""
        try:
            now = datetime.now()
            self.cursor.execute('''
                INSERT INTO connected_devices 
                (mac_address, ip_address, vendor, first_seen, last_seen, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                device_data.get('mac_address'),
                device_data.get('ip_address'),
                device_data.get('vendor'),
                now,
                now,
                True
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error saving device: {e}")
            return -1
    
    def save_performance_log(self, perf_data: Dict) -> int:
        """Save performance test results"""
        try:
            self.cursor.execute('''
                INSERT INTO performance_logs 
                (download_speed, upload_speed, latency, packet_loss, jitter, network_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                perf_data.get('download_speed'),
                perf_data.get('upload_speed'),
                perf_data.get('latency'),
                perf_data.get('packet_loss'),
                perf_data.get('jitter'),
                perf_data.get('network_id')
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error saving performance log: {e}")
            return -1
    
    def save_security_event(self, event_data: Dict) -> int:
        """Save security event"""
        try:
            self.cursor.execute('''
                INSERT INTO security_events 
                (event_type, severity, description, source_mac, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                event_data.get('event_type'),
                event_data.get('severity'),
                event_data.get('description'),
                event_data.get('source_mac'),
                event_data.get('details')
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error saving security event: {e}")
            return -1
    
    def save_ai_recommendation(self, rec_data: Dict) -> int:
        """Save AI recommendation"""
        try:
            import json
            self.cursor.execute('''
                INSERT INTO ai_recommendations 
                (recommendation_type, health_score, issues, suggestions)
                VALUES (?, ?, ?, ?)
            ''', (
                rec_data.get('recommendation_type'),
                rec_data.get('health_score'),
                json.dumps(rec_data.get('issues', [])),
                json.dumps(rec_data.get('suggestions', []))
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error saving AI recommendation: {e}")
            return -1
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get application setting"""
        try:
            self.cursor.execute('SELECT value FROM app_settings WHERE key = ?', (key,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting setting: {e}")
            return None
    
    def set_setting(self, key: str, value: str) -> bool:
        """Set application setting"""
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO app_settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error setting setting: {e}")
            return False
    
    def get_recent_scans(self, limit: int = 100) -> List[Dict]:
        """Get recent network scans"""
        try:
            self.cursor.execute('''
                SELECT * FROM network_scans ORDER BY scan_timestamp DESC LIMIT ?
            ''', (limit,))
            
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error getting recent scans: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
