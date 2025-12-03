from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List
from src.crud.orders import (
    get_order_by_id, 
    create_order, 
    list_orders, 
    update_order, 
    delete_order
)
from src.schemas.order import OrderDB, OrderInput, OrderUpdate
from src.security import verify_token # Importa a dependência de segurança

# 1. Criação do Roteador
router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)

# -------------------------------------------------------------
# 2. Rota POST: Criar Pedido (Protegida por JWT)
# -------------------------------------------------------------
@router.post(
    "/", 
    response_model=OrderDB, 
    status_code=status.HTTP_201_CREATED,
    # Adicionando responses para documentar os erros comuns
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Não Autorizado (Token Inválido/Ausente)"},
        status.HTTP_400_BAD_REQUEST: {"description": "Requisição Inválida (Chave Duplicada ou Erro de Validação)"}
    }
)
async def create_new_order(
    order: OrderInput, 
    current_user_id: str = Depends(verify_token) 
):
    """
    Cria um **novo pedido** no sistema. 
    
    O cálculo do `total_value` é feito automaticamente com base nos itens.
    
    ### Requer Autenticação JWT.
    
    :param order: Dados do novo pedido (OrderInput).
    :returns: O objeto OrderDB criado (201 Created).
    """
    new_order = await create_order(order)
    
    if new_order:
        return new_order

    # No caso de erro de DB não capturado pelo handler 400
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
        detail="Falha inesperada ao criar o pedido."
    )

# -------------------------------------------------------------
# 3. Rota GET: Listar Todos os Pedidos com Paginação
# -------------------------------------------------------------
@router.get(
    "/", 
    response_model=List[OrderDB],
    description="Lista pedidos com suporte a paginação. Ordenado por 'created_at' decrescente."
)
@router.get("/list", response_model=List[OrderDB], include_in_schema=False)
async def get_all_orders(
    skip: int = Query(0, ge=0, description="Número de registros a serem ignorados (offset)."),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a serem retornados.")
):
    """
    Retorna uma lista paginada de todos os pedidos.
    """
    orders = await list_orders(skip=skip, limit=limit)
    return orders

# -------------------------------------------------------------
# 4. Rota GET: Obter Pedido por ID
# -------------------------------------------------------------
@router.get(
    "/{orderId}", 
    response_model=OrderDB,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Pedido não encontrado"}
    }
)
async def get_order(orderId: str):
    """
    Busca um pedido específico utilizando seu ID (gerado pelo MongoDB, tipo string).
    """
    order = await get_order_by_id(orderId)
    
    if order:
        return order
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Pedido com ID '{orderId}' não encontrado."
    )

# -------------------------------------------------------------
# 5. Rota DELETE: Excluir Pedido por ID
# -------------------------------------------------------------
@router.delete(
    "/{orderId}", 
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Pedido não encontrado para exclusão"}
    }
)
async def delete_existing_order(orderId: str):
    """
    Exclui um pedido específico pelo seu ID. Retorna 204 No Content em caso de sucesso.
    """
    success = await delete_order(orderId)
    
    if success:
        return 
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Pedido com ID '{orderId}' não encontrado para exclusão."
    )

# -------------------------------------------------------------
# 6. Rota PATCH: Atualizar Pedido Parcialmente
# -------------------------------------------------------------
@router.patch(
    "/{orderId}", 
    response_model=OrderDB,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Pedido não encontrado"},
        status.HTTP_400_BAD_REQUEST: {"description": "Corpo da requisição vazio ou inválido"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Não Autorizado (Token Inválido/Ausente)"}
    }
)
async def update_existing_order(
    orderId: str, 
    order_data: OrderUpdate,
    current_user_id: str = Depends(verify_token) # Exige JWT
):
    """
    Atualiza **parcialmente** um pedido existente (PATCH).
    
    Os campos `items` são opcionais, mas se forem fornecidos, o `total_value` é recalculado automaticamente.
    
    ### Requer Autenticação JWT.
    """
    if not order_data.model_dump(exclude_none=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pelo menos um campo deve ser fornecido para a atualização."
        )

    updated_order = await update_order(orderId, order_data)
    
    if updated_order:
        return updated_order
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Pedido com ID '{orderId}' não encontrado para atualização."
    )