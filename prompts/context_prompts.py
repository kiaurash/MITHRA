"""Context collection prompts for personalized learning"""

INITIAL_GREETING = """Welcome to MITHRA - your personalized research learning assistant!

I've received your paper. To create the best learning experience for you, I need to understand your background and goals.

This will take about 2-3 minutes. Let's start:

**What's your professional role?** (e.g., ML engineer, research scientist, data scientist, product manager, student)"""

CONTEXT_PROMPTS = {
    "role": "What's your professional role? (e.g., ML engineer, research scientist, data scientist)",

    "background": """Great! Now, what's your technical background in the area this paper covers?

For example:
- "Strong - I've worked with similar techniques before"
- "Moderate - I understand the basics but not deeply"
- "Beginner - This is new territory for me"
""",

    "goal": """Perfect! What's your main goal for learning this paper?

Choose one:
a) Solve a specific problem I'm facing at work
b) Explore a potential new capability/product idea
c) Continuous learning to stay current in my field
d) Other (please describe)
""",

    "time": """How much time do you have for this learning session?

- Quick (20-30 min): High-level overview
- Standard (45-60 min): Solid understanding
- Deep (90+ min): In-depth exploration
""",

    "depth": """Last question - what level of depth do you want?

- Overview: Key concepts and takeaways
- Balanced: Concepts + how they connect to existing knowledge
- Technical: Deep dive into methodology and implementation details
"""
}

def get_context_summary_prompt(context: dict) -> str:
    """Generate summary of collected context"""
    return f"""Perfect! Here's what I understand about you:

- **Role**: {context.get('role', 'Not specified')}
- **Background**: {context.get('background', 'Not specified')}
- **Goal**: {context.get('goal', 'Not specified')}
- **Time Available**: {context.get('time', 'Not specified')}
- **Desired Depth**: {context.get('depth', 'Not specified')}

I'm now analyzing the paper and creating a personalized learning plan for you. This will take about 30 seconds...
"""
