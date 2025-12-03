from typing import Optional, List, Dict, Any
from src.schemas.order import OrderDB, OrderInput, OrderUpdate
from src.config.db import get_database
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult # Importa DeleteResult
from bson import ObjectId
from pymongo import DESCENDING

# Nome da coleção no MongoDB
COLLECTION_NAME = "orders"

# --- 1. FUNÇÃO: CREATE ---
async def create_order(order_data: OrderInput) -> Optional[OrderDB]:
    """
    Insere um novo pedido no MongoDB e retorna o objeto OrderDB completo.
    """
    db = get_database()
    if not db:
        return None

    try:
        # Converte o objeto Pydantic para um dicionário para inserção
        order_dict = order_data.model_dump(mode="json", by_alias=True)
        
        # Define campos gerados (se não vierem já calculados pelo Pydantic)
        if 'created_at' not in order_dict:
            from datetime import datetime
            order_dict['created_at'] = datetime.utcnow()
            order_dict['status'] = "PENDING"
        
        collection = db[COLLECTION_NAME]
        
        result: InsertOneResult = await collection.insert_one(order_dict)
        
        if result.inserted_id:
            # Consulta o documento recém-inserido
            new_order_doc = await collection.find_one({"_id": result.inserted_id})
            
            if new_order_doc:
                # Mapeamento: MongoDB '_id' (ObjectId) para Pydantic 'id' (str)
                new_order_doc["id"] = str(new_order_doc.pop("_id")) 
                return OrderDB(**new_order_doc)
            
    except Exception as e:
        print(f"❌ ERRO ao inserir pedido no MongoDB: {e}")
        return None
    
    return None

# --- 2. FUNÇÃO: READ by ID ---
async def get_order_by_id(order_id: str) -> Optional[OrderDB]:
    """
    Busca um pedido no MongoDB pelo seu ID (chave primária).
    """
    db = get_database()
    if not db:
        return None

    try:
        # Converte a string de ID para o formato ObjectId do MongoDB
        object_id = ObjectId(order_id) 
        collection = db[COLLECTION_NAME]
        
        order_doc = await collection.find_one({"_id": object_id})

        if order_doc:
            # Mapeamento de Retorno
            order_doc["id"] = str(order_doc.pop("_id")) 
            return OrderDB(**order_doc)
            
    except Exception as e:
        print(f"❌ ERRO ao buscar pedido por ID {order_id}: {e}")
        return None
    
    return None

# --- 3. FUNÇÃO: READ all (Listagem com Paginação) ---
async def list_orders(skip: int = 0, limit: int = 10) -> List[OrderDB]:
    """
    Busca uma lista de pedidos no MongoDB com suporte a paginação (skip, limit).
    """
    db = get_database()
    if not db:
        return []

    try:
        collection = db[COLLECTION_NAME]
        
        cursor = collection.find({})
        cursor.sort("created_at", DESCENDING) # Ordena pelo mais recente
        cursor = cursor.skip(skip).limit(limit) # Aplica Paginação
        
        orders_list = await cursor.to_list(length=limit)
        
        mapped_orders: List[OrderDB] = []
        for order_doc in orders_list:
            # Mapeamento: MongoDB '_id' (ObjectId) para Pydantic 'id' (str)
            order_doc["id"] = str(order_doc.pop("_id"))
            mapped_orders.append(OrderDB(**order_doc))
            
        return mapped_orders
            
    except Exception as e:
        print(f"❌ ERRO ao listar pedidos: {e}")
        return []

# --- 4. FUNÇÃO: UPDATE (Parcial) ---
async def update_order(order_id: str, order_data: OrderUpdate) -> Optional[OrderDB]:
    """
    Atualiza parcialmente um pedido no MongoDB, recalculando o total_value se 'items' mudar.
    """
    db = get_database()
    if not db:
        return None

    try:
        object_id = ObjectId(order_id)
        collection = db[COLLECTION_NAME]
        
        # Obtém apenas os campos que não são None para atualização parcial (PATCH)
        update_dict: Dict[str, Any] = order_data.model_dump(exclude_none=True, by_alias=True)

        if not update_dict:
            return await get_order_by_id(order_id)

        # Lógica de Recálculo Condicional
        if "items" in update_dict:
            current_order_doc = await collection.find_one({"_id": object_id})
            if not current_order_doc:
                return None
            
            # Revalida os dados, permitindo que o Pydantic recalcule 'total_value'
            data_to_revalidate = {
                **current_order_doc, 
                **update_dict,
                "id": str(current_order_doc["_id"])
            }
            validated_order = OrderDB(**data_to_revalidate)
            
            # Adiciona o novo valor total calculado ao dicionário de atualização
            update_dict["total_value"] = validated_order.total_value

        # Executa a Atualização Parcial com $set
        result: UpdateResult = await collection.update_one(
            {"_id": object_id},
            {"$set": update_dict}
        )

        if result.matched_count == 0:
            return None # Pedido não encontrado
        
        # Retorna o documento atualizado
        return await get_order_by_id(order_id)

    except Exception as e:
        print(f"❌ ERRO ao atualizar pedido {order_id}: {e}")
        return None
    
# --- 5. FUNÇÃO: DELETE ---

async def delete_order(order_id: str) -> bool:
    """
    Exclui um pedido do MongoDB pelo seu ID.

    :param order_id: O ID do pedido a ser excluído.
    :return: True se o pedido foi excluído com sucesso (matched_count > 0), False caso contrário.
    """
    db = get_database()
    if not db:
        return False

    try:
        # 1. Converte a string de ID para o formato ObjectId
        object_id = ObjectId(order_id)
        collection = db[COLLECTION_NAME]
        
        # 2. Executa a exclusão assíncrona
        result: DeleteResult = await collection.delete_one(
            {"_id": object_id}
        )

        # 3. Verifica o resultado
        # Se acknowledged for True e deleted_count for 1, a exclusão ocorreu.
        return result.acknowledged and result.deleted_count > 0

    except Exception as e:
        # Captura erros de conversão (ObjectId inválido) ou de DB
        print(f"❌ ERRO ao excluir pedido {order_id}: {e}")
        return False