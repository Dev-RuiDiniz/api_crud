from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from .config.db import connect_to_mongo, close_mongo_connection, get_database
from .routers.orders import router as orders_router
from pymongo.errors import DuplicateKeyError # Importado para o Exception Handler

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

# --- NOVO: Handler de Exceção Global para MongoDB ---
@app.exception_handler(DuplicateKeyError)
async def duplicate_key_exception_handler(request: Request, exc: DuplicateKeyError):
    """
    Traduz o erro de chave duplicada (código 11000) do MongoDB 
    para um erro HTTP 400 Bad Request padronizado.
    """
    detail_message = "Recurso já existente. O valor fornecido para um campo único já está em uso."
    
    # Retorna uma resposta JSON com status 400
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": detail_message},
    )

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