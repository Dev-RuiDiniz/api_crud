from fastapi import APIRouter, HTTPException, status, Query # Query para validação de parâmetros
from typing import List
from src.crud.orders import get_order_by_id, create_order, list_orders # Importa a nova função CRUD
from src.schemas.order import OrderDB, OrderInput

# 1. Criação do Roteador
router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)

# --- 2. Rota POST: Criar Pedido (Ainda placeholder) ---
@router.post("/", response_model=OrderDB, status_code=status.HTTP_201_CREATED)
async def create_new_order(order: OrderInput):
    # Lógica de Criação (a ser implementada)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Criação ainda não implementada.")

# --- 3. Rota GET: Listar Todos os Pedidos com Paginação ---
@router.get("/", response_model=List[OrderDB]) # Usa List[OrderDB] como modelo de resposta
@router.get("/list", response_model=List[OrderDB], include_in_schema=False) # Adiciona /list (opcional)
async def get_all_orders(
    # Parâmetros de Query com valores default e validação
    skip: int = Query(0, ge=0, description="Número de registros a serem ignorados (offset)."),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a serem retornados.")
):
    """
    Lista todos os pedidos no sistema com suporte a paginação (skip e limit).
    """
    
    # 1. Chama a função da camada CRUD com os parâmetros de paginação
    orders = await list_orders(skip=skip, limit=limit)
    
    # 2. Retorna a lista. Se a lista estiver vazia, o FastAPI retorna 200 OK com []
    return orders

# --- 4. Rota GET: Obter Pedido por ID (Mantida) ---
@router.get("/{orderId}", response_model=OrderDB)
async def get_order(orderId: str):
    # Lógica de busca por ID (mantida)
    order = await get_order_by_id(orderId)
    
    if order:
        return order
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Pedido com ID '{orderId}' não encontrado."
    )