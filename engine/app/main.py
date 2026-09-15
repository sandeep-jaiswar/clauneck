"""
FastAPI service for scientific prototyping engine.
Exposes REST endpoint for model solving.
"""
from fastapi import FastAPI, HTTPException
from app.model import ScientificModel, PrototypeResponse
from app.solver import GeneralSolver

app = FastAPI(
    title="Clauneck Engine",
    description="Deterministic scientific prototyping: symbolic and numeric solving",
    version="0.1.0"
)

solver = GeneralSolver()


@app.post("/api/solve", response_model=PrototypeResponse)
def solve_model(model: ScientificModel) -> PrototypeResponse:
    """
    Solve a scientific model.

    Input: ScientificModel (schema-validated)
    Output: PrototypeResponse with model (echoed) and results

    Determinism guarantee: same model input always produces byte-identical results.
    """
    try:
        result = solver.solve(model)
        return PrototypeResponse(model=model, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Solver error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "clauneck-engine"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
