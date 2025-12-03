from fastapi import APIRouter, HTTPException, status, Query, Depends # Importa o Depends
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

# --- 2. Rota POST: Criar Pedido (Placeholder para contexto) ---
@router.post("/", response_model=OrderDB, status_code=status.HTTP_201_CREATED)
async def create_new_order(
    order: OrderInput, 
    # NOVO: Adiciona a dependência. Se o token for inválido, o código abaixo NUNCA roda.
    current_user_id: str = Depends(verify_token) 
):
    """
    Cria um novo pedido no sistema. Requer autenticação JWT válida.
    O ID do usuário autenticado (current_user_id) está disponível aqui.
    """
    
    # OPCIONAL: Se quisermos garantir que o pedido seja feito pelo usuário logado
    # if order.customer_id != int(current_user_id):
    #    raise HTTPException(status_code=403, detail="Acesso negado: ID do cliente não corresponde ao usuário logado.")

    new_order = await create_order(order)
    
    if new_order:
        # Se houver sucesso (201 Created), retorna o objeto OrderDB completo.
        return new_order

    # Este caso seria capturado pelo exception handler de DuplicateKeyError
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
        detail="Falha ao criar o pedido."
    )

# --- 3. Rota GET: Listar Todos os Pedidos com Paginação (Mantida) ---
@router.get("/", response_model=List[OrderDB])
@router.get("/list", response_model=List[OrderDB], include_in_schema=False)
async def get_all_orders(
    skip: int = Query(0, ge=0, description="Número de registros a serem ignorados (offset)."),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a serem retornados.")
):
    orders = await list_orders(skip=skip, limit=limit)
    return orders

# --- 4. Rota GET: Obter Pedido por ID (Mantida) ---
@router.get("/{orderId}", response_model=OrderDB)
async def get_order(orderId: str):
    order = await get_order_by_id(orderId)
    
    if order:
        return order
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Pedido com ID '{orderId}' não encontrado."
    )

# --- 5. Rota DELETE: Excluir Pedido por ID ---
@router.delete("/{orderId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_order(orderId: str):
    """
    Exclui um pedido específico pelo seu ID.

    :param orderId: O ID do pedido a ser excluído.
    :returns: Resposta vazia (204 No Content) em caso de sucesso.
    :raises HTTPException 404: Se o pedido não for encontrado para exclusão.
    """
    
    # 1. Chama a função da camada CRUD
    success = await delete_order(orderId)
    
    # 2. Verifica o resultado booleano
    if success:
        # Se True, o pedido foi excluído. Retorna 204.
        return 
    
    # 3. Se False, o pedido não existia ou houve erro (assumimos 404 para simplicidade)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Pedido com ID '{orderId}' não encontrado para exclusão."
    )

# --- Próxima Rota: PATCH /orders/{orderId} ---
@router.patch("/{orderId}", response_model=OrderDB)
async def update_existing_order(
    orderId: str, 
    order_data: OrderUpdate
):
    # Lógica de Atualização (implementaremos em seguida)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Atualização PATCH ainda não implementada.")