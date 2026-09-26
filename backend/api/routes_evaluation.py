"""
SWARMOS Evaluation API Route
Allows the frontend command center or external CI pipelines to trigger the benchmark suite.
"""
from fastapi import APIRouter
from evaluation.scenarios_eval import SwarmEvaluator

router = APIRouter(prefix="/api/evaluate", tags=["evaluation"])

@router.post("")
async def run_evaluation_suite():
    """Trigger the 5-scenario evaluation suite and return empirical metrics."""
    evaluator = SwarmEvaluator()
    results = await evaluator.run_full_suite()
    return results
