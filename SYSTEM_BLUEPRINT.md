# LinkedIn Manager - System Blueprint

## Overview

A sophisticated LinkedIn automation system built on a 3-layer architecture (Directives → Orchestration → Execution) that manages posting, networking, and engagement tracking while respecting platform safety limits.

---

## 1. Folder Structure

```
LinkedIN/
├── .tmp/                          # Temporary/intermediate files
│   ├── generated_posts.json       # Queue of posts ready to publish
│   ├── target_profiles.json       # Scraped profile data
│   ├── scheduled_posts.json       # Posts scheduled for future dates
│   ├── engagement_metrics.json    # Tracked engagement data
│   ├── activity_log.json          # Daily activity tracker
│   └── session_cache/             # Browser session data
│
├── directives/                    # SOP documentation (Layer 1)
│   ├── create_linkedin_post.md
│   ├── publish_linkedin_post.md
│   ├── find_target_profiles.md
│   ├── send_connection_requests.md
│   ├── monitor_account_activity.md
│   ├── engagement_tracking.md
│   ├── content_scheduler.md
│   └── safety_rate_limits.md
│
├── execution/                     # Deterministic Python scripts (Layer 3)
│   ├── __init__.py
│   ├── login_linkedin.py          # Authentication & session management
│   ├── post_linkedin_content.py   # Post publishing logic
│   ├── scrape_profiles.py         # Profile data extraction
│   ├── send_connection_request.py # Connection request automation
│   ├── get_notifications.py       # Activity monitoring
│   ├── get_engagement_metrics.py  # Analytics collection
│   ├── schedule_post.py           # Content scheduling
│   ├── generate_post_content.py   # AI-assisted post creation
│   ├── check_rate_limits.py       # Safety validation
│   └── utils/
│       ├── browser_config.py      # Playwright configuration
│       ├── rate_limiter.py        # Rate limit enforcement
│       ├── data_storage.py        # SQLite/file operations
│       └── logger.py              # Logging configuration
│
├── .env                           # Credentials (LINKEDIN_EMAIL, LINKEDIN_PASSWORD, etc.)
├── .gitignore
├── requirements.txt               # Python dependencies
└── AGENTS.md                      # Architecture documentation
```

---

## 2. Directives Required (Layer 1)

### 2.1 `create_linkedin_post.md`
**Purpose**: Generate high-quality LinkedIn posts using templates  
**Inputs**: Topic, post type (story/value/contrarian/insight/learning), tone, key points  
**Scripts**: `execution/generate_post_content.py`, `execution/check_rate_limits.py`  
**Process**:
1. Validate topic appropriateness
2. Select appropriate template
3. Generate draft content
4. Check against duplicate posts
5. Save to `.tmp/generated_posts.json`
**Outputs**: Draft post in queue  
**Error Handling**: Invalid topics, duplicate detection failures  
**Edge Cases**: Empty input, overly promotional content

### 2.2 `publish_linkedin_post.md`
**Purpose**: Safely publish posts to LinkedIn  
**Inputs**: Post ID from queue, scheduling preferences  
**Scripts**: `execution/login_linkedin.py`, `execution/post_linkedin_content.py`, `execution/check_rate_limits.py`  
**Process**:
1. Verify LinkedIn session
2. Check daily post limits
3. Validate content formatting
4. Publish with appropriate media
5. Log publication timestamp
6. Remove from queue
**Outputs**: Published post confirmation, activity log update  
**Error Handling**: Session expiry, posting failures, rate limit exceeded  
**Edge Cases**: Network failures mid-post, duplicate posts

### 2.3 `find_target_profiles.md`
**Purpose**: Identify and scrape relevant professional profiles  
**Inputs**: Industry, job title keywords, geography, company names  
**Scripts**: `execution/login_linkedin.py`, `execution/scrape_profiles.py`  
**Process**:
1. Build search queries from criteria
2. Execute LinkedIn search
3. Scrape profile data (name, title, company, location)
4. Filter by relevance score
5. Store in `.tmp/target_profiles.json`
6. Respect scraping rate limits
**Outputs**: Structured profile database  
**Error Handling**: Search result pagination, blocked selectors  
**Edge Cases**: Empty results, private profiles

### 2.4 `send_connection_requests.md`
**Purpose**: Send personalized connection requests at scale  
**Inputs**: Target profile list, optional message templates  
**Scripts**: `execution/login_linkedin.py`, `execution/send_connection_request.py`, `execution/check_rate_limits.py`  
**Process**:
1. Load target profiles
2. Verify daily connection limit not exceeded
3. Navigate to each profile
4. Click "Connect" button
5. Add personalized note (if provided)
6. Track sent requests
7. Update activity log
**Outputs**: Connection request confirmations  
**Error Handling**: Profiles no longer available, CAPTCHA challenges  
**Edge Cases**: Already connected, premium account required

### 2.5 `monitor_account_activity.md`
**Purpose**: Track notifications, messages, and profile views  
**Inputs**: None (automated check)  
**Scripts**: `execution/login_linkedin.py`, `execution/get_notifications.py`  
**Process**:
1. Authenticate to LinkedIn
2. Navigate to notifications page
3. Extract new notifications since last check
4. Categorize (likes, comments, connection requests, mentions)
5. Store in `.tmp/activity_log.json`
**Outputs**: Activity summary report  
**Error Handling**: Notification feed changes, session timeout  
**Edge Cases**: No new activity, notification overload

### 2.6 `engagement_tracking.md`
**Purpose**: Measure post performance metrics  
**Inputs**: Date range, specific post URLs  
**Scripts**: `execution/login_linkedin.py`, `execution/get_engagement_metrics.py`  
**Process**:
1. Access analytics dashboard
2. Extract impressions, likes, comments, shares per post
3. Calculate engagement rates
4. Store historical data
5. Generate trend reports
**Outputs**: Engagement metrics database, performance insights  
**Error Handling**: Analytics page structure changes  
**Edge Cases**: New posts with zero data, premium analytics features

### 2.7 `content_scheduler.md`
**Purpose**: Manage posting calendar and frequency  
**Inputs**: Generated posts, desired posting times, frequency rules  
**Scripts**: `execution/schedule_post.py`, `execution/check_rate_limits.py`  
**Process**:
1. Load post queue
2. Check optimal posting times
3. Verify frequency compliance (max 1-2 posts/day)
4. Schedule posts in `.tmp/scheduled_posts.json`
5. Trigger publishing at scheduled time
**Outputs**: Scheduled post queue, automated publishing triggers  
**Error Handling**: Scheduling conflicts, missed windows  
**Edge Cases**: Timezone changes, weekend/holiday rules

### 2.8 `safety_rate_limits.md`
**Purpose**: Enforce LinkedIn usage limits to avoid restrictions  
**Inputs**: Current activity counts, account age/tier  
**Scripts**: `execution/check_rate_limits.py`  
**Process**:
1. Load daily activity from logs
2. Compare against safe limits:
   - Connections: 20-30/day (new accounts: 10/day)
   - Profile views: 50-100/day
   - Posts: 1-2/day
   - Messages: 15-20/day
3. Block actions if limits reached
4. Implement cooldown periods
5. Log all limit checks
**Outputs**: Go/no-go decisions for actions  
**Error Handling**: Missing activity data  
**Edge Cases**: Account restrictions, temporary bans

---

## 3. Execution Scripts Required (Layer 3)

### Core Automation Scripts

| Script | Purpose | Key Functions |
|--------|---------|---------------|
| `login_linkedin.py` | Session management | Browser launch, cookie handling, MFA support |
| `post_linkedin_content.py` | Publishing | Text posts, image uploads, hashtag insertion |
| `scrape_profiles.py` | Data extraction | Search execution, profile parsing, pagination |
| `send_connection_request.py` | Networking | Connect button clicks, message injection |
| `get_notifications.py` | Monitoring | Notification extraction, categorization |
| `get_engagement_metrics.py` | Analytics | Dashboard scraping, metric calculation |
| `schedule_post.py` | Timing | Cron-like scheduling, timezone handling |
| `generate_post_content.py` | Content creation | Template filling, uniqueness validation |
| `check_rate_limits.py` | Safety | Limit validation, cooldown enforcement |

### Utility Modules (`execution/utils/`)

| Module | Purpose |
|--------|---------|
| `browser_config.py` | Playwright setup, headless mode, user agent rotation |
| `rate_limiter.py` | Throttling, random delays, human-like behavior |
| `data_storage.py` | SQLite schema, JSON file I/O, data versioning |
| `logger.py` | Structured logging, error tracking, audit trails |

---

## 4. Data Flow Between Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     USER REQUEST                            │
│  "Create a post about AI trends"                            │
│  "Find software engineers in NYC"                           │
│  "Send 10 connection requests"                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              LAYER 1: DIRECTIVES                            │
│  Read SOP → Understand process → Identify scripts needed    │
│  Example: directives/create_linkedin_post.md                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           LAYER 2: ORCHESTRATION (The Agent)                │
│  1. Parse directive                                         │
│  2. Validate inputs                                         │
│  3. Call execution scripts in order                         │
│  4. Handle errors                                           │
│  5. Ask for missing info                                    │
│  6. Store intermediates in .tmp/                            │
│  7. Update directive with learnings                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            LAYER 3: EXECUTION                               │
│  Deterministic Python scripts perform actual work:          │
│  - API calls                                                │
│  - Browser automation                                       │
│  - Data parsing                                             │
│  - File storage                                             │
│  - Rate limit enforcement                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   OUTPUTS                                   │
│  - .tmp/generated_posts.json                                │
│  - .tmp/target_profiles.json                                │
│  - .tmp/activity_log.json                                   │
│  - Published LinkedIn content                               │
│  - Sent connection requests                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Automation Cycle (Daily Workflow)

### Morning Cycle (9:00 AM)
1. **Check Notifications** (5 min)
   - Run `monitor_account_activity.md`
   - Review overnight engagement
   - Respond to urgent messages

2. **Publish Scheduled Post** (10 min)
   - Run `content_scheduler.md`
   - Execute `publish_linkedin_post.md`
   - Verify post went live

3. **Send Connection Requests** (15 min)
   - Run `find_target_profiles.md` (if list empty)
   - Execute `send_connection_requests.md` (up to daily limit)
   - Update activity log

### Afternoon Cycle (2:00 PM)
1. **Engagement Check** (10 min)
   - Run `engagement_tracking.md`
   - Analyze morning post performance
   - Log metrics

2. **Content Creation** (20 min)
   - Run `create_linkedin_post.md`
   - Generate 2-3 post drafts
   - Add to scheduled queue

### Evening Cycle (6:00 PM)
1. **Final Activity Check** (5 min)
   - Monitor afternoon engagement
   - Track new connections accepted
   - Update daily summary

2. **Safety Validation** (2 min)
   - Run `safety_rate_limits.md`
   - Ensure all limits respected
   - Reset counters if new day

### Weekly Tasks (Friday)
- Review weekly engagement trends
- Adjust targeting criteria based on acceptance rates
- Generate weekly performance report
- Archive old activity logs

---

## 6. Safety Mechanisms

### 6.1 Rate Limits by Account Type

| Action | New Accounts (<3 mo) | Established (3-12 mo) | Premium (>1 yr) |
|--------|---------------------|----------------------|-----------------|
| Connection requests/day | 10 | 20-25 | 30-40 |
| Profile views/day | 30 | 60-80 | 100-120 |
| Posts/day | 1 | 1-2 | 2-3 |
| Messages/day | 10 | 15-20 | 25-30 |

### 6.2 Cooldown Implementation

```python
# Pseudo-code for rate limiter
def check_and_wait(action_type):
    daily_count = get_daily_count(action_type)
    limit = get_limit_for_account(action_type)
    
    if daily_count >= limit:
        log(f"Daily limit reached for {action_type}")
        schedule_for_tomorrow(action_type)
        return False
    
    # Random delay between actions (2-5 minutes)
    delay = random.randint(120, 300)
    sleep(delay)
    
    return True
```

### 6.3 Human-Like Behavior

- Random delays between actions (2-5 min)
- Vary activity times (don't post exactly at 9 AM daily)
- Mix action types (don't only send connections)
- Take breaks (no activity for 1-2 hours periodically)
- Weekend reduction (50% activity on Sat/Sun)

### 6.4 Detection Avoidance

- Use realistic user agents
- Maintain consistent IP address
- Don't automate during LinkedIn maintenance windows
- Stop immediately on CAPTCHA detection
- Log out cleanly after sessions

### 6.5 Failure Recovery

```
IF CAPTCHA detected:
    1. Stop all automation
    2. Alert user to solve manually
    3. Wait 24 hours before resuming
    4. Reduce future activity by 30%

IF session expired:
    1. Attempt re-authentication
    2. If MFA required, alert user
    3. Resume queued actions after login

IF action fails 3+ times:
    1. Skip to next action
    2. Log failure pattern
    3. Update selector/strategy
    4. Test fix before resuming
```

---

## 7. Logging System

### 7.1 Log Levels

| Level | Usage | Examples |
|-------|-------|----------|
| DEBUG | Detailed diagnostic info | Selector found, button clicked |
| INFO | Normal operations | Post published, connection sent |
| WARNING | Recoverable issues | Rate limit approaching, retry needed |
| ERROR | Failures requiring attention | Login failed, element not found |
| CRITICAL | System halted | Account restricted, legal risk |

### 7.2 Log Structure

```json
{
  "timestamp": "2026-03-13T09:15:23Z",
  "level": "INFO",
  "module": "post_linkedin_content",
  "action": "post_published",
  "details": {
    "post_id": "urn:li:share:7041234567890",
    "content_preview": "Excited to share...",
    "media_type": "image",
    "scheduled_time": "09:00:00"
  },
  "session_id": "abc123xyz"
}
```

### 7.3 Log Storage

- **Console**: Real-time debugging during execution
- **File**: `logs/linkedin_manager_YYYY-MM-DD.log` (daily rotation)
- **Database**: SQLite table for querying and reporting
- **Activity Log**: `.tmp/activity_log.json` for quick reference

### 7.4 Audit Trail Requirements

All actions must log:
- Timestamp (UTC + local timezone)
- Action type (post, connect, view, message)
- Target (profile URL, post content)
- Result (success/failure + reason)
- Rate limit status before/after
- Session identifier

### 7.5 Alert System

Critical events trigger immediate user notification:
- Account restriction warnings
- CAPTCHA challenges
- Unusual activity patterns
- Credential expiry
- Persistent automation failures

---

## 8. Post Templates

### 8.1 Story Post Template
```
[Hook: Surprising moment or realization]
[Context: What led to this moment]
[Challenge: What went wrong or was difficult]
[Resolution: How it was solved]
[Lesson: Key takeaway for audience]
[Call-to-action: Question or engagement prompt]

#hashtags (3-5 relevant)
```

### 8.2 Value Post Template
```
[Problem statement your audience faces]
[Why common solutions fail]
[Your framework/approach in 3-5 steps]
[Specific example or case study]
[Invitation to implement]

#hashtags
```

### 8.3 Contrarian Take Template
```
[Common belief in your industry]
[Why it's wrong or outdated]
[Your alternative perspective]
[Evidence or reasoning]
[When your approach works best]

#hashtags
```

### 8.4 Industry Insight Template
```
[Trend observation with data/statistic]
[Why this matters now]
[Who it impacts most]
[Prediction for next 6-12 months]
[Advice for adapting]

#hashtags
```

### 8.5 Personal Learning Post Template
```
[What you set out to learn/do]
[What actually happened]
[Unexpected discovery]
[How you'll apply it]
[Question to crowdsource insights]

#hashtags
```

---

## 9. Profile Targeting Criteria

### 9.1 Search Parameters

```python
target_criteria = {
    "job_titles": ["Software Engineer", "CTO", "VP Engineering"],
    "industries": ["Technology", "Financial Services", "Healthcare Tech"],
    "locations": ["New York City", "San Francisco Bay Area"],
    "companies": ["Google", "Microsoft", "Stripe", "Startups"],
    "keywords": ["AI", "machine learning", "cloud infrastructure"],
    "connection_degree": [2, 3],  # 2nd and 3rd degree connections
    "profile_language": "en"
}
```

### 9.2 Relevance Scoring

Score each profile 1-10 based on:
- Title match (3 points)
- Industry alignment (2 points)
- Location match (2 points)
- Company desirability (2 points)
- Keyword overlap (1 point)

Only send requests to profiles scoring ≥7/10

### 9.3 Personalized Message Templates

**For peer connections:**
```
Hi {{first_name}}, I noticed your work in {{industry}} and found your 
perspective on {{topic}} interesting. Would love to connect and learn 
from your insights!
```

**For senior professionals:**
```
Hi {{first_name}}, I've been following your career at {{company}} and 
admire your approach to {{specific_achievement}}. Would be honored to 
connect and occasionally learn from your posts.
```

**For recruiters/hiring managers:**
```
Hi {{first_name}}, I see you're building teams in {{domain}}. I'm 
passionate about {{relevant_skill}} and always interested in connecting 
with leaders shaping our industry.
```

---

## 10. Technical Specifications

### 10.1 Dependencies (requirements.txt)

```txt
playwright==1.42.0
python-dotenv==1.0.0
sqlite3-helper==3.1.0
pydantic==2.6.0
rich==13.7.0  # For nice terminal output
apscheduler==3.10.0  # For scheduling
```

### 10.2 Environment Variables (.env)

```env
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
LINKEDIN_MFA_SECRET=  # Optional, for TOTP
TIMEZONE=Asia/Kolkata  # Change to your timezone (e.g., Asia/Kolkata for India)
MAX_CONNECTIONS_PER_DAY=20
MAX_POSTS_PER_DAY=2
LOG_LEVEL=INFO
BROWSER_HEADLESS=false  # true for production, false for debugging
```

### 10.3 Database Schema (SQLite)

```sql
-- Activity Log
CREATE TABLE activity_log (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    action_type TEXT NOT NULL,
    target_url TEXT,
    result TEXT,
    details JSON,
    session_id TEXT
);

-- Profile Database
CREATE TABLE profiles (
    id INTEGER PRIMARY KEY,
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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Posts Archive
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    content TEXT,
    post_type TEXT,
    scheduled_for DATETIME,
    published_at DATETIME,
    post_url TEXT,
    impressions INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0
);

-- Rate Limit Tracking
CREATE TABLE rate_limits (
    date DATE PRIMARY KEY,
    connections_sent INTEGER DEFAULT 0,
    profiles_viewed INTEGER DEFAULT 0,
    posts_published INTEGER DEFAULT 0,
    messages_sent INTEGER DEFAULT 0
);
```

---

## 11. Error Handling Strategy

### 11.1 Error Classification

**Retryable Errors:**
- Network timeouts
- Temporary LinkedIn outages
- Element not found (transient)
- Rate limit temporarily exceeded

**Non-Retryable Errors:**
- Invalid credentials
- Account restriction
- Permanent element selector change
- Legal/compliance blocks

### 11.2 Retry Logic

```python
def execute_with_retry(func, max_retries=3, backoff_seconds=60):
    for attempt in range(max_retries):
        try:
            return func()
        except RetryableError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = backoff_seconds * (attempt + 1)
            log(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
            sleep(wait_time)
```

### 11.3 Escalation Path

```
Level 1: Script handles automatically (retry, skip, workaround)
Level 2: Log warning, continue with reduced functionality
Level 3: Pause automation, alert user for manual intervention
Level 4: Emergency stop, require user review before resuming
```

---

## 12. Testing Strategy

### 12.1 Unit Tests (per script)
- Mock LinkedIn responses
- Test selector accuracy
- Validate data parsing
- Verify rate limit logic

### 12.2 Integration Tests (monthly)
- Full workflow execution
- Multi-script coordination
- Database integrity
- Log completeness

### 12.3 Manual Verification (weekly)
- Review posted content quality
- Check connection acceptance rates
- Validate targeting accuracy
- Audit safety compliance

---

## 13. Compliance Notes

⚠️ **Important Legal Considerations:**

1. LinkedIn's Terms of Service prohibit automated scraping
2. This system is for educational purposes only
3. Users assume all risks of account restrictions
4. Always prioritize manual oversight
5. Respect individual privacy settings
6. Don't store sensitive personal data beyond necessity

**Recommendation**: Use LinkedIn's official API where possible for lower-risk automation.

---

## 14. Future Enhancements

- [ ] AI-powered message personalization
- [ ] A/B testing for post content
- [ ] Competitor analysis tracking
- [ ] Multi-account management
- [ ] Slack/Discord notifications
- [ ] Mobile app integration
- [ ] Advanced analytics dashboards
- [ ] CRM integration (HubSpot, Salesforce)

---

## Summary

This LinkedIn Manager system provides:
- ✅ Modular 3-layer architecture
- ✅ Comprehensive automation workflows
- ✅ Robust safety mechanisms
- ✅ Detailed logging and audit trails
- ✅ Scalable design for future growth
- ✅ Clear separation of concerns

**Next Steps**: Begin implementing Layer 1 directives and Layer 3 execution scripts, starting with the core posting workflow.
