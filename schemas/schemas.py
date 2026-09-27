from pydantic import BaseModel, EmailStr
from typing import List, Literal, Optional

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: Literal["cliente", "atendente", "gerente"] = "cliente"
    consentimento_fidelidade: bool = False

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

class UnidadeCreate(BaseModel):
    nome: str
    cidade: str
    endereco: str

class ProdutoCreate(BaseModel):
    nome: str
    preco: float
    descricao: Optional[str] = None

class EstoqueCreate(BaseModel):
    produto_id: int
    unidade_id: int
    quantidade: int

class ItemPedidoInput(BaseModel):
    produtoId: int
    quantidade: int

class PedidoCreate(BaseModel):
    unidadeId: int
    canalPedido: str
    formaPagamento: str = "mock"
    itens: List[ItemPedidoInput]
    clienteId: int = 1

class PromocaoCreate(BaseModel):
    nome: str
    desconto_percentual: float
    canal_aplicavel: Optional[str] = None

class ResgatePontos(BaseModel):
    cliente_id: int
    pontos: int