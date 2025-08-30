import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from workflow.graph import graph_app
from workflow.state import InputState

# --- FastAPI App Setup ---

app = FastAPI(
    title="Fact-Checker Agent API",
    description="An API for fact-checking claims using a LangGraph agent.",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (HTML, CSS, JS) at /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Pydantic Models ---

class ClaimRequest(BaseModel):
    """Request model for the claim to be analyzed."""
    claim: str

# --- Helper Function for SSE Formatting ---

def format_sse(data: dict) -> str:
    """Formats a dictionary into a Server-Sent Event string."""
    json_data = json.dumps(data)
    return f"data: {json_data}\n\n"

# --- API Endpoint ---

@app.post("/api/analyze-claim")
async def analyze_claim(request: ClaimRequest):
    """
    Analyzes a claim and streams the progress and results back to the client.
    """
    claim = request.claim
    inputs = InputState(claim=claim)

    async def stream_events():
        """The async generator that yields events from the LangGraph stream."""
        
        # Keep track of state to avoid sending duplicate progress messages
        sent_searching_message = False
        final_post = ""
        verdict = {}

        try:
            # Use astream() to get an async generator of events
            async for mode, chunk in graph_app.astream(
                inputs,
                stream_mode=["updates", "messages"]
            ):
                if mode == "updates":
                    node_name = list(chunk.keys())[0]
                    node_output = list(chunk.values())[0]

                    # Map node names to user-facing progress messages
                    if node_name == "generate_search_queries":
                        yield format_sse({"event": "progress", "data": "Analyzed the claim..."})
                    
                    elif node_name == "web_search" and not sent_searching_message:
                        yield format_sse({"event": "progress", "data": "Searching for sources..."})
                        sent_searching_message = True # Ensure this message is sent only once
                    
                    elif node_name == "fact_checker":
                        yield format_sse({"event": "progress", "data": "Analyzing evidence..."})
                        # Capture the verdict to send at the end
                        if 'verdict' in node_output:
                            verdict = node_output['verdict'].dict()

                    elif node_name == "aggregate_results":
                        yield format_sse({"event": "progress", "data": f"Gathered {node_output['search_results_count']} Sources..."})
                        
                elif mode == "messages":
                    token, metadata = chunk
                    if metadata.get("langgraph_node") == "post_writer" and token.content:
                        # Stream the tokens for the social media post
                        final_post += token.content
                        yield format_sse({"event": "token", "data": token.content})
            
            # After the stream is complete, send the final compiled objects
            yield format_sse({
                "event": "final_result",
                "data": {
                    "post": final_post,
                    "verdict": verdict
                }
            })

        except Exception as e:
            print(f"Error during stream: {e}")
            yield format_sse({"event": "error", "data": str(e)})
        finally:
            # Signal the end of the stream
            yield format_sse({"event": "end"})

    return StreamingResponse(stream_events(), media_type="text/event-stream")

# --- Health Check Endpoint ---

@app.get("/health")
def read_health():
    return {"status": "Fact-Checker API is running"}

# --- Serve Frontend at Root ---

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serves the index.html frontend at the root path."""
    with open("static/index.html") as f:
        return f.read()