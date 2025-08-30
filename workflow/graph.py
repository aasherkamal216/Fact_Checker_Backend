from langgraph.graph import StateGraph, END, START
from langgraph.types import Send
from .state import OverallState, InputState, OutputState
from .nodes import (
    generate_search_queries,
    web_search,
    aggregate_results,
    fact_checker,
    post_writer,
)

def route_to_search(state: OverallState):
    """
    A conditional edge that routes to the web_search node for each query.
    """
    return [Send("web_search", {"query": q}) for q in state["search_queries"]]

def build_graph():
    """Builds the LangGraph workflow."""
    workflow = StateGraph(
        OverallState,
        input_schema=InputState,
        output_schema=OutputState,
    )

    # Add nodes to the graph
    workflow.add_node("generate_search_queries", generate_search_queries)
    workflow.add_node("web_search", web_search)
    workflow.add_node("aggregate_results", aggregate_results)
    workflow.add_node("fact_checker", fact_checker)
    workflow.add_node("post_writer", post_writer)

    # Define the workflow's edges
    workflow.add_edge(START, "generate_search_queries")
    
    # This is the "fan-out" step. The conditional edge calls 'route_to_search',
    # which returns a list of Send objects, triggering parallel execution of web_search.
    workflow.add_conditional_edges("generate_search_queries", route_to_search)
    
    # This is the "fan-in" step. After all parallel web_search nodes complete,
    # their outputs are aggregated (due to the reducer), and the flow continues
    # to the aggregate_results node.
    workflow.add_edge("web_search", "aggregate_results")
    
    workflow.add_edge("aggregate_results", "fact_checker")
    workflow.add_edge("fact_checker", "post_writer")
    workflow.add_edge("post_writer", END)

    # Compile the graph into a runnable app
    return workflow.compile()

# A single, compiled graph instance to be imported and used
graph_app = build_graph()