from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import Pedido, ItemPedido, Produto, Estoque, Usuario, Unidade, MovimentoFidelidade
from schemas.schemas import PedidoCreate
from dependencies import get_atendente_ou_gerente, get_current_user

router = APIRouter(tags=["Pedidos"])

@router.post("/pedidos", status_code=201)
def criar_pedido(dados: PedidoCreate, db: Session = Depends(get_db)):
    canais = ["APP", "TOTEM", "BALCAO", "WEB"]
    if dados.canalPedido not in canais:
        raise HTTPException(422, f"canalPedido invalido. Use: {canais}")
    formas = ["PIX", "CARTAO_CREDITO", "CARTAO_DEBITO", "DINHEIRO"]
    if dados.formaPagamento not in formas:
        raise HTTPException(422, f"formaPagamento invalida. Use: {formas}")

    cliente = db.query(Usuario).filter(Usuario.id == dados.clienteId).first()
    unidade = db.query(Unidade).filter(Unidade.id == dados.unidadeId).first()
    if not cliente or not unidade: raise HTTPException(404, "Cliente ou Unidade nao encontrada")

    pedido = Pedido(cliente_id=dados.clienteId, unidade_id=dados.unidadeId, canal_pedido=dados.canalPedido, forma_pagamento=dados.formaPagamento, status="AGUARDANDO_PAGAMENTO", total=0)
    db.add(pedido); db.commit(); db.refresh(pedido)

    total = 0.0
    itens_ret = []
    for i in dados.itens:
        prod = db.query(Produto).filter(Produto.id == i.produtoId).first()
        est = db.query(Estoque).filter(Estoque.produto_id == i.produtoId, Estoque.unidade_id == dados.unidadeId).first()
        if not prod or not est or est.quantidade < i.quantidade: raise HTTPException(409, f"Estoque insuficiente para produto {i.produtoId}")
        est.quantidade -= i.quantidade
        db.add(ItemPedido(pedido_id=pedido.id, produto_id=i.produtoId, quantidade=i.quantidade, preco_unitario=prod.preco))
        total += prod.preco * i.quantidade
        itens_ret.append({"produtoId": prod.id, "quantidade": i.quantidade, "precoUnitario": prod.preco})

    pontos = int(total) if cliente.consentimento_fidelidade else 0
    if pontos > 0:
        cliente.pontos += pontos
        db.add(MovimentoFidelidade(cliente_id=cliente.id, tipo="GANHO", pontos=pontos, descricao=f"Pedido {pedido.id}"))

    pedido.total = total; pedido.pontos_gerados = pontos
    print(f"[AUDIT] Pedido criado ID {pedido.id} canal {pedido.canal_pedido} total {total}")
    db.commit(); db.refresh(pedido)

    return {"pedidoId": pedido.id, "status": pedido.status, "total": pedido.total, "formaPagamento": pedido.forma_pagamento, "canalPedido": pedido.canal_pedido, "itens": itens_ret, "createdAt": pedido.created_at}

@router.get("/pedidos")
def listar_pedidos(canalPedido: str = None, status: str = None, db: Session = Depends(get_db), current_user = Depends(get_atendente_ou_gerente)):
    q = db.query(Pedido)
    if canalPedido: q = q.filter(Pedido.canal_pedido == canalPedido)
    if status: q = q.filter(Pedido.status == status)
    return q.all()

@router.get("/pedidos/{pedido_id}")
def buscar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    p = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not p: raise HTTPException(404, "Pedido nao encontrado")
    return p

@router.put("/pedidos/{pedido_id}/status")
def atualizar_status(pedido_id: int, novo_status: str, db: Session = Depends(get_db)):
    p = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not p: raise HTTPException(404, "Pedido nao encontrado")
    p.status = novo_status
    print(f"[AUDIT] Status pedido {p.id} alterado para {novo_status}")
    db.commit(); return {"pedidoId": p.id, "novo_status": p.status}