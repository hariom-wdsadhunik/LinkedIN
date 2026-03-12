

**Get up and running in 15 minutes!**

---

## ⚡ Prerequisites Check

Before you begin, ensure you have:

- ✅ Python 3.9 or higher installed
- ✅ A LinkedIn account in good standing
- ✅ 15 minutes of time
- ✅ Your LinkedIn email and password

---

## 🚀 Step-by-Step Installation

### Step 1: Install Dependencies (5 minutes)

Open your terminal/PowerShell and navigate to the project folder:

```bash
cd "c:\Users\LENOVO\Desktop\LinkedIN"
```

Create a virtual environment (recommended):

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Mac/Linux
```

Install required packages:

```bash
pip install -r requirements.txt
```

Install Playwright browser:

```bash
playwright install chromium
```

✅ **Done?** You should see "Playwright browsers installed" message.

---

### Step 2: Configure Credentials (2 minutes)

Copy the example environment file:

```bash
copy .env.example .env  # Windows
# OR
cp .env.example .env  # Mac/Linux
```

Edit `.env` with your favorite text editor and add your credentials:

```env
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_actual_password_here
BROWSER_HEADLESS=false  # Keep false for first run
TIMEZONE=America/New_York  # Change to your timezone
```

⚠️ **Important**: Never commit `.env` to git!

---

### Step 3: Test Authentication (3 minutes)

Test if you can log in:

```bash
python execution/login_linkedin.py --action check_session
```

**Expected output:**
```
✓ Ensuring authenticated session...
✓ Starting browser...
✓ Attempting LinkedIn login...
✓ Login successful
✓ Session saved
```

**If you see errors:**
- ❌ "Invalid credentials" → Check your email/password in `.env`
- ❌ "MFA required" → See MFA setup section below
- ❌ "Browser error" → Run `playwright install chromium --force`

---

### Step 4: Verify Rate Limits (1 minute)

Check your daily limits:

```bash
python execution/check_rate_limits.py
```

**Expected output:**
```
Rate limit check: connection_sent = 0/20 (✓)
Rate limit check: post_published = 0/2 (✓)
Rate limit check: profile_viewed = 0/60 (✓)
```

✅ **Success!** System is ready.

---

## 📝 Your First Automated Task

### Option 1: Publish a Test Post

#### Create a draft post manually:

Create file `.tmp/generated_posts.json`:

```json
{
  "post_id": "test_001",
  "content": "🎉 Excited to announce my new LinkedIn automation project!\n\nI've been working on an intelligent system that helps manage professional networking while maintaining authentic engagement.\n\nKey features:\n✓ Smart content generation\n✓ Safety-first automation\n✓ Engagement tracking\n✓ Rate limit enforcement\n\nThis is just the beginning. Stay tuned for updates!\n\n#Automation #LinkedIn #ProfessionalNetworking #TechInnovation",
  "post_type": "announcement",
  "hashtags": ["#Automation", "#LinkedIn", "#ProfessionalNetworking", "#TechInnovation"],
  "status": "draft",
  "created_at": "2026-03-13T12:00:00Z"
}
```

#### Publish it:

```bash
python execution/post_linkedin_content.py --post-id "test_001"
```

The system will:
1. Load your saved session
2. Navigate to LinkedIn
3. Click "Start a post"
4. Type your content
5. Add hashtags
6. Click "Post"
7. Return success message

**You should see your post go live!**

---

### Option 2: Let the AI Agent Help

If you're using this with an AI agent, simply say:

> "Publish a post about my excitement for LinkedIn automation technology"

The agent will:
1. Read the appropriate directives
2. Generate content
3. Ask for your approval
4. Publish when you confirm

---

## 🔐 MFA Setup (Optional but Recommended)

If you have Two-Factor Authentication enabled:

### Method 1: TOTP (Automatic)

1. Get your TOTP secret from your authenticator app's backup codes
2. Add to `.env`:

```env
LINKEDIN_MFA_SECRET=YOUR_TOTP_SECRET_HERE
```

3. The system will auto-generate codes

### Method 2: Manual Entry

If MFA secret not set:
- System will pause and ask you to enter code manually
- You have 2 minutes to input the 6-digit code
- Code expires quickly, so be ready!

---

## 📊 Daily Workflow Examples

### Morning Routine (9 AM)

```bash
# Check notifications from overnight
python execution/get_notifications.py --since "yesterday"

# Review daily limits
python execution/check_rate_limits.py

# Publish scheduled post
python execution/post_linkedin_content.py --post-id "scheduled_001"
```

### Afternoon Routine (2 PM)

```bash
# Find new target profiles (when implemented)
python execution/scrape_profiles.py --keywords "software engineer" --location "New York"

# Send connection requests (when implemented)
python execution/send_connection_request.py --limit 10
```

### Evening Routine (6 PM)

```bash
# Check engagement metrics (when implemented)
python execution/get_engagement_metrics.py --date-range "today"

# Review daily summary
python execution/check_rate_limits.py
```

---

## 🛡️ Safety First!

### Recommended Starting Limits (First Month)

Edit `.env`:

```env
MAX_CONNECTIONS_PER_DAY=10
MAX_POSTS_PER_DAY=1
MAX_PROFILE_VIEWS_PER_DAY=30
```

### Monitor These Metrics

- **Connection acceptance rate**: Should be >20%
- **Profile view response rate**: Track engagement
- **Post engagement**: Likes/comments per post

If rates drop, reduce activity by 30%.

---

## 🐛 Troubleshooting Common Issues

### "Module not found" error

```bash
# Make sure virtual environment is activated
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### "Browser won't launch" error

```bash
# Reinstall Playwright browsers
playwright install chromium --force

# Clear cache
rm -rf ~/.cache/ms-playwright  # Mac/Linux
rmdir /s /q %LOCALAPPDATA%\ms-playwright  # Windows
playwright install chromium
```

### "Login failed" error

1. Manually log into LinkedIn in your browser
2. Verify credentials work
3. Check if MFA is required
4. Try clearing session: delete `.tmp/session_cache/`
5. Retry authentication

### "Element not found" error

LinkedIn changes their UI frequently. Check:
1. Is LinkedIn down? (try manual access)
2. Are you logged in? (check browser)
3. Selectors may need updating (check logs)

---

## 📁 Important Files & Folders

| Path | Purpose | Can Delete? |
|------|---------|-------------|
| `.tmp/` | Temporary data | ✅ Yes (auto-regenerates) |
| `.tmp/session_cache/` | Browser cookies | ✅ Yes (will re-login) |
| `logs/` | Activity logs | ✅ Yes (helpful for debugging) |
| `.env` | Your credentials | ❌ NO (must recreate) |
| `linkedin_manager.db` | Database | ✅ Yes (loses history) |

---

## 🎯 Next Steps After Setup

### Immediate (Day 1)
- ✅ Test login works
- ✅ Publish a test post
- ✅ Review all documentation files

### Short-term (Week 1)
- [ ] Implement remaining scripts
- [ ] Set up daily automation schedule
- [ ] Monitor engagement metrics
- [ ] Adjust rate limits based on results

### Long-term (Month 1+)
- [ ] Analyze growth trends
- [ ] Optimize posting times
- [ ] Refine targeting criteria
- [ ] Scale activity gradually

---

## 📚 Documentation Quick Links

| Document | Purpose | When to Read |
|----------|---------|--------------|
| [README.md](README.md) | User manual | First-time setup |
| [SYSTEM_BLUEPRINT.md](SYSTEM_BLUEPRINT.md) | System design | Understanding architecture |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Status report | What's done/what's next |
| [ARCHITECTURE_VISUALIZATION.md](ARCHITECTURE_VISUALIZATION.md) | Diagrams | Visual learners |
| [AGENTS.md](AGENTS.md) | 3-layer architecture | Working with AI agent |
| **This file** | Quick start | Getting started |

---

## 🆘 Getting Help

### Check Logs First

```bash
# Most recent log file
ls logs/linkedin_manager_*.log  # Mac/Linux
dir logs\linkedin_manager_*.log  # Windows
```

### Enable Debug Mode

Add to `.env`:

```env
LOG_LEVEL=DEBUG
```

Run again and check detailed output.

### Common Resources

- **Playwright Docs**: https://playwright.dev/python/
- **LinkedIn Help**: https://www.linkedin.com/help/linkedin
- **Project Issues**: Check/create GitHub issues

---

## ✅ Success Checklist

Before considering yourself "done" with setup:

- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] Playwright browsers installed
- [ ] `.env` file configured with credentials
- [ ] Login test successful
- [ ] Rate limits display correctly
- [ ] Test post published successfully
- [ ] Logs are being written
- [ ] Understand safety limits
- [ ] Know how to troubleshoot common errors

---

## 🎉 You're Ready!

Congratulations! Your LinkedIn Manager is set up and ready to automate your professional networking.

**Next actions:**
1. Review the [directives](directives/) to understand workflows
2. Check [SYSTEM_BLUEPRINT.md](SYSTEM_BLUEPRINT.md) for full system design
3. Start using the AI agent to orchestrate tasks
4. Implement remaining scripts as needed

---

## 💡 Pro Tips

1. **Always start conservative** - Lower limits for first month
2. **Monitor closely** - Check logs daily initially
3. **Vary your timing** - Don't automate at exact same time daily
4. **Mix activities** - Posts, connections, comments, likes
5. **Stay human** - Automation assists, doesn't replace you
6. **Document everything** - Update directives as you learn
7. **Test before automating** - Run scripts manually first
8. **Keep backups** - Export database periodically

---

**Happy networking! 🚀**

*Remember: Use responsibly and always maintain authentic engagement.*
