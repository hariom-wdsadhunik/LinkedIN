"""
Rate limiting and safety enforcement for LinkedIn automation.

Ensures compliance with LinkedIn's usage limits and implements
human-like behavior patterns to avoid detection.
"""

import os
import sys
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.utils.logger import get_logger
from execution.utils.data_storage import activity_logger

logger = get_logger(__name__)

# Configuration - Safe Limits by Account Age/Maturity
LIMITS_BY_ACCOUNT_TIER = {
    "new": {  # < 3 months
        "connections_per_day": 10,
        "profiles_viewed_per_day": 30,
        "posts_per_day": 1,
        "messages_per_day": 10,
        "profile_visits_per_hour": 5
    },
    "established": {  # 3-12 months
        "connections_per_day": 20,
        "profiles_viewed_per_day": 60,
        "posts_per_day": 2,
        "messages_per_day": 15,
        "profile_visits_per_hour": 10
    },
    "premium": {  # > 1 year
        "connections_per_day": 30,
        "profiles_viewed_per_day": 100,
        "posts_per_day": 3,
        "messages_per_day": 25,
        "profile_visits_per_hour": 15
    }
}

# Default to established tier
DEFAULT_TIER = "established"

# Cooldown settings
COOLDOWN_BETWEEN_ACTIONS_MIN = 120  # 2 minutes
COOLDOWN_BETWEEN_ACTIONS_MAX = 300  # 5 minutes
COOLDOWN_AFTER_LIMIT_REACHED = 86400  # 24 hours


class RateLimiter:
    """Manage rate limits and enforce safe automation patterns."""
    
    def __init__(self, account_tier: Optional[str] = None):
        """
        Initialize rate limiter.
        
        Args:
            account_tier: Account maturity level (new/established/premium)
        """
        self.account_tier = account_tier or DEFAULT_TIER
        self.limits = LIMITS_BY_ACCOUNT_TIER.get(self.account_tier, LIMITS_BY_ACCOUNT_TIER["established"])
        
        # Override from environment if set
        self.limits["connections_per_day"] = int(os.getenv("MAX_CONNECTIONS_PER_DAY", self.limits["connections_per_day"]))
        self.limits["posts_per_day"] = int(os.getenv("MAX_POSTS_PER_DAY", self.limits["posts_per_day"]))
    
    def check_limit(self, action_type: str) -> Tuple[bool, int, int]:
        """
        Check if action is within daily limits.
        
        Args:
            action_type: Type of action to check
        
        Returns:
            Tuple of (can_proceed, current_count, limit)
        """
        # Map action types to limit keys
        type_map = {
            "connection_sent": "connections_per_day",
            "profile_viewed": "profiles_viewed_per_day",
            "post_published": "posts_per_day",
            "message_sent": "messages_per_day"
        }
        
        limit_key = type_map.get(action_type)
        if not limit_key:
            logger.debug(f"No rate limit defined for: {action_type}")
            return True, 0, 0
        
        limit = self.limits[limit_key]
        current_count = activity_logger.get_daily_count(action_type)
        
        can_proceed = current_count < limit
        
        logger.info(
            f"Rate limit check: {action_type} = {current_count}/{limit} "
            f"({'✓' if can_proceed else '✗'})"
        )
        
        return can_proceed, current_count, limit
    
    def increment_action(self, action_type: str, count: int = 1) -> None:
        """
        Increment action counter in database.
        
        Args:
            action_type: Type of action performed
            count: Amount to increment
        """
        activity_logger.update_rate_limit(action_type, count)
        logger.debug(f"Incremented {action_type} count by {count}")
    
    def enforce_cooldown(self, action_type: str) -> bool:
        """
        Enforce random cooldown between actions to mimic human behavior.
        
        Args:
            action_type: Type of action being performed
        
        Returns:
            True if cooldown applied, False if skipped
        """
        # Skip cooldown for certain actions
        skip_cooldown = ["login", "logout", "check_session"]
        
        if action_type in skip_cooldown:
            logger.debug(f"Skipping cooldown for {action_type}")
            return False
        
        # Random delay between min and max
        delay_seconds = random.randint(COOLDOWN_BETWEEN_ACTIONS_MIN, COOLDOWN_BETWEEN_ACTIONS_MAX)
        
        logger.info(f"Enforcing {delay_seconds}s cooldown before next {action_type}...")
        time.sleep(delay_seconds)
        
        return True
    
    def wait_if_needed(self, action_type: str) -> bool:
        """
        Check limits and wait if necessary.
        
        Args:
            action_type: Type of action to perform
        
        Returns:
            True if action can proceed, False if blocked
        """
        can_proceed, current, limit = self.check_limit(action_type)
        
        if not can_proceed:
            logger.warning(
                f"⚠️ Daily limit reached for {action_type} ({current}/{limit}). "
                f"Resuming tomorrow."
            )
            
            # Log the limit event
            activity_logger.log_action(
                action_type="rate_limit_reached",
                result="blocked",
                details={
                    "action_type": action_type,
                    "current_count": current,
                    "limit": limit
                }
            )
            
            return False
        
        # Apply cooldown
        self.enforce_cooldown(action_type)
        
        return True
    
    def get_daily_summary(self) -> Dict[str, Dict[str, int]]:
        """
        Get summary of all daily activities vs limits.
        
        Returns:
            Dictionary with action stats
        """
        today_stats = activity_logger.get_today_rate_limits()
        
        summary = {}
        
        for action_type, limit_key in [
            ("connection_sent", "connections_per_day"),
            ("profile_viewed", "profiles_viewed_per_day"),
            ("post_published", "posts_per_day"),
            ("message_sent", "messages_per_day")
        ]:
            current = today_stats.get(f"{action_type.replace('_sent', '_').replace('_viewed', '_')}_sent", 0)
            limit = self.limits.get(limit_key, 0)
            remaining = max(0, limit - current)
            percentage = (current / limit * 100) if limit > 0 else 0
            
            summary[action_type] = {
                "current": current,
                "limit": limit,
                "remaining": remaining,
                "percentage": round(percentage, 1)
            }
        
        return summary
    
    def print_daily_status(self) -> None:
        """Print formatted daily activity status to console."""
        summary = self.get_daily_summary()
        
        logger.info("=" * 60)
        logger.info("DAILY ACTIVITY SUMMARY")
        logger.info("=" * 60)
        
        for action_type, stats in summary.items():
            bar_length = 30
            filled = int(stats["percentage"] / 100 * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            status_icon = "✓" if stats["percentage"] < 100 else "⚠️"
            
            logger.info(
                f"{status_icon} {action_type.replace('_', ' ').title():20} | "
                f"{bar} | {stats['current']:3}/{stats['limit']} "
                f"({stats['remaining']} remaining)"
            )
        
        logger.info("=" * 60)


def human_delay(min_seconds: int = 2, max_seconds: int = 5) -> None:
    """
    Add human-like delay between actions.
    
    Args:
        min_seconds: Minimum delay
        max_seconds: Maximum delay
    """
    delay = random.uniform(min_seconds, max_seconds)
    logger.debug(f"Human delay: {delay:.1f}s")
    time.sleep(delay)


def random_wait_in_range(min_minutes: int = 2, max_minutes: int = 5) -> None:
    """
    Wait for a random period within specified range.
    
    Args:
        min_minutes: Minimum wait time
        max_minutes: Maximum wait time
    """
    wait_seconds = random.randint(min_minutes * 60, max_minutes * 60)
    logger.info(f"Waiting {wait_seconds // 60}m {wait_seconds % 60}s...")
    time.sleep(wait_seconds)


def is_within_business_hours() -> bool:
    """
    Check if current time is within typical business hours.
    
    Returns:
        True if between 8 AM and 6 PM local time
    """
    now = datetime.now()
    hour = now.hour
    
    # Business hours: 8 AM - 6 PM
    return 8 <= hour < 18


def is_weekend() -> bool:
    """
    Check if current day is weekend.
    
    Returns:
        True if Saturday (5) or Sunday (6)
    """
    return datetime.now().weekday() >= 5


def should_reduce_activity() -> bool:
    """
    Determine if activity should be reduced (weekends, holidays, etc.).
    
    Returns:
        True if should operate at reduced capacity
    """
    # Reduce activity on weekends
    if is_weekend():
        logger.info("Weekend detected - reducing activity by 50%")
        return True
    
    # Reduce activity outside business hours
    if not is_within_business_hours():
        logger.info("Outside business hours - reducing activity")
        return True
    
    return False


# Convenience instance
rate_limiter = RateLimiter()
