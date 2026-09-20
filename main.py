from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import FastAPI, Request, HTTPException
from core.database import engine, Base
from routers import auth, catalogo, pedidos, fidelidade, dashboard, pagamentos
import uuid
from datetime import datetime, timezone



Base.metadata.create_all(bind=engine)

app = FastAPI(title="Rede Raizes do Nordeste", version="1.0")


@app.exception_handler(HTTPException)
async def http_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "VALIDATION_ERROR",
            "message": str(exc.detail),
            "details": [{"field": "canalPedido", "issue": str(exc.detail)}],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url.path),
            "requestId": str(uuid.uuid4())
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Erro de validação",
            "details": [{"field": err['loc'][-1], "issue": err['msg']} for err in exc.errors()],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url.path),
            "requestId": str(uuid.uuid4())
        }
    )

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