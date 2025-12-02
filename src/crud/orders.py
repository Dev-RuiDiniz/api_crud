from typing import Optional
from src.schemas.order import OrderDB, OrderInput
from src.config.db import get_database
from pymongo.results import InsertOneResult
from bson import ObjectId

# Nome da coleção no MongoDB
COLLECTION_NAME = "orders"

async def create_order(order_data: OrderInput) -> Optional[OrderDB]:
    """
    Insere um novo pedido no MongoDB e retorna o objeto OrderDB completo.

    :param order_data: O objeto OrderInput (ou OrderDB) contendo os dados do pedido.
    :return: O objeto OrderDB com o ID e o timestamp gerados pelo DB, ou None em caso de falha.
    """
    
    # 1. Obtém a instância do banco de dados (AsyncIOMotorDatabase)
    db = get_database()
    
    if not db:
        print("❌ ERRO: Banco de dados não conectado.")
        return None

    # 2. Converte o objeto Pydantic para um dicionário (formatado para MongoDB)
    # .model_dump() é a forma correta no Pydantic v2 para obter um dict.
    # by_alias=True garante que campos com alias sejam usados.
    order_dict = order_data.model_dump(mode="json", by_alias=True)
    
    # 3. Define campos que seriam gerados pelo servidor (timestamp e status)
    # Em um cenário real, OrderDB já deveria vir com alguns destes dados.
    if 'created_at' not in order_dict:
        # Nota: O MongoDB gera o campo _id automaticamente
        from datetime import datetime
        order_dict['created_at'] = datetime.utcnow()
        order_dict['status'] = "PENDING"
    
    # 4. Acessa a coleção e executa a operação de inserção assíncrona
    try:
        # A coleção é criada automaticamente se não existir
        collection = db[COLLECTION_NAME]
        
        result: InsertOneResult = await collection.insert_one(order_dict)
        
        # 5. Obtém o ID gerado e consulta o documento completo inserido
        if result.inserted_id:
            # Consulta o documento recém-inserido para ter a certeza dos dados
            new_order_doc = await collection.find_one({"_id": result.inserted_id})
            
            if new_order_doc:
                # Transforma o documento do MongoDB de volta para o modelo Pydantic OrderDB
                # Nota: MongoDB usa '_id' (ObjectId) e Pydantic espera 'id' (int/str, dependendo do mapping)
                
                # Mapeamento do '_id' do MongoDB para 'id' do Pydantic
                new_order_doc["id"] = str(new_order_doc.pop("_id")) 
                
                return OrderDB(**new_order_doc)
            
    except Exception as e:
        print(f"❌ ERRO ao inserir pedido no MongoDB: {e}")
        return None
    
    return None