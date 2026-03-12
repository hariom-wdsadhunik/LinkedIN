"""
Login to LinkedIn and manage session authentication.

This script handles:
- Browser initialization with Playwright
- Cookie/session management
- MFA support (if enabled)
- Session persistence for reuse
- Clean logout

Usage:
    python execution/login_linkedin.py --action login
    python execution/login_linkedin.py --action check_session
    python execution/login_linkedin.py --action logout

Environment Variables Required:
    LINKEDIN_EMAIL
    LINKEDIN_PASSWORD
    LINKEDIN_MFA_SECRET (optional, for TOTP-based 2FA)
    BROWSER_HEADLESS (default: false)
    TIMEZONE (default: UTC)
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import pytz
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from execution.utils.logger import get_logger
from execution.utils.data_storage import ActivityLogger

# Configuration
LINKEDIN_URL = "https://www.linkedin.com"
LOGIN_URL = f"{LINKEDIN_URL}/login"
SESSION_FILE = Path(".tmp/session_cache/linkedin_session.json")
COOKIE_MAX_AGE = timedelta(days=30)

logger = get_logger(__name__)
activity_logger = ActivityLogger()


class LinkedInSession:
    """Manage LinkedIn browser sessions and authentication."""
    
    def __init__(self, headless: bool = False):
        """
        Initialize LinkedIn session manager.
        
        Args:
            headless: Run browser in headless mode (default: False for debugging)
        """
        self.email = os.getenv("LINKEDIN_EMAIL")
        self.password = os.getenv("LINKEDIN_PASSWORD")
        self.mfa_secret = os.getenv("LINKEDIN_MFA_SECRET")
        self.headless = headless or os.getenv("BROWSER_HEADLESS", "false").lower() == "true"
        
        if not self.email or not self.password:
            raise ValueError("LINKEDIN_EMAIL and LINKEDIN_PASSWORD must be set in .env")
        
        self.browser = None
        self.context = None
        self.page = None
        self.session_data: Dict[str, Any] = {}
        
    def start_browser(self) -> None:
        """Launch Playwright browser with anti-detection settings."""
        logger.info("Starting browser...")
        
        playwright = sync_playwright().start()
        
        # Browser launch arguments for stealth
        browser_args = {
            "headless": self.headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            ]
        }
        
        self.browser = playwright.chromium.launch(**browser_args)
        
        # Context configuration
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id=os.getenv("TIMEZONE", "UTC"),
            permissions=["geolocation"],
            geolocation={"latitude": 40.7128, "longitude": -74.0060}  # NYC
        )
        
        # Add init script to evade detection
        self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US']});
        """)
        
        self.page = self.context.new_page()
        logger.debug("Browser started successfully")
    
    def close_browser(self) -> None:
        """Close browser and cleanup resources."""
        if self.browser:
            logger.info("Closing browser...")
            self.browser.close()
            self.browser = None
            self.context = None
            self.page = None
    
    def save_session(self) -> None:
        """Save current session cookies to file for reuse."""
        if not self.context:
            return
        
        try:
            cookies = self.context.cookies()
            session_data = {
                "cookies": cookies,
                "timestamp": datetime.now().isoformat(),
                "email": self.email
            }
            
            SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SESSION_FILE, "w") as f:
                json.dump(session_data, f, indent=2)
            
            logger.info(f"Session saved to {SESSION_FILE}")
            
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def load_session(self) -> bool:
        """
        Load saved session cookies.
        
        Returns:
            True if session loaded successfully, False otherwise
        """
        if not SESSION_FILE.exists():
            logger.debug("No saved session found")
            return False
        
        try:
            with open(SESSION_FILE, "r") as f:
                session_data = json.load(f)
            
            # Check if session is expired
            timestamp = datetime.fromisoformat(session_data["timestamp"])
            if datetime.now() - timestamp > COOKIE_MAX_AGE:
                logger.info("Session expired (older than 30 days)")
                SESSION_FILE.unlink()
                return False
            
            # Verify email matches
            if session_data.get("email") != self.email:
                logger.info("Saved session is for different account")
                return False
            
            # Load cookies
            self.context.add_cookies(session_data["cookies"])
            logger.info("Loaded saved session")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return False
    
    def is_logged_in(self) -> bool:
        """
        Check if currently logged in by visiting LinkedIn homepage.
        
        Returns:
            True if authenticated, False otherwise
        """
        if not self.page:
            return False
        
        try:
            self.page.goto(LINKEDIN_URL, timeout=10000, wait_until="domcontentloaded")
            self.page.wait_for_timeout(3000)  # Wait for dynamic content
            
            # Check for feed element (only visible when logged in)
            is_logged = self.page.is_visible("div.feed-container") or \
                       self.page.is_visible("button[data-test-id='topbar-logo']") or \
                       "/feed/" in self.page.url
            
            logger.debug(f"Login status check: {'logged in' if is_logged else 'not logged in'}")
            return is_logged
            
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False
    
    def login(self) -> bool:
        """
        Perform LinkedIn login.
        
        Returns:
            True if login successful, False otherwise
        
        Raises:
            ValueError: If credentials missing
            Exception: If login fails after retries
        """
        logger.info("Attempting LinkedIn login...")
        
        if not self.page:
            self.start_browser()
        
        try:
            # Navigate to login page
            self.page.goto(LOGIN_URL, timeout=30000, wait_until="domcontentloaded")
            self.page.wait_for_timeout(2000)
            
            # Check if already logged in
            if self.is_logged_in():
                logger.info("Already logged in")
                self.save_session()
                return True
            
            # Find and fill email field
            logger.debug("Entering credentials...")
            email_field = self.page.locator('input[id="username"]')
            email_field.fill(self.email)
            
            # Find and fill password field
            password_field = self.page.locator('input[id="password"]')
            password_field.fill(self.password)
            
            # Click sign in button
            sign_in_button = self.page.locator('button[type="submit"]')
            sign_in_button.click()
            
            logger.debug("Submitted login form")
            self.page.wait_for_timeout(3000)
            
            # Handle MFA if enabled
            if self.page.is_visible('input[id="verificationCode"]'):
                logger.info("MFA detected, handling 2FA...")
                self._handle_mfa()
            
            # Wait for navigation to feed
            try:
                self.page.wait_for_url("*/feed/*", timeout=15000)
                self.page.wait_for_timeout(3000)
            except PlaywrightTimeout:
                logger.warning("Navigation to feed timed out, checking login status anyway")
            
            # Verify login success
            if self.is_logged_in():
                logger.info("✅ Login successful")
                self.save_session()
                activity_logger.log_action(
                    action_type="login",
                    result="success",
                    details={"method": "credentials"}
                )
                return True
            else:
                logger.error("❌ Login failed - unable to verify authentication")
                activity_logger.log_action(
                    action_type="login",
                    result="failure",
                    details={"reason": "authentication_failed"}
                )
                return False
                
        except PlaywrightTimeout as e:
            logger.error(f"Login timed out: {e}")
            activity_logger.log_action(
                action_type="login",
                result="failure",
                details={"reason": "timeout", "error": str(e)}
            )
            return False
            
        except Exception as e:
            logger.error(f"Login failed with error: {e}", exc_info=True)
            activity_logger.log_action(
                action_type="login",
                result="failure",
                details={"reason": "exception", "error": str(e)}
            )
            return False
    
    def _handle_mfa(self) -> None:
        """
        Handle Multi-Factor Authentication if enabled.
        
        Supports:
        - TOTP (Time-based One-Time Password) via secret key
        - Manual entry by user (fallback)
        """
        if self.mfa_secret:
            try:
                import pyotp
                totp = pyotp.TOTP(self.mfa_secret)
                code = totp.now()
                
                logger.debug("Entering MFA code from TOTP")
                mfa_input = self.page.locator('input[id="verificationCode"]')
                mfa_input.fill(code)
                
                submit_button = self.page.locator('button[type="submit"]')
                submit_button.click()
                
                self.page.wait_for_timeout(3000)
                logger.info("MFA code submitted")
                
            except ImportError:
                logger.warning("pyotp not installed, falling back to manual MFA entry")
                self._manual_mfa_entry()
            except Exception as e:
                logger.error(f"MFA automation failed: {e}")
                self._manual_mfa_entry()
        else:
            self._manual_mfa_entry()
    
    def _manual_mfa_entry(self) -> None:
        """Prompt user to manually enter MFA code."""
        logger.warning("=" * 60)
        logger.warning("MFA CODE REQUIRED")
        logger.warning("Please enter the 6-digit code from your authenticator app")
        logger.warning("You have 2 minutes before this expires")
        logger.warning("=" * 60)
        
        try:
            # Wait for user to enter code manually (max 2 minutes)
            self.page.wait_for_function(
                "() => document.querySelector('input[id=\"verificationCode\"]').value.length >= 6",
                timeout=120000
            )
            
            # Wait for submit button and click it
            submit_button = self.page.locator('button[type="submit"]')
            submit_button.click()
            
            self.page.wait_for_timeout(5000)
            logger.info("Manual MFA entry completed")
            
        except PlaywrightTimeout:
            logger.error("MFA entry timed out after 2 minutes")
            raise Exception("MFA verification failed")
    
    def logout(self) -> None:
        """Log out from LinkedIn and clear session."""
        logger.info("Logging out from LinkedIn...")
        
        try:
            if self.page and self.is_logged_in():
                # Navigate to me dropdown and click sign out
                self.page.goto(f"{LINKEDIN_URL}/me/settings/", timeout=15000)
                self.page.wait_for_timeout(2000)
                
                # Try to find sign out button
                sign_out_buttons = self.page.locator('button:has-text("Sign out")')
                if sign_out_buttons.count() > 0:
                    sign_out_buttons.first.click()
                    self.page.wait_for_timeout(3000)
                    logger.info("Logged out successfully")
                else:
                    logger.warning("Sign out button not found")
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
        
        finally:
            # Clear saved session
            if SESSION_FILE.exists():
                SESSION_FILE.unlink()
                logger.debug("Session file deleted")
            
            activity_logger.log_action(
                action_type="logout",
                result="success"
            )
            
            self.close_browser()
    
    def ensure_authenticated(self) -> bool:
        """
        Ensure valid LinkedIn session, login if needed.
        
        Returns:
            True if authenticated, False if login failed
        """
        logger.info("Ensuring authenticated session...")
        
        try:
            self.start_browser()
            
            # Try loading saved session
            if self.load_session() and self.is_logged_in():
                logger.info("✓ Valid session restored")
                return True
            
            # Session invalid or expired, perform fresh login
            logger.info("Performing fresh login...")
            return self.login()
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(description="LinkedIn Session Manager")
    parser.add_argument(
        "--action",
        choices=["login", "check_session", "logout", "ensure"],
        default="ensure",
        help="Action to perform"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )
    
    args = parser.parse_args()
    
    session = LinkedInSession(headless=args.headless)
    
    try:
        if args.action == "login":
            success = session.login()
            sys.exit(0 if success else 1)
            
        elif args.action == "check_session":
            session.start_browser()
            is_valid = session.load_session() and session.is_logged_in()
            print(json.dumps({"authenticated": is_valid}))
            session.close_browser()
            sys.exit(0 if is_valid else 1)
            
        elif args.action == "logout":
            session.ensure_authenticated()
            session.logout()
            sys.exit(0)
            
        elif args.action == "ensure":
            success = session.ensure_authenticated()
            if success:
                logger.info("Session ready for use")
                # Keep browser open for subsequent scripts to use
                # Caller should call session.close_browser() when done
                return session
            else:
                sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        session.close_browser()
        sys.exit(130)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        session.close_browser()
        sys.exit(1)


if __name__ == "__main__":
    main()
