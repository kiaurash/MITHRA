# Deploy MITHRA to Hugging Face Spaces

Complete guide to deploying your MITHRA application on Hugging Face Spaces for FREE.

---

## Prerequisites

- GitHub account with MITHRA repo: https://github.com/kiaurash/MITHRA
- Hugging Face account (free)
- Anthropic API key

---

## Step-by-Step Deployment

### Step 1: Create Hugging Face Account (2 minutes)

1. Go to **https://huggingface.co/join**
2. Sign up (it's free - no credit card required)
3. Verify your email
4. Complete your profile (optional but recommended)

---

### Step 2: Create a New Space (3 minutes)

1. Go to **https://huggingface.co/spaces**
2. Click the **"Create new Space"** button (top right)

3. Fill in the details:
   - **Owner:** Your username
   - **Space name:** `mithra-research-assistant` (or any name you prefer)
   - **License:** MIT
   - **Select the Space SDK:** Choose **Gradio** ⚡
   - **Space hardware:** CPU basic (free tier) - this is plenty for MITHRA
   - **Visibility:**
     - **Public** = anyone can use it (recommended for demos)
     - **Private** = only you can access

4. Click **"Create Space"**

You'll be taken to your new Space page.

---

### Step 3: Connect Your GitHub Repository (2 minutes)

**Option A: Direct GitHub Sync (Recommended)**

1. In your new Space, you'll see it's empty with instructions
2. Look for **"Files and versions"** tab at the top
3. Click the **"⚙️ Settings"** button (top right)
4. Scroll down to **"Repository secrets"** section (we'll use this in Step 4)
5. Scroll further to find **"Linked repositories"** or use git method below

**Option B: Git Clone Method (Easier)**

1. On your Space page, look for the git clone instructions
2. Copy the command, it looks like:
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/mithra-research-assistant
   ```

3. On your local machine (or in Replit/Colab), run:
   ```bash
   cd /tmp
   git clone https://huggingface.co/spaces/YOUR_USERNAME/mithra-research-assistant
   cd mithra-research-assistant

   # Add your GitHub repo as remote
   git remote add github https://github.com/kiaurash/MITHRA.git

   # Pull from your GitHub repo
   git pull github mithra-app --allow-unrelated-histories

   # Push to Hugging Face
   git push origin main
   ```

**Option C: Manual Upload (Simplest)**

1. On your Space page, click **"Files and versions"** tab
2. Click **"Add file"** → **"Upload files"**
3. Download your repo from GitHub as ZIP:
   - Go to https://github.com/kiaurash/MITHRA
   - Click green "Code" button
   - Download ZIP
   - Extract files
4. Upload these files to your Space:
   - `app.py` (or `main.py`)
   - `config.py`
   - `requirements.txt`
   - `README.md`
   - All folders: `utils/`, `workflows/`, `prompts/`
5. Click **"Commit changes to main"**

---

### Step 4: Add Your API Key (1 minute)

**IMPORTANT: Do this BEFORE the app starts building!**

1. In your Space, click **"Settings"** (⚙️ icon, top right)
2. Scroll down to **"Repository secrets"** section
3. Click **"New secret"**
4. Add your secret:
   - **Name:** `ANTHROPIC_API_KEY`
   - **Value:** Your Claude API key (starts with `sk-ant-api03-...`)
5. Click **"Save"**

**Security Note:** This keeps your API key private - it won't be visible in logs or to other users.

---

### Step 5: Wait for Build & Deploy (2-5 minutes)

1. Hugging Face will automatically:
   - Detect it's a Gradio app (from `app.py` or `main.py`)
   - Install dependencies from `requirements.txt`
   - Build and launch the app

2. Watch the **"Building"** status at the top of your Space
   - You'll see logs in the **"Logs"** section
   - Build usually takes 2-5 minutes

3. When you see **"Running"** with a green dot ✅, your app is live!

---

### Step 6: Test Your App (2 minutes)

1. Your Space will show the Gradio interface directly on the page
2. Test it:
   - Upload a research paper PDF
   - Answer the context questions
   - Verify the learning modules generate correctly

3. Get your public URL:
   - It's at the top: `https://huggingface.co/spaces/YOUR_USERNAME/mithra-research-assistant`
   - Share this link with anyone to let them use MITHRA!

---

## Troubleshooting

### ❌ "Application startup failed"

**Check logs:**
1. Click on **"Logs"** tab in your Space
2. Look for error messages

**Common issues:**

**Missing API Key:**
```
Error: ANTHROPIC_API_KEY not configured
```
→ Go back to Step 4, add the secret

**Wrong file structure:**
```
Error: No module named 'workflows'
```
→ Make sure you uploaded all folders (utils, workflows, prompts)

**Dependency issues:**
```
ERROR: Could not find a version that satisfies...
```
→ Check `requirements.txt` has correct versions

---

### ⚠️ App is slow or timing out

**Solution:** Upgrade to better hardware (still free!)

1. Go to Space **Settings**
2. Under **"Space hardware"**, select:
   - **CPU upgrade** (still free on HF)
   - Or **T4 small** (free GPU - overkill but faster)
3. Click **"Save"**
4. Space will restart with better resources

---

### 🔧 Need to update your code?

**Method 1: Edit on Hugging Face**
1. Go to **"Files and versions"** tab
2. Click on file you want to edit
3. Click **"Edit"** button
4. Make changes
5. Commit

**Method 2: Push from GitHub**
- If you set up git sync, just push to your GitHub repo
- Changes will auto-sync to HF Spaces

**Method 3: Re-upload**
- Upload updated files via web interface
- Overwrites existing files

---

## Features of Your HF Space

✅ **Free forever** (within generous usage limits)
✅ **Public URL** for sharing
✅ **SSL/HTTPS** automatic
✅ **Auto-restart** if crashes
✅ **Version control** built-in
✅ **Logs** for debugging
✅ **Usage analytics** (see how many people use it)

---

## Customization Options

### Change Space Name
1. Settings → Space name
2. Can change anytime

### Make Space Private
1. Settings → Visibility → Private
2. Only you can access

### Add Collaborators
1. Settings → Add member
2. Invite by username

### Custom Domain (Advanced)
- Requires Hugging Face Pro ($9/mo)
- Can use your own domain like `mithra.yourdomain.com`

---

## Cost & Limits (Free Tier)

**What's included FREE:**
- Unlimited app hosting
- Unlimited visitors
- 2 CPU cores
- 16 GB RAM
- 50 GB storage

**You only pay for:**
- Your Anthropic API usage (~$0.20 per user session)
- Optional: HF Pro for custom domains/priority support ($9/mo)

**For your MVP testing:**
- Hosting: **FREE** ✅
- 50 test sessions: **~$10** in API costs
- Total: **$10** (vs. Replit burning credits fast)

---

## Sharing Your Space

**Direct link:**
```
https://huggingface.co/spaces/YOUR_USERNAME/mithra-research-assistant
```

**Embed in website:**
```html
<iframe
  src="https://YOUR_USERNAME-mithra-research-assistant.hf.space"
  width="100%"
  height="800px"
></iframe>
```

**Share on social:**
- HF creates nice preview cards automatically
- Just paste the link on Twitter, Slack, etc.

---

## Monitoring & Analytics

### View Usage
1. Go to your Space
2. Click **"Insights"** (if available)
3. See: visitors, sessions, popularity

### Check Logs
1. **"Logs"** tab shows real-time app output
2. Useful for debugging
3. See errors, API calls, user actions

---

## Next Steps After Deployment

### 1. Test with Real Users (Week 1)
- Share link with 3-5 ML practitioners
- Collect feedback
- Monitor logs for errors

### 2. Iterate Based on Feedback (Week 2)
- Update code on GitHub
- Changes auto-deploy to HF Space
- No downtime needed

### 3. Add Features (Sprint 2-3)
- RAG integration (ChromaDB)
- Visualization scripts
- Experiment design guidance

### 4. Demo Prep
- Record session showing workflow
- Prepare metrics (time saved, comprehension quality)
- Create presentation

---

## Support Resources

**Hugging Face Docs:**
- Spaces guide: https://huggingface.co/docs/hub/spaces
- Gradio docs: https://www.gradio.app/docs

**MITHRA Docs:**
- See `README.md` for setup
- See `DEPLOYMENT_GUIDE.md` for general info
- See `PROJECT_SUMMARY.md` for architecture

**Community:**
- HF Discord: https://discuss.huggingface.co/
- Anthropic Discord: For API issues

---

## Summary Checklist

- [ ] Created Hugging Face account
- [ ] Created new Space (Gradio SDK)
- [ ] Uploaded all MITHRA files
- [ ] Added ANTHROPIC_API_KEY secret
- [ ] Waited for build to complete
- [ ] Tested with sample PDF
- [ ] Shared link with test users
- [ ] Monitoring logs and usage

---

**Your MITHRA app is now live and FREE! 🎉**

**Questions?** Check the troubleshooting section above or reach out to your bootcamp cohort.

Built for **Anthropic AI Engineering Bootcamp 2025** 🚀
