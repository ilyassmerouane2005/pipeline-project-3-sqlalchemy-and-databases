from datetime import datetime
import polars as pl
from src.cleaner import clean_customers, clean_orders

TS = datetime(2026, 11, 6, 12, 0, 0)


# ---------- helpers ----------
def make_customers(rows):
    """rows: list of (name, email, country) tuples -> raw customers DataFrame."""
    return pl.DataFrame({

        'customer_id': list(range(1, len(rows) + 1)),
        'name': [r[0] for r in rows],
        'email': [r[1] for r in rows],
        'country': [r[2] for r in rows],
        'created_at': [TS] * len(rows),
        'updated_at': [TS] * len(rows),
    },
        schema_overrides={
            'name': pl.String,
            'email': pl.String,
            'country': pl.String,
    },
)


def make_orders(rows):
    """rows: list of (total_amount, status) tuples -> raw orders DataFrame."""
    return pl.DataFrame({
        'order_id': list(range(1, len(rows) + 1)),
        'customer_id': [1] * len(rows),
        'order_date': [TS] * len(rows),
        'total_amount': [r[0] for r in rows],
        'status': [r[1] for r in rows],
        'updated_at': [TS] * len(rows),
    },
        schema_overrides={
            'total_amount': pl.Float64,
            'status': pl.String,
    },
)

CUSTOMER_COLUMNS = ['customer_id', 'name', 'email', 'country', 'created_at', 'updated_at']
ORDER_COLUMNS = ['order_id', 'customer_id', 'order_date', 'total_amount', 'status', 'updated_at']

def test_clean_customers_strips_and_lowercases():
    df = make_customers([("  Youssef BENALI ", " Youssef@Example.COM ", " Morocco ")])
    result = clean_customers(df)
    assert result['name'][0] == 'youssef benali'
    assert result['email'][0] == 'youssef@example.com'
    assert result['country'][0] == 'morocco'

def test_clean_customers_keeps_expected_columns():
    df = make_customers([("A", "a@x.com", "France")])
    assert clean_customers(df).columns == CUSTOMER_COLUMNS

def test_clean_customers_null_country_stays_null():
    df = make_customers([("A", "a@x.com", None)])
    result = clean_customers(df)
    assert result['country'][0] is None

def test_clean_customers_keeps_all_rows():
    df = make_customers([("A", "a@x.com", "France"), ("B", "b@x.com", "Spain")])
    assert clean_customers(df).height == 2

def test_clean_customers_empty_dataframe():
    empty = make_customers([("A", "a@x.com", "France")]).clear()
    result = clean_customers(empty)
    assert result.is_empty()
    assert result.columns == CUSTOMER_COLUMNS

def test_clean_orders_removes_zero_and_negative_amounts():
    df = make_orders([(100.0, "delivered"), (0.0, "delivered"), (-5.0, "delivered")])
    result = clean_orders(df)
    assert result.height == 1
    assert result['total_amount'][0] == 100.0

def test_clean_orders_strips_and_lowercases_status():
    df = make_orders([(50.0, "  DELIVERED ")])
    assert clean_orders(df)['status'][0] == 'delivered'

def test_clean_orders_keeps_expected_columns():
    df = make_orders([(50.0, "shipped")])
    assert clean_orders(df).columns == ORDER_COLUMNS

def test_clean_orders_empty_dataframe():
    empty = make_orders([(50.0, "shipped")]).clear()
    result = clean_orders(empty)
    assert result.is_empty()
    assert result.columns == ORDER_COLUMNS