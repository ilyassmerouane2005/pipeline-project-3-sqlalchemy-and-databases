import os
import polars as pl
from src.extractor import load_watermark, get_new_rows, update_watermark, save_watermark, WATERMARK_PATH


def clean_customers(data: pl.DataFrame) -> pl.DataFrame:
    clean_df = data.select(
        'customer_id',
        pl.col('name').str.strip_chars().str.to_lowercase(),
        pl.col('email').str.strip_chars().str.to_lowercase(),
        pl.col('country').str.strip_chars().str.to_lowercase(),
        'created_at',
        'updated_at',
    )
    return clean_df


def clean_orders(data: pl.DataFrame) -> pl.DataFrame:
    clean_df = (
        data
        .filter(pl.col('total_amount') > 0)
        .select(
            'order_id',
            'customer_id',
            'order_date',
            'total_amount',
            pl.col('status').str.strip_chars().str.to_lowercase(),
            'updated_at',
        )
    )
    return clean_df


def run(engine=None, watermark_path=WATERMARK_PATH, output_dir='data/clean'):
    watermark = load_watermark(watermark_path)
    os.makedirs(output_dir, exist_ok=True)

    df_customers = get_new_rows('customers', watermark, engine)
    df_orders = get_new_rows('orders', watermark, engine)

    if not df_customers.is_empty():
        clean_customers(df_customers).write_parquet(f'{output_dir}/customers.parquet')
        update_watermark('customers', df_customers, watermark)
    else:
        print('no new rows for customers table')

    if not df_orders.is_empty():
        clean_orders(df_orders).write_parquet(f'{output_dir}/orders.parquet')
        update_watermark('orders', df_orders, watermark)
    else:
        print('no new rows for orders table')

    save_watermark(watermark, watermark_path)


if __name__ == '__main__':
    run()