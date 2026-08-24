from .tools import Action, DiagnosisResult, PlanResult
async def plan(diagnosis: DiagnosisResult) -> PlanResult:
    actions = [Action(action="book_expedited_freight", cost=3200, detail="Move critical pallets by air"), Action(action="notify_customer", cost=0, detail="Publish revised ETA and recovery plan")]
    return PlanResult(actions=actions, estimated_cost=sum(a.cost for a in actions))
