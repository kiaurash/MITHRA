"""Context collection workflow - gathers user background and goals"""
from prompts.context_prompts import INITIAL_GREETING, CONTEXT_PROMPTS, get_context_summary_prompt
from workflows.session_manager import SessionManager
from config import State

class ContextCollector:
    """Manages the context collection dialogue"""

    def __init__(self, session: SessionManager):
        self.session = session

    def get_initial_message(self) -> str:
        """
        Get initial greeting after paper upload.

        Returns:
            Welcome message with first question
        """
        return INITIAL_GREETING

    def process_user_response(self, user_message: str) -> str:
        """
        Process user's answer and return next question or completion message.

        Args:
            user_message: User's response to current question

        Returns:
            Next question or completion summary
        """
        # Get current question being answered
        current_q_key = self.session.get_next_context_question()

        if current_q_key is None:
            # All questions answered - shouldn't happen but handle gracefully
            return get_context_summary_prompt(self.session.user_context)

        # Store the answer
        self.session.add_context_answer(current_q_key, user_message)

        # Check if done
        if self.session.is_context_complete():
            return get_context_summary_prompt(self.session.user_context)

        # Get next question
        next_q_key = self.session.get_next_context_question()
        if next_q_key and next_q_key in CONTEXT_PROMPTS:
            return CONTEXT_PROMPTS[next_q_key]
        else:
            # Fallback
            return get_context_summary_prompt(self.session.user_context)

    def is_complete(self) -> bool:
        """Check if context collection is finished"""
        return self.session.is_context_complete()
