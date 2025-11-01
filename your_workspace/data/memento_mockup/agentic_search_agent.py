"""
Memento-Inspired Agentic Search Agent
--------------------------------------
Simplified implementation demonstrating:
1. Episodic memory for search trajectories
2. Case-based retrieval of successful past searches
3. Policy learning for search strategy selection

Based on: https://github.com/Agent-on-the-Fly/Memento
Adapted for: Continuous-learning agentic search
"""

import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np
from collections import defaultdict


@dataclass
class SearchTrajectory:
    """Stores a complete search interaction"""
    query_text: str
    query_embedding: List[float]  # Would use actual embeddings in production
    user_context: Dict  # background, history, preferences

    # Actions taken
    search_strategy: str  # "semantic", "keyword", "hybrid", etc.
    ranking_method: str   # "relevance", "citations", "recency"
    diversity_param: float  # 0.0 = focused, 1.0 = diverse

    # Outcomes
    results_shown: List[str]
    clicks: List[int]  # indices of clicked results
    dwell_times: List[float]  # seconds spent on each clicked result
    user_satisfied: bool
    follow_up_query: Optional[str]

    # Metadata
    timestamp: str
    reward: float  # computed from outcomes


@dataclass
class SearchAction:
    """Represents a search strategy decision"""
    search_strategy: str
    ranking_method: str
    diversity_param: float


class EpisodicMemory:
    """Stores and retrieves past search trajectories"""

    def __init__(self, max_size: int = 10000):
        self.trajectories: List[SearchTrajectory] = []
        self.max_size = max_size

    def store(self, trajectory: SearchTrajectory):
        """Store a trajectory in memory"""
        self.trajectories.append(trajectory)

        # Keep memory bounded
        if len(self.trajectories) > self.max_size:
            # Remove oldest trajectories (could use more sophisticated eviction)
            self.trajectories = self.trajectories[-self.max_size:]

    def retrieve_similar(self, query_embedding: List[float], top_k: int = 5,
                        min_reward: float = 0.5) -> List[SearchTrajectory]:
        """
        Retrieve similar successful past searches

        In production, this would use:
        - Vector database (Pinecone, Weaviate, Qdrant)
        - Actual embeddings from sentence transformers
        - More sophisticated similarity metrics
        """
        # Filter for successful trajectories
        successful = [t for t in self.trajectories if t.reward >= min_reward]

        if not successful:
            return []

        # Compute similarity scores (simplified - would use cosine similarity in production)
        similarities = []
        for traj in successful:
            # Simplified: dot product (assumes normalized embeddings)
            sim = sum(a * b for a, b in zip(query_embedding, traj.query_embedding))
            similarities.append((sim, traj))

        # Return top-k most similar
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [traj for _, traj in similarities[:top_k]]

    def get_stats(self) -> Dict:
        """Get memory statistics"""
        if not self.trajectories:
            return {"count": 0, "avg_reward": 0.0}

        return {
            "count": len(self.trajectories),
            "avg_reward": np.mean([t.reward for t in self.trajectories]),
            "success_rate": sum(1 for t in self.trajectories if t.user_satisfied) / len(self.trajectories)
        }


class SearchPolicy:
    """
    Policy network for selecting search strategies

    In Memento, this uses Soft Actor-Critic (SAC) RL.
    Here, we use a simplified approach for illustration.
    """

    def __init__(self):
        # Strategy performance tracking (simplified policy)
        self.strategy_stats = defaultdict(lambda: {"successes": 0, "attempts": 0})

        # Available strategies
        self.search_strategies = ["semantic", "keyword", "hybrid", "citation_based"]
        self.ranking_methods = ["relevance", "citations", "recency", "popularity"]

    def select_action(self, query_embedding: List[float],
                     retrieved_memories: List[SearchTrajectory],
                     exploration_rate: float = 0.1) -> SearchAction:
        """
        Select search strategy based on query and retrieved memories

        Real implementation would use:
        - Neural network (policy network from SAC)
        - Learned from (state, action, reward) experience
        - Balances exploration vs exploitation
        """

        # If we have similar successful past queries, learn from them
        if retrieved_memories:
            # Extract common successful strategies
            strategy_votes = defaultdict(int)
            ranking_votes = defaultdict(int)
            diversity_values = []

            for mem in retrieved_memories:
                strategy_votes[mem.search_strategy] += mem.reward
                ranking_votes[mem.ranking_method] += mem.reward
                diversity_values.append(mem.diversity_param)

            # Weighted voting by reward
            best_strategy = max(strategy_votes.items(), key=lambda x: x[1])[0]
            best_ranking = max(ranking_votes.items(), key=lambda x: x[1])[0]
            avg_diversity = np.mean(diversity_values) if diversity_values else 0.5

            # Exploration: occasionally try something different
            if np.random.random() < exploration_rate:
                best_strategy = np.random.choice(self.search_strategies)
                best_ranking = np.random.choice(self.ranking_methods)
                avg_diversity = np.random.random()

            return SearchAction(
                search_strategy=best_strategy,
                ranking_method=best_ranking,
                diversity_param=avg_diversity
            )

        else:
            # No similar memories - use heuristic or random exploration
            return SearchAction(
                search_strategy="semantic",  # reasonable default
                ranking_method="relevance",
                diversity_param=0.5
            )

    def update(self, action: SearchAction, reward: float):
        """
        Update policy based on observed reward

        Real implementation would:
        - Compute policy gradient
        - Update neural network weights
        - Use SAC loss function
        """
        # Simplified: track success rates
        key = f"{action.search_strategy}_{action.ranking_method}"
        self.strategy_stats[key]["attempts"] += 1
        if reward > 0.5:
            self.strategy_stats[key]["successes"] += 1

    def get_performance(self) -> Dict:
        """Get policy performance statistics"""
        performance = {}
        for strategy, stats in self.strategy_stats.items():
            if stats["attempts"] > 0:
                performance[strategy] = {
                    "success_rate": stats["successes"] / stats["attempts"],
                    "attempts": stats["attempts"]
                }
        return performance


class MementoSearchAgent:
    """
    Main agent combining episodic memory + policy learning
    """

    def __init__(self):
        self.memory = EpisodicMemory()
        self.policy = SearchPolicy()

    def search(self, query: str, user_context: Dict) -> Tuple[SearchAction, List[str]]:
        """
        Execute search with learned strategy

        Returns: (action_taken, search_results)
        """
        # 1. Encode query (simplified - would use sentence transformers)
        query_embedding = self._encode_query(query)

        # 2. Retrieve similar past successful searches
        similar_memories = self.memory.retrieve_similar(query_embedding, top_k=5)

        print(f"\n[QUERY] {query}")
        print(f"[MEMORY] Retrieved {len(similar_memories)} similar past searches")

        # 3. Policy selects action based on query + memories
        action = self.policy.select_action(query_embedding, similar_memories)

        print(f"[ACTION] Selected strategy: {action.search_strategy} + {action.ranking_method}")
        print(f"         Diversity: {action.diversity_param:.2f}")

        # 4. Execute search (mock implementation)
        results = self._execute_search(query, action)

        return action, results

    def record_outcome(self, query: str, action: SearchAction, results: List[str],
                      clicks: List[int], dwell_times: List[float],
                      user_satisfied: bool, follow_up_query: Optional[str] = None):
        """
        Record search outcome and learn from it
        """
        # Compute reward from user behavior
        reward = self._compute_reward(clicks, dwell_times, user_satisfied)

        # Create trajectory
        trajectory = SearchTrajectory(
            query_text=query,
            query_embedding=self._encode_query(query),
            user_context={},  # Would include user profile
            search_strategy=action.search_strategy,
            ranking_method=action.ranking_method,
            diversity_param=action.diversity_param,
            results_shown=results,
            clicks=clicks,
            dwell_times=dwell_times,
            user_satisfied=user_satisfied,
            follow_up_query=follow_up_query,
            timestamp=datetime.now().isoformat(),
            reward=reward
        )

        # Store in episodic memory
        self.memory.store(trajectory)

        # Update policy
        self.policy.update(action, reward)

        print(f"\n[OUTCOME] Reward: {reward:.2f}")
        print(f"          Memory size: {len(self.memory.trajectories)}")

    def get_stats(self) -> Dict:
        """Get agent statistics"""
        return {
            "memory": self.memory.get_stats(),
            "policy_performance": self.policy.get_performance()
        }

    # Helper methods

    def _encode_query(self, query: str) -> List[float]:
        """
        Encode query to vector

        Production: Use sentence-transformers, OpenAI embeddings, etc.
        """
        # Mock: create pseudo-embedding from query hash
        np.random.seed(hash(query) % (2**32))
        return np.random.randn(384).tolist()  # 384-dim like sentence-transformers

    def _execute_search(self, query: str, action: SearchAction) -> List[str]:
        """
        Execute actual search

        Production: Call your search backend with the selected strategy
        """
        # Mock search results
        return [
            f"Result {i}: {action.search_strategy} search for '{query[:30]}...'"
            for i in range(10)
        ]

    def _compute_reward(self, clicks: List[int], dwell_times: List[float],
                       user_satisfied: bool) -> float:
        """
        Compute reward from user behavior

        This is critical - defines what "good search" means
        """
        reward = 0.0

        # Click-through rate contributes
        if clicks:
            reward += 0.2 * (len(clicks) / 10)  # normalized by results shown

        # Dwell time indicates engagement
        if dwell_times:
            avg_dwell = np.mean(dwell_times)
            reward += 0.3 * min(avg_dwell / 60, 1.0)  # normalized to 1 minute

        # User satisfaction is strongest signal
        if user_satisfied:
            reward += 0.5

        return min(reward, 1.0)  # cap at 1.0


def demo_usage():
    """Demonstrate the Memento search agent"""

    print("=" * 70)
    print("MEMENTO-INSPIRED AGENTIC SEARCH AGENT")
    print("Demonstrating continuous learning from search interactions")
    print("=" * 70)

    # Initialize agent
    agent = MementoSearchAgent()

    # Simulate search interactions
    queries = [
        ("best practices for RAG systems", [1, 2, 5], [45, 120, 30], True),
        ("how to implement RAG", [0, 1], [60, 90], True),
        ("RAG architecture patterns", [2, 4], [20, 15], False),  # Not satisfied
        ("retrieval augmented generation tutorial", [0, 1, 2], [90, 120, 60], True),
        ("RAG vs fine-tuning comparison", [1, 3], [75, 80], True),
    ]

    print("\n" + "=" * 70)
    print("PHASE 1: Learning from initial searches")
    print("=" * 70)

    for query, clicks, dwell_times, satisfied in queries:
        # Execute search
        action, results = agent.search(query, user_context={})

        # Record outcome
        agent.record_outcome(query, action, results, clicks, dwell_times, satisfied)
        print()

    # Show learning progress
    print("=" * 70)
    print("LEARNING PROGRESS")
    print("=" * 70)
    stats = agent.get_stats()
    print(f"\nMemory Statistics:")
    print(f"  Total trajectories: {stats['memory']['count']}")
    print(f"  Average reward: {stats['memory']['avg_reward']:.3f}")
    print(f"  Success rate: {stats['memory']['success_rate']:.1%}")

    print(f"\nPolicy Performance:")
    for strategy, perf in stats['policy_performance'].items():
        print(f"  {strategy}: {perf['success_rate']:.1%} success ({perf['attempts']} attempts)")

    # Test with new query
    print("\n" + "=" * 70)
    print("PHASE 2: Testing on similar new query")
    print("=" * 70)

    new_query = "RAG implementation guide"
    action, results = agent.search(new_query, user_context={})

    print(f"\n[INSIGHT] Agent has learned from past RAG queries!")
    print(f"          It automatically selected strategies that worked well before.")

    print("\n" + "=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    print("""
    This demonstrates Memento's core approach:

    1. [+] Episodic Memory: Stores complete search trajectories
    2. [+] Retrieval: Finds similar past successful searches
    3. [+] Policy Learning: Learns which strategies work for which queries
    4. [+] Continuous Improvement: Gets better with every search
    5. [+] No LLM Fine-tuning: Base model stays frozen

    For production, you would:
    - Use real embeddings (sentence-transformers, OpenAI)
    - Implement actual RL (Soft Actor-Critic from Stable-Baselines3)
    - Use vector database (Pinecone, Weaviate, Qdrant)
    - Define better reward signals (clicks + dwell + explicit feedback)
    - Add user personalization (track user context)
    """)


if __name__ == "__main__":
    demo_usage()
