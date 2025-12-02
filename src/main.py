from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from .config.db import connect_to_mongo, close_mongo_connection, get_database

# 1. Instância do FastAPI
app = FastAPI(
    title="API CRUD de Pedidos",
    description="API de exemplo para gerenciamento de pedidos, construída com FastAPI e MongoDB.",
    version="1.0.0",
)

# 2. Configuração do Middleware CORS
# Permite que aplicações front-end em diferentes domínios acessem a API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens (mudar em produção)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# 3. Event Handlers para a Conexão com o MongoDB

@app.on_event("startup")
async def startup_db_client():
    """Função executada ANTES da API começar a receber requisições."""
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    """Função executada DEPOIS da API parar de receber requisições."""
    await close_mongo_connection()

# 4. Rota de Teste (Health Check)
@app.get("/", tags=["Health Check"])
def health_check():
    """Endpoint simples para verificar se a API está online e o status do DB."""
    db = get_database()
    db_status = "Conectado" if db else "Desconectado"
    
    return {
        "message": "API CRUD está online!",
        "database_status": db_status
    }

# 5. Roteadores (Futura Inclusão)
# Aqui, futuramente, você incluirá seus roteadores:
# from .routers.user import router as user_router
# app.include_router(user_router, prefix="/api/v1/users", tags=["Usuários"])

# Para rodar a aplicação: uvicorn src.main:app --reload