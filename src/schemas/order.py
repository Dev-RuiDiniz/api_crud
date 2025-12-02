from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import List, Optional, Dict, Any

# --- 1. Schema para o Item dentro de um Pedido ---
class ItemInput(BaseModel):
    """
    Define a estrutura esperada para um Item e permite calcular o subtotal.
    """
    product_id: int = Field(..., description="ID do produto no catálogo.")
    quantity: int = Field(..., gt=0, description="Quantidade do item. Deve ser maior que zero.")
    price: float = Field(..., gt=0.0, description="Preço unitário do item no momento da compra.")
    
    # Propriedade calculada para uso interno
    @property
    def subtotal(self) -> float:
        return round(self.quantity * self.price, 2)

# --- 2. Schema de Entrada para o Pedido (Input) ---
class OrderInput(BaseModel):
    """
    Define a estrutura de um novo Pedido.
    Usa um 'alias' para mapear um nome de campo do cliente ('numeroPedido') para um campo interno ('id').
    """
    id: Optional[int] = Field(None, validation_alias="numeroPedido", description="ID/número do pedido (opcional na entrada).")
    customer_id: int = Field(..., description="ID do cliente que realizou o pedido.")
    items: List[ItemInput] = Field(..., min_length=1, description="Lista de itens do pedido.")
    shipping_address: Optional[str] = Field(None, description="Endereço de entrega (opcional).")

    # Configuração para Pydantic v2
    model_config = ConfigDict(populate_by_name=True) # Permite que aliases sejam usados na criação

# --- 3. Schema de Persistência e Saída (Data Mapping) ---
class OrderDB(OrderInput):
    """
    Define o modelo completo do Pedido, incluindo campos gerados e calculados.
    Herda OrderInput e adiciona a lógica de mapeamento e cálculo.
    """
    # Herda 'id' de OrderInput, mas o nome real do campo no BD pode ser diferente.
    # Exemplo: Se o BD usa '_id' (MongoDB) ou 'order_id'
    
    # Novo campo calculado
    total_value: float = Field(0.0, description="Valor total calculado do pedido, incluindo todos os itens.")
    
    # Campos gerados pelo sistema
    created_at: datetime = Field(..., description="Timestamp de criação do pedido.")
    status: str = Field("PENDING", description="Status atual do pedido.")

    # Pydantic v2: Validator para calcular o valor total
    @field_validator('total_value', mode='before')
    @classmethod
    def calculate_total_value(cls, value: Any, info: field_validator.ValidationInfo) -> float:
        """
        Calcula o valor total somando o subtotal de todos os ItemInput.
        Esta função é executada antes da validação do campo total_value.
        """
        # Se 'total_value' for passado (ex: na leitura do BD), o aceitamos.
        if value != 0.0:
            return value
        
        # Se os dados brutos de 'items' estiverem disponíveis, calculamos.
        raw_items = info.data.get('items', [])
        
        total = 0.0
        for item_data in raw_items:
            # Assumimos que item_data é um dicionário com 'quantity' e 'price'
            try:
                quantity = item_data.get('quantity', 0)
                price = item_data.get('price', 0.0)
                total += quantity * price
            except AttributeError:
                # Caso o dado já tenha sido convertido para ItemInput, usamos a propriedade subtotal
                if isinstance(item_data, ItemInput):
                     total += item_data.subtotal
                else:
                    # Lidar com erro de formato, se necessário
                    pass
        
        return round(total, 2)


    model_config = ConfigDict(
        populate_by_name=True, # Importante para usar aliases
        from_attributes=True   # Permite conversão de objetos ORM/DB
    )
    
# --- 4. Schema de Atualização Parcial (PATCH) ---
class OrderUpdate(BaseModel):
    """
    Define a estrutura para atualização parcial de um Pedido.
    Todos os campos são Optional.
    """
    customer_id: Optional[int] = Field(None, description="ID do cliente que realizou o pedido.")
    items: Optional[List[ItemInput]] = Field(None, min_length=1, description="Lista de itens do pedido.")
    shipping_address: Optional[str] = Field(None, description="Endereço de entrega (opcional).")
    status: Optional[str] = Field(None, description="Status atual do pedido.")
    # Nota: Não incluímos 'id' ou 'created_at' aqui, pois não devem ser alterados.