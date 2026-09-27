from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import Usuario

security = HTTPBearer()
SECRET_KEY = "segredo-raizes-2026"
ALGORITHM = "HS256"

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = creds.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return usuario

def get_gerente(usuario = Depends(get_current_user)):
    if usuario.perfil not in ["gerente", "admin"]:
        raise HTTPException(status_code=403, detail="Apenas gerente pode fazer isso")
    return usuario

def get_atendente_ou_gerente(usuario = Depends(get_current_user)):
    if usuario.perfil not in ["atendente", "gerente", "admin"]:
        raise HTTPException(status_code=403, detail="Apenas atendente ou gerente")
    return usuario