from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# --- 1. Schema para o Item dentro de um Pedido ---
class ItemInput(BaseModel):
    """
    Define a estrutura esperada para um Item ao ser enviado pelo cliente.
    Usado no Body de um POST/PUT para Pedido.
    """
    product_id: int = Field(..., description="ID do produto no catálogo.")
    quantity: int = Field(..., gt=0, description="Quantidade do item. Deve ser maior que zero.")
    price: float = Field(..., gt=0.0, description="Preço unitário do item no momento da compra.")

# --- 2. Schema de Entrada para o Pedido (Input) ---
class OrderInput(BaseModel):
    """
    Define a estrutura de um novo Pedido ao ser criado.
    Representa o Body da requisição HTTP (POST).
    """
    customer_id: int = Field(..., description="ID do cliente que realizou o pedido.")
    items: List[ItemInput] = Field(..., min_length=1, description="Lista de itens do pedido.")
    shipping_address: Optional[str] = Field(None, description="Endereço de entrega (opcional).")

    # Garante que a lista de items não esteja vazia
    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items)

# --- 3. Schema de Persistência (Data Mapping / Saída) ---
class OrderDB(OrderInput):
    """
    Define o modelo completo do Pedido, incluindo campos gerados pelo sistema.
    Usado para enviar o Pedido como Resposta da API e interagir com o DB.
    """
    id: int = Field(..., description="ID único gerado pelo banco de dados.")
    created_at: datetime = Field(..., description="Timestamp de criação do pedido.")
    status: str = Field("PENDING", description="Status atual do pedido (PENDING, SHIPPED, DELIVERED, CANCELLED).")

    class Config:
        # Permite que a classe seja instanciada a partir de ORMs (como SQLAlchemy)
        from_attributes = True