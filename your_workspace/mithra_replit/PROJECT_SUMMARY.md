# MITHRA Replit MVP - Project Summary

## ✅ What We Built

A simplified version of MITHRA (Machine Intelligence for Translating Human Research into Action) ready to deploy on Replit.

**Core Features:**
- PDF upload and text extraction
- Personalized context collection (5 questions about user background/goals)
- AI-generated learning modules tailored to user
- Interactive teaching conversation with Claude
- Gradio web interface with chat + file upload

**Excluded from MVP (future enhancements):**
- Vector database / RAG system
- Visualization script generation
- Experiment design guidance
- Session persistence across restarts

---

## 📂 Project Structure

```
mithra_replit/
├── main.py                          # Gradio app entry point
├── config.py                        # Configuration & state management
├── requirements.txt                 # Python dependencies
├── README.md                        # Setup instructions
├── DEPLOYMENT_GUIDE.md              # Detailed deployment steps
├── PROJECT_SUMMARY.md               # This file
├── .env.example                     # API key template
│
├── utils/
│   ├── __init__.py
│   └── pdf_processor.py             # PDF text extraction
│
├── workflows/
│   ├── __init__.py
│   ├── session_manager.py           # Session state tracking
│   ├── context_collector.py         # User intake dialogue
│   └── module_generator.py          # Module creation & teaching
│
└── prompts/
    ├── __init__.py
    ├── context_prompts.py           # Context collection templates
    └── pedagogy_prompts.py          # Teaching & module generation prompts
```

**Total Files:** 14 files
**Lines of Code:** ~800 lines

---

## 🔄 User Workflow

1. **Upload Paper** → User uploads research paper PDF
2. **Extract Text** → PyPDF2 extracts text content
3. **Collect Context** → 5 questions about background, goal, time, depth
4. **Generate Modules** → Claude analyzes paper + user context → creates personalized learning plan
5. **Teach** → Conversational delivery of modules with Q&A
6. **Complete** → User gains understanding of paper concepts

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **UI Framework** | Gradio 4.44 | Web interface with chat + file upload |
| **LLM** | Claude Sonnet 4 (Anthropic API) | Module generation & teaching |
| **PDF Processing** | PyPDF2 | Text extraction from uploaded papers |
| **Hosting** | Replit | Cloud deployment with auto-scaling |
| **State Management** | In-memory (SessionManager) | Track conversation & user context |

---

## 🎯 Key Design Decisions

### 1. No Vector DB (Simplified MVP)
**Decision:** Hardcoded prompts instead of RAG retrieval
**Rationale:** Faster to build, test core workflow first
**Trade-off:** Less sophisticated personalization
**Future:** Add ChromaDB in Sprint 2

### 2. Gradio for UI
**Decision:** Use Gradio instead of custom React/HTML
**Rationale:** Built-in chat interface, easy deployment on Replit
**Trade-off:** Less UI customization
**Benefit:** 1-hour implementation vs. days for custom UI

### 3. Session-based (not persistent)
**Decision:** In-memory session state
**Rationale:** Simpler for MVP testing
**Trade-off:** Session lost on restart
**Future:** Add Replit DB for persistence

### 4. PDF Upload (not text paste)
**Decision:** User uploads PDF file
**Rationale:** Better UX, handles formatting
**Trade-off:** Requires PyPDF2, may fail on scanned PDFs
**Benefit:** More professional, matches real workflow

### 5. Anthropic API (not local models)
**Decision:** Use Claude via API
**Rationale:** Best quality, no GPU needed
**Trade-off:** API costs (~$0.20/session)
**Benefit:** Superior personalization quality

---

## 📊 Expected Performance

### Response Times
- **PDF Upload & Processing:** 1-3 seconds
- **Context Collection:** < 1 second per question (templated)
- **Module Generation:** 10-20 seconds (analyzes full paper)
- **Teaching Responses:** 3-5 seconds

### Cost per Session
- **Tokens per session:** ~20,000 tokens (10 messages)
- **Cost (Sonnet 4):** ~$0.20 per session
- **Alternative (Haiku):** ~$0.02 per session (faster, lower quality)

### Scalability
- **Concurrent users:** 5-10 on free Replit tier
- **Storage:** Minimal (no persistent data)
- **Bottleneck:** Anthropic API rate limits

---

## 🧪 Testing Checklist

Before deploying to Replit:

- [ ] Upload sample research paper (arXiv PDF)
- [ ] Verify text extraction works
- [ ] Complete full context collection (5 questions)
- [ ] Check module generation quality
- [ ] Test teaching conversation (ask questions)
- [ ] Verify "next module" advance works
- [ ] Test reset session functionality
- [ ] Check error handling (no API key, bad PDF)

**Test Papers:**
- "Attention Is All You Need" (Transformers paper)
- "RAG: Retrieval-Augmented Generation"
- Any recent arXiv paper in your domain

---

## 🚀 Deployment Steps (Quick Reference)

1. **Create Replit** → Import files or upload manually
2. **Add API Key** → Replit Secrets: `ANTHROPIC_API_KEY`
3. **Install Deps** → `pip install -r requirements.txt`
4. **Run App** → `python main.py`
5. **Test** → Upload paper, complete workflow
6. **Share** → Get public URL from Replit

Full details in `DEPLOYMENT_GUIDE.md`

---

## 🔮 Future Enhancements (Roadmap)

### Sprint 2 (Weeks 3-4)
- [ ] Add ChromaDB for RAG-based best practices
- [ ] Visualization script generation module
- [ ] Session persistence with Replit DB
- [ ] Multi-paper support (compare papers)

### Sprint 3 (Weeks 5-6)
- [ ] Experiment design guidance
- [ ] Voice synthesis (ElevenLabs integration)
- [ ] Socratic questioning for application
- [ ] Learning retention follow-ups

### Post-Bootcamp
- [ ] User accounts & history
- [ ] Mobile-responsive UI
- [ ] Paper discovery/recommendation
- [ ] Code repository analysis (Stage 4)

---

## 📈 Success Metrics (MVP)

### Primary Metrics
1. **Time to understanding:** ≤ 75 minutes (vs. 1-5 hours traditional)
2. **Comprehension quality:** Users can explain core concepts
3. **Personalization value:** Users report explanations matched their background

### Secondary Metrics
4. **User satisfaction:** Would use again vs. traditional reading
5. **Engagement:** Avg. questions asked per session
6. **Completion rate:** % of users who finish full session

### Data Collection
- Session logs (anonymized)
- Post-session survey (5 questions)
- Follow-up assessment (1 week later)

---

## 🐛 Known Limitations

1. **PDF Extraction:** Fails on scanned images/poor quality PDFs
   - *Workaround:* Use text-selectable PDFs

2. **Session Persistence:** Lost on Replit restart
   - *Workaround:* Complete session in one sitting (~60 min)

3. **No RAG:** Less sophisticated than full MITHRA design
   - *Acceptable for MVP:* Hardcoded prompts still effective

4. **Single Paper:** No multi-paper comparison
   - *Future feature:* Sprint 2 enhancement

5. **Context Truncation:** Only first 8000 chars of paper analyzed
   - *Acceptable:* Usually captures abstract + intro + methodology

---

## 💡 Customization Tips

### Change Personality/Tone
Edit `prompts/pedagogy_prompts.py`:
- `LEARNING_STRATEGY_SYSTEM_PROMPT` - Module generation style
- `TEACHING_SYSTEM_PROMPT` - Teaching delivery tone

### Add/Remove Context Questions
Edit `config.py`:
- Modify `CONTEXT_QUESTIONS` list
- Add prompts in `prompts/context_prompts.py`

### Adjust Paper Length Limit
Edit `prompts/pedagogy_prompts.py`:
- Change `paper_text[:8000]` to desired character limit
- Trade-off: More context = slower + more expensive

### Switch Claude Model
Edit `config.py`:
- Change `CLAUDE_MODEL` constant
- Options: sonnet-4, sonnet-3.5, haiku

---

## 📝 Code Quality Notes

### Architecture Patterns
- **Separation of Concerns:** Workflows, prompts, utils separated
- **Session State Machine:** Clear state transitions
- **Dependency Injection:** SessionManager passed to workflows
- **Error Handling:** Try/except blocks for API calls

### Code Style
- Type hints for function signatures
- Docstrings for all public functions
- PEP 8 compliant (mostly)
- Simple > clever (KISS principle)

### Maintainability
- Prompts in separate files (easy to edit)
- Config centralized in config.py
- Minimal dependencies (4 packages)
- Clear file organization

---

## 🎓 Learning Outcomes (Bootcamp Context)

This MVP demonstrates:
- **Multi-turn conversational AI** with state management
- **Prompt engineering** for personalization
- **Gradio deployment** for quick prototyping
- **API integration** (Anthropic Claude)
- **User-centered design** (context collection for personalization)

Skills practiced:
- Python project structuring
- LLM application architecture
- User experience design
- Deployment workflows

---

**Next Steps:** Deploy to Replit and test with 3-5 users!

See `DEPLOYMENT_GUIDE.md` for detailed instructions.

Built for **Anthropic AI Engineering Bootcamp 2025** 🚀
