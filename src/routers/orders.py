from fastapi import APIRouter, HTTPException, status
from typing import List
from src.crud.orders import get_order_by_id, create_order # Importamos as funções CRUD
from src.schemas.order import OrderDB, OrderInput

# 1. Criação do Roteador
router = APIRouter(
    prefix="/orders",  # Define o prefixo base para todas as rotas neste arquivo
    tags=["Orders"],   # Agrupa as rotas na documentação (Swagger UI/Redoc)
)

# --- 2. Rota POST: Criar Pedido (Para referência) ---
@router.post("/", response_model=OrderDB, status_code=status.HTTP_201_CREATED)
async def create_new_order(order: OrderInput):
    """
    Cria um novo pedido no sistema.
    """
    # Aqui, a lógica de inserção seria chamada (apenas para contexto futuro)
    # new_order = await create_order(order)
    # return new_order
    
    # Nota: Vamos manter esta rota comentada por agora para focar no GET
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Criação ainda não implementada.")

# --- 3. Rota GET: Obter Pedido por ID ---
@router.get("/{orderId}", response_model=OrderDB)
async def get_order(orderId: str):
    """
    Busca um pedido específico pelo seu ID.

    :param orderId: O ID do pedido gerado pelo sistema (ObjectId do MongoDB).
    :return: Objeto OrderDB se encontrado.
    :raises HTTPException 404: Se o pedido não for encontrado.
    """
    
    # 1. Chama a função da camada CRUD
    order = await get_order_by_id(orderId)
    
    # 2. Verifica o resultado
    if order:
        # Retorna 200 OK e o objeto OrderDB
        return order
    
    # 3. Se não encontrado, levanta a exceção
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Pedido com ID '{orderId}' não encontrado."
    )