from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    sku: str = Field(default="", max_length=50)
    category: str = "Wooden item"
    wood_type: str = "General"
    dimensions: str | None = None
    pieces_per_bundle: int = Field(default=350, ge=1)
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=5, ge=0)


class ProductRead(ProductCreate):
    id: int
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class PurchaseCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=0, ge=0)
    unit_cost: float = Field(gt=0)
    member: str = "bhai-1"
    bundles: int = Field(default=0, ge=0)
    pieces: int = Field(default=0, ge=0)


class SaleCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=0, ge=0)
    unit_price: float | None = Field(default=None, gt=0)
    customer_name: str | None = None
    channel: str = "online"
    member: str = "bhai-1"
    bundles: int = Field(default=0, ge=0)
    pieces: int = Field(default=0, ge=0)


class ExpenseCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    amount: float = Field(gt=0)
    category: str = "General"
    member: str = "bhai-1"


class AssistantRequest(BaseModel):
    message: str = Field(min_length=2, max_length=2000)


class AssistantResponse(BaseModel):
    answer: str
    mode: str


class DashboardResponse(BaseModel):
    revenue: float
    units_sold: int
    purchase_cost: float
    expenses: float
    gross_profit: float
    net_profit: float
    stock_units: int
    stock_value: float
    low_stock_count: int
    products_count: int
    online_sales: float
    wholesale_sales: float
