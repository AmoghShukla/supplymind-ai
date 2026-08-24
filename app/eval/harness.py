import asyncio
from ..db import SessionLocal
from ..agents.orchestrator import run_pipeline
from .golden_set import GOLDEN_SCENARIOS
async def evaluate(runs: int = 3) -> dict:
    results = []
    async with SessionLocal() as db:
        for scenario in GOLDEN_SCENARIOS:
            outputs = [await run_pipeline(db, scenario["shipment_id"]) for _ in range(runs)]
            consistent = all(o["status"] == scenario["expected_status"] for o in outputs)
            structural = all(len(o["steps"]) >= 4 for o in outputs)
            results.append({"scenario": scenario["name"], "consistent": consistent, "structurally_valid": structural, "score": 1.0 if consistent and structural else 0.0})
    return {"passed": all(x["score"] >= .8 for x in results), "results": results}
if __name__ == "__main__": print(asyncio.run(evaluate()))
