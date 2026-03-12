"""
Browser configuration for Playwright.

Handles:
- Browser launch settings
- Anti-detection configurations
- User agent rotation
- Viewport randomization
"""

import os
import sys
import random
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.utils.logger import get_logger

logger = get_logger(__name__)

# Realistic User Agents (rotate to avoid detection)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
]

# Common viewport sizes
VIEWPORT_SIZES = {
    "desktop": {"width": 1920, "height": 1080},
    "laptop": {"width": 1366, "height": 768},
    "large_desktop": {"width": 2560, "height": 1440},
}


def get_random_user_agent() -> str:
    """Get a random user agent string."""
    return random.choice(USER_AGENTS)


def get_random_viewport() -> Dict[str, int]:
    """Get a random viewport size."""
    return random.choice(list(VIEWPORT_SIZES.values()))


def get_browser_args(headless: bool = False) -> Dict[str, Any]:
    """
    Get browser launch arguments with anti-detection settings.
    
    Args:
        headless: Run in headless mode
    
    Returns:
        Dictionary of browser arguments
    """
    return {
        "headless": headless,
        "args": [
            # Anti-detection flags
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-web-security",
            "--disable-features=IsolateOrigins,site-per-process",
            
            # Additional stealth
            "--disable-site-isolation-trials",
            "--disable-features=AudioVideoOutOfProcess",
            "--disable-background-networking",
            "--disable-default-apps",
            "--disable-extensions",
            "--disable-sync",
            "--disable-translate",
            "--hide-scrollbars",
            "--metrics-recording-only",
            "--mute-audio",
            "--no-first-run",
            "--safebrowsing-disable-auto-update",
            
            # Performance optimizations
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--ignore-certificate-errors",
            "--allow-running-insecure-content",
        ],
        "ignore_default_args": [
            "--enable-automation",
        ]
    }


def get_context_options(
    user_agent: Optional[str] = None,
    viewport: Optional[Dict[str, int]] = None,
    timezone_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get browser context options.
    
    Args:
        user_agent: Specific user agent (random if not provided)
        viewport: Specific viewport (random if not provided)
        timezone_id: Timezone identifier
    
    Returns:
        Dictionary of context options
    """
    return {
        "user_agent": user_agent or get_random_user_agent(),
        "viewport": viewport or get_random_viewport(),
        "locale": "en-US",
        "timezone_id": timezone_id or os.getenv("TIMEZONE", "UTC"),
        "permissions": ["geolocation"],
        "geolocation": {
            "latitude": 40.7128,  # NYC
            "longitude": -74.0060
        },
        "color_scheme": "light",
        "accept_downloads": True,
        "extra_http_headers": {
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Upgrade-Insecure-Requests": "1"
        }
    }


def get_stealth_scripts() -> list:
    """
    Get JavaScript scripts to run on page init for stealth.
    
    Returns:
        List of JavaScript code strings
    """
    return [
        # Hide webdriver property
        """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """,
        
        # Mock plugins
        """
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        """,
        
        # Mock languages
        """
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        """,
        
        # Mock connection
        """
        Object.defineProperty(navigator, 'connection', {
            get: () => ({
                effectiveType: '4g',
                rtt: 50,
                downlink: 10,
                saveData: false
            })
        });
        """,
        
        # Mock hardware concurrency
        """
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });
        """,
        
        # Mock device memory
        """
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8
        });
        """,
        
        # Override permissions
        """
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        """
    ]


def apply_stealth_mode(page) -> None:
    """
    Apply all stealth scripts to a page.
    
    Args:
        page: Playwright page object
    """
    scripts = get_stealth_scripts()
    
    for script in scripts:
        try:
            page.add_init_script(script)
        except Exception as e:
            logger.warning(f"Failed to add stealth script: {e}")
    
    logger.debug("Stealth mode applied to page")


def simulate_human_movement(page, duration_ms: int = 1000) -> None:
    """
    Simulate human-like mouse movements.
    
    Args:
        page: Playwright page object
        duration_ms: Duration of movement
    """
    try:
        # Get current mouse position
        viewport = page.viewport_size
        
        if viewport:
            # Random small movements
            for _ in range(random.randint(3, 7)):
                x = random.randint(100, viewport["width"] - 100)
                y = random.randint(100, viewport["height"] - 100)
                
                page.mouse.move(x, y, steps=random.randint(10, 30))
                page.wait_for_timeout(random.randint(50, 200))
        
        logger.debug("Human mouse movement simulated")
        
    except Exception as e:
        logger.warning(f"Failed to simulate mouse movement: {e}")


async def scroll_page_humanly(page) -> None:
    """
    Scroll page in a human-like pattern.
    
    Args:
        page: Playwright page object
    """
    try:
        # Get page height
        page_height = await page.evaluate("document.body.scrollHeight")
        viewport_height = page.viewport_size["height"]
        
        # Scroll in chunks with pauses
        current_position = 0
        while current_position < page_height - viewport_height:
            scroll_amount = random.randint(100, 300)
            current_position += scroll_amount
            
            await page.evaluate(f"window.scrollTo(0, {current_position})")
            page.wait_for_timeout(random.randint(500, 2000))
            
            # Sometimes scroll back up slightly
            if random.random() < 0.2:
                back_amount = random.randint(20, 100)
                current_position -= back_amount
                await page.evaluate(f"window.scrollTo(0, {current_position})")
                page.wait_for_timeout(random.randint(200, 500))
        
        logger.debug("Human scrolling simulated")
        
    except Exception as e:
        logger.warning(f"Failed to simulate scrolling: {e}")
