from typing import TypedDict

from tavily import TavilyClient

from .state import OverallState, SearchResult
from .utils import get_llm
from .prompts import GENERATE_QUERIES_PROMPT, FACT_CHECKER_PROMPT, POST_WRITER_PROMPT
from .schemas import SearchQueries, FactCheckVerdict
from core.config import settings

# Initialize the Tavily search tool
tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)


def generate_search_queries(state: OverallState):
    """Generates search queries based on the user's claim."""
    print("---NODE: Generating Search Queries---")

    claim = state["claim"]
    prompt = GENERATE_QUERIES_PROMPT.format(claim=claim)
    search_queries: SearchQueries = (
        get_llm(settings.QUERIES_GENERATOR_MODEL)
        .with_structured_output(SearchQueries)
        .invoke(prompt)
    )

    return {"search_queries": search_queries.queries}

class WebSearchInput(TypedDict):
    """Input schema for the web_search_node."""
    query: str

def web_search(state: WebSearchInput):
    """
    Worker node that performs a web search for a single query.
    This node will be invoked in parallel for each query.
    """
    print(f"---EXECUTING WORKER: WEB_SEARCH for query: '{state['query']}'---")

    results = tavily.search(
        query=state["query"],
        search_depth=settings.TAVILY_SEARCH_DEPTH,
        max_results=settings.MAX_RESULTS,
    )

    search_results: list[SearchResult] = [
        SearchResult(
            title=res.get("title", "N/A"),
            url=res.get("url"),
            content=res.get("content")
        ) for res in results['results']
    ]

    return {"search_results": search_results}

def aggregate_results(state: OverallState):
    """
    Aggregates and formats the search results from all workers into an XML string.
    """
    print("---EXECUTING NODE: AGGREGATE_RESULTS---")

    search_results = state["search_results"]

    formatted_results = "\n\n---\n\n".join(
        [
            f"Title: {res['title']}\nURL: {res['url']}\nContent: {res['content']}" for res in search_results
        ]
    )
    return {"formatted_results": formatted_results, "search_results_count": len(search_results)}


def fact_checker(state: OverallState):
    """Analyzes search results and provides a verdict on the claim."""
    print("---NODE: Checking Facts---")

    claim = state["claim"]
    formatted_results = state["formatted_results"]

    prompt = FACT_CHECKER_PROMPT.format(claim=claim, search_results=formatted_results)

    structured_output = (
        get_llm(settings.FACT_CHECKER_MODEL)
        .with_structured_output(FactCheckVerdict)
        .invoke(prompt)
    )

    return {"verdict": structured_output}


def post_writer(state: OverallState):
    """Generates a social media post based on the fact-checking verdict."""
    print("---NODE: Writing Social Media Post---")
    claim = state["claim"]
    verdict_data = state["verdict"]
    prompt = POST_WRITER_PROMPT.format(
        claim=claim,
        verdict=verdict_data.verdict,
        rationale=verdict_data.rationale,
        confidence_score=verdict_data.confidence_score,
        citations=verdict_data.citations
    )
    structured_output = get_llm(settings.POST_WRITER_MODEL).invoke(prompt)

    return {"post": structured_output}
