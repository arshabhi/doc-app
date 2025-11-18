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


def extract_content(file):
    """
    Extracts content from a file (UploadFile or local path)
    Returns {'extension': str, 'content': str|bytes}
    """
    if hasattr(file, "filename"):  # FastAPI UploadFile
        filename = file.filename
        file_obj = file.file
    elif isinstance(file, (str, Path)):  # Local path
        filename = os.path.basename(file)
        file_obj = open(file, "rb")
    else:
        raise TypeError("file must be a path or UploadFile")

    extension = Path(filename).suffix.lower().lstrip(".")

    try:
        if extension in {"txt", "csv", "log"}:
            content = file_obj.read().decode("utf-8", errors="ignore")

        elif extension == "json":
            content = json.load(file_obj)

        elif extension == "pdf":
            with fitz.open(stream=file_obj.read(), filetype="pdf") as doc:
                content = "\n".join(page.get_text("text") for page in doc)

        elif extension in {"jpg", "jpeg", "png"}:
            content = file_obj.read()

        else:
            content = file_obj.read()

    finally:
        if not hasattr(file, "filename"):
            file_obj.close()

    return {"extension": extension, "content": content}


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
