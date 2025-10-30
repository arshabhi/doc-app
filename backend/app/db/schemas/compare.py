from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime


# -------------------------------------------------
# Core request schema
# -------------------------------------------------
class ComparisonOptions(BaseModel):
    ignoreFormatting: bool = True
    caseSensitive: bool = False
    highlightChanges: bool = True


class ComparisonRequest(BaseModel):
    documentId1: UUID
    documentId2: UUID
    comparisonType: str = Field(default="full", description="full | structure | content | metadata")
    options: Optional[ComparisonOptions] = ComparisonOptions()


# -------------------------------------------------
# Common response detail models
# -------------------------------------------------
class ComparisonChangeLocation(BaseModel):
    document: int
    page: Optional[int] = None
    section: Optional[str] = None
    lineNumber: Optional[int] = None


class ComparisonChange(BaseModel):
    id: str
    type: str
    location: ComparisonChangeLocation
    content: Any
    severity: Optional[str] = None
    category: Optional[str] = None


class ComparisonSummary(BaseModel):
    totalChanges: int
    additions: int
    deletions: int
    modifications: int
    similarityScore: float
    changesPercentage: float


class ComparisonData(BaseModel):
    id: str
    documentId1: UUID
    documentId2: UUID
    document1Name: Optional[str] = None
    document2Name: Optional[str] = None
    comparisonType: str
    status: str
    createdAt: datetime
    completedAt: Optional[datetime] = None
    summary: Optional[ComparisonSummary] = None
    changes: Optional[List[ComparisonChange]] = []
    categoryBreakdown: Optional[Dict[str, int]] = {}
    diffUrl: Optional[str] = None
    sideBySideUrl: Optional[str] = None


# -------------------------------------------------
# Individual response models
# -------------------------------------------------
class CompareResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]


class CompareDetailResponse(BaseModel):
    success: bool = True
    data: Dict[str, ComparisonData]


class CompareHistoryItem(BaseModel):
    id: str
    document1Name: Optional[str]
    document2Name: Optional[str]
    status: str
    createdAt: datetime
    summary: Optional[ComparisonSummary]


class CompareHistoryPagination(BaseModel):
    currentPage: int
    totalPages: int
    totalItems: int


class CompareHistoryResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]


class CompareDeleteResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]


# -------------------------------------------------
# Batch comparison schemas
# -------------------------------------------------
class CompareBatchItem(BaseModel):
    documentId1: UUID
    documentId2: UUID
    comparisonType: str = "full"


class CompareBatchRequest(BaseModel):
    comparisons: List[CompareBatchItem]


class CompareBatchResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]
