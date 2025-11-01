# MITHRA Architecture - Demo Version

**Sprint 1 Deliverable - November 2025**

---

## 🎯 System Overview

MITHRA transforms dense academic research papers into personalized learning experiences in under an hour (vs. 1-5 hours traditional reading).

```
┌─────────────┐
│   Researcher │
│  Practitioner│
└──────┬──────┘
       │ Upload PDF
       ▼
┌─────────────────────────────────┐
│     MITHRA Learning System      │
│  ┌──────────────────────────┐  │
│  │  1. PDF Processor        │  │
│  │     Extract + Analyze    │  │
│  └──────────────────────────┘  │
│  ┌──────────────────────────┐  │
│  │  2. Context Collector    │  │
│  │     5 Questions Profile  │  │
│  └──────────────────────────┘  │
│  ┌──────────────────────────┐  │
│  │  3. Module Generator     │◄─┼─ Claude API
│  │     Personalized Plan    │  │  (Anthropic)
│  └──────────────────────────┘  │
│  ┌──────────────────────────┐  │
│  │  4. Interactive Teaching │  │
│  │     Q&A + Adaptation     │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
       │
       ▼ Deep Understanding
┌──────────────────┐
│  Apply to Work   │
│ Design Experiments│
└──────────────────┘
```

---

## 🏗️ Core Components

### **Input Layer**
```
📄 Research Paper PDF
    ↓ PyPDF2
📝 Plain Text + Metadata
```

### **Personalization Layer**
```
👤 User Profile (5 Questions)
   ├─ Professional Role
   ├─ Technical Background
   ├─ Learning Goal
   ├─ Time Available
   └─ Desired Depth
```

### **AI Generation Layer**
```
🤖 Claude Sonnet 4
   ├─ Analyzes Paper
   ├─ Considers User Profile
   ├─ Creates 3-5 Learning Modules
   └─ Delivers Interactive Teaching
```

### **Output Layer**
```
📚 Personalized Learning Session
   ├─ Tailored Explanations
   ├─ Relevant Examples
   ├─ Q&A Support
   └─ Application Guidance
```

---

## 🔄 User Journey

```
Step 1: Upload Paper
        ↓
Step 2: Answer 5 Questions (2 min)
        ↓
Step 3: Review Learning Plan (1 min)
        ↓
Step 4: Interactive Learning (40-60 min)
        ├─ Read Module 1
        ├─ Ask Questions
        ├─ Request Examples
        ├─ Next Module
        └─ Repeat...
        ↓
Step 5: Apply Knowledge
```

**Total Time:** 45-75 minutes
**vs Traditional:** 1-5 hours

---

## 💻 Technical Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **UI** | Gradio | Web interface |
| **Runtime** | Python 3.10 | Application logic |
| **AI** | Claude Sonnet 4 | Content generation |
| **PDF** | PyPDF2 | Text extraction |
| **Hosting** | Render.com | Free cloud deployment |
| **Deploy** | Git + GitHub | Auto-deploy pipeline |

---

## 🎨 Key Features (Sprint 1 MVP)

✅ **PDF Upload** - Any research paper
✅ **Smart Extraction** - Title, length, content
✅ **Context Collection** - 5-question profile
✅ **Personalization** - Matched to user expertise
✅ **Modular Learning** - Digestible chunks
✅ **Interactive Q&A** - Ask anytime
✅ **Cloud Deployed** - Public URL for testing

---

## 🔮 Future Enhancements

### Sprint 2 (Nov 10)
- **RAG Integration** - ChromaDB knowledge base
- **Best Practices** - 60+ curated teaching strategies
- **Visualization Scripts** - Hypnosis/meditation generation

### Sprint 3 (Nov 24)
- **Voice Synthesis** - ElevenLabs audio output
- **Experiment Design** - Guided validation planning
- **Multi-Paper** - Comparative analysis

---

## 📊 Current Metrics

**Performance:**
- Module Generation: 10-20 seconds
- Response Time: 3-5 seconds
- Session Length: 45-75 minutes

**Cost:**
- Hosting: FREE (Render.com)
- API Usage: ~$0.20 per session
- 50 test sessions: ~$10 total

**User Capacity:**
- Free tier: 1-2 concurrent users
- Sufficient for bootcamp testing

---

## 🔒 Security & Privacy

✅ **Code Private** - GitHub repo not public
✅ **API Keys Secure** - Environment secrets
✅ **No Data Storage** - PDFs processed in-memory
✅ **HTTPS** - Encrypted connections
✅ **Prompts Hidden** - Not visible to users

---

## 🚀 Live Demo

**URL:** https://mithra-jerx.onrender.com

**Test Flow:**
1. Upload sample research paper
2. Answer profile questions
3. Receive personalized learning plan
4. Interactive teaching session

**Note:** First load may take 30-60 sec (cold start on free tier)

---

## 🎯 Problem → Solution

### Problem
Practitioners spend 1-5 hours struggling with dense academic papers written for experts, often failing to extract actionable insights.

### Solution
MITHRA creates personalized learning experiences that:
- Match the user's expertise level
- Focus on their specific goals
- Teach interactively (not just summarize)
- Connect concepts to practical applications

### Result
Deep understanding in 45-75 minutes with confidence to apply learnings.

---

**Built for Anthropic AI Engineering Bootcamp 2025** 🚀

Sprint 1 Demo - November 1, 2025
