# MITHRA Deployment Guide for Replit

## Quick Start (5 minutes)

### Step 1: Create Replit Project
1. Go to https://replit.com
2. Click "Create Repl"
3. Choose "Import from GitHub" OR "Blank Repl" with Python template
4. Name it: `mithra-research-assistant`

### Step 2: Upload Files
If you created a blank Repl:
- Upload all files from `mithra_replit/` directory
- Maintain the same folder structure:
  ```
  utils/
  workflows/
  prompts/
  main.py
  config.py
  requirements.txt
  ```

### Step 3: Configure API Key
1. In Replit, click the **lock icon** (🔒) or go to **Tools → Secrets**
2. Add a new secret:
   - Key: `ANTHROPIC_API_KEY`
   - Value: Your Claude API key from https://console.anthropic.com/
3. Click "Add Secret"

### Step 4: Install Dependencies
In the Replit Shell tab, run:
```bash
pip install -r requirements.txt
```

Wait for installation to complete (~1-2 minutes).

### Step 5: Run the App
Click the green **Run** button, or in Shell:
```bash
python main.py
```

You should see:
```
🚀 Starting MITHRA...
📚 Upload a research paper to begin your personalized learning session

Running on local URL:  http://0.0.0.0:7860
```

Replit will automatically open the Gradio interface in a new tab.

---

## Testing the Workflow

### Test with Sample Paper
1. **Upload PDF**: Use any research paper PDF (ML, NLP, computer vision papers work well)
   - Good test papers: arXiv papers on Transformers, RAG, prompt engineering
   - Make sure PDF has selectable text (not scanned images)

2. **Answer Context Questions**:
   - Role: "ML engineer"
   - Background: "Moderate - understand basics but not deeply"
   - Goal: "Solve a specific problem at work"
   - Time: "Standard (45-60 min)"
   - Depth: "Balanced"

3. **Wait for Module Generation** (~10-20 seconds)
   - AI will analyze paper and create personalized learning plan

4. **Engage with Modules**:
   - Read Module 1 content
   - Ask questions: "Can you explain X in simpler terms?"
   - Ask for examples: "Give me a concrete example"
   - Request connections: "How does this relate to Y?"
   - Advance: Say "next module" or "continue"

5. **Complete Session**:
   - Work through all modules
   - Ask clarifying questions
   - Test understanding

---

## Troubleshooting

### Error: "ANTHROPIC_API_KEY not configured"
- **Solution**: Make sure you added the API key to Replit Secrets (not .env file)
- Restart the app after adding the secret

### Error: "Could not extract text from PDF"
- **Solution**: PDF might be scanned images. Try a different paper.
- Alternative: Copy/paste paper text directly (would need code modification)

### App crashes or restarts
- **Cause**: Replit containers restart periodically (free tier)
- **Impact**: Session data lost (user needs to re-upload paper)
- **Future fix**: Add session persistence with Replit DB

### Slow response times
- **Normal**: First API call to Claude can take 5-10 seconds
- **Module generation**: 10-20 seconds (analyzing full paper)
- **Teaching responses**: 3-5 seconds typically

### Dependencies not installing
- Try manual install: `pip install anthropic gradio pypdf2 python-dotenv`
- Check Python version (should be 3.9+)

---

## Customization

### Change Model
In `config.py`, modify:
```python
CLAUDE_MODEL = "claude-sonnet-4-20250514"  # Change to different model
```

Options:
- `claude-sonnet-4-20250514` - Latest, best quality (recommended)
- `claude-3-5-sonnet-20241022` - Previous version, faster
- `claude-3-haiku-20240307` - Cheapest, faster but lower quality

### Adjust Teaching Style
Edit prompts in `prompts/pedagogy_prompts.py`:
- `LEARNING_STRATEGY_SYSTEM_PROMPT` - Controls module generation style
- `TEACHING_SYSTEM_PROMPT` - Controls teaching delivery tone

### Add More Context Questions
In `config.py`, modify `CONTEXT_QUESTIONS` list and add corresponding prompts in `prompts/context_prompts.py`.

---

## Sharing Your App

### Public URL
- Replit automatically provides a public URL
- Look for "Open in new tab" icon when app is running
- Share this URL with test users

### Embedding
- Gradio apps can be embedded in webpages
- Use the "Share" button in Gradio interface for iframe code

---

## Next Steps

### Add Vector DB (RAG)
See `RAG_IMPLEMENTATION_PLAN.md` for adding ChromaDB:
1. Add `chromadb` to requirements.txt
2. Create knowledge base corpus
3. Modify module_generator.py to query RAG
4. Enhanced personalization with retrieved best practices

### Add Visualization Scripts
1. Create `workflows/visualization_scripter.py`
2. Add hypnosis script templates
3. Generate personalized guided meditation/visualization

### Add Experiment Design
1. Create `workflows/experiment_designer.py`
2. Help users design validation experiments
3. Connect research concepts to their specific problems

---

## Performance Optimization

### Token Usage
Current configuration:
- Context collection: ~500 tokens
- Module generation: ~8000 tokens input + ~2000 output
- Teaching per message: ~1500 tokens output

Cost per session (typical 10-message conversation):
- ~20,000 tokens total
- ~$0.20 with Sonnet-4 pricing

### Reduce Costs
1. Switch to Haiku model (10x cheaper)
2. Truncate paper text more aggressively
3. Reduce max_tokens in responses

### Speed Up Responses
1. Use Haiku for context collection (fast, simple task)
2. Use Sonnet only for module generation and teaching
3. Reduce max_tokens (faster generation)

---

## Production Readiness Checklist

- [ ] API key in Secrets (not hardcoded)
- [ ] Error handling for failed API calls
- [ ] Session timeout handling
- [ ] Rate limiting (if many users)
- [ ] User feedback collection
- [ ] Analytics/logging for improvements
- [ ] Privacy policy for uploaded papers
- [ ] Persistent storage for sessions (Replit DB)

---

**Questions or Issues?**

Check the main README.md or contact the bootcamp cohort on Slack.

Built for **Anthropic AI Engineering Bootcamp 2025** 🚀
