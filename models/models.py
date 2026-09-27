from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True, index=True)
    senha_hash = Column(String)
    perfil = Column(String, default="CLIENTE")
    consentimento_fidelidade = Column(Boolean, default=False)
    pontos = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Unidade(Base):
    __tablename__ = "unidades"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    cidade = Column(String)
    endereco = Column(String)

class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    preco = Column(Float)
    descricao = Column(String, nullable=True)

class Estoque(Base):
    __tablename__ = "estoques"
    id = Column(Integer, primary_key=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    unidade_id = Column(Integer, ForeignKey("unidades.id"))
    quantidade = Column(Integer, default=0)

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"))
    unidade_id = Column(Integer, ForeignKey("unidades.id"))
    canal_pedido = Column(String)
    forma_pagamento = Column(String, default="PIX")
    status = Column(String, default="AGUARDANDO_PAGAMENTO")
    total = Column(Float, default=0.0)
    pontos_gerados = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    itens = relationship("ItemPedido", back_populates="pedido")

class ItemPedido(Base):
    __tablename__ = "itens_pedido"
    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    quantidade = Column(Integer)
    preco_unitario = Column(Float)
    pedido = relationship("Pedido", back_populates="itens")

class PagamentoMock(Base):
    __tablename__ = "pagamentos_mock"
    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    forma_pagamento = Column(String)
    status = Column(String)
    valor = Column(Float)
    transacao_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class MovimentoFidelidade(Base):
    __tablename__ = "fidelidades"
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"))
    tipo = Column(String)
    pontos = Column(Integer)
    descricao = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Promocao(Base):
    __tablename__ = "promocoes"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    desconto_percentual = Column(Float)
    canal_aplicavel = Column(String, nullable=True)
    ativo = Column(Boolean, default=True)