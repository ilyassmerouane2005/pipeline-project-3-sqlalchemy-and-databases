"""
we write this script to extract the rows that have not been treated yet and update the watermark.json with 
the max of updated_at for each table in our database 
"""
from sqlalchemy import create_engine , MetaData , select , Table
from datetime import datetime
import polars as pl

DB_URL = 'sqlite:///data/database/operational.db'
WATERMARK_PATH = 'data/database/watermark.json'

default_engine = create_engine(DB_URL)
forme = '%Y-%m-%d %H:%M:%S'

import json
def load_watermark(path : str = WATERMARK_PATH) -> dict:
    with open(path) as f:
        return json.load(f)

def get_new_rows (name : str , watermark : dict , engine = None):
    engine = engine or default_engine
    table = Table(name , MetaData() , autoload_with=engine)
    last_updated_at = datetime.strptime(watermark[name]['updated_at'] , forme)
    query = select(table).where(table.c.updated_at > last_updated_at)
    with engine.connect() as conn :
        data = pl.read_database(query , conn)
    return data

def update_watermark (name : str , df : pl.DataFrame , watermark : dict):
    if not df.is_empty():
        max_watermark = df['updated_at'].max()
        watermark[name]['updated_at'] = max_watermark.strftime(forme)

def save_watermark(watermark: dict , path : str = WATERMARK_PATH) -> None:
    with open(path, 'w') as file:
        json.dump(watermark, file, indent=4)