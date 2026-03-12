"""
Data storage utilities for LinkedIn Manager.

Handles:
- SQLite database operations
- JSON file I/O
- Activity logging
- Data versioning
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.utils.logger import get_logger

logger = get_logger(__name__)

# Configuration
DB_FILE = Path(".tmp/linkedin_manager.db")
TMP_DIR = Path(".tmp")

# Ensure directories exist
TMP_DIR.mkdir(parents=True, exist_ok=True)


class DatabaseManager:
    """Manage SQLite database operations."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or DB_FILE
        self.conn: Optional[sqlite3.Connection] = None
        
    def connect(self) -> sqlite3.Connection:
        """
        Establish database connection and initialize schema.
        
        Returns:
            Database connection object
        """
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row  # Enable dict-like access
            
            # Initialize schema
            self._init_schema()
            
            logger.debug(f"Connected to database: {self.db_path}")
            return self.conn
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def _init_schema(self) -> None:
        """Create database tables if they don't exist."""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        
        # Activity Log Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                action_type TEXT NOT NULL,
                target_url TEXT,
                result TEXT NOT NULL,
                details JSON,
                session_id TEXT
            )
        """)
        
        # Profiles Database
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                linkedin_url TEXT UNIQUE,
                full_name TEXT,
                headline TEXT,
                company TEXT,
                location TEXT,
                industry TEXT,
                relevance_score INTEGER,
                connection_sent BOOLEAN DEFAULT FALSE,
                connection_accepted BOOLEAN DEFAULT FALSE,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Posts Archive
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                post_type TEXT,
                scheduled_for DATETIME,
                published_at DATETIME,
                post_url TEXT UNIQUE,
                impressions INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Rate Limit Tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_limits (
                date DATE PRIMARY KEY,
                connections_sent INTEGER DEFAULT 0,
                profiles_viewed INTEGER DEFAULT 0,
                posts_published INTEGER DEFAULT 0,
                messages_sent INTEGER DEFAULT 0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_timestamp 
            ON activity_log(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_type 
            ON activity_log(action_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_profiles_company 
            ON profiles(company)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_posts_published 
            ON posts(published_at)
        """)
        
        self.conn.commit()
        logger.debug("Database schema initialized")
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.debug("Database connection closed")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class ActivityLogger:
    """Log and retrieve activity events."""
    
    def __init__(self):
        """Initialize activity logger."""
        self.db = DatabaseManager()
    
    def log_action(
        self,
        action_type: str,
        result: str,
        details: Optional[Dict[str, Any]] = None,
        target_url: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> int:
        """
        Log an action to the database.
        
        Args:
            action_type: Type of action (login, post_published, connection_sent, etc.)
            result: success, failure, skipped
            details: Additional information as dictionary
            target_url: Related URL if applicable
            session_id: Session identifier
        
        Returns:
            ID of inserted record
        """
        try:
            with self.db as db:
                cursor = db.conn.cursor()
                
                cursor.execute("""
                    INSERT INTO activity_log 
                    (action_type, result, details, target_url, session_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    action_type,
                    result,
                    json.dumps(details) if details else None,
                    target_url,
                    session_id
                ))
                
                db.conn.commit()
                
                record_id = cursor.lastrowid
                logger.debug(f"Logged action: {action_type} ({result}) - ID: {record_id}")
                return record_id
                
        except Exception as e:
            logger.error(f"Failed to log action: {e}")
            return -1
    
    def get_daily_count(self, action_type: str, target_date: Optional[date] = None) -> int:
        """
        Get count of actions for a specific date.
        
        Args:
            action_type: Type of action to count
            target_date: Date to query (default: today)
        
        Returns:
            Count of actions
        """
        if target_date is None:
            target_date = date.today()
        
        try:
            with self.db as db:
                cursor = db.conn.cursor()
                
                cursor.execute("""
                    SELECT COUNT(*) FROM activity_log
                    WHERE action_type = ?
                    AND DATE(timestamp) = ?
                """, (action_type, target_date.isoformat()))
                
                result = cursor.fetchone()
                count = result[0] if result else 0
                
                logger.debug(f"{action_type} count for {target_date}: {count}")
                return count
                
        except Exception as e:
            logger.error(f"Failed to get daily count: {e}")
            return 0
    
    def get_recent_activities(
        self,
        action_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent activities.
        
        Args:
            action_type: Filter by action type (optional)
            limit: Maximum number of records
        
        Returns:
            List of activity records
        """
        try:
            with self.db as db:
                cursor = db.conn.cursor()
                
                if action_type:
                    cursor.execute("""
                        SELECT * FROM activity_log
                        WHERE action_type = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    """, (action_type, limit))
                else:
                    cursor.execute("""
                        SELECT * FROM activity_log
                        ORDER BY timestamp DESC
                        LIMIT ?
                    """, (limit,))
                
                rows = cursor.fetchall()
                activities = []
                
                for row in rows:
                    activity = dict(row)
                    # Parse JSON details
                    if activity.get("details"):
                        try:
                            activity["details"] = json.loads(activity["details"])
                        except:
                            pass
                    activities.append(activity)
                
                return activities
                
        except Exception as e:
            logger.error(f"Failed to get recent activities: {e}")
            return []
    
    def update_rate_limit(self, action_type: str, increment: int = 1) -> None:
        """
        Update rate limit counter for today.
        
        Args:
            action_type: Type of action to increment
            increment: Amount to increment by
        """
        today = date.today().isoformat()
        
        # Map action types to rate limit columns
        column_map = {
            "connection_sent": "connections_sent",
            "profile_viewed": "profiles_viewed",
            "post_published": "posts_published",
            "message_sent": "messages_sent"
        }
        
        column = column_map.get(action_type)
        if not column:
            logger.debug(f"No rate limit tracking for: {action_type}")
            return
        
        try:
            with self.db as db:
                cursor = db.conn.cursor()
                
                # Upsert logic
                cursor.execute("""
                    INSERT INTO rate_limits (date, {column}, last_updated)
                    VALUES (?, COALESCE((SELECT {column} FROM rate_limits WHERE date = ?), 0) + ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(date) DO UPDATE SET
                        {column} = {column} + ?,
                        last_updated = CURRENT_TIMESTAMP
                """.format(column=column), (today, today, increment, increment))
                
                db.conn.commit()
                logger.debug(f"Updated rate limit: {column} += {increment}")
                
        except Exception as e:
            logger.error(f"Failed to update rate limit: {e}")
    
    def get_today_rate_limits(self) -> Dict[str, int]:
        """
        Get all rate limit counts for today.
        
        Returns:
            Dictionary of action counts
        """
        today = date.today().isoformat()
        
        try:
            with self.db as db:
                cursor = db.conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM rate_limits
                    WHERE date = ?
                """, (today,))
                
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                else:
                    return {
                        "date": today,
                        "connections_sent": 0,
                        "profiles_viewed": 0,
                        "posts_published": 0,
                        "messages_sent": 0
                    }
                
        except Exception as e:
            logger.error(f"Failed to get rate limits: {e}")
            return {}


def save_json(data: Any, file_path: Union[str, Path]) -> bool:
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        file_path: Output file path
    
    Returns:
        True if successful
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Saved JSON to {path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save JSON: {e}")
        return False


def load_json(file_path: Union[str, Path], default: Any = None) -> Any:
    """
    Load data from JSON file.
    
    Args:
        file_path: File to load
        default: Default value if file doesn't exist
    
    Returns:
        Loaded data or default
    """
    path = Path(file_path)
    
    if not path.exists():
        logger.debug(f"JSON file not found: {path}")
        return default
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        logger.debug(f"Loaded JSON from {path}")
        return data
        
    except Exception as e:
        logger.error(f"Failed to load JSON: {e}")
        return default


# Convenience functions
activity_logger = ActivityLogger()
