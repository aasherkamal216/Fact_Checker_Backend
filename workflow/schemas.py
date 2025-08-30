from pydantic import BaseModel, Field
from typing import List, Literal

class SearchQueries(BaseModel):
    """The set of search queries to research the user's claim."""
    queries: List[str] = Field(
        description="A list of 2-5 search queries that are relevant to the user's claim."
    )

class FactCheckVerdict(BaseModel):
    """The final verdict on the user's claim, with rationale and citations."""
    verdict: Literal["True", "False", "Misleading", "Unverified"]
    confidence_score: float = Field(description="A confidence score from 0.0 to 1.0 representing the certainty of the verdict.")
    rationale: str = Field(description="A short, neutral rationale for the verdict, based ONLY on the provided sources.")
    citations: List[str] = Field(description="A list of URLs from the search results that support the rationale.")