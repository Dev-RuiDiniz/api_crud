from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware # Usaremos para o CORS, essencial em APIs

# 1. Instância do FastAPI
app = FastAPI(
    title="API CRUD de Pedidos",
    description="API de exemplo para gerenciamento de pedidos, construída com FastAPI.",
    version="1.0.0",
)

# 2. Configuração do Middleware CORS (Cross-Origin Resource Sharing)
# Essencial para permitir que um front-end em outro domínio acesse esta API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite qualquer origem. Em produção, liste domínios específicos.
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# 3. Importar e Incluir Roteadores (Futuro)
# No momento, o roteador de pedidos está vazio, mas esta linha o incluirá:
# from .routers import order_router # (Exemplo: se você criar o order_router)
# app.include_router(order_router, prefix="/api/v1")

# 4. Rota de Teste (Health Check)
@app.get("/", tags=["Health Check"])
def health_check():
    """Endpoint simples para verificar se a API está online."""
    return {"message": "API CRUD está online!"}

# ---
# Para rodar a aplicação, use o Uvicorn no terminal (com o ambiente virtual ativo):
# uvicorn src.main:app --reload --port 8000