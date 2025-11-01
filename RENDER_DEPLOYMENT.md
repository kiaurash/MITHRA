# Deploy MITHRA to Render.com

Complete guide to deploying your MITHRA application on Render.com for FREE with private code.

---

## ✨ Why Render?

- ✅ **FREE forever** (750 hours/month)
- ✅ **Private GitHub repos** supported
- ✅ Works with Gradio, ChromaDB, all APIs
- ✅ No credit card required to start
- ✅ Auto-deploy on git push
- ✅ Environment secrets management
- ✅ Perfect for bootcamp testing (6 weeks)

---

## 📋 Prerequisites

- GitHub account with MITHRA repo: https://github.com/kiaurash/MITHRA
- Render account (free - we'll create this)
- Anthropic API key

---

## 🚀 Step-by-Step Deployment (15 minutes)

### Step 1: Create Render Account (2 minutes)

1. Go to **https://render.com**
2. Click **"Get Started"** (top right)
3. Sign up with:
   - **GitHub** (recommended - easy repo access)
   - Or email/Google
4. Verify your email
5. You're in! No credit card needed.

---

### Step 2: Connect Your GitHub Repository (3 minutes)

1. In Render Dashboard, click **"New +"** (top right)
2. Select **"Web Service"**
3. You'll see "Connect a repository" page

**If you signed up with GitHub:**
- Click **"Connect account"** next to GitHub
- Authorize Render to access your repos
- Select: **"Only select repositories"**
- Choose: **kiaurash/MITHRA**
- Click **"Install"**

**If you signed up with email:**
- Click **"Connect GitHub"**
- Authorize Render
- Follow same steps above

4. After connecting, you'll see **MITHRA** in the list
5. Click **"Connect"** next to MITHRA repo

---

### Step 3: Configure Your Web Service (5 minutes)

You'll see a configuration form. Fill it in:

**Basic Settings:**
- **Name:** `mithra-research-assistant` (or any name you like)
- **Region:** Choose closest to you (or leave default)
- **Branch:** `mithra-app` ⚠️ **Important: Select mithra-app, not master!**
- **Root Directory:** Leave blank (files are at repo root)
- **Runtime:** **Python 3** (auto-detected)

**Build & Deploy:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py`

**Instance Type:**
- Select **"Free"** ✅

Click **"Advanced"** to expand more options:

**Environment Variables:**
- Click **"Add Environment Variable"**
- **Key:** `ANTHROPIC_API_KEY`
- **Value:** Paste your Claude API key (starts with `sk-ant-api03-...`)
- Click **"Add"**

**Auto-Deploy:**
- ✅ Keep "Auto-Deploy" enabled (deploys on git push)

---

### Step 4: Create Web Service (1 minute)

1. Scroll to bottom
2. Click **"Create Web Service"**
3. Render will start building your app!

---

### Step 5: Wait for Build & Deploy (3-5 minutes)

**You'll see:**
1. **Building...** - Installing dependencies
2. **Deploying...** - Starting your app
3. **Live** ✅ - App is running!

**Watch the logs** (shows in real-time):
```
==> Installing dependencies...
==> Building...
==> Starting service...
🚀 Starting MITHRA...
📚 Upload a research paper to begin...
Running on local URL:  http://0.0.0.0:10000
```

When you see **"Live"** with a green dot, you're deployed! 🎉

---

### Step 6: Access Your App (1 minute)

At the top of your service page, you'll see:
```
https://mithra-research-assistant-xxxx.onrender.com
```

1. **Click the URL** (or copy it)
2. Opens your MITHRA Gradio interface!
3. **Test it:**
   - Upload a research paper PDF
   - Go through the context questions
   - Verify it works!

---

## 🎯 Your App is Live!

**Share this URL with testers:**
```
https://mithra-research-assistant-xxxx.onrender.com
```

Anyone with the link can use MITHRA!

**Your code stays private** - visitors can't see your GitHub repo or prompts.

---

## ⚙️ Managing Your Deployment

### Update Your App (Auto-Deploy)

**Every time you push to GitHub:**
1. Make changes locally
2. Commit: `git commit -m "Update MITHRA"`
3. Push: `git push origin mithra-app`
4. Render **automatically rebuilds** (~2-3 min)
5. Your app updates!

**Manual Deploy:**
- In Render Dashboard → Your service
- Click **"Manual Deploy"** → **"Deploy latest commit"**

---

### View Logs (Debugging)

**Real-time logs:**
1. Go to your service in Render Dashboard
2. Click **"Logs"** tab
3. See all output (errors, API calls, user activity)

**Useful for:**
- Debugging errors
- Monitoring API usage
- Seeing when users access the app

---

### Update Environment Variables

**To change your API key or add new secrets:**
1. Service Dashboard → **"Environment"** tab
2. Update existing or add new variables
3. Click **"Save Changes"**
4. App will automatically restart

---

### Monitor Usage

**Check your free tier usage:**
1. Render Dashboard → Account Settings
2. See hours used this month
3. Free tier: 750 hours/month
4. Your app uses ~1 hour per hour it's running

---

## ⚠️ Important: Cold Starts

**Free tier apps sleep after 15 minutes of inactivity.**

**What this means:**
- First visitor after sleep: **30-60 second wait** (app waking up)
- Then: normal speed
- Subsequent visitors: instant (while awake)

**Solutions:**

### Option 1: Accept It (Free)
- For bootcamp testing, 30-60 sec wait is fine
- Just warn testers: "First load may take a minute"

### Option 2: Keep-Alive Service (Free)
Use a free service to ping your app every 10 minutes:
- **UptimeRobot** (https://uptimerobot.com) - free, pings every 5 min
- **Cron-Job.org** (https://cron-job.org) - free, custom intervals
- Set them to ping: `https://your-app.onrender.com`

### Option 3: Upgrade to Paid ($7/month)
- Always-on (no cold starts)
- Faster instance
- Only if you want instant loads

---

## 🔒 Security & Privacy

### Your Code is Private ✅
- Visitors can't see your GitHub repo
- Prompts and logic are hidden
- Only the Gradio UI is exposed

### API Key is Secure ✅
- Stored in Render environment secrets
- Never exposed in logs or to users
- Encrypted at rest

### User Data
- Uploaded PDFs are processed in-memory
- Not stored after session ends
- Conversations not logged (unless you add logging)

---

## 📊 Monitoring & Analytics

### Built-in Metrics:
1. Service Dashboard → **"Metrics"** tab
2. See:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

### Add Google Analytics (Optional):
- Add GA tracking code to your Gradio interface
- Track user sessions, popular features

---

## 🐛 Troubleshooting

### ❌ "Build Failed"

**Check build logs:**
- Click **"Logs"** → scroll to error
- Common issues:
  - Missing dependency in requirements.txt
  - Python version mismatch
  - Import errors

**Fix:**
1. Fix the issue locally
2. Push to GitHub
3. Render auto-rebuilds

---

### ❌ "Service Unavailable"

**Possible causes:**
- App crashed after starting
- Port binding issue
- Out of memory

**Check logs:**
1. Go to **"Logs"** tab
2. Look for error messages
3. Common fixes:
   - Increase instance size (upgrade from free)
   - Fix code errors shown in logs

---

### ❌ "Application Error"

**User sees error when using app:**
1. Check **"Logs"** for Python errors
2. Often API key issues or Claude API errors
3. Verify `ANTHROPIC_API_KEY` is set correctly

---

### ⚠️ App is Slow

**Free tier is slower than paid:**
- Normal for free instances
- Cold starts add 30-60 sec
- Upgrade to paid tier for better performance

---

## 💰 Cost After Bootcamp

### Free Tier (Forever):
- 750 hours/month free
- Perfect for:
  - Personal projects
  - Low-traffic demos
  - Portfolio pieces

**If you exceed 750 hours:**
- Render pauses your service
- No charges
- Resets next month

### Paid Tiers (Optional):
**Starter ($7/month):**
- Always-on (no cold starts)
- Better performance
- 1GB RAM

**Standard ($25/month):**
- Even better performance
- 2GB RAM
- Multiple instances

**For production MITHRA:** $7/month Starter is plenty

---

## 🚀 Next Steps After Deployment

### Week 1: Test & Share
- [ ] Test with different research papers
- [ ] Share URL with 3-5 beta testers
- [ ] Collect feedback in Slack/email
- [ ] Monitor logs for errors

### Week 2-3: Iterate
- [ ] Fix issues found in testing
- [ ] Improve prompts based on feedback
- [ ] Push updates (auto-deploys!)

### Sprint 2: Add Features
- [ ] Add ChromaDB for RAG
  - Store corpus in Render persistent disk
  - Update requirements.txt
  - Push → auto-deploys!
- [ ] Vector DB data persists across restarts

### Sprint 3: Add Voice
- [ ] Add ElevenLabs integration
  - Add API key to environment variables
  - Import elevenlabs library
  - Generate voice from scripts
- [ ] No platform changes needed!

---

## 📁 File Structure on Render

Your deployed app has this structure:
```
/opt/render/project/src/
├── main.py                    # Entry point
├── app.py                     # (unused on Render)
├── config.py
├── requirements.txt
├── utils/
├── workflows/
└── prompts/
```

**Persistent disk** (for future ChromaDB):
```
/opt/render/project/.data/
└── chromadb/                  # Your vector DB data (persists)
```

---

## 🔗 Useful Links

**Your Render Dashboard:**
https://dashboard.render.com

**Render Docs:**
- Python apps: https://render.com/docs/deploy-python
- Environment vars: https://render.com/docs/environment-variables
- Persistent disks: https://render.com/docs/disks

**MITHRA GitHub:**
https://github.com/kiaurash/MITHRA

**Support:**
- Render Community: https://community.render.com
- Your Bootcamp Slack

---

## ✅ Deployment Checklist

- [ ] Created Render account
- [ ] Connected GitHub repo (mithra-app branch)
- [ ] Configured web service (Python, main.py)
- [ ] Added ANTHROPIC_API_KEY environment variable
- [ ] Clicked "Create Web Service"
- [ ] Waited for build to complete
- [ ] Tested app with sample PDF
- [ ] Shared URL with test users
- [ ] Set up UptimeRobot (optional - keeps app awake)

---

## 🎉 Success!

Your MITHRA app is now:
- ✅ Deployed and accessible via public URL
- ✅ Running on free tier (750 hrs/month)
- ✅ Auto-deploying on git push
- ✅ Code staying private on GitHub
- ✅ Ready for bootcamp testing!

**Next:** Share your Render URL with test users and start collecting feedback!

---

**Questions?** Check Render docs or ask in your bootcamp Slack channel.

**Built for Anthropic AI Engineering Bootcamp 2025** 🚀
