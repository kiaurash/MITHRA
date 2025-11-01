# Memento-Inspired Agentic Search Agent

A simplified implementation demonstrating how to build a continuously-learning search agent based on the **Memento** paper approach.

## Overview

This mock-up shows the core concepts from [Memento: Fine-tuning LLM Agents without Fine-tuning LLMs](https://arxiv.org/abs/2508.16153) applied to agentic search.

**Key Features:**
- ✅ Episodic memory storing complete search trajectories
- ✅ Case-based retrieval of similar past successful searches
- ✅ Policy learning for search strategy selection
- ✅ Continuous improvement from every search interaction
- ✅ No LLM fine-tuning required

## Architecture

```
User Query
    ↓
Query Encoding
    ↓
Memory Retrieval (find similar past successful searches)
    ↓
Policy Selection (choose search strategy based on past experience)
    ↓
Execute Search
    ↓
Record Outcome (clicks, dwell time, satisfaction)
    ↓
Update Policy & Store Trajectory
```

## Components

### 1. EpisodicMemory
Stores and retrieves past search trajectories:
- Query text and embeddings
- Search strategies used
- User behavior (clicks, dwell times)
- Satisfaction outcomes
- Computed rewards

### 2. SearchPolicy
Learns which search strategies work for different queries:
- Selects actions based on query + retrieved memories
- Balances exploration (trying new strategies) vs exploitation (using known good strategies)
- Updates based on observed rewards

### 3. MementoSearchAgent
Main orchestrator combining memory + policy:
- Encodes queries
- Retrieves similar past searches
- Selects optimal strategy
- Records outcomes
- Continuously learns

## Quick Start

```bash
# Install dependencies
pip install numpy

# Run demo
python agentic_search_agent.py
```

## Demo Output

The demo simulates 5 search interactions and shows:
1. **Initial searches** - Agent starts with default strategies
2. **Learning progress** - Memory accumulates, policy improves
3. **New query** - Agent applies learned strategies to similar new query
4. **Statistics** - Success rates, memory size, policy performance

## Key Differences from Full Memento

This is a **simplified educational mock-up**. The full Memento implementation includes:

| Component | Mock-up | Full Memento |
|-----------|---------|--------------|
| Embeddings | Random hash-based | Sentence transformers / OpenAI |
| Memory Retrieval | In-memory list | Vector database (Pinecone, Weaviate) |
| Policy Learning | Weighted voting | Soft Actor-Critic (SAC) RL |
| Action Space | 3 parameters | Complex action spaces |
| Reward Function | Simple heuristic | Learned from outcomes |

## Extending to Production

To build a production system, enhance:

### 1. Embeddings
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
query_embedding = model.encode(query)
```

### 2. Vector Database
```python
import pinecone

# Store trajectories with vector embeddings
index.upsert([(id, embedding, metadata)])

# Retrieve similar
results = index.query(query_embedding, top_k=5)
```

### 3. RL Policy (Soft Actor-Critic)
```python
from stable_baselines3 import SAC

# Train policy on (state, action, reward) experiences
model = SAC("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)
```

### 4. Better Reward Signals
```python
def compute_reward(interaction):
    reward = 0.0

    # Click-through rate
    reward += 0.2 * ctr

    # Dwell time (engagement)
    reward += 0.3 * normalized_dwell_time

    # Explicit feedback
    if interaction.thumbs_up:
        reward += 0.3

    # Business metrics
    if interaction.conversion:
        reward += 0.2

    return reward
```

### 5. User Personalization
```python
# Include user context in state
state = {
    "query_embedding": query_emb,
    "user_profile": {
        "expertise_level": "expert",
        "preferred_sources": ["arxiv", "github"],
        "recent_searches": [...]
    },
    "session_context": {
        "time_of_day": "morning",
        "device": "desktop"
    }
}
```

## Architecture for Your Team

```python
# Phase 1: Logging (Week 1-2)
# Start collecting data
log_search_trajectory(query, action, outcome)

# Phase 2: Memory Retrieval (Week 3-4)
# Add similarity-based retrieval
similar_searches = retrieve_similar(query_embedding)

# Phase 3: Policy Learning (Week 5-8)
# Implement RL optimization
policy = train_sac_policy(trajectories)
action = policy.select_action(state)

# Phase 4: Continuous Learning (Ongoing)
# Online learning from every interaction
policy.update(state, action, reward)
```

## References

- **Paper:** [Memento: Fine-tuning LLM Agents without Fine-tuning LLMs](https://arxiv.org/abs/2508.16153)
- **Official Repo:** https://github.com/Agent-on-the-Fly/Memento
- **Learning Session:** See `../sessions/session_2025-10-31_*.md` for detailed concept explanations

## Questions for Your Team

1. **Reward function:** What defines a "good search" in your domain?
2. **Action space:** What search parameters should the agent control?
3. **State representation:** What user context is relevant?
4. **Exploration strategy:** How to balance trying new approaches vs. using proven ones?
5. **Evaluation:** How to measure continuous improvement?

---

**Created:** 2025-10-31
**Context:** MITHRA learning session on Memento for agentic search
