"""Configuration for MITHRA application"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"  # Latest Sonnet model

# Session Configuration
MAX_HISTORY_LENGTH = 20  # Keep last 20 messages in context

# Workflow States
class State:
    INIT = "init"
    PAPER_RECEIVED = "paper_received"
    COLLECTING_CONTEXT = "collecting_context"
    CONTEXT_COMPLETE = "context_complete"
    GENERATING_MODULES = "generating_modules"
    TEACHING = "teaching"
    COMPLETE = "complete"

# Context Collection Questions
CONTEXT_QUESTIONS = [
    "role",           # Professional role
    "background",     # Educational/technical background
    "goal",          # Learning goal for this paper
    "time",          # Time available
    "depth"          # Desired depth (overview vs deep-dive)
]
