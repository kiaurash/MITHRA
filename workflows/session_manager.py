"""Session state management for MITHRA conversations"""
from typing import Dict, List, Optional
from config import State, CONTEXT_QUESTIONS

class SessionManager:
    """Manages conversation state and user context throughout learning session"""

    def __init__(self):
        self.state = State.INIT
        self.paper_text = None
        self.paper_metadata = {}
        self.user_context = {}
        self.current_question_idx = 0
        self.module_plan = None
        self.current_module = 0
        self.conversation_history = []

    def set_paper(self, text: str, metadata: dict):
        """Store uploaded paper and move to context collection"""
        self.paper_text = text
        self.paper_metadata = metadata
        self.state = State.PAPER_RECEIVED

    def start_context_collection(self):
        """Begin collecting user context"""
        self.state = State.COLLECTING_CONTEXT
        self.current_question_idx = 0

    def add_context_answer(self, question_key: str, answer: str):
        """Store user's answer to context question"""
        self.user_context[question_key] = answer
        self.current_question_idx += 1

        # Check if all questions answered
        if self.current_question_idx >= len(CONTEXT_QUESTIONS):
            self.state = State.CONTEXT_COMPLETE

    def get_next_context_question(self) -> Optional[str]:
        """Get the next context collection question key"""
        if self.current_question_idx < len(CONTEXT_QUESTIONS):
            return CONTEXT_QUESTIONS[self.current_question_idx]
        return None

    def is_context_complete(self) -> bool:
        """Check if all context has been collected"""
        return len(self.user_context) >= len(CONTEXT_QUESTIONS)

    def set_module_plan(self, plan: str):
        """Store generated learning module plan"""
        self.module_plan = plan
        self.state = State.TEACHING
        self.current_module = 0

    def advance_module(self):
        """Move to next module"""
        self.current_module += 1

    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })

    def get_context_summary(self) -> str:
        """Get formatted summary of user context"""
        return f"""
Role: {self.user_context.get('role', 'N/A')}
Background: {self.user_context.get('background', 'N/A')}
Goal: {self.user_context.get('goal', 'N/A')}
Time: {self.user_context.get('time', 'N/A')}
Depth: {self.user_context.get('depth', 'N/A')}
Paper: {self.paper_metadata.get('title', 'Unknown')}
        """.strip()

    def reset(self):
        """Reset session for new paper"""
        self.__init__()
