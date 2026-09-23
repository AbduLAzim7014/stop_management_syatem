from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.assistant import answer_question, business_snapshot
from app.config import get_settings
from app.database import get_db
from app.models import Expense, Product, Purchase, Sale
from app.schemas import AssistantRequest, AssistantResponse, DashboardResponse, ExpenseCreate, ProductCreate, ProductRead, PurchaseCreate, SaleCreate

router = APIRouter()


def get_product(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "smart-shop-ai"}


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> Product:
    sku = payload.sku.strip() or "-".join(payload.name.upper().split())[:42]
    if db.scalar(select(Product).where(Product.sku == sku)):
        raise HTTPException(status_code=409, detail="SKU already exists")
    product = Product(**payload.model_dump(exclude={"sku"}), sku=sku)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/products", response_model=list[ProductRead])
def list_products(db: Session = Depends(get_db)) -> list[Product]:
    return list(db.scalars(select(Product).order_by(Product.name)).all())


@router.post("/purchases", status_code=status.HTTP_201_CREATED)
def record_purchase(payload: PurchaseCreate, db: Session = Depends(get_db)) -> dict:
    product = get_product(db, payload.product_id)
    total_pieces = payload.bundles * product.pieces_per_bundle + payload.pieces
    if total_pieces < 1:
        raise HTTPException(status_code=400, detail="Bundle ya pieces ki quantity bharein")
    purchase = Purchase(product_id=product.id, quantity=total_pieces, unit_cost=payload.unit_cost, member=payload.member, total=total_pieces * payload.unit_cost)
    product.stock += total_pieces
    db.add(purchase)
    db.commit()
    return {"message": "Purchase recorded", "purchase_id": purchase.id, "new_stock": product.stock}


@router.post("/sales", status_code=status.HTTP_201_CREATED)
def record_sale(payload: SaleCreate, db: Session = Depends(get_db)) -> dict:
    product = get_product(db, payload.product_id)
    total_pieces = payload.bundles * product.pieces_per_bundle + payload.pieces
    if total_pieces < 1:
        raise HTTPException(status_code=400, detail="Bundle ya pieces ki quantity bharein")
    if product.stock < total_pieces:
        raise HTTPException(status_code=400, detail=f"Insufficient stock. Available: {product.stock}")
    unit_price = payload.unit_price or product.price
    sale = Sale(product_id=product.id, quantity=total_pieces, total=total_pieces * unit_price, customer_name=payload.customer_name, channel=payload.channel, member=payload.member)
    product.stock -= total_pieces
    db.add(sale)
    db.commit()
    return {"message": "Sale recorded", "sale_id": sale.id, "new_stock": product.stock}


@router.post("/expenses", status_code=status.HTTP_201_CREATED)
def record_expense(payload: ExpenseCreate, db: Session = Depends(get_db)) -> dict:
    expense = Expense(**payload.model_dump())
    db.add(expense)
    db.commit()
    return {"message": "Expense recorded", "expense_id": expense.id}


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(member: str | None = None, db: Session = Depends(get_db)) -> dict:
    if member is None:
        return business_snapshot(db)
    return business_snapshot(db, member)


@router.get("/sales")
def list_sales(db: Session = Depends(get_db)) -> list[dict]:
    sales = db.scalars(select(Sale).order_by(Sale.sold_at.desc())).all()
    return [{"id": sale.id, "product_id": sale.product_id, "quantity": sale.quantity, "total": sale.total, "customer_name": sale.customer_name, "channel": sale.channel, "sold_at": sale.sold_at} for sale in sales]


@router.get("/reports/items")
def item_report(member: str = "bhai-1", db: Session = Depends(get_db)) -> list[dict]:
    products = db.scalars(select(Product).order_by(Product.name)).all()
    report = []
    for product in products:
        sold_qty = db.scalar(select(func.coalesce(func.sum(Sale.quantity), 0)).where(Sale.product_id == product.id, Sale.member == member)) or 0
        sale_total = db.scalar(select(func.coalesce(func.sum(Sale.total), 0.0)).where(Sale.product_id == product.id, Sale.member == member)) or 0.0
        bought_qty = db.scalar(select(func.coalesce(func.sum(Purchase.quantity), 0)).where(Purchase.product_id == product.id, Purchase.member == member)) or 0
        purchase_total = db.scalar(select(func.coalesce(func.sum(Purchase.total), 0.0)).where(Purchase.product_id == product.id, Purchase.member == member)) or 0.0
        average_cost = float(purchase_total) / int(bought_qty) if bought_qty else 0.0
        report.append({"name": product.name, "wood_type": product.wood_type, "sold_qty": int(sold_qty), "sale_total": round(float(sale_total), 2), "bought_qty": int(bought_qty), "purchase_total": round(float(purchase_total), 2), "profit": round(float(sale_total) - average_cost * int(sold_qty), 2)})
    return report


@router.get("/reports/monthly")
def monthly_report(member: str = "bhai-1", db: Session = Depends(get_db)) -> list[dict]:
    rows = db.execute(select(func.strftime("%Y-%m", Sale.sold_at).label("month"), func.sum(Sale.total).label("sale_total"), func.sum(Sale.quantity).label("sold_qty")).where(Sale.member == member).group_by("month").order_by("month")).all()
    return [{"month": row.month, "sale_total": round(float(row.sale_total or 0), 2), "sold_qty": int(row.sold_qty or 0)} for row in rows]


@router.post("/assistant", response_model=AssistantResponse)
async def assistant(payload: AssistantRequest, db: Session = Depends(get_db)) -> AssistantResponse:
    answer, mode = await answer_question(payload.message, db, get_settings())
    return AssistantResponse(answer=answer, mode=mode)
