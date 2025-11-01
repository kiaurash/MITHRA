# MITHRA - Research Learning Assistant (MVP)

Machine Intelligence for Translating Human Research into Action

## Setup Instructions for Replit

### 1. Create New Replit Project
- Go to replit.com
- Create new Repl, choose "Python" template
- Upload all files from this directory

### 2. Set Up API Key
- In Replit, go to "Secrets" (Tools → Secrets, or lock icon)
- Add secret: `ANTHROPIC_API_KEY` = your Claude API key
- Get key from: https://console.anthropic.com/

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the App
```bash
python main.py
```

Replit will automatically expose the Gradio interface with a public URL.

## How It Works

### Current MVP Features (No Vector DB):
1. **PDF Upload** - User uploads research paper
2. **Context Collection** - AI asks about user's background, goals, time available
3. **Module Generation** - Creates personalized learning modules based on paper
4. **Session State** - Maintains conversation context

### Architecture:
- **Gradio**: Web UI with chat + file upload
- **Claude API**: LLM for personalization and generation
- **PyPDF2**: Extract text from uploaded PDFs
- **Session Manager**: Track conversation state

### Workflow States:
1. `INIT` - Waiting for paper upload
2. `PAPER_RECEIVED` - Paper uploaded, ready for context collection
3. `COLLECTING_CONTEXT` - Asking user questions
4. `GENERATING_MODULES` - Creating personalized learning content
5. `TEACHING` - Delivering modules, answering questions
6. `COMPLETE` - Session finished

## Future Enhancements:
- Vector DB (ChromaDB) for RAG best practices
- Visualization script generation
- Reflection/experiment design guidance
- Multi-session persistence

## Usage:
1. Upload research paper PDF
2. Answer questions about your background and goals
3. Receive personalized learning modules
4. Ask questions to deepen understanding
5. Get guidance on applying concepts

---

**Built for Anthropic's AI Engineering Bootcamp 2025**
