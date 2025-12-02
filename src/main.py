from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
# Funções para ciclo de vida do DB
from .config.db import connect_to_mongo, close_mongo_connection, get_database

# --- Roteadores ---
# Importa a instância do APIRouter que criamos em src/routers/orders.py
from .routers.orders import router as orders_router

# 1. Instância do FastAPI
app = FastAPI(
    title="API CRUD de Pedidos",
    description="API de exemplo para gerenciamento de pedidos, construída com FastAPI e MongoDB.",
    version="1.0.0",
)

# 2. Configuração do Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Event Handlers para a Conexão com o MongoDB

@app.on_event("startup")
async def startup_db_client():
    """Conecta ao MongoDB quando a API inicia."""
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    """Fecha a conexão do MongoDB quando a API é encerrada."""
    await close_mongo_connection()

# 4. Inclusão dos Roteadores
# Inclui as rotas definidas em src/routers/orders.py
app.include_router(orders_router)

# 5. Rota de Teste (Health Check)
@app.get("/", tags=["Health Check"])
def health_check():
    """Endpoint simples para verificar se a API está online e o status do DB."""
    db = get_database()
    db_status = "Conectado" if db else "Desconectado"
    
    return {
        "message": "API CRUD está online!",
        "database_status": db_status
    }

# Para rodar a aplicação: uvicorn src.main:app --reload