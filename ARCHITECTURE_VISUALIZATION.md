# LinkedIn Manager - Architecture Visualization

## System Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Natural Language Requests (Chat/Commands)                  │   │
│  │  "Create a post about AI trends"                            │   │
│  │  "Find software engineers in NYC"                           │   │
│  │  "Send 10 connection requests"                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    LAYER 1: DIRECTIVES                              │
│  (Standard Operating Procedures in Markdown)                        │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ create_linkedin_ │  │ publish_linkedin_│  │ find_target_     │  │
│  │ post.md          │  │ post.md          │  │ profiles.md      │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ send_connection_ │  │ monitor_account_ │  │ engagement_      │  │
│  │ requests.md      │  │ activity.md      │  │ tracking.md      │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│  ┌──────────────────┐  ┌──────────────────┐                       │
│  │ content_sche-    │  │ safety_rate_     │                       │
│  │ duler.md         │  │ limits.md        │                       │
│  └──────────────────┘  └──────────────────┘                       │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                 LAYER 2: ORCHESTRATION                              │
│                    (The Intelligent Agent)                          │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  1. Read Directive & Parse Requirements                      │  │
│  │  2. Validate Inputs                                          │  │
│  │  3. Identify Required Execution Scripts                      │  │
│  │  4. Call Scripts in Correct Order                            │  │
│  │  5. Handle Errors & Retries                                  │  │
│  │  6. Ask User for Missing Information                         │  │
│  │  7. Store Intermediate Results in .tmp/                      │  │
│  │  8. Update Directives with Learnings                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                LAYER 3: EXECUTION                                   │
│              (Deterministic Python Scripts)                         │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ login_linkedin.  │  │ post_linkedin_   │  │ scrape_profiles. │  │
│  │ py               │  │ content.py       │  │ py               │  │
│  │ [Authentication] │  │ [Publishing]     │  │ [Data Extract]   │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ send_connection_ │  │ get_notifica-    │  │ get_engagement_  │  │
│  │ request.py       │  │ tions.py         │  │ metrics.py       │  │
│  │ [Networking]     │  │ [Monitoring]     │  │ [Analytics]      │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ schedule_post.py │  │ generate_post_   │  │ check_rate_      │  │
│  │ [Timing]         │  │ content.py       │  │ limits.py        │  │
│  │ [Scheduling]     │  │ [AI Content]     │  │ [Safety]         │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                      │
│  Utils Layer:                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ logger.py    │  │ data_storage.│  │ rate_limiter.│             │
│  │ [Logging]    │  │ py           │  │ py           │             │
│  │              │  │ [DB/Files]   │  │ [Safety]     │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│  ┌──────────────────────┐                                         │
│  │ browser_config.py    │                                         │
│  │ [Stealth Settings]   │                                         │
│  └──────────────────────┘                                         │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                     │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  SQLite Database (.tmp/linkedin_manager.db)                  │  │
│  │  ├─ activity_log (all actions taken)                         │  │
│  │  ├─ profiles (target professionals)                          │  │
│  │  ├─ posts (published content archive)                        │  │
│  │  └─ rate_limits (daily counters)                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  JSON Files (.tmp/)                                          │  │
│  │  ├─ generated_posts.json (post queue)                        │  │
│  │  ├─ target_profiles.json (scraped data)                      │  │
│  │  ├─ scheduled_posts.json (future posts)                      │  │
│  │  └─ session_cache/ (browser cookies)                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                                 │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ LinkedIn         │  │ Playwright       │  │ Optional:        │  │
│  │ Platform         │  │ Browser          │  │ OpenAI API       │  │
│  │ [Target]         │  │ [Automation]     │  │ [Content Gen]    │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Creating & Publishing a Post

```
USER REQUEST
│
│  "Create and publish a value post about time management"
│
↓
┌─────────────────────────────────────────────────────────┐
│ ORCHESTRATION reads: directives/create_linkedin_post.md │
└─────────────────────────────────────────────────────────┘
│
├─→ Step 1: Validate inputs (topic, post_type, key_points)
│
├─→ Step 2: Check recent posts for duplicates
│       └─→ Query SQLite: posts table
│
├─→ Step 3: Verify posting frequency
│       └─→ execution/check_rate_limits.py
│           └─→ Can post? YES (1/2 today)
│
├─→ Step 4: Generate content
│       └─→ execution/generate_post_content.py
│           ├─ Select template: "value"
│           ├─ Fill structure
│           ├─ Add hashtags
│           └─ Output → .tmp/generated_posts.json
│
├─→ Step 5: Present to user for approval
│       └─ "Here's your draft. Publish now?"
│
│  ← USER: "Yes, publish it"
│
├─→ Step 6: Ensure authentication
│       └─→ execution/login_linkedin.py
│           ├─ Load saved session
│           ├─ Verify still valid
│           └─ Keep browser open
│
├─→ Step 7: Publish post
│       └─→ execution/post_linkedin_content.py
│           ├─ Navigate to feed
│           ├─ Click "Start a post"
│           ├─ Type content
│           ├─ Add hashtags
│           ├─ Click "Post"
│           └─ Capture URL
│
├─→ Step 8: Update records
│       ├─ Mark post as "published" in JSON
│       ├─ Add to SQLite posts table
│       └─ Log action in activity_log
│
└─→ Step 9: Increment rate limit counter
        └─→ posts_published: 1/2
    
SUCCESS! Post is live at: linkedin.com/feed/update/...
```

---

## Authentication Flow

```
┌──────────────────────────────────────────────────────┐
│ execution/login_linkedin.py                          │
└──────────────────────────────────────────────────────┘
         │
         ├─→ Check for saved session (.tmp/session_cache/)
         │   ├─ Load cookies
         │   └─ Test if still valid
         │
         │   ✓ Valid? → Use existing session
         │
         │   ✗ Invalid? → Fresh login required
         │
         └─→ Perform Login
             ├─ Navigate to linkedin.com/login
             ├─ Fill email + password
             ├─ Submit form
             │
             ├─ MFA Required?
             │   ├─ YES: Auto-generate TOTP code OR manual entry
             │   └─ NO: Continue
             │
             ├─ Wait for navigation to /feed/
             ├─ Verify logged in successfully
             ├─ Save session cookies
             └─ Return session object
```

---

## Rate Limiting Logic

```
┌─────────────────────────────────────────────────────┐
│ execution/utils/rate_limiter.py                     │
└─────────────────────────────────────────────────────┘
         │
         ├─→ Get account tier (new/established/premium)
         │
         ├─→ Load daily limits from config
         │   ├─ connections_per_day: 20
         │   ├─ posts_per_day: 2
         │   ├─ profiles_viewed_per_day: 60
         │   └─ messages_per_day: 15
         │
         ├─→ Query today's activity from SQLite
         │
         ├─→ For each action request:
         │   │
         │   ├─ Check: current_count < limit?
         │   │   ├─ YES → Apply random cooldown (2-5 min)
         │   │   │        → Allow action
         │   │   │        → Increment counter
         │   │   │
         │   │   └─ NO → Block action
         │   │            → Log event
         │   │            → Schedule for tomorrow
         │
         └─→ Print daily summary dashboard
```

---

## Safety Mechanisms Hierarchy

```
┌────────────────────────────────────────────────────────┐
│ SAFETY ENFORCEMENT (Multiple Layers)                   │
└────────────────────────────────────────────────────────┘
         │
         ├─→ LAYER 1: Pre-Action Checks
         │   ├─ Validate daily limits
         │   ├─ Check cooldown timers
         │   └─ Verify session validity
         │
         ├─→ LAYER 2: During Action
         │   ├─ Human-like delays (typing speed)
         │   ├─ Random mouse movements
         │   ├─ Natural scrolling patterns
         │   └─ Browser fingerprint rotation
         │
         ├─→ LAYER 3: Post-Action
         │   ├─ Log all activities
         │   ├─ Update rate counters
         │   ├─ Monitor for errors/warnings
         │   └─ Detect CAPTCHA/restrictions
         │
         └─→ EMERGENCY STOP
             ├─ Account restriction detected
             ├─ Multiple failed attempts
             ├─ Unusual error patterns
             └─ → Halt all automation, alert user
```

---

## Error Handling Strategy

```
ERROR DETECTED
      │
      ├─→ Classify Error Type
      │   │
      │   ├─ RETRYABLE (network timeout, temporary block)
      │   │   └─→ Retry up to 3 times with exponential backoff
      │   │       (wait 30s, 60s, 120s)
      │   │
      │   ├─ NON-RETRYABLE (invalid credentials, permanent block)
      │   │   └─→ Stop immediately, alert user
      │   │
      │   └─→ WARNING (rate limit approaching, UI change)
      │       └─→ Log warning, continue with caution
      │
      ├─→ Attempt Recovery
      │   ├─ Refresh session
      │   ├─ Try alternative selectors
      │   ├─ Switch to manual mode
      │   └─ Skip to next action
      │
      ├─→ Log Everything
      │   ├─ Error message
      │   ├─ Stack trace
      │   ├─ Context (what was being attempted)
      │   └─ Resolution attempt
      │
      └─→ Self-Anneal
          ├─ Analyze root cause
          ├─ Fix script if needed
          ├─ Test fix
          └─ Update directive with new knowledge
```

---

## File Organization

```
Project Root
│
├─► .tmp/ (Temporary - Can be deleted anytime)
│   ├─ session_cache/ (Browser cookies)
│   ├─ generated_posts.json (Post drafts)
│   ├─ target_profiles.json (Scraped data)
│   ├─ scheduled_posts.json (Future posts)
│   └─ linkedin_manager.db (SQLite database)
│
├─► logs/ (Auto-created)
│   ├─ linkedin_manager_20260313.log
│   ├─ linkedin_manager_20260314.log
│   └─ ... (daily rotation)
│
├─► directives/ (SOPs - Layer 1)
│   ├─ create_linkedin_post.md
│   ├─ publish_linkedin_post.md
│   ├─ [future: 6 more files]
│   └─ 
│
├─► execution/ (Scripts - Layer 3)
│   ├─ login_linkedin.py ✅
│   ├─ post_linkedin_content.py ✅
│   ├─ [6 placeholder scripts]
│   └─ utils/
│       ├─ __init__.py
│       ├─ logger.py ✅
│       ├─ data_storage.py ✅
│       ├─ rate_limiter.py ✅
│       └─ browser_config.py ✅
│
├─► Configuration Files
│   ├─ .env (Credentials - NEVER COMMIT)
│   ├─ .env.example (Template)
│   ├─ .gitignore (Git rules)
│   └─ requirements.txt (Dependencies)
│
└─► Documentation
    ├─ README.md (User guide)
    ├─ SYSTEM_BLUEPRINT.md (System design)
    ├─ IMPLEMENTATION_SUMMARY.md (Status report)
    ├─ AGENTS.md (Architecture overview)
    └─ ARCHITECTURE_VISUALIZATION.md (This file)
```

---

## Component Interactions

```
┌──────────────────────────────────────────────────────────┐
│ USER makes request                                       │
└──────────────────────────────────────────────────────────┘
        │
        ↓
┌──────────────────────────────────────────────────────────┐
│ ORCHESTRATION (Agent)                                    │
│ 1. Identifies task type                                  │
│ 2. Loads appropriate directive                           │
│ 3. Plans execution sequence                              │
└──────────────────────────────────────────────────────────┘
        │
        ├─► Calls: login_linkedin.py
        │   └─► Uses: browser_config.py (stealth)
        │   └─► Uses: logger.py (logging)
        │
        ├─► Calls: check_rate_limits.py
        │   └─► Queries: SQLite rate_limits table
        │   └─► Uses: rate_limiter.py (logic)
        │
        ├─► Calls: post_linkedin_content.py
        │   └─► Uses: playwright (browser control)
        │   └─► Writes: SQLite posts table
        │   └─► Updates: .tmp/generated_posts.json
        │
        └─► Logs everything via:
            └─► logger.py → Console + File
            └─► data_storage.py → Database
            
Result: Post published, records updated, user notified
```

---

## Security Architecture

```
┌──────────────────────────────────────────────────────────┐
│ SECURITY LAYERS                                          │
└──────────────────────────────────────────────────────────┘
        │
        ├─► Credential Storage
        │   ├─ .env file (not in git)
        │   ├─ Never logged or printed
        │   └─ Loaded at runtime only
        │
        ├─► Session Management
        │   ├─ Encrypted cookie storage
        │   ├─ Automatic renewal
        │   └─ Clean logout handling
        │
        ├─► Browser Stealth
        │   ├─ Anti-detection scripts
        │   ├─ User agent rotation
        │   ├─ Viewport randomization
        │   └─ Human-like behavior simulation
        │
        ├─► Rate Limiting
        │   ├─ Daily action caps
        │   ├─ Cooldown enforcement
        │   ├─ Activity logging
        │   └─ Emergency stop triggers
        │
        └─► Data Protection
            ├─ Local database only (no cloud)
            ├─ Minimal PII storage
            ├─ Automatic log rotation
            └─ Git ignore for sensitive files
```

---

## Scaling Considerations

### Current Design (Single User)
```
User → Agent → Scripts → LinkedIn
            ↓
        SQLite DB
        JSON Files
```

### Future Multi-User Design
```
User 1 ─┐
User 2 ─┼─→ Load Balancer → Agent Pool → Script Instances
User 3 ─┘                      ↓
                        PostgreSQL (multi-user DB)
                        Redis (caching)
                        Task Queue (Celery/RQ)
```

---

## Monitoring Dashboard (Conceptual)

```
┌──────────────────────────────────────────────────────────┐
│ LINKEDIN MANAGER - DASHBOARD                             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Today's Activity (March 13, 2026)                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Connections Sent:    ████████░░░░░░  12/20       │  │
│  │ Posts Published:     ████░░░░░░░░░░   1/2        │  │
│  │ Profile Views:       ██████████░░░░  30/60       │  │
│  │ Messages Sent:       ██░░░░░░░░░░░░   3/15       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Recent Posts                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │ ✓ "AI Trends in 2026" - 245 impressions          │  │
│  │ ✓ "Remote Work Tips" - 189 impressions           │  │
│  │ ○ Scheduled for tomorrow: "Leadership Lessons"   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Connection Pipeline                                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Sent: 45  |  Accepted: 12  |  Pending: 33       │  │
│  │ Acceptance Rate: 26.7%                           │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Account Status                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ ✓ No restrictions                                │  │
│  │ ✓ Session valid                                  │  │
│  │ ✓ Rate limits healthy                            │  │
│  │ Next automation: 2 hours                         │  │
│  └──────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Automation** | Playwright | Browser control |
| **Language** | Python 3.9+ | Scripting |
| **Database** | SQLite 3 | Local storage |
| **Logging** | Rich + logging | Console/file output |
| **Scheduling** | APScheduler | Time-based triggers |
| **Environment** | python-dotenv | Config management |
| **Data Validation** | Pydantic | Input validation |
| **Timezone** | pytz | Time handling |

---

## Implementation Status Legend

✅ = Fully implemented and tested  
🔜 = Placeholder created, needs implementation  
❌ = Not yet started  

```
Core Scripts:
✅ login_linkedin.py
✅ post_linkedin_content.py
✅ check_rate_limits.py
🔜 generate_post_content.py
🔜 scrape_profiles.py
🔜 send_connection_request.py
🔜 get_notifications.py
🔜 get_engagement_metrics.py
🔜 schedule_post.py

Utilities:
✅ logger.py
✅ data_storage.py
✅ rate_limiter.py
✅ browser_config.py

Directives:
✅ create_linkedin_post.md
✅ publish_linkedin_post.md
🔜 6 more SOPs pending
```

---

**This architecture provides:**
- ✅ Clear separation of concerns
- ✅ Modularity for easy updates
- ✅ Robust error handling
- ✅ Scalability potential
- ✅ Comprehensive logging
- ✅ Safety-first design

**Next Steps**: Implement remaining scripts following established patterns!
