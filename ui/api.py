from __future__ import annotations

import os
from fastapi import FastAPI, HTTPException, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from intelliquery.config import load_settings
from intelliquery.agents.graph import build_agent_graph

app = FastAPI(title="IntelliQuery-RAG API")

# Allow CORS for React frontend (Vite defaults to 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent on startup to keep it warm
settings = load_settings()
try:
    agent = build_agent_graph(settings)
except Exception as e:
    # If FAISS isn't built yet, it will fail here. We can defer or handle it.
    agent = None
    startup_error = str(e)


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    final_response: str
    reasoning_trace: list[str]
    execution_plan: list[dict]


@app.get("/api/health")
def health_check():
    if agent is None:
        return {"status": "error", "message": startup_error}
    return {"status": "ok"}


@app.post("/api/query", response_model=QueryResponse)
def execute_query(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    if agent is None:
        raise HTTPException(status_code=500, detail=f"Agent failed to load: {startup_error}")

    try:
        result = agent.invoke({"query": req.query})
        
        return QueryResponse(
            final_response=result.get("final_response", "_No answer generated._"),
            reasoning_trace=result.get("reasoning_trace", []),
            execution_plan=result.get("execution_plan", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/query/stream")
def execute_query_stream(query: str):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    if agent is None:
        raise HTTPException(status_code=500, detail=f"Agent failed to load: {startup_error}")

    def event_generator():
        try:
            import json
            for event in agent.stream({"query": query}):
                for node_name, state_values in event.items():
                    data = {
                        "type": "node",
                        "node": node_name,
                    }
                    if "execution_plan" in state_values:
                        data["execution_plan"] = state_values["execution_plan"]
                    if "reasoning_trace" in state_values:
                        data["reasoning_trace"] = state_values["reasoning_trace"]
                    if "final_response" in state_values:
                        data["final_response"] = state_values["final_response"]
                    
                    for key in ["active_task_description", "distilled_context", "is_grounded", "unsupported_claims"]:
                        if key in state_values:
                            data[key] = state_values[key]
                            
                    yield f"data: {json.dumps(data)}\n\n"
        except Exception as e:
            import json
            yield f"data: {json.dumps({'type': 'error', 'detail': str(e)})}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ui.api:app", host="0.0.0.0", port=8000, reload=True)
