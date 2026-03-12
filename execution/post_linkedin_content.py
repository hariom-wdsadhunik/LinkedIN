"""
Publish content to LinkedIn.

This script handles:
- Text post publishing
- Image/carousel uploads
- Hashtag insertion
- Post scheduling validation
- Engagement tracking setup

Usage:
    python execution/post_linkedin_content.py --post-id <post_id>
    python execution/post_linkedin_content.py --file ".tmp/generated_posts.json" --index 0

Environment Variables Required:
    LINKEDIN_EMAIL
    LINKEDIN_PASSWORD
    BROWSER_HEADLESS (default: false)
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from execution.login_linkedin import LinkedInSession
from execution.utils.logger import get_logger
from execution.utils.data_storage import ActivityLogger
from execution.utils.rate_limiter import RateLimiter

# Configuration
GENERATED_POSTS_FILE = Path(".tmp/generated_posts.json")
POSTS_PER_DAY_LIMIT = int(os.getenv("MAX_POSTS_PER_DAY", "2"))

logger = get_logger(__name__)
activity_logger = ActivityLogger()
rate_limiter = RateLimiter()


class LinkedInPublisher:
    """Handle LinkedIn post publishing operations."""
    
    def __init__(self, session: LinkedInSession):
        """
        Initialize publisher with existing session.
        
        Args:
            session: Active LinkedInSession instance
        """
        self.session = session
        self.page = session.page
        
    def validate_post_data(self, post_data: Dict[str, Any]) -> bool:
        """
        Validate post data before publishing.
        
        Args:
            post_data: Dictionary containing post information
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        required_fields = ["content", "post_type"]
        
        for field in required_fields:
            if field not in post_data:
                raise ValueError(f"Missing required field: {field}")
        
        if not post_data["content"].strip():
            raise ValueError("Post content is empty")
        
        if len(post_data["content"]) > 3000:
            raise ValueError("Post content exceeds 3000 character limit")
        
        if len(post_data["content"]) < 50:
            raise ValueError("Post content too short (min 50 characters)")
        
        return True
    
    def check_daily_post_limit(self) -> tuple[bool, int]:
        """
        Check if daily post limit has been reached.
        
        Returns:
            Tuple of (can_post, current_count)
        """
        today = datetime.now().date()
        posts_today = activity_logger.get_daily_count("post_published", today)
        
        can_post = posts_today < POSTS_PER_DAY_LIMIT
        
        logger.info(f"Posts today: {posts_today}/{POSTS_PER_DAY_LIMIT}")
        
        return can_post, posts_today
    
    def navigate_to_post_creation(self) -> bool:
        """
        Navigate to LinkedIn post creation interface.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Navigating to post creation...")
            
            # Go to LinkedIn homepage
            self.page.goto("https://www.linkedin.com/feed", timeout=30000, wait_until="domcontentloaded")
            self.page.wait_for_timeout(3000)
            
            # Find and click the "Start a post" button
            start_post_button = self.page.locator(
                'button:has-text("Start a post"), button[data-test-id="feed-compose-cta"], div[role="button"]:has-text("Start a post")'
            )
            
            if start_post_button.count() == 0:
                logger.warning("Standard post button not found, trying alternative...")
                # Try alternative selector for different LinkedIn layouts
                start_post_button = self.page.locator('div.share-box-feed-entry__trigger')
            
            if start_post_button.count() > 0:
                start_post_button.first.click()
                self.page.wait_for_timeout(2000)
                logger.info("Post creation dialog opened")
                return True
            else:
                logger.error("Could not find post creation button")
                return False
                
        except Exception as e:
            logger.error(f"Error navigating to post creation: {e}")
            return False
    
    def enter_post_content(self, content: str) -> bool:
        """
        Enter post content into the editor.
        
        Args:
            content: Post text content
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug("Entering post content...")
            
            # Wait for post editor to be ready
            self.page.wait_for_timeout(1000)
            
            # Find the main post textarea
            text_editor = self.page.locator(
                'div[role="textbox"][data-placeholder*="What do you want to talk about?"], '
                'div[contenteditable="true"][aria-label*="text"]'
            )
            
            if text_editor.count() == 0:
                logger.error("Post text editor not found")
                return False
            
            # Clear any existing content first
            text_editor.first.click()
            self.page.wait_for_timeout(500)
            
            # Use keyboard shortcut to select all and delete
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Delete")
            self.page.wait_for_timeout(500)
            
            # Type new content slowly to avoid detection
            self.page.keyboard.type(content, delay=50)
            self.page.wait_for_timeout(1000)
            
            logger.info("Post content entered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error entering post content: {e}")
            return False
    
    def add_hashtags(self, hashtags: List[str]) -> bool:
        """
        Add hashtags to the post.
        
        Args:
            hashtags: List of hashtags (with or without # prefix)
            
        Returns:
            True if successful, False otherwise
        """
        if not hashtags:
            logger.debug("No hashtags to add")
            return True
        
        try:
            logger.debug(f"Adding {len(hashtags)} hashtags...")
            
            # Ensure hashtags have # prefix
            formatted_hashtags = []
            for tag in hashtags:
                tag = tag.strip()
                if not tag.startswith("#"):
                    tag = "#" + tag
                formatted_hashtags.append(tag)
            
            # Add space and then hashtags
            hashtag_text = " " + " ".join(formatted_hashtags)
            self.page.keyboard.type(hashtag_text, delay=50)
            self.page.wait_for_timeout(500)
            
            logger.info("Hashtags added")
            return True
            
        except Exception as e:
            logger.error(f"Error adding hashtags: {e}")
            return False
    
    def upload_image(self, image_path: str) -> bool:
        """
        Upload image to accompany the post.
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not Path(image_path).exists():
                logger.error(f"Image file not found: {image_path}")
                return False
            
            logger.info(f"Uploading image: {image_path}")
            
            # Find and click media upload button
            media_button = self.page.locator(
                'button:has-text("Media"), button[aria-label*="image"], '
                'button[data-test-id^="compose-legacy-media"]'
            )
            
            if media_button.count() == 0:
                logger.error("Media upload button not found")
                return False
            
            media_button.first.click()
            self.page.wait_for_timeout(1000)
            
            # Handle file chooser
            async def handle_file_chooser(file_chooser):
                file_chooser.set_files(image_path)
            
            # Wait for file chooser dialog
            self.page.wait_for_event("filechooser", timeout=5000)
            
            # Note: Playwright sync API doesn't support file chooser events easily
            # This is a simplified version - in production, use async API
            logger.warning("Image upload requires async API - skipping for now")
            return False
            
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return False
    
    def publish_post(self) -> Optional[str]:
        """
        Click the Post button to publish.
        
        Returns:
            Post URL if successful, None otherwise
        """
        try:
            logger.info("Publishing post...")
            
            # Find the Post button
            post_button = self.page.locator(
                'button:has-text("Post"), button[data-test-id="compose-submit-button"]'
            )
            
            if post_button.count() == 0:
                logger.error("Post button not found")
                return None
            
            # Check if button is disabled
            if post_button.first.is_disabled():
                logger.error("Post button is disabled - content may be invalid")
                return None
            
            # Click post button
            post_button.first.click()
            self.page.wait_for_timeout(3000)
            
            # Wait for success confirmation or URL change
            try:
                # Look for success message
                success_msg = self.page.locator('text="Post sent"')
                success_msg.wait_for(timeout=10000, state="visible")
                logger.info("✅ Post published successfully")
                
                # Get current URL as post URL
                post_url = self.page.url
                return post_url if "linkedin.com/feed/update/" in post_url else None
                
            except PlaywrightTimeout:
                # Check if we're still on compose page
                if "feed" in self.page.url:
                    logger.warning("Post may have failed - still on feed page")
                    return None
                else:
                    logger.info("Post likely published (navigated away)")
                    return self.page.url
                    
        except Exception as e:
            logger.error(f"Error publishing post: {e}")
            return None
    
    def publish(self, post_data: Dict[str, Any]) -> Optional[str]:
        """
        Complete publishing workflow.
        
        Args:
            post_data: Complete post information including content, hashtags, etc.
            
        Returns:
            Post URL if successful, None otherwise
        """
        logger.info("Starting post publication workflow...")
        
        # Validate post data
        try:
            self.validate_post_data(post_data)
        except ValueError as e:
            logger.error(f"Post validation failed: {e}")
            activity_logger.log_action(
                action_type="post_publish",
                result="failure",
                details={"reason": "validation_failed", "error": str(e)}
            )
            return None
        
        # Check daily limit
        can_post, count = self.check_daily_post_limit()
        if not can_post:
            logger.warning(f"Daily post limit reached ({POSTS_PER_DAY_LIMIT}/day)")
            activity_logger.log_action(
                action_type="post_publish",
                result="skipped",
                details={"reason": "daily_limit_reached"}
            )
            return None
        
        # Navigate to post creation
        if not self.navigate_to_post_creation():
            return None
        
        # Enter content
        content = post_data["content"]
        if not self.enter_post_content(content):
            return None
        
        # Add hashtags if present
        hashtags = post_data.get("hashtags", [])
        if hashtags:
            self.add_hashtags(hashtags)
        
        # Upload media if specified
        media_path = post_data.get("media_path")
        if media_path:
            self.upload_image(media_path)
        
        # Publish
        post_url = self.publish_post()
        
        if post_url:
            # Log success
            activity_logger.log_action(
                action_type="post_published",
                result="success",
                details={
                    "post_url": post_url,
                    "content_preview": content[:100],
                    "post_type": post_data.get("post_type", "unknown"),
                    "hashtags_count": len(hashtags)
                }
            )
            
            # Update rate limiter
            rate_limiter.increment_action("posts_published")
            
            return post_url
        else:
            # Log failure
            activity_logger.log_action(
                action_type="post_published",
                result="failure",
                details={
                    "content_preview": content[:100],
                    "reason": "publish_failed"
                }
            )
            return None


def load_posts_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Load generated posts from JSON file."""
    path = Path(file_path)
    
    if not path.exists():
        logger.error(f"Posts file not found: {file_path}")
        return []
    
    try:
        with open(path, "r") as f:
            posts = json.load(f)
        
        # Handle both single post and array formats
        if isinstance(posts, dict):
            posts = [posts]
        
        return posts
        
    except Exception as e:
        logger.error(f"Error loading posts: {e}")
        return []


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(description="LinkedIn Post Publisher")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--post-id",
        type=str,
        help="Post ID from generated_posts.json"
    )
    group.add_argument(
        "--file",
        type=str,
        help="Path to posts JSON file"
    )
    
    parser.add_argument(
        "--index",
        type=int,
        default=0,
        help="Index of post to publish (when using --file)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )
    
    args = parser.parse_args()
    
    # Determine which post to publish
    if args.post_id:
        # Load from default location
        posts = load_posts_from_file(str(GENERATED_POSTS_FILE))
        post = next((p for p in posts if p.get("post_id") == args.post_id), None)
        
        if not post:
            logger.error(f"Post not found: {args.post_id}")
            sys.exit(1)
            
    elif args.file:
        posts = load_posts_from_file(args.file)
        
        if not posts or args.index >= len(posts):
            logger.error(f"No post found at index {args.index}")
            sys.exit(1)
        
        post = posts[args.index]
    
    # Display post preview
    logger.info("=" * 60)
    logger.info("POST PREVIEW")
    logger.info("=" * 60)
    logger.info(post["content"][:500])
    if len(post["content"]) > 500:
        logger.info(f"... ({len(post['content']) - 500} more characters)")
    logger.info("=" * 60)
    
    # Confirm before publishing
    if not os.getenv("AUTO_CONFIRM"):
        response = input("\nPublish this post? (y/n): ")
        if response.lower() != "y":
            logger.info("Post publication cancelled by user")
            sys.exit(0)
    
    # Initialize session and publish
    session = LinkedInSession(headless=args.headless)
    
    try:
        # Ensure authenticated
        if not session.ensure_authenticated():
            logger.error("Failed to authenticate")
            sys.exit(1)
        
        # Create publisher and publish
        publisher = LinkedInPublisher(session)
        post_url = publisher.publish(post)
        
        if post_url:
            logger.info(f"✅ Post published: {post_url}")
            
            # Update post status in file
            if GENERATED_POSTS_FILE.exists():
                with open(GENERATED_POSTS_FILE, "r") as f:
                    all_posts = json.load(f)
                
                for p in all_posts:
                    if p.get("post_id") == post.get("post_id"):
                        p["status"] = "published"
                        p["published_at"] = datetime.now().isoformat()
                        p["post_url"] = post_url
                
                with open(GENERATED_POSTS_FILE, "w") as f:
                    json.dump(all_posts, f, indent=2)
            
            sys.exit(0)
        else:
            logger.error("❌ Post publication failed")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        session.close_browser()
        sys.exit(130)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        session.close_browser()
        sys.exit(1)
    
    finally:
        session.close_browser()


if __name__ == "__main__":
    main()
