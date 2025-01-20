from pathlib import Path

CATS = [
    "delete",
    "baby",
    "books",
    "car",
    "cash",
    "clothing",
    "date",
    "daycare",
    "amazon",
    "groceries",
    "health",
    "home",
    "income",
    "KDP",
    "mistake",
    "mitzvot/gifts",
    "recreation/entertainment",
    "rent",
    "restaurant",
    "transport",
    "transportation",
    "unknown",
    "utilities",
]

COLS = ["Date", "Description", "Debit", "Credit", "Category"]

BASE_PATH = Path("/Users/anaavda/Desktop/SubDesktop/CodeProjects/accountant/data")

OUT_PATH = (
    "/Users/anaavda/Desktop/SubDesktop/CodeProjects/accountant/data/out/{month}.csv"
)


CAT_SAVE_PATH = Path(
    "/Users/anaavda/Desktop/SubDesktop/CodeProjects/accountant/data/cat_store/cat_store.json"
)

AMZ_ORDERS_PATH = "/Users/anaavda/Desktop/SubDesktop/CodeProjects/accountant/data/amz/Your Orders/Retail.OrderHistory.1/Retail.OrderHistory.1.csv"
