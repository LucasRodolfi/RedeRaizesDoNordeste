# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from core.database import get_db
from models.models import Usuario
from schemas.schemas import UsuarioCreate, UsuarioLogin

router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "segredo-raizes-2026"
ALGORITHM = "HS256"
security = HTTPBearer()

def criar_token(dados: dict):
    exp = datetime.now(timezone.utc) + timedelta(minutes=60)
    dados.update({"exp": exp})
    return jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", status_code=201)
def registrar(dados: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == dados.email).first():
        raise HTTPException(409, "Email já cadastrado")
    print(f"[AUDIT] Novo usuário {dados.email} perfil {dados.perfil}")
    novo = Usuario(
        nome=dados.nome, 
        email=dados.email, 
        senha_hash=pwd_context.hash(dados.senha), 
        perfil=dados.perfil,
        consentimento_fidelidade=dados.consentimento_fidelidade
    )
    db.add(novo); db.commit(); db.refresh(novo)
    return novo

@router.post("/login")
def login(dados: UsuarioLogin, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if not user or not pwd_context.verify(dados.senha, user.senha_hash):
        raise HTTPException(status_code=401, detail={
            "error": "CREDENCIAIS_INVALIDAS",
            "message": "E-mail ou senha inválidos."
        })
    token = criar_token({"sub": user.email, "perfil": user.perfil})
    return {
        "accessToken": token,
        "tokenType": "Bearer",
        "expiresIn": 3600,
        "user": {"id": user.id, "nome": user.nome, "perfil": user.perfil}
    }

def get_usuario_atual(creds: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(Usuario).filter(Usuario.email == payload.get("sub")).first()
        if not user:
            raise HTTPException(401, "Token inválido")
        return user
    except:
        raise HTTPException(401, "Token inválido")