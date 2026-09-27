from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from dependencies import get_atendente_ou_gerente
from models.models import Unidade, Produto, Estoque, Promocao
from schemas.schemas import UnidadeCreate, ProdutoCreate, EstoqueCreate, PromocaoCreate

router = APIRouter(tags=["Catalogo"])

@router.post("/unidades", status_code=201)
def criar_unidade(dados: UnidadeCreate, db: Session = Depends(get_db)):
    nova = Unidade(**dados.dict()); db.add(nova); db.commit(); db.refresh(nova); return nova

@router.get("/unidades")
def listar_unidades(db: Session = Depends(get_db)): return db.query(Unidade).all()

@router.post("/produtos", status_code=201)
def criar_produto(dados: ProdutoCreate, db: Session = Depends(get_db)):
    novo = Produto(**dados.dict()); db.add(novo); db.commit(); db.refresh(novo); return novo

@router.get("/produtos")
def listar_produtos(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Produto).offset((page-1)*limit).limit(limit).all()

@router.post("/estoque", status_code=201)
def add_estoque(dados: EstoqueCreate, db: Session = Depends(get_db)):
    novo = Estoque(**dados.dict()); db.add(novo); db.commit(); db.refresh(novo); return novo

@router.get("/estoque")
def ver_estoque(unidadeId: int = None, db: Session = Depends(get_db),current_user = Depends(get_atendente_ou_gerente)):
    q = db.query(Estoque)
    if unidadeId: q = q.filter(Estoque.unidade_id == unidadeId)
    return q.all()

@router.post("/promocoes", status_code=201, tags=["Promocoes"])
def criar_promo(dados: PromocaoCreate, db: Session = Depends(get_db)):
    nova = Promocao(**dados.dict()); db.add(nova); db.commit(); db.refresh(nova); return nova

@router.get("/promocoes", tags=["Promocoes"])
def listar_promo(db: Session = Depends(get_db)): return db.query(Promocao).filter(Promocao.ativo == True).all()