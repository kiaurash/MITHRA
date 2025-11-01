"""
MITHRA - Machine Intelligence for Translating Human Research into Action
Main Gradio interface for research paper learning assistant
"""
import gradio as gr
from typing import Optional
import os

from config import State, ANTHROPIC_API_KEY
from utils.pdf_processor import extract_text_from_pdf, get_paper_metadata
from workflows.session_manager import SessionManager
from workflows.context_collector import ContextCollector
from workflows.module_generator import ModuleGenerator

# Global session (in production, use proper session management)
session = SessionManager()
context_collector = None
module_generator = None

def process_pdf(file) -> str:
    """
    Process uploaded PDF and extract text.

    Args:
        file: Gradio file upload object

    Returns:
        Confirmation message or error
    """
    global session, context_collector, module_generator

    if file is None:
        return "Please upload a PDF file."

    # Extract text from PDF
    text = extract_text_from_pdf(file.name)

    if not text:
        return "❌ Error: Could not extract text from PDF. Please try a different file."

    # Get metadata
    metadata = get_paper_metadata(text)

    # Store in session
    session.set_paper(text, metadata)

    # Initialize context collector
    context_collector = ContextCollector(session)
    session.start_context_collection()

    # Return welcome message
    return f"""✅ **Paper uploaded successfully!**

**Title:** {metadata['title']}
**Length:** ~{metadata['word_count']} words ({metadata['estimated_pages']} pages)

{context_collector.get_initial_message()}"""

def chat(message: str, history: list) -> str:
    """
    Main chat handler - routes messages based on session state.

    Args:
        message: User's message
        history: Chat history (Gradio format)

    Returns:
        Assistant's response
    """
    global session, context_collector, module_generator

    # Check if API key is configured
    if not ANTHROPIC_API_KEY:
        return "⚠️ **Error**: ANTHROPIC_API_KEY not configured. Please set it in Replit Secrets."

    # Check if paper uploaded
    if session.state == State.INIT:
        return "👆 Please upload a research paper PDF using the file upload above to get started."

    # Handle context collection
    if session.state == State.COLLECTING_CONTEXT:
        response = context_collector.process_user_response(message)

        # Check if context collection complete
        if context_collector.is_complete():
            session.state = State.CONTEXT_COMPLETE

        return response

    # Handle module generation
    if session.state == State.CONTEXT_COMPLETE:
        session.state = State.GENERATING_MODULES

        # Initialize module generator
        module_generator = ModuleGenerator(session)

        # Generate learning plan
        plan = module_generator.generate_learning_plan()
        return plan

    # Handle teaching/conversation
    if session.state == State.TEACHING:
        if module_generator is None:
            module_generator = ModuleGenerator(session)

        response = module_generator.teach_module(message)

        # Check if user wants to advance module (simple heuristic)
        if module_generator.check_for_module_advance(message):
            session.advance_module()

        return response

    # Default fallback
    return "I'm not sure how to respond. Current state: " + session.state

def reset_session():
    """Reset the session for a new paper"""
    global session, context_collector, module_generator
    session.reset()
    context_collector = None
    module_generator = None
    return "Session reset. Please upload a new paper to start."

# Build Gradio interface
with gr.Blocks(
    title="MITHRA - Research Learning Assistant",
    theme=gr.themes.Soft()
) as demo:
    gr.Markdown("""
    # 📚 MITHRA
    ## Machine Intelligence for Translating Human Research into Action

    Your personalized AI tutor for understanding research papers.

    **How it works:**
    1. Upload a research paper (PDF)
    2. Answer a few questions about your background and goals
    3. Get a personalized learning experience tailored to you
    """)

    with gr.Row():
        with gr.Column(scale=1):
            pdf_upload = gr.File(
                label="📄 Upload Research Paper (PDF)",
                file_types=[".pdf"],
                type="filepath"
            )
            upload_btn = gr.Button("Process Paper", variant="primary")
            reset_btn = gr.Button("Reset Session", variant="secondary")

            gr.Markdown("""
            ### 💡 Tips
            - Make sure PDF has selectable text (not scanned images)
            - Papers work best if they're 10-50 pages
            - You can ask questions anytime during learning
            """)

        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                label="Learning Session",
                height=600,
                show_label=True
            )
            msg = gr.Textbox(
                label="Your message",
                placeholder="Type your answer or question here...",
                lines=2
            )
            submit_btn = gr.Button("Send", variant="primary")

    # Event handlers
    upload_btn.click(
        fn=process_pdf,
        inputs=[pdf_upload],
        outputs=[chatbot],
        api_name="upload_paper"
    ).then(
        lambda: None,
        None,
        [pdf_upload]  # Clear file upload after processing
    )

    msg.submit(
        fn=chat,
        inputs=[msg, chatbot],
        outputs=[chatbot]
    ).then(
        lambda: "",
        None,
        [msg]  # Clear message box after send
    )

    submit_btn.click(
        fn=chat,
        inputs=[msg, chatbot],
        outputs=[chatbot]
    ).then(
        lambda: "",
        None,
        [msg]  # Clear message box after send
    )

    reset_btn.click(
        fn=reset_session,
        outputs=[chatbot]
    )

    gr.Markdown("""
    ---
    **Built for Anthropic's AI Engineering Bootcamp 2025**

    *MITHRA helps practitioners understand research papers faster through personalized, pedagogically-sound learning.*
    """)

# Only run launch() when executed directly (not imported by HF Spaces)
if __name__ == "__main__":
    import os

    # Check for API key
    if not ANTHROPIC_API_KEY:
        print("⚠️  WARNING: ANTHROPIC_API_KEY not found!")
        print("Please set it in Replit Secrets or your .env file")
        print("")

    print("🚀 Starting MITHRA...")
    print("📚 Upload a research paper to begin your personalized learning session")
    print("")

    # Only launch if not on HF Spaces (HF Spaces launches automatically)
    # HF Spaces sets SPACE_ID environment variable
    if os.getenv("SPACE_ID") is None:
        # Get port from environment (for Render, Railway, etc.) or use default
        port = int(os.getenv("PORT", 7860))

        demo.launch(
            server_name="0.0.0.0",  # Listen on all interfaces
            server_port=port,
            share=False
        )
