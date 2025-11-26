import os
import json
from pathlib import Path
import fitz  # PyMuPDF
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from uuid import uuid4
from openai import OpenAI

# Initialize OpenAI client (make sure OPENAI_API_KEY is set in your env)
# openai_client = OpenAI()

# Initialize Qdrant client
qdrant = QdrantClient(host="localhost", port=6333)

def extract_content(file, filename: str | None = None):
    """
    Extracts content from:
    - UploadFile
    - bytes (memory buffer)
    - local file path

    Returns only structured page-level content where applicable.
    Example:
    [
        {"page": 1, "content": "..."},
        {"page": 2, "content": "..."}
    ]
    """

    import os, json
    from pathlib import Path
    import fitz  # PyMuPDF

    # -----------------
    # Determine input type
    # -----------------
    if hasattr(file, "filename"):                 
        filename = file.filename
        file_bytes = file.file.read()             
    elif isinstance(file, bytes):                 
        file_bytes = file
        if not filename:
            raise ValueError("filename must be provided when passing raw bytes")
    elif isinstance(file, (str, Path)):           
        filename = os.path.basename(file)
        with open(file, "rb") as f:
            file_bytes = f.read()
    else:
        raise TypeError("file must be UploadFile, bytes, or a path")

    extension = Path(filename).suffix.lower().lstrip(".")
    page_data = []

    # -----------------
    # Extraction
    # -----------------
    if extension in {"txt", "csv", "log"}:
        text = file_bytes.decode("utf-8", errors="ignore")
        lines = text.splitlines()
        page_data = [{"page": i + 1, "content": line} for i, line in enumerate(lines)]

    elif extension == "json":
        # JSON doesn't have pagination → wrap whole value in page 1
        parsed = json.loads(file_bytes)
        page_data = [{"page": 1, "content": parsed}]

    elif extension == "pdf":
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            page_data = [
                {"page": i + 1, "content": page.get_text("text")}
                for i, page in enumerate(doc)
            ]

    elif extension in {"jpg", "jpeg", "png"}:
        # No OCR here — return raw indication only
        page_data = [{"page": 1, "content": "<IMAGE FILE - NO OCR>"}]

    else:
        page_data = [{"page": 1, "content": "<UNSUPPORTED FORMAT>"}]

    return {
        "extension": extension,
        "pages": page_data
    }

# def process_text_and_save_to_qdrant(content: str, collection_name: str = "documents", chunk_size: int = 500):
#     """
#     Splits text, embeds it, and saves embeddings to Qdrant.

#     Args:
#         content (str): text to embed
#         collection_name (str): name of Qdrant collection
#         chunk_size (int): number of characters per chunk
#     """
#     # Create collection if not exists
#     qdrant.recreate_collection(
#         collection_name=collection_name,
#         vectors_config={"size": 1536, "distance": "Cosine"}
#     )

#     # Split text into chunks
#     chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

#     # Generate embeddings
#     embeddings = []
#     for chunk in chunks:
#         response = openai_client.embeddings.create(
#             model="text-embedding-3-small",
#             input=chunk
#         )
#         vector = response.data[0].embedding
#         embeddings.append(vector)

#     # Prepare points for Qdrant
#     points = [
#         PointStruct(
#             id=str(uuid4()),
#             vector=embeddings[i],
#             payload={"text": chunks[i]}
#         )
#         for i in range(len(chunks))
#     ]

#     # Upload to Qdrant
#     qdrant.upsert(collection_name=collection_name, points=points)
#     print(f"✅ Stored {len(chunks)} text chunks in Qdrant collection '{collection_name}'.")


# def process_file_and_store(file):
#     """
#     Extracts file content and stores embeddings in Qdrant (for text files only).
#     """
#     result = extract_content(file)
#     ext = result["extension"]
#     content = result["content"]

#     if ext in {"txt", "csv", "log", "json", "pdf"} and isinstance(content, str):
#         process_text_and_save_to_qdrant(content)
#     else:
#         print(f"⚠️ Skipped embedding for non-text file type: {ext}")

#     return {"extension": ext}


# # if __name__ == "__main__":
# #     # Example local file processing
# #     file_path = "sample.pdf"
# #     process_file_and_store(file_path)
