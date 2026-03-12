# LinkedIn Manager - Intelligent Automation System

A sophisticated 3-layer architecture LinkedIn automation tool that manages posting, networking, and engagement tracking while maintaining safety and authenticity.

---

## 🎯 What This Does

This system automates your LinkedIn presence with:

- ✅ **Smart Post Creation** - Generate and publish engaging content using proven templates
- ✅ **Automated Publishing** - Schedule and post at optimal times
- ✅ **Profile Targeting** - Find and connect with relevant professionals
- ✅ **Engagement Tracking** - Monitor likes, comments, and growth metrics
- ✅ **Safety First** - Built-in rate limiting and human-like behavior patterns
- ✅ **Account Monitoring** - Track notifications and activity

---

## 🏗️ Architecture

Built on a **3-layer architecture** for maximum reliability:

```
┌─────────────────────────────────────┐
│  LAYER 1: DIRECTIVES (SOPs)         │
│  - What to do                       │
│  - Markdown instructions            │
│  - directives/*.md                  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  LAYER 2: ORCHESTRATION (Agent)     │
│  - Decision making                  │
│  - Read directives, call tools      │
│  - Handle errors, ask questions     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  LAYER 3: EXECUTION (Python)        │
│  - Deterministic scripts            │
│  - Browser automation               │
│  - execution/*.py                   │
└─────────────────────────────────────┘
```

**Why this works:** LLMs are probabilistic, but business logic needs to be deterministic. This architecture isolates complexity.

---

## 📁 Project Structure

```
LinkedIN/
├── .tmp/                          # Temporary files (auto-generated)
│   ├── generated_posts.json       # Post queue
│   ├── target_profiles.json       # Scraped profiles
│   ├── scheduled_posts.json       # Scheduled content
│   └── linkedin_manager.db        # SQLite database
│
├── directives/                    # Layer 1: SOPs
│   ├── create_linkedin_post.md
│   ├── publish_linkedin_post.md
│   ├── find_target_profiles.md
│   ├── send_connection_requests.md
│   ├── monitor_account_activity.md
│   ├── engagement_tracking.md
│   ├── content_scheduler.md
│   └── safety_rate_limits.md
│
├── execution/                     # Layer 3: Python scripts
│   ├── login_linkedin.py          # Authentication
│   ├── post_linkedin_content.py   # Post publishing
│   ├── scrape_profiles.py         # Profile extraction
│   ├── send_connection_request.py # Connection automation
│   ├── get_notifications.py       # Activity monitoring
│   ├── get_engagement_metrics.py  # Analytics
│   ├── schedule_post.py           # Timing management
│   ├── generate_post_content.py   # Content creation
│   ├── check_rate_limits.py       # Safety checks
│   └── utils/
│       ├── logger.py              # Logging
│       ├── data_storage.py        # Database I/O
│       ├── rate_limiter.py        # Rate limiting
│       └── browser_config.py      # Browser settings
│
├── .env                           # Your credentials (create from .env.example)
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Python dependencies
├── AGENTS.md                      # Architecture docs
├── SYSTEM_BLUEPRINT.md            # Complete system design
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** installed
- **LinkedIn account** in good standing
- **Text editor** (VS Code recommended)

### Installation

1. **Clone or download this repository**

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

5. **Setup environment variables**:
   ```bash
   # Copy example file
   cp .env.example .env
   
   # Edit .env with your credentials
   ```

6. **Edit `.env` file**:
   ```env
   LINKEDIN_EMAIL=your_email@example.com
   LINKEDIN_PASSWORD=your_password
   BROWSER_HEADLESS=false  # Set to true after testing
   MAX_POSTS_PER_DAY=2
   MAX_CONNECTIONS_PER_DAY=20
   ```

7. **Test the installation**:
   ```bash
   python execution/login_linkedin.py --action check_session
   ```

---

## 📖 Usage Guide

### Creating & Publishing a Post

#### Method 1: Manual Workflow

1. **Generate post content** (future feature):
   ```bash
   python execution/generate_post_content.py \
     --topic "AI trends in 2026" \
     --type "insight" \
     --points '["point1", "point2"]'
   ```

2. **Review generated post** in `.tmp/generated_posts.json`

3. **Publish the post**:
   ```bash
   python execution/post_linkedin_content.py \
     --post-id "post_20260313_103000"
   ```

#### Method 2: Using the Agent (Recommended)

Simply tell the AI agent:

> "Create and publish a value post about time management tips for remote workers"

The agent will:
1. Read `directives/create_linkedin_post.md`
2. Generate content
3. Validate against duplicates
4. Ask for your approval
5. Publish via `execution/post_linkedin_content.py`
6. Log the result

---

### Checking Daily Limits

```bash
python execution/check_rate_limits.py
```

Output:
```
✓ Connection Sent    | ██████░░░░░░░░░░░░░░ |  12/20 (8 remaining)
✓ Posts Published    | ████░░░░░░░░░░░░░░░░ |   1/2 (1 remaining)
✓ Profiles Viewed    | ██████████░░░░░░░░░░ |  30/60 (30 remaining)
```

---

### Monitoring Account Activity

```bash
python execution/get_notifications.py --since "today"
```

---

## ⚙️ Configuration

### Rate Limits

Adjust in `.env`:

```env
# Conservative limits for new accounts (<3 months)
ACCOUNT_TIER=new
MAX_CONNECTIONS_PER_DAY=10
MAX_POSTS_PER_DAY=1

# Standard limits for established accounts
ACCOUNT_TIER=established
MAX_CONNECTIONS_PER_DAY=20
MAX_POSTS_PER_DAY=2

# Higher limits for premium accounts (>1 year)
ACCOUNT_TIER=premium
MAX_CONNECTIONS_PER_DAY=30
MAX_POSTS_PER_DAY=3
```

### Browser Settings

**Debugging mode** (see browser):
```env
BROWSER_HEADLESS=false
```

**Production mode** (invisible browser):
```env
BROWSER_HEADLESS=true
```

### Timezone

Set your timezone for scheduling:
```env
TIMEZONE=Asia/Kolkata  # Change to your timezone (e.g., Asia/Kolkata for India)
```

---

## 🛡️ Safety Features

### Automatic Protection

- **Daily limits** enforced per account tier
- **Random delays** between actions (2-5 minutes)
- **Human-like typing** speeds (50ms/character)
- **Session persistence** to avoid repeated logins
- **Cooldown periods** after reaching limits

### Best Practices

1. **Start conservative**: Use lower limits for first month
2. **Monitor acceptance rates**: If <20%, reduce activity
3. **Vary timing**: Don't post exactly same time daily
4. **Mix action types**: Don't only send connections
5. **Weekend reduction**: 50% activity on Sat/Sun

### Warning Signs

Stop automation if you see:
- CAPTCHA challenges
- "Account restricted" messages
- Unusual verification requests
- Sudden drop in connection acceptance

---

## 📊 Directives Overview

### Content Creation

| Directive | Purpose | Status |
|-----------|---------|--------|
| [create_linkedin_post.md](directives/create_linkedin_post.md) | Generate posts | ✅ Implemented |
| [publish_linkedin_post.md](directives/publish_linkedin_post.md) | Publish content | ✅ Implemented |
| content_scheduler.md | Schedule posts | 🔜 TODO |

### Networking

| Directive | Purpose | Status |
|-----------|---------|--------|
| find_target_profiles.md | Find professionals | 🔜 TODO |
| send_connection_requests.md | Send invites | 🔜 TODO |
| monitor_account_activity.md | Track notifications | 🔜 TODO |

### Analytics

| Directive | Purpose | Status |
|-----------|---------|--------|
| engagement_tracking.md | Measure performance | 🔜 TODO |
| safety_rate_limits.md | Enforce limits | ✅ Partial |

---

## 🔧 Troubleshooting

### Login Fails

**Problem**: Can't authenticate  
**Solution**:
1. Verify credentials in `.env`
2. Check if MFA enabled (add `LINKEDIN_MFA_SECRET`)
3. Try manual login in browser first
4. Clear `.tmp/session_cache/` and retry

### Post Not Publishing

**Problem**: Script hangs or fails  
**Solution**:
1. Run with `BROWSER_HEADLESS=false` to see what's happening
2. Check LinkedIn for UI changes
3. Verify post content isn't too long/short
4. Look for error in `logs/` directory

### Rate Limit Errors

**Problem**: Hitting limits too fast  
**Solution**:
1. Reduce `MAX_CONNECTIONS_PER_DAY`
2. Increase cooldown times in `rate_limiter.py`
3. Add more randomization to delays

### Playwright Errors

**Problem**: Browser won't launch  
**Solution**:
```bash
# Reinstall browsers
playwright install chromium --force

# Clear cache
rm -rf ~/.cache/ms-playwright
```

---

## 📝 Post Templates

The system supports 5 proven post types:

### 1. Story Post
```
[Hook: Surprising moment]
[Context: What led here]
[Challenge: What went wrong]
[Resolution: How solved]
[Lesson: Key takeaway]
[CTA: Question for audience]
```

### 2. Value Post
```
[Problem your audience faces]
[Why common solutions fail]
[Your framework in 3-5 steps]
[Specific example]
[Invitation to implement]
```

### 3. Contrarian Take
```
[Common belief]
[Why it's wrong]
[Your alternative]
[Evidence/reasoning]
[When your approach works]
```

### 4. Industry Insight
```
[Trend observation with data]
[Why this matters now]
[Who it impacts]
[Prediction for 6-12 months]
[Advice for adapting]
```

### 5. Personal Learning
```
[What you set out to learn]
[What actually happened]
[Unexpected discovery]
[How you'll apply it]
[Question to crowdsource]
```

---

## 🎓 Advanced Usage

### Customizing Templates

Edit post generation logic in `execution/generate_post_content.py` (future implementation).

### Adding New Actions

1. Create script in `execution/`
2. Write directive in `directives/`
3. Update `SYSTEM_BLUEPRINT.md`
4. Test thoroughly before full automation

### Multi-Account Management

**Not recommended** - LinkedIn prohibits multiple accounts per person.

---

## ⚠️ Legal & Compliance

### Important Notices

1. **LinkedIn Terms of Service**: Automated scraping may violate LinkedIn's ToS
2. **Use at your own risk**: Account restrictions are possible
3. **Educational purpose**: This is a learning project
4. **Manual oversight recommended**: Review all automated actions

### Recommendations

- Use official LinkedIn API when possible
- Respect other users' privacy
- Don't store sensitive personal data
- Be transparent about automation use
- Follow LinkedIn Professional Community Policies

---

## 📈 Roadmap

### Phase 1: Core Features (Current)
- ✅ Login/session management
- ✅ Post publishing
- ✅ Rate limiting
- ✅ Basic logging
- 🔜 Profile scraping
- 🔜 Connection requests

### Phase 2: Intelligence
- 🔜 AI-powered content generation
- 🔜 Optimal timing algorithms
- 🔜 A/B testing framework
- 🔜 Engagement prediction

### Phase 3: Analytics
- 🔜 Performance dashboards
- 🔜 Weekly reports
- 🔜 Competitor tracking
- 🔜 ROI measurement

### Phase 4: Scale
- 🔜 Team collaboration features
- 🔜 Multi-platform support
- 🔜 CRM integration
- 🔜 Advanced targeting

---

## 🤝 Contributing

This is a personal project, but improvements welcome!

### How to Contribute

1. Fork the repository
2. Create feature branch
3. Implement enhancement
4. Test thoroughly
5. Submit pull request

### Contribution Guidelines

- Follow 3-layer architecture strictly
- Write tests for new features
- Update documentation
- Keep security in mind
- Maintain code quality

---

## 📚 Additional Resources

- **Full System Design**: See [SYSTEM_BLUEPRINT.md](SYSTEM_BLUEPRINT.md)
- **Architecture Details**: See [AGENTS.md](AGENTS.md)
- **Playwright Docs**: https://playwright.dev/python/
- **LinkedIn API**: https://learn.microsoft.com/en-us/linkedin/

---

## 📞 Support

### Common Issues

For troubleshooting, check:
1. Logs in `logs/` directory
2. Console output for errors
3. `.tmp/` for intermediate data
4. Database with SQLite browser

### Getting Help

1. Search existing issues
2. Check logs for error details
3. Enable debug mode: `LOG_LEVEL=DEBUG`
4. Review directive for expected flow

---

## 📄 License

MIT License - Feel free to use for personal projects.

---

## 🙏 Acknowledgments

Built following best practices from:
- LinkedIn automation research
- Browser automation community
- 3-layer architecture pattern
- Rate limiting best practices

---

**Last Updated**: March 13, 2026  
**Version**: 1.0.0  
**Status**: Active Development

---

**Ready to get started?** Run your first command:

```bash
python execution/login_linkedin.py --action ensure
```

Then tell the agent: *"Create and publish a post about your expertise"*

Happy networking! 🚀
