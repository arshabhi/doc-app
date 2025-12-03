# app/processing/pdf_processor.py

import base64
import asyncio
import fitz
import pymupdf4llm
from uuid import uuid4
from io import BytesIO
from PIL import Image


class PDFExtractor:
    def __init__(self, llm, mode="balanced"):
        self.llm = llm
        self.mode = mode  # fast / balanced / full

    def _pdf_to_text_markdown(self, doc):
        """Fast static extraction."""
        return pymupdf4llm.to_markdown(doc)

    def _extract_images(self, page):
        imgs = []
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = page.parent.extract_image(xref)
            pil = Image.open(BytesIO(base_image["image"]))
            imgs.append(pil)
        return imgs

    async def _summarize_page(self, full_image, images):
        """
        Single Gemini call that:
        - extracts OCR if scanned
        - summarizes images if present
        """

        message = [
            {
                "type": "text",
                "text": (
                    "You will receive one or more page images.\n"
                    "If readable text exists, extract it.\n"
                    "If it's a scanned page, perform OCR.\n"
                    "If there are diagrams/images, also summarize them.\n"
                    "Return: one unified description, no bullet points.\n"
                ),
            }
        ]

        # First image = full scanned page
        for img in [full_image] + images:

            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")

            buf = BytesIO()
            img.save(buf, format="PNG")
            base64_data = base64.b64encode(buf.getvalue()).decode("utf-8")

            message.append({
                "type": "image_url",
                "image_url": f"data:image/png;base64,{base64_data}"
            })

        response = await self.llm.ainvoke([
            {"role": "user", "content": message}
        ])

        content = getattr(response, "content", response)

        # Combine pieces if Gemini returns segmented output
        if isinstance(content, list):
            return "\n".join([p.get("text", str(p)) for p in content])

        return str(content)

    async def extract(self, file_bytes: bytes) -> dict:
        """
        Fully async extraction:
        - Always extract text normally
        - Detect scanned pages
        - Run one Gemini call PER page (batch images)
        """

        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            markdown = self._pdf_to_text_markdown(doc)
            md_pages = markdown.split("\n---\n")

            extracted = []
            async_tasks = []

            for i, page in enumerate(doc):
                extracted_text = md_pages[i].strip() if i < len(md_pages) else ""
                images = self._extract_images(page)

                result = {
                    "page": i + 1,
                    "text": extracted_text,
                    "img_description": None,
                }

                # Determine if we need Gemini
                scanned = not extracted_text and len(images) > 0

                # Filter real images (skip logos/icons below threshold)
                filtered_images = [img for img in images if img.width * img.height > 120_000]

                if scanned or filtered_images:
                    # Prepare full page as PIL image
                    pix = page.get_pixmap(dpi=200)
                    full_img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

                    # async queue for processing
                    async_tasks.append((i, asyncio.create_task(self._summarize_page(full_img, filtered_images))))

                extracted.append(result)

        # Await all async LLM work
        for idx, task in async_tasks:
            extracted[idx]["img_description"] = await task

        return {
            "pages": extracted,
            "metadata": {
                "page_count": len(extracted),
                "processed_with_ai": any(p["img_description"] for p in extracted),
            }
        }


class ImageExtractor:
    def __init__(self, llm):
        self.llm = llm

    async def summarize(self, file_bytes: bytes) -> dict:
        """Async animated vision call for standalone image."""

        img = Image.open(BytesIO(file_bytes))
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        buf = BytesIO()
        img.save(buf, format="PNG")
        base64_data = base64.b64encode(buf.getvalue()).decode()

        prompt = "Extract text, describe content, and summarize meaning."

        response = await self.llm.ainvoke([
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": f"data:image/png;base64,{base64_data}"},
                ],
            }
        ])

        content = getattr(response, "content", response)

        if isinstance(content, list):
            final = "\n".join([
                p.get("text", str(p)) for p in content
            ])
        else:
            final = str(content)

        return {
            "page": 1,
            "image_id": f"image-{uuid4().hex}.png",
            "content": final
        }
