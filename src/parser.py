"""Resume text extraction (PDF / TXT)."""
import re

from pypdf import PdfReader


def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def read_resume(file) -> str:
    """`file` is a Streamlit UploadedFile (or any file-like object with .name)."""
    if file.name.lower().endswith(".pdf"):
        reader = PdfReader(file)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        text = file.read().decode("utf-8", errors="ignore")
    return clean_text(text)
