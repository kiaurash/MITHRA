"""
MITHRA - Machine Intelligence for Translating Human Research into Action
Hugging Face Spaces entry point
"""
# This is the entry point for Hugging Face Spaces
# It imports and runs the main application

from main import demo

if __name__ == "__main__":
    print("🚀 Starting MITHRA on Hugging Face Spaces...")
    print("📚 Upload a research paper to begin your personalized learning session")

    demo.launch()
