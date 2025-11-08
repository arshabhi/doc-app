import difflib
import random
from datetime import datetime
from uuid import uuid4
from typing import Dict, Any, Tuple

# ----------------------------------------------
# Helper: Mock semantic categories
# ----------------------------------------------
CATEGORIES = ["financial", "timeline", "content", "structure"]

# ----------------------------------------------
# Core comparison engine (mock or diff-based)
# ----------------------------------------------

async def compare_documents(
    doc1_content: str,
    doc2_content: str,
    comparison_type: str = "full",
    options: Dict[str, Any] = None
) -> Tuple[Dict[str, Any], Dict[str, int], list]:
    """
    Compare two document contents and return structured differences.
    """

    options = options or {}

    # 1️⃣ Simple diff using difflib for text comparison
    diff = difflib.unified_diff(
        doc1_content.splitlines(),
        doc2_content.splitlines(),
        lineterm=""
    )

    changes = []
    additions = deletions = modifications = 0

    for i, line in enumerate(diff):
        if line.startswith("+ ") and not line.startswith("+++"):
            additions += 1
            changes.append({
                "id": f"chg_{uuid4().hex[:6]}",
                "type": "addition",
                "location": {"document": 2, "lineNumber": i},
                "content": line[2:],
                "severity": random.choice(["minor", "major"]),
                "category": random.choice(CATEGORIES),
            })
        elif line.startswith("- ") and not line.startswith("---"):
            deletions += 1
            changes.append({
                "id": f"chg_{uuid4().hex[:6]}",
                "type": "deletion",
                "location": {"document": 1, "lineNumber": i},
                "content": line[2:],
                "severity": random.choice(["minor", "major"]),
                "category": random.choice(CATEGORIES),
            })
        elif line.startswith("! "):
            modifications += 1

    total_changes = additions + deletions + modifications

    # 2️⃣ Mock similarity
    similarity_score = round(random.uniform(0.75, 0.98), 2)
    changes_percentage = round(100 - similarity_score * 100, 2)

    summary = {
        "totalChanges": total_changes,
        "additions": additions,
        "deletions": deletions,
        "modifications": modifications,
        "similarityScore": similarity_score,
        "changesPercentage": changes_percentage
    }

    # 3️⃣ Count per category
    category_breakdown = {}
    for c in changes:
        cat = c.get("category", "other")
        category_breakdown[cat] = category_breakdown.get(cat, 0) + 1

    return summary, category_breakdown, changes


# ----------------------------------------------
# Orchestrator function (to be used in router)
# ----------------------------------------------
async def run_document_comparison(document1, document2, comparison_type="full", options=None):
    """
    Run comparison between two document objects.
    document1, document2 should each have a `.meta_data['text']` or `.content` field.
    """

    content1 = document1.meta_data.get("text") if hasattr(document1, "meta_data") else document1.get("text")
    content2 = document2.meta_data.get("text") if hasattr(document2, "meta_data") else document2.get("text")

    if not content1 or not content2:
        raise ValueError("Documents must contain text for comparison.")

    summary, category_breakdown, changes = await compare_documents(content1, content2, comparison_type, options)

    result = {
        "id": str(uuid4()),
        "documentId1": str(document1.id),
        "documentId2": str(document2.id),
        "comparisonType": comparison_type,
        "status": "completed",
        "createdAt": datetime.utcnow().isoformat(),
        "completedAt": datetime.utcnow().isoformat(),
        "summary": summary,
        "changes": changes,
        "categoryBreakdown": category_breakdown,
        "diffUrl": f"https://storage.example.com/comparisons/{uuid4().hex}_diff.pdf",
        "sideBySideUrl": f"https://storage.example.com/comparisons/{uuid4().hex}_sidebyside.pdf"
    }

    return result
