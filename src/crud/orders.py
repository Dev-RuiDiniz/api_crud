from typing import Optional, List
from src.schemas.order import OrderDB, OrderInput
from src.config.db import get_database
from src.schemas.order import OrderDB, OrderInput, OrderUpdate # Importa o novo schema
from pymongo.results import InsertOneResult
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING # Importação para ordenação (sort)

# Nome da coleção no MongoDB
COLLECTION_NAME = "orders"

# --- Função de Criação (Mantida) ---
async def create_order(order_data: OrderInput) -> Optional[OrderDB]:
    """
    Insere um novo pedido no MongoDB e retorna o objeto OrderDB completo.
    ... (Implementação de create_order) ...
    """
    
    # 1. Obtém a instância do banco de dados (AsyncIOMotorDatabase)
    db = get_database()
    
    if not db:
        # Simplificando a verificação de conexão para este exemplo
        return None

    # 2. Converte o objeto Pydantic para um dicionário
    order_dict = order_data.model_dump(mode="json", by_alias=True)
    
    # 3. Define campos gerados (se não vierem do OrderDB com valores default)
    if 'created_at' not in order_dict:
        from datetime import datetime
        order_dict['created_at'] = datetime.utcnow()
        order_dict['status'] = "PENDING"
    
    # 4. Acessa a coleção e executa a operação de inserção assíncrona
    try:
        collection = db[COLLECTION_NAME]
        
        result: InsertOneResult = await collection.insert_one(order_dict)
        
        # 5. Obtém o ID gerado e consulta o documento completo inserido
        if result.inserted_id:
            new_order_doc = await collection.find_one({"_id": result.inserted_id})
            
            if new_order_doc:
                # Mapeamento: MongoDB '_id' (ObjectId) para Pydantic 'id' (str)
                new_order_doc["id"] = str(new_order_doc.pop("_id")) 
                return OrderDB(**new_order_doc)
            
    except Exception as e:
        print(f"❌ ERRO ao inserir pedido no MongoDB: {e}")
        return None
    
    return None

# --- NOVA FUNÇÃO: Obter Pedido por ID ---
async def get_order_by_id(order_id: str) -> Optional[OrderDB]:
    """
    Busca um pedido no MongoDB pelo seu ID (chave primária).

    :param order_id: O ID do pedido (string).
    :return: O objeto OrderDB encontrado, ou None se não existir.
    """
    db = get_database()

    if not db:
        return None

    try:
        # MongoDB usa ObjectId para o campo _id. Precisamos converter a string
        # de ID que recebemos para ObjectId antes de buscar.
        object_id = ObjectId(order_id) 
        
        collection = db[COLLECTION_NAME]
        
        # 1. Executa a busca assíncrona
        order_doc = await collection.find_one({"_id": object_id})

        if order_doc:
            # 2. Mapeamento de Retorno: Converte o documento MongoDB para Pydantic
            # Retira '_id' e adiciona 'id' (como string) para o Pydantic
            order_doc["id"] = str(order_doc.pop("_id")) 
            
            # 3. Retorna o objeto Pydantic validado
            return OrderDB(**order_doc)
            
    except Exception as e:
        # Captura erros de conversão (ex: string de ID inválida para ObjectId) ou de DB
        print(f"❌ ERRO ao buscar pedido por ID {order_id}: {e}")
        return None
    
    return None

# --- NOVA FUNÇÃO: Listar Todos os Pedidos com Paginação ---
async def list_orders(skip: int = 0, limit: int = 10) -> List[OrderDB]:
    """
    Busca uma lista de pedidos no MongoDB com suporte a paginação.

    :param skip: Número de documentos a serem ignorados (offset).
    :param limit: Número máximo de documentos a serem retornados.
    :return: Uma lista de objetos OrderDB.
    """
    db = get_database()

    if not db:
        return []

    try:
        collection = db[COLLECTION_NAME]
        
        # 1. Constrói a query usando cursor assíncrono do Motor
        cursor = collection.find({}) # Busca todos os documentos
        
        # 2. Aplica Ordenação (sort)
        # Ordenamos por data de criação (created_at) de forma decrescente (mais recente primeiro)
        cursor.sort("created_at", DESCENDING) 
        
        # 3. Aplica Paginação (skip e limit)
        # O cursor do Motor suporta os métodos .skip() e .limit()
        cursor = cursor.skip(skip).limit(limit)
        
        # 4. Converte o cursor em uma lista de documentos (execução assíncrona)
        orders_list = await cursor.to_list(length=limit)
        
        # 5. Mapeamento de Retorno: Converte cada documento MongoDB para Pydantic
        mapped_orders: List[OrderDB] = []
        for order_doc in orders_list:
            # Mapeamento: MongoDB '_id' (ObjectId) para Pydantic 'id' (str)
            order_doc["id"] = str(order_doc.pop("_id"))
            
            # Instancia e valida o modelo Pydantic
            mapped_orders.append(OrderDB(**order_doc))
            
        return mapped_orders
            
    except Exception as e:
        print(f"❌ ERRO ao listar pedidos: {e}")
        return []
    
# --- NOVA FUNÇÃO: Atualização de Pedido (PATCH) ---
async def update_order(order_id: str, order_data: OrderUpdate) -> Optional[OrderDB]:
    """
    Atualiza parcialmente um pedido no MongoDB. Recalcula o total_value se 'items' for modificado.

    :param order_id: O ID do pedido a ser atualizado.
    :param order_data: O objeto OrderUpdate contendo apenas os campos a serem alterados.
    :return: O objeto OrderDB atualizado, ou None se o pedido não for encontrado.
    """
    db = get_database()
    if not db:
        return None

    try:
        object_id = ObjectId(order_id)
        collection = db[COLLECTION_NAME]
        
        # 1. Obtém apenas os campos que foram realmente passados para atualização
        # Excluímos campos não definidos/None (partial update)
        update_dict: Dict[str, Any] = order_data.model_dump(exclude_none=True, by_alias=True)

        if not update_dict:
            # Não há dados para atualizar
            return await get_order_by_id(order_id)

        # 2. Lógica de Recálculo Condicional
        if "items" in update_dict:
            # Se os itens foram modificados, precisamos recalcular o total_value.
            
            # Criamos uma instância temporária de OrderDB (não salvamos) para usar o validator interno
            # Recuperamos o documento atual para ter o created_at/status, etc.
            current_order_doc = await collection.find_one({"_id": object_id})
            
            if not current_order_doc:
                return None # Pedido não encontrado

            # Preparamos os dados para revalidação/recálculo
            data_to_revalidate = {
                **current_order_doc, 
                **update_dict,
                "id": str(current_order_doc["_id"])
            }
            # Criamos uma instância OrderDB temporária para forçar o recálculo do total_value
            # O Pydantic validator em OrderDB garantirá o cálculo correto
            validated_order = OrderDB(**data_to_revalidate)
            
            # Adicionamos o valor calculado ao dicionário de atualização
            update_dict["total_value"] = validated_order.total_value


        # 3. Executa a Atualização no MongoDB com $set
        result: UpdateResult = await collection.update_one(
            {"_id": object_id},
            {"$set": update_dict}
        )

        if result.matched_count == 0:
            return None # Pedido não encontrado
        
        # 4. Retorna o documento atualizado
        # Já que o update_one é rápido, consultamos o documento após a atualização
        return await get_order_by_id(order_id)

    except Exception as e:
        print(f"❌ ERRO ao atualizar pedido {order_id}: {e}")
        return None