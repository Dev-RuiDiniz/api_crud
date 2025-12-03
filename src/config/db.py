import motor.motor_asyncio
from pymongo.errors import ConnectionFailure, OperationFailure
from pymongo import ASCENDING, DESCENDING # Para definir a ordem do índice

# Variáveis Globais de Conexão
MONGO_DETAILS = "mongodb://localhost:27017"
DB_NAME = "api_crud_db"
COLLECTION_NAME = "orders" # Usaremos aqui também

client: motor.motor_asyncio.AsyncIOMotorClient = None
database: motor.motor_asyncio.AsyncIOMotorDatabase = None


# --- NOVA FUNÇÃO: Configuração de Índices ---
async def configure_indexes():
    """Garante que os índices necessários para otimizar as consultas existam."""
    global database
    
    if not database:
        print("⚠️ Não foi possível configurar índices: DB não está conectado.")
        return

    try:
        orders_collection = database[COLLECTION_NAME]
        
        # 1. Índice para Ordenação/Listagem (created_at)
        await orders_collection.create_index(
            [("created_at", DESCENDING)],
            name="created_at_desc_index"
        )
        print("✅ Índice 'created_at' configurado.")
        
        # 2. Índice para Chave de Negócio ou Consultas por Cliente (customer_id)
        # Índice composto ou simples, dependendo das necessidades.
        # Vamos criar um índice simples no customer_id para eficiência na filtragem.
        await orders_collection.create_index(
            "customer_id",
            name="customer_id_index",
            # unique=True, # Não é único, um cliente pode ter muitos pedidos
        )
        print("✅ Índice 'customer_id' configurado.")
        
        # 3. (Opcional) Índice para o status do pedido, se a filtragem for comum
        await orders_collection.create_index(
            "status",
            name="status_index"
        )
        print("✅ Índice 'status' configurado.")
        
    except Exception as e:
        print(f"❌ Erro ao configurar índices do MongoDB: {e}")
        
# --- Função de Conexão Atualizada para incluir a Configuração ---
async def connect_to_mongo():
    """Inicializa a conexão assíncrona com o MongoDB E configura os índices."""
    global client, database
    
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(
            MONGO_DETAILS,
            serverSelectionTimeoutMS=5000
        )
        
        await client.admin.command('ping') 
        
        database = client[DB_NAME]
        print("✅ Conexão com MongoDB estabelecida com sucesso!")
        
        # --- NOVO: Chamada para configurar os índices APÓS a conexão ---
        await configure_indexes()
        
    except ConnectionFailure:
        print("❌ ERRO: Falha ao conectar ao MongoDB. Verifique se o servidor está ativo.")
        client = None
        database = None
    except OperationFailure as e:
        print(f"❌ ERRO: Falha de operação no MongoDB. Detalhes: {e}")
        client = None
        database = None
    except Exception as e:
        print(f"❌ ERRO INESPERADO ao conectar ao MongoDB: {e}")
        client = None
        database = None

async def close_mongo_connection():
    """Fecha a conexão com o MongoDB de forma limpa."""
    global client
    if client:
        client.close()
        print("🔌 Conexão com MongoDB fechada.")
        
def get_database() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    """Retorna a instância do banco de dados (usada na camada CRUD)."""
    return database