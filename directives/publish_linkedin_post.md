# Directive: Publish LinkedIn Post

## Purpose

Safely publish generated LinkedIn posts while respecting rate limits, validating content quality, and ensuring successful publication.

---

## Inputs

**Required:**
- `post_id`: ID of post from `.tmp/generated_posts.json`
- OR `post_data`: Complete post object with content, hashtags, etc.

**Optional:**
- `scheduled_time`: Specific time to publish (if scheduling)
- `auto_confirm`: Skip manual confirmation (default: false)
- `media_path`: Path to image/media file to attach

---

## Execution Scripts Used

1. **`execution/login_linkedin.py`** - Ensure authenticated session
2. **`execution/post_linkedin_content.py`** - Main publishing logic
3. **`execution/check_rate_limits.py`** - Verify within daily limits

---

## Step-by-Step Process

### Phase 1: Pre-Publication Checks

1. **Load post data**
   - Read `.tmp/generated_posts.json`
   - Find post by ID
   - Validate post exists and is in "draft" status

2. **Verify rate limits**
   - Check daily post count
   - Ensure < MAX_POSTS_PER_DAY (default: 2)
   - If limit reached, queue for tomorrow

3. **Content validation**
   - Check for prohibited content (sales pitches, spam)
   - Verify character count (1000-3000 optimal)
   - Validate hashtag count (3-5 recommended)
   - Ensure call-to-action present

4. **User confirmation** (unless auto_confirm=true)
   - Display post preview
   - Show current daily stats
   - Ask for final approval

### Phase 2: Authentication & Session

5. **Ensure LinkedIn session**
   - Run `login_linkedin.py --action ensure`
   - Load saved cookies if available
   - Perform fresh login if needed
   - Handle MFA if enabled

6. **Session validation**
   - Navigate to LinkedIn homepage
   - Verify logged in successfully
   - Check for any LinkedIn warnings/restrictions

### Phase 3: Publication

7. **Navigate to post creation**
   - Go to linkedin.com/feed
   - Click "Start a post" button
   - Wait for editor to load

8. **Enter content**
   - Clear any placeholder text
   - Type post content with human-like delays
   - Add line breaks and formatting

9. **Add hashtags**
   - Append 3-5 relevant hashtags
   - Ensure proper spacing

10. **Attach media** (if provided)
    - Click media upload button
    - Select image file
    - Wait for upload to complete
    - Add alt text if required

11. **Publish**
    - Click "Post" button
    - Wait for success confirmation
    - Capture post URL
    - Screenshot for records (optional)

### Phase 4: Post-Publication

12. **Update records**
    - Mark post as "published" in JSON
    - Add published timestamp
    - Store post URL
    - Update SQLite posts table

13. **Log activity**
    - Record publication event
    - Track engagement metrics baseline
    - Update daily counter

14. **Clean exit**
    - Close browser gracefully
    - Save session cookies
    - Log completion

---

## Expected Outputs

**Primary Output:**
- Published LinkedIn post with URL
- Updated post status in `.tmp/generated_posts.json`

**Secondary Outputs:**
- Activity log entry in database
- Console confirmation message
- Daily post count incremented

**Success Criteria:**
- ✅ Post visible on LinkedIn profile
- ✅ Post URL captured and stored
- ✅ No LinkedIn errors or warnings
- ✅ Within daily limits
- ✅ Proper logging completed

---

## Error Handling

| Error | Detection | Response |
|-------|-----------|----------|
| Session expired | Login check fails | Re-authenticate and retry |
| Daily limit reached | Count >= MAX_POSTS_PER_DAY | Queue for next day, notify user |
| Content rejected | LinkedIn error message | Review content guidelines, edit post |
| Network timeout | Request timeout | Retry up to 3 times with backoff |
| Media upload failed | Upload error | Continue without media or abort |
| Post button disabled | UI element disabled | Check content validity, debug |
| CAPTCHA detected | CAPTCHA challenge shown | Stop automation, alert user |
| Account restriction | Warning banner shown | Halt all automation, notify user |

---

## Edge Cases

### 1. Very Long Posts
**Scenario**: Content > 3000 characters
**Handling**: Truncate with ellipsis, suggest splitting into thread

### 2. Special Characters/Emojis
**Scenario**: Post contains emojis or unicode
**Handling**: Validate encoding, test rendering, use sparingly

### 3. External Links
**Scenario**: Post includes URLs
**Handling**: Shorten links, add UTM parameters, verify preview renders

### 4. Mention Tags (@person)
**Scenario**: Tagging connections
**Handling**: Ensure proper tag format, verify tags resolve correctly

### 5. Duplicate Content
**Scenario**: Similar to recent post
**Handling**: Check uniqueness score, suggest modifications

### 6. Timezone Mismatch
**Scenario**: Scheduled time vs actual time off
**Handling**: Use consistent timezone (from .env), convert properly

---

## Safety Mechanisms

### Posting Frequency
- Max 2 posts per day (established accounts)
- Minimum 4 hours between posts
- Reduce to 1 post/day on weekends

### Content Quality
- No false/misleading claims
- No overly promotional language
- Respectful discourse only
- Proper attribution for quotes/data

### Account Protection
- Human-like typing delays (50ms per character)
- Random pauses between actions
- Browser fingerprint rotation
- Session cookie persistence

---

## Manual Override

User can intervene at any point:
- Press Ctrl+C to cancel operation
- Set `AUTO_CONFIRM=false` to require approval
- Manually review post before publishing
- Abort if LinkedIn shows warnings

---

## Related Directives

- **create_linkedin_post.md** - Previous step: generate content
- **content_scheduler.md** - Schedule future posts
- **engagement_tracking.md** - Monitor post performance
- **safety_rate_limits.md** - Overall safety policies

---

*Last Updated: 2026-03-13*  
*Version: 1.0*
