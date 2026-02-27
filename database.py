from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

def run_query(query: str):
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return result.mappings().all()