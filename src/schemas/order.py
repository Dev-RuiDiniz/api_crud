from pydantic import (
    BaseModel, 
    Field, 
    field_validator, 
    ConfigDict,
    ValidationInfo # CORREÇÃO FINAL para Pydantic v2
)
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
    
    @property
    def subtotal(self) -> float:
        return round(self.quantity * self.price, 2)

# --- 2. Schema de Entrada para o Pedido (Input) ---
class OrderInput(BaseModel):
    """
    Define a estrutura de um novo Pedido.
    """
    id: Optional[str] = Field(None, validation_alias="numeroPedido", description="ID/número do pedido (string/ObjectId).")
    customer_id: int = Field(..., description="ID do cliente que realizou o pedido.")
    items: List[ItemInput] = Field(..., min_length=1, description="Lista de itens do pedido.")
    shipping_address: Optional[str] = Field(None, description="Endereço de entrega (opcional).")

    model_config = ConfigDict(populate_by_name=True) 

# --- 3. Schema de Persistência e Saída (Data Mapping e Cálculo) ---
class OrderDB(OrderInput):
    """
    Define o modelo completo do Pedido, incluindo campos gerados, calculados e mapeados.
    """
    total_value: float = Field(0.0, description="Valor total calculado do pedido, incluindo todos os itens.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de criação do pedido.")
    status: str = Field("PENDING", description="Status atual do pedido.")

    @field_validator('total_value', mode='before')
    @classmethod
    def calculate_total_value(cls, value: Any, info: ValidationInfo) -> float:
        """
        Calcula o valor total somando o subtotal de todos os ItemInput.
        """
        if value is not None and value != 0.0:
            return value
        
        raw_items = info.data.get('items', [])
        total = 0.0
        for item_data in raw_items:
            try:
                quantity = item_data.get('quantity', 0)
                price = item_data.get('price', 0.0)
                total += quantity * price
            except AttributeError:
                if isinstance(item_data, ItemInput):
                     total += item_data.subtotal
                else:
                    pass

        return round(total, 2)


    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
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