from fastapi import FastAPI
app = FastAPI(title="Rede Raizes do Nordeste")

@app.get("/")
def inicio():
    return {"mensagem": "API Raizes do Nordeste", "swagger": "/docs"}