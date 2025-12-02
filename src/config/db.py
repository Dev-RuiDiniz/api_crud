import motor.motor_asyncio
from pymongo.errors import ConnectionFailure, OperationFailure

# Variáveis Globais de Conexão
# NOTA: O ideal é que MONGO_DETAILS venha de src/config/settings.py (.env)
MONGO_DETAILS = "mongodb://localhost:27017"
DB_NAME = "api_crud_db"

client: motor.motor_asyncio.AsyncIOMotorClient = None
database: motor.motor_asyncio.AsyncIOMotorDatabase = None

async def connect_to_mongo():
    """Inicializa a conexão assíncrona com o MongoDB."""
    global client, database
    
    try:
        # Inicializa o cliente do Motor
        client = motor.motor_asyncio.AsyncIOMotorClient(
            MONGO_DETAILS,
            serverSelectionTimeoutMS=5000  # Timeout de 5 segundos
        )
        
        # Tenta pingar o servidor para verificar se ele está rodando
        await client.admin.command('ping') 
        
        database = client[DB_NAME]
        print("✅ Conexão com MongoDB estabelecida com sucesso!")
        
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