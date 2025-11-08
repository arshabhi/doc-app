async def generate_summary(req, doc, custom=False):
    # Mock summarization logic for now
    return {
        "content": f"Summary for document {doc.filename}",
        "keyPoints": ["Point 1", "Point 2"],
        "wordCount": 100,
        "confidence": 0.95,
        "meta_data": {"model": "gpt-4", "processingTime": 2.5, "sourcePages": [1, 2, 3]},
    }
