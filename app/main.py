from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import usuarios, eventos, recomendacoes, gamificacao
from app.database import connect_to_mongo, close_mongo_connection

app = FastAPI(
    title="KidsAdvisor API",
    description="Sistema de recomendações de eventos infantis com gamificação",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
app.include_router(eventos.router, prefix="/eventos", tags=["eventos"])
app.include_router(recomendacoes.router, prefix="/recomendacoes", tags=["recomendacoes"])
app.include_router(gamificacao.router, prefix="/gamificacao", tags=["gamificacao"])

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

@app.get("/")
async def root():
    return {"message": "KidsAdvisor API - Sistema de recomendações de eventos infantis"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}