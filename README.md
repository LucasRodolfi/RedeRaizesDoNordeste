# Raízes do Nordeste / Back-end

Trilha: Back-end
Tecnologia: FastAPI + SQLAlchemy + SQLite

## Requisitos
Python 3.10+
Banco: SQLite (não precisa instalar)
Dependências: ver requirements.txt

## Como rodar
pip install -r requirements.txt
uvicorn app.main:app --reload

para usar GET pedidos e GET estoque (Rotas com permissão).

1. Criar um usuário gerente
POST /auth/register

json {
  "email": "gerente@raizes.com",
  "senha": "123",
  "nome": "Gerente Teste",
  "perfil": "gerente"
  }

2. Logar e pegar o token
POST /auth/login

json{
  "email": "gerente@raizes.com",
  "senha": "123"
}

Retorno:

json{
  "accessToken": "eyJhbGciOi..."
}

3. Autorizar no Swagger
Clique no botão Authorize (cadeado) no topo da página -> Cole o accessToken gerado no login como gerente em HTTPBearer  (http, Bearer).


## Documentação
http://localhost:8000/docs - Swagger

## Endpoints principais
POST /usuarios
POST /auth/login
GET /estoques?unidadeId=1
POST /pedidos - campo obrigatório canalPedido ENUM(APP, TOTEM, BALCAO, PICKUP, WEB)
POST /pagamentos/mock/{pedidoId} - retorna transacaoId MOCK

## Regra de negócio crítica
campo canalPedido obrigatório em pedidos para rastreabilidade multicanal
estoque por unidade via tabela estoques
pagamento mock 80% APROVADO 20% RECUSADO com idempotência