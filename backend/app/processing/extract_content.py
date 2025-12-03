import os
import json
from pathlib import Path
from uuid import uuid4
import aiofiles

from langchain_google_genai import ChatGoogleGenerativeAI
from app.processing.pdf_processor import PDFExtractor, ImageExtractor

# Global LLM instance (reuse across calls)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.1
)


def normalize_page(page: dict) -> dict:
    """
    Convert the new rich format (text, ocr_text, image_summary)
    into the old structure: { page: X, content: "...combined text..." }
    """
    parts = []

    if page.get("ocr_text"):
        parts.append(page["ocr_text"])

    if page.get("text"):
        parts.append(page["text"])

    if page.get("summary"):   # ImageExtractor output
        parts.append(page["summary"])

    if page.get("image_summary"):
        parts.extend(page["image_summary"])

    # fallback for older format
    if not parts and page.get("content"):
        parts.append(page["content"])

    final_text = "\n\n".join(p.strip() for p in parts if p and p.strip())

    return {
        "page": page.get("page", 1),
        "content": final_text
    }


async def extract_content(file, filename: str | None = None):
    """
    Fully async file content extraction supporting:
    - PDF w/ Gemini OCR + vision (async, batched)
    - Image OCR with Gemini
    - Text/JSON lightweight extraction

    Returns normalized format:
    {
        "extension": "pdf",
        "pages": [{ "page": 1, "content": "..."}]
    }
    """

    # -----------------
    # Determine input type
    # -----------------
    if hasattr(file, "filename"):  # FastAPI UploadFile
        filename = file.filename
        file_bytes = await file.read()

    elif isinstance(file, bytes):  # raw buffer
        file_bytes = file
        if not filename:
            raise ValueError("filename must be provided when passing raw bytes")

    elif isinstance(file, (str, Path)):  # local path
        filename = os.path.basename(file)
        async with aiofiles.open(file, "rb") as f:
            file_bytes = await f.read()

    else:
        raise TypeError("file must be UploadFile, bytes, or a path")

    extension = Path(filename).suffix.lower().lstrip(".")

    # -----------------
    # Extraction Logic
    # -----------------

    # Simple text formats
    if extension in {"txt", "csv", "log"}:
        text = file_bytes.decode("utf-8", errors="ignore")
        lines = text.splitlines()
        return {
            "extension": extension,
            "pages": [{"page": i + 1, "content": line} for i, line in enumerate(lines)]
        }

    # JSON
    elif extension == "json":
        parsed = json.loads(file_bytes)
        return {"extension": extension, "pages": [{"page": 1, "content": parsed}]}

    # PDF (async Gemini OCR)
    elif extension == "pdf":
        if llm is None:
            raise ValueError("LLM client required for PDF extraction.")

        pdf_extractor = PDFExtractor(llm)
        raw = await pdf_extractor.extract(file_bytes)  # <-- async call

        normalized_pages = [normalize_page(p) for p in raw["pages"]]

        return {"extension": extension, "pages": normalized_pages}

    # Image OCR (async Gemini Vision)
    elif extension in {"jpg", "jpeg", "png"}:
        if llm is None:
            raise ValueError("LLM required for image processing.")

        img_extractor = ImageExtractor(llm)
        raw = await img_extractor.summarize(file_bytes)  # <-- async call

        return {"extension": extension, "pages": [normalize_page(raw)]}

    # Unsupported
    else:
        return {
            "extension": extension,
            "pages": [{"page": 1, "content": "<UNSUPPORTED FORMAT>"}]
        }
