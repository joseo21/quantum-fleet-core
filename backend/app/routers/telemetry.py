from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import TelemetryQuery
from ..models import Telemetry
from ..auth import get_current_user

router = APIRouter(prefix="/telemetry", tags=["telemetry"])

@router.post("/query")
def query_telemetry(q: TelemetryQuery, db: Session = Depends(get_db), user=Depends(get_current_user)):
    items = (db.query(Telemetry)
              .filter(Telemetry.tenant_id==user.tenant_id, Telemetry.device_id==q.device_id)
              .order_by(Telemetry.ts.desc())
              .limit(q.limit).all())
    return [{"ts": t.ts.isoformat(), "data": t.data} for t in items]
