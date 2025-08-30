import operator
from typing import TypedDict, List, Annotated
from .schemas import SearchQueries, FactCheckVerdict

class SearchResult(TypedDict):
    """Represents a single search result."""
    title: str
    url: str
    content: str

class InputState(TypedDict):
    """The input schema for the graph."""
    claim: str

class OutputState(TypedDict):
    """The output schema for the graph."""
    verdict: FactCheckVerdict
    post: str

class OverallState(InputState):
    """
    The comprehensive internal state of the fact-checker agent.
    This is what is passed between nodes.
    """
    search_queries: list[str]
    search_results: Annotated[List[SearchResult], operator.add]
    search_results_count : int
    formatted_results: str
    verdict: FactCheckVerdict
    post: str