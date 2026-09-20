from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from core.database import engine, Base
from routers import auth, catalogo, pedidos, fidelidade, dashboard, pagamentos

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Rede Raizes do Nordeste", version="1.0")

@app.exception_handler(Exception)
async def erro_padrao(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"erro": "Erro interno", "mensagem": str(exc), "codigo": "INTERNAL_ERROR"})

app.include_router(auth.router)
app.include_router(catalogo.router)
app.include_router(pedidos.router)
app.include_router(fidelidade.router)
app.include_router(dashboard.router)
app.include_router(pagamentos.router)

@app.get("/")
def inicio(): return {"mensagem": "API Raizes do Nordeste-Lucas"}

@app.get("/health")
def health(): return {"status": "ok"}