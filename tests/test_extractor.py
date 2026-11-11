from datetime import datetime
import pytest
import polars as pl
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime

from src.extractor import get_new_rows, update_watermark, load_watermark, save_watermark

EPOCH = '1970-01-01 00:00:00'
D1, D2, D3 = datetime(2026, 1, 1, 10), datetime(2026, 2, 1, 10), datetime(2026, 3, 1, 10)


def make_watermark(customers=EPOCH, orders=EPOCH):
    return {'customers': {'updated_at': customers}, 'orders': {'updated_at': orders}}


@pytest.fixture
def engine(tmp_path):
    """Temporary SQLite db with 3 customers (updated on D1, D2, D3)."""
    eng = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    md = MetaData()
    customers = Table(
        'customers', md,
        Column('customer_id', Integer, primary_key=True),
        Column('name', String),
        Column('updated_at', DateTime),
    )
    md.create_all(eng)
    with eng.begin() as conn:
        conn.execute(customers.insert(), [
            dict(customer_id=i, name=f'c{i}', updated_at=d)
            for i, d in [(1, D1), (2, D2), (3, D3)]
        ])
    return eng


# which rows come back for a given watermark
@pytest.mark.parametrize("wm, expected", [
    (EPOCH,                 [1, 2, 3]),
    ('2026-01-15 00:00:00', [2, 3]),
    ('2026-02-01 10:00:00', [3]),      # a row equal to the watermark is excluded
    ('2026-03-01 10:00:00', []),
])
def test_get_new_rows(engine, wm, expected):
    df = get_new_rows('customers', make_watermark(customers=wm), engine)
    assert sorted(df['customer_id'].to_list()) == expected


def test_update_watermark_moves_to_max():
    wm = make_watermark()
    update_watermark('customers', pl.DataFrame({'updated_at': [D1, D3, D2]}), wm)
    assert wm['customers']['updated_at'] == '2026-03-01 10:00:00'
    assert wm['orders']['updated_at'] == EPOCH          # other table untouched


def test_update_watermark_ignores_empty():
    wm = make_watermark(customers='2026-01-01 10:00:00')
    empty = pl.DataFrame(schema={'updated_at': pl.Datetime})
    update_watermark('customers', empty, wm)
    assert wm['customers']['updated_at'] == '2026-01-01 10:00:00'


def test_second_extraction_returns_nothing(engine):
    wm = make_watermark()
    first = get_new_rows('customers', wm, engine)
    update_watermark('customers', first, wm)
    assert first.height == 3
    assert get_new_rows('customers', wm, engine).is_empty()


def test_save_then_load_round_trip(tmp_path):
    path = str(tmp_path / 'wm.json')
    wm = make_watermark(customers='2026-01-01 10:00:00')
    save_watermark(wm, path)
    assert load_watermark(path) == wm