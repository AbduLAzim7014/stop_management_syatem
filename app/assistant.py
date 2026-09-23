import httpx
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import Expense, Product, Purchase, Sale


def business_snapshot(db: Session, member: str | None = None) -> dict[str, float | int]:
    sale_filter = Sale.member == member if member else True
    purchase_filter = Purchase.member == member if member else True
    expense_filter = Expense.member == member if member else True
    revenue = db.scalar(select(func.coalesce(func.sum(Sale.total), 0.0)).where(sale_filter)) or 0.0
    units_sold = db.scalar(select(func.coalesce(func.sum(Sale.quantity), 0)).where(sale_filter)) or 0
    purchase_cost = db.scalar(select(func.coalesce(func.sum(Purchase.total), 0.0)).where(purchase_filter)) or 0.0
    expenses = db.scalar(select(func.coalesce(func.sum(Expense.amount), 0.0)).where(expense_filter)) or 0.0
    online_sales = db.scalar(select(func.coalesce(func.sum(Sale.total), 0.0)).where(sale_filter, Sale.channel == "online")) or 0.0
    wholesale_sales = db.scalar(select(func.coalesce(func.sum(Sale.total), 0.0)).where(sale_filter, Sale.channel == "wholesale")) or 0.0
    products = db.scalars(select(Product)).all()
    return {
        "revenue": round(float(revenue), 2),
        "units_sold": int(units_sold),
        "purchase_cost": round(float(purchase_cost), 2),
        "expenses": round(float(expenses), 2),
        "gross_profit": round(float(revenue) - float(purchase_cost), 2),
        "net_profit": round(float(revenue) - float(purchase_cost) - float(expenses), 2),
        "stock_units": sum(product.stock for product in products),
        "stock_value": round(sum(product.stock * product.price for product in products), 2),
        "low_stock_count": sum(product.stock <= product.reorder_level for product in products),
        "products_count": len(products),
        "online_sales": round(float(online_sales), 2),
        "wholesale_sales": round(float(wholesale_sales), 2),
    }


async def answer_question(message: str, db: Session, settings: Settings) -> tuple[str, str]:
    snapshot = business_snapshot(db)
    if settings.ai_provider == "demo" or not settings.ai_api_key:
        answer = (
            f"Business report: total sale {snapshot['revenue']}, sold units {snapshot['units_sold']}, "
            f"stock units {snapshot['stock_units']}, net profit {snapshot['net_profit']}. "
            f"Online sale {snapshot['online_sales']} aur wholesale sale {snapshot['wholesale_sales']} hain. "
            f"{snapshot['low_stock_count']} products reorder karne ki zaroorat hai."
        )
        return answer, "demo"

    payload = {
        "model": settings.ai_model,
        "messages": [
            {"role": "system", "content": "You are a practical shop accountant. Answer in the user's language and never invent records."},
            {"role": "user", "content": f"Snapshot: {snapshot}\nQuestion: {message}"},
        ],
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {settings.ai_api_key}"}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(f"{settings.ai_base_url}/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"], "ai"
