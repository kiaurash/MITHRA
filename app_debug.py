"""
MITHRA - Diagnostic version to debug HF Spaces initialization
"""
import sys
print("=== MITHRA Debug Start ===")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

try:
    print("Importing gradio...")
    import gradio as gr
    print("✓ gradio imported")
except Exception as e:
    print(f"✗ gradio import failed: {e}")
    sys.exit(1)

try:
    print("Importing config...")
    from config import State, ANTHROPIC_API_KEY
    print(f"✓ config imported, API key present: {bool(ANTHROPIC_API_KEY)}")
except Exception as e:
    print(f"✗ config import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("Importing utils...")
    from utils.pdf_processor import extract_text_from_pdf, get_paper_metadata
    print("✓ utils imported")
except Exception as e:
    print(f"✗ utils import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("Importing workflows...")
    from workflows.session_manager import SessionManager
    from workflows.context_collector import ContextCollector
    from workflows.module_generator import ModuleGenerator
    print("✓ workflows imported")
except Exception as e:
    print(f"✗ workflows import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Creating simple demo...")
demo = gr.Interface(
    fn=lambda x: f"Debug test: {x}",
    inputs=gr.Textbox(label="Test input"),
    outputs=gr.Textbox(label="Test output"),
    title="MITHRA Debug - If you see this, imports work!"
)

print("✓ Demo created successfully!")
print("=== MITHRA Debug End ===")
