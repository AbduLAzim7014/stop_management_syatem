# Smart Shop AI

Wholesale and online trader shop management backend.

## What it tracks

- Products, SKU, stock units, selling price, and reorder level.
- Purchases: quantity, buying cost, and automatic stock increase.
- Sales: online or wholesale channel, customer name, quantity, revenue, and automatic stock decrease.
- Expenses and net profit.
- Dashboard totals for revenue, units sold, stock, gross profit, net profit, online sales, wholesale sales, and low-stock products.
- AI assistant that works in demo mode without an API key and supports an OpenAI-compatible provider.

## Run on Windows

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -e ".[dev]"
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the usable API screen.

Typical flow: create a product, record a purchase, record an online/wholesale sale, add expenses, then open `/api/dashboard`.

Set `AI_PROVIDER=openai` and `AI_API_KEY` in `.env` to enable real AI responses. Keep the key only in `.env`.
