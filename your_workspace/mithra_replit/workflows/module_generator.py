"""Module generation and teaching workflow"""
import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from workflows.session_manager import SessionManager
from prompts.pedagogy_prompts import (
    LEARNING_STRATEGY_SYSTEM_PROMPT,
    TEACHING_SYSTEM_PROMPT,
    get_module_generation_prompt,
    get_teaching_prompt
)

class ModuleGenerator:
    """Generates personalized learning modules and delivers teaching content"""

    def __init__(self, session: SessionManager):
        self.session = session
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def generate_learning_plan(self) -> str:
        """
        Generate personalized learning modules based on paper and user context.

        Returns:
            Learning plan with modules
        """
        prompt = get_module_generation_prompt(
            self.session.paper_text,
            self.session.user_context
        )

        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=2000,
                system=LEARNING_STRATEGY_SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            plan = response.content[0].text
            self.session.set_module_plan(plan)

            # Return intro message with plan
            return f"""**Your Personalized Learning Plan**

{plan}

---

Ready to start? I'll guide you through each module. Feel free to ask questions anytime!

Let's begin with Module 1..."""

        except Exception as e:
            return f"Error generating learning plan: {str(e)}\n\nPlease check your API key configuration."

    def teach_module(self, user_message: str) -> str:
        """
        Deliver teaching content or respond to user questions.

        Args:
            user_message: User's question or response

        Returns:
            Teaching content or answer to question
        """
        if not self.session.module_plan:
            return "Error: No learning plan generated yet."

        # Build conversation context
        messages = []

        # Add module plan context
        teaching_prompt = get_teaching_prompt(
            self.session.module_plan,
            self.session.current_module,
            user_message
        )

        messages.append({
            "role": "user",
            "content": teaching_prompt
        })

        # Add recent conversation history for context
        for msg in self.session.conversation_history[-6:]:  # Last 3 exchanges
            messages.append(msg)

        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1500,
                system=TEACHING_SYSTEM_PROMPT,
                messages=messages
            )

            reply = response.content[0].text

            # Store in conversation history
            self.session.add_message("user", user_message)
            self.session.add_message("assistant", reply)

            return reply

        except Exception as e:
            return f"Error during teaching: {str(e)}"

    def check_for_module_advance(self, user_message: str) -> bool:
        """
        Heuristic to detect if user wants to move to next module.

        Args:
            user_message: User's message

        Returns:
            True if should advance to next module
        """
        advance_keywords = [
            "next module",
            "move on",
            "continue",
            "next topic",
            "got it",
            "makes sense",
            "clear"
        ]

        msg_lower = user_message.lower()
        return any(keyword in msg_lower for keyword in advance_keywords)
