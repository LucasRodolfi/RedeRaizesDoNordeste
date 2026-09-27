from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import Pedido, PagamentoMock
import uuid, random

router = APIRouter(tags=["Pagamentos Mock"])

@router.post("/pagamentos/mock/{pedido_id}")
def pagar_mock(pedido_id: int, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido: raise HTTPException(404, "Pedido nao encontrado")
    if pedido.status!= "AGUARDANDO_PAGAMENTO": raise HTTPException(409, f"Pedido com status {pedido.status} nao pode ser pago")

    aprovado = random.choice([True, True, True, True, False])
    status_pag = "APROVADO" if aprovado else "RECUSADO"

    pag = PagamentoMock(pedido_id=pedido.id, forma_pagamento=pedido.forma_pagamento, status=status_pag, valor=pedido.total, transacao_id=str(uuid.uuid4())[:8])
    db.add(pag)
    if aprovado: pedido.status = "PAGO"
    db.commit(); db.refresh(pag)

    print(f"[AUDIT] Pagamento {status_pag} pedido {pedido_id} transacao {pag.transacao_id}")
    return {"pedidoId": pedido.id, "statusPagamento": pag.status, "statusPedido": pedido.status, "transacaoId": pag.transacao_id, "valor": pag.valor, "mensagem": "Aprovado - enviado para cozinha" 
        if aprovado 
        else "Recusado"}

@router.get("/pagamentos/{pedido_id}")
def consultar(pedido_id: int, db: Session = Depends(get_db)):
    pag = db.query(PagamentoMock).filter(PagamentoMock.pedido_id == pedido_id).first()
    if not pag: raise HTTPException(404, "Pagamento nao encontrado")
    return pag