from .tools import CriticResult, PlanResult

async def critique(plan: PlanResult, budget: float = 5000) -> CriticResult:
    approved = plan.estimated_cost <= budget
    return CriticResult(
        approved=approved, 
        risk_score=.28 if approved else .85, 
        reason="Within expedited-freight guardrail" if approved else "Plan exceeds $5,000 guardrail"
        )
