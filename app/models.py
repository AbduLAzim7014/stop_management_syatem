from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(80), default="General")
    wood_type: Mapped[str] = mapped_column(String(80), default="General")
    dimensions: Mapped[str | None] = mapped_column(String(80), nullable=True)
    pieces_per_bundle: Mapped[int] = mapped_column(Integer, default=350)
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    reorder_level: Mapped[int] = mapped_column(Integer, default=5)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    total: Mapped[float] = mapped_column(Float)
    customer_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    channel: Mapped[str] = mapped_column(String(30), default="online", index=True)
    member: Mapped[str] = mapped_column(String(30), default="bhai-1", index=True)
    sold_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_cost: Mapped[float] = mapped_column(Float)
    total: Mapped[float] = mapped_column(Float)
    member: Mapped[str] = mapped_column(String(30), default="bhai-1", index=True)
    purchased_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    amount: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String(80), default="General")
    member: Mapped[str] = mapped_column(String(30), default="bhai-1", index=True)
    spent_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
