"""PDF text extraction utility"""
import PyPDF2
from typing import Optional

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Extract text content from PDF file.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Extracted text as string, or None if extraction fails
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            # Extract text from all pages
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"

            # Basic cleanup
            text = text.strip()

            if not text:
                return None

            return text

    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return None

def get_paper_metadata(text: str) -> dict:
    """
    Extract basic metadata from paper text.
    Simple heuristic - looks for title (first significant line).

    Args:
        text: Extracted paper text

    Returns:
        Dictionary with metadata (title, length)
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Assume first non-empty line is title
    title = lines[0] if lines else "Unknown Paper"

    # Count words for length estimate
    word_count = len(text.split())

    return {
        "title": title[:100],  # Truncate long titles
        "word_count": word_count,
        "estimated_pages": len(text) // 2000  # Rough estimate
    }
