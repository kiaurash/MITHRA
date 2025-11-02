"""Module generation and teaching workflow - DEBUG VERSION"""
import anthropic
import sys
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
        print("DEBUG: ModuleGenerator.__init__ called", file=sys.stderr)
        self.session = session
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        print(f"DEBUG: Using model: {CLAUDE_MODEL}", file=sys.stderr)
        print(f"DEBUG: API key exists: {bool(ANTHROPIC_API_KEY)}", file=sys.stderr)

    def generate_learning_plan(self) -> str:
        """Generate personalized learning modules based on paper and user context."""
        print("DEBUG: generate_learning_plan called", file=sys.stderr)
        
        try:
            print("DEBUG: Getting module generation prompt", file=sys.stderr)
            # Truncate paper text if too long
            paper_text = self.session.paper_text
            if len(paper_text) > 100000:
                paper_text = paper_text[:100000] + "\n\n[Paper truncated for processing...]"
            
            print(f"DEBUG: Paper text length: {len(paper_text)}", file=sys.stderr)
            print(f"DEBUG: User context: {self.session.user_context}", file=sys.stderr)
            
            prompt = get_module_generation_prompt(
                paper_text,
                self.session.user_context
            )
            
            print(f"DEBUG: Prompt generated, length: {len(prompt)}", file=sys.stderr)
            print(f"DEBUG: About to call Anthropic API with model: {CLAUDE_MODEL}", file=sys.stderr)
            
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=4000,
                timeout=60.0,
                system=LEARNING_STRATEGY_SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            print("DEBUG: API call successful!", file=sys.stderr)
            plan = response.content[0].text
            print(f"DEBUG: Plan generated, length: {len(plan)}", file=sys.stderr)
            
            self.session.set_module_plan(plan)

            return f"""**Your Personalized Learning Plan**

{plan}

---

Ready to start? I'll guide you through each module. Feel free to ask questions anytime!

Let's begin with Module 1..."""

        except anthropic.APITimeoutError as e:
            print(f"DEBUG: Timeout error: {e}", file=sys.stderr)
            return f"⏱️ **Timeout Error**: The learning plan generation took too long. This might be due to a very large paper. Please try with a shorter paper or check your connection."
        
        except anthropic.APIError as e:
            print(f"DEBUG: API error: {e}", file=sys.stderr)
            return f"🔴 **API Error**: {str(e)}\n\nPlease check your API key and model configuration."
        
        except Exception as e:
            print(f"DEBUG: Unexpected error: {type(e).__name__}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return f"❌ **Error**: {type(e).__name__}: {str(e)}\n\nPlease check the Render logs for more details."

    def teach_module(self, user_message: str) -> str:
        """Deliver teaching content or respond to user questions."""
        if not self.session.module_plan:
            return "Error: No learning plan generated yet."

        messages = []
        teaching_prompt = get_teaching_prompt(
            self.session.module_plan,
            self.session.current_module,
            user_message
        )

        messages.append({
            "role": "user",
            "content": teaching_prompt
        })

        for msg in self.session.conversation_history[-6:]:
            messages.append(msg)

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
            self.session.add_message("user", user_message)
            self.session.add_message("assistant", reply)

            return reply

        except Exception as e:
            return f"Error during teaching: {str(e)}"

    def check_for_module_advance(self, user_message: str) -> bool:
        """Heuristic to detect if user wants to move to next module."""
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
