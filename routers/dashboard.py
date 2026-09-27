from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import Pedido

router = APIRouter(tags=["Dashboard"])

@router.get("/dashboard")
def dash(db: Session = Depends(get_db)):
    total = db.query(func.count(Pedido.id)).scalar() or 0
    faturamento = db.query(func.sum(Pedido.total)).scalar() or 0.0
    por_canal = db.query(Pedido.canal_pedido, func.count(Pedido.id)).group_by(Pedido.canal_pedido).all()
    return {"total_pedidos": total, "faturamento": faturamento, "por_canal": [{"canal": c[0], "qtd": c[1]} for c in por_canal]}