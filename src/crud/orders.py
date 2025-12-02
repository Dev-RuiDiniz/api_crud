from typing import Optional, List
from src.schemas.order import OrderDB, OrderInput
from src.config.db import get_database
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