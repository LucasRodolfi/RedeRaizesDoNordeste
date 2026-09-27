from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import Usuario, MovimentoFidelidade
from schemas.schemas import ResgatePontos

router = APIRouter(tags=["Fidelidade"])

@router.get("/fidelidade/{cliente_id}")
def ver(cliente_id: int, db: Session = Depends(get_db)):
    cli = db.query(Usuario).filter(Usuario.id == cliente_id).first()
    if not cli: raise HTTPException(404, "Cliente nao encontrado")
    hist = db.query(MovimentoFidelidade).filter(MovimentoFidelidade.cliente_id == cliente_id).all()
    return {"cliente": cli.nome, "saldo_pontos": cli.pontos, "consentimento": cli.consentimento_fidelidade, "historico": hist}

@router.post("/fidelidade/resgatar")
def resgatar(dados: ResgatePontos, db: Session = Depends(get_db)):
    cli = db.query(Usuario).filter(Usuario.id == dados.cliente_id).first()
    if not cli or cli.pontos < dados.pontos: raise HTTPException(409, "Saldo insuficiente")
    cli.pontos -= dados.pontos
    print(f"[AUDIT] Resgate {dados.pontos} pontos cliente {cli.id}")
    db.add(MovimentoFidelidade(cliente_id=cli.id, tipo="RESGATE", pontos=-dados.pontos, descricao="Resgate"))
    db.commit()
    return {"saldo_restante": cli.pontos}