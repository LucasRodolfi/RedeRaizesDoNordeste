from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from pydantic import BaseModel, EmailStr
from datetime import datetime
from passlib.context import CryptContext
from jose import jwt
from datetime import timedelta
from typing import Optional, List

DATABASE_URL = "sqlite:///./raizes.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String); email = Column(String, unique=True)
    senha_hash = Column(String); perfil = Column(String, default="CLIENTE")
    consentimento_fidelidade = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Unidade(Base):
    __tablename__ = "unidades"
    id = Column(Integer, primary_key=True); nome = Column(String)
    cidade = Column(String); endereco = Column(String)

class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True); nome = Column(String)
    preco = Column(Float); descricao = Column(String, nullable=True)

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
    status = Column(String, default="CRIADO")
    total = Column(Float, default=0.0)
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

Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "segredo-raizes-2026"
def hash_senha(senha: str): return pwd_context.hash(senha)
def verificar_senha(senha: str, hash_salvo: str): return pwd_context.verify(senha, hash_salvo)
def criar_token(dados: dict):
    exp = datetime.utcnow() + timedelta(minutes=60)
    dados.update({"exp": exp})
    return jwt.encode(dados, SECRET_KEY, algorithm="HS256")

class UsuarioCreate(BaseModel):
    nome: str; email: EmailStr; senha: str
    perfil: str = "CLIENTE"; consentimento_fidelidade: bool = False
class UsuarioLogin(BaseModel): email: EmailStr; senha: str
class UnidadeCreate(BaseModel): nome: str; cidade: str; endereco: str
class ProdutoCreate(BaseModel): nome: str; preco: float; descricao: Optional[str] = None
class EstoqueCreate(BaseModel): produto_id: int; unidade_id: int; quantidade: int

class ItemPedidoCreate(BaseModel):
    produto_id: int
    quantidade: int

class PedidoCreate(BaseModel):
    cliente_id: int
    unidade_id: int
    canal_pedido: str
    itens: List[ItemPedidoCreate]

app = FastAPI(title="Rede Raizes do Nordeste")

@app.get("/")
def inicio(): return {"mensagem": "API"}

@app.post("/auth/register", tags=["Auth"])
def registrar(dados: UsuarioCreate, db: Session = Depends(get_db)):
    existe = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if existe: raise HTTPException(status_code=409, detail="Email já cadastrado")
    novo = Usuario(nome=dados.nome, email=dados.email, senha_hash=hash_senha(dados.senha), perfil=dados.perfil, consentimento_fidelidade=dados.consentimento_fidelidade)
    db.add(novo); db.commit(); db.refresh(novo)
    return {"id": novo.id, "email": novo.email}

@app.post("/auth/login", tags=["Auth"])
def login(dados: UsuarioLogin, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if not user or not verificar_senha(dados.senha, user.senha_hash): raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    token = criar_token({"sub": user.email, "perfil": user.perfil})
    return {"accessToken": token, "perfil": user.perfil, "id": user.id}

@app.post("/unidades", tags=["Catalogo"])
def criar_unidade(dados: UnidadeCreate, db: Session = Depends(get_db)):
    nova = Unidade(**dados.dict()); db.add(nova); db.commit(); db.refresh(nova); return nova
@app.get("/unidades", tags=["Catalogo"])
def listar_unidades(db: Session = Depends(get_db)): return db.query(Unidade).all()
@app.post("/produtos", tags=["Catalogo"])
def criar_produto(dados: ProdutoCreate, db: Session = Depends(get_db)):
    novo = Produto(**dados.dict()); db.add(novo); db.commit(); db.refresh(novo); return novo
@app.get("/produtos", tags=["Catalogo"])
def listar_produtos(db: Session = Depends(get_db)): return db.query(Produto).all()
@app.post("/estoque", tags=["Catalogo"])
def adicionar_estoque(dados: EstoqueCreate, db: Session = Depends(get_db)):
    novo = Estoque(**dados.dict()); db.add(novo); db.commit(); db.refresh(novo); return novo
@app.get("/estoque", tags=["Catalogo"])
def ver_estoque(db: Session = Depends(get_db)): return db.query(Estoque).all()

@app.post("/pedidos", tags=["Pedidos"])
def criar_pedido(dados: PedidoCreate, db: Session = Depends(get_db)):
    canais_validos = ["LOJA", "APP", "WHATSAPP"]
    if dados.canal_pedido not in canais_validos:
        raise HTTPException(status_code=400, detail=f"canal_pedido deve ser um de: {canais_validos}")

    cliente = db.query(Usuario).filter(Usuario.id == dados.cliente_id).first()
    unidade = db.query(Unidade).filter(Unidade.id == dados.unidade_id).first()
    if not cliente or not unidade:
        raise HTTPException(status_code=404, detail="Cliente ou Unidade não encontrada")

    pedido = Pedido(cliente_id=dados.cliente_id, unidade_id=dados.unidade_id, canal_pedido=dados.canal_pedido, total=0)
    db.add(pedido); db.commit(); db.refresh(pedido)

    total_pedido = 0.0
    for item_in in dados.itens:
        produto = db.query(Produto).filter(Produto.id == item_in.produto_id).first()
        if not produto:
            raise HTTPException(status_code=404, detail=f"Produto {item_in.produto_id} não encontrado")

        estoque = db.query(Estoque).filter(Estoque.produto_id == item_in.produto_id, Estoque.unidade_id == dados.unidade_id).first()
        if not estoque or estoque.quantidade < item_in.quantidade:
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente para produto {produto.nome}")

        estoque.quantidade -= item_in.quantidade

        item = ItemPedido(pedido_id=pedido.id, produto_id=item_in.produto_id, quantidade=item_in.quantidade, preco_unitario=produto.preco)
        db.add(item)
        total_pedido += produto.preco * item_in.quantidade

    pedido.total = total_pedido
    db.commit(); db.refresh(pedido)
    return {"id": pedido.id, "canal_pedido": pedido.canal_pedido, "total": pedido.total, "status": pedido.status, "mensagem": "Pedido criado"}

@app.get("/pedidos", tags=["Pedidos"])
def listar_pedidos(db: Session = Depends(get_db)):
    return db.query(Pedido).all()

@app.get("/pedidos/{pedido_id}", tags=["Pedidos"])
def ver_pedido(pedido_id: int, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido: raise HTTPException(status_code=404, detail="Pedido não encontrado")
    itens = db.query(ItemPedido).filter(ItemPedido.pedido_id == pedido_id).all()
    return {"pedido": pedido, "itens": itens}