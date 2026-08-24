from ..models import Shipment
async def assess(shipment: Shipment) -> dict:
    risk = shipment.status in {"delayed", "exception", "customs_hold"}
    return {"action_needed": risk, "signal": f"Shipment {shipment.po_number} has status {shipment.status}"}
