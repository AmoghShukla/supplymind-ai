from datetime import datetime
from pydantic import BaseModel, Field
class Token(BaseModel): access_token: str; token_type: str = "bearer"
class Login(BaseModel): email: str; password: str
class VendorCreate(BaseModel): name: str; region: str; reliability_score: float = Field(ge=0, le=1); contract_terms: str
class ShipmentCreate(BaseModel): po_number: str; vendor_id: int; status: str = "in_transit"; eta: datetime; origin: str; destination: str
class IncidentCreate(BaseModel): shipment_id: int | None = None; type: str; description: str; resolution: str
class RunRequest(BaseModel): shipment_id: int; auto_execute: bool = False
class ApprovalDecision(BaseModel): approved: bool
