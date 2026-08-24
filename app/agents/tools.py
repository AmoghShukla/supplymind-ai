from pydantic import BaseModel
class Action(BaseModel): action: str; cost: float; detail: str
class DiagnosisResult(BaseModel): root_cause: str; confidence: float; supporting_incident_ids: list[int]
class PlanResult(BaseModel): actions: list[Action]; estimated_cost: float
class CriticResult(BaseModel): approved: bool; risk_score: float; reason: str
