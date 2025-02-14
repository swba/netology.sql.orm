import json

from environs import Env
from sqlalchemy import create_engine, Engine, select, ScalarResult
from sqlalchemy.orm import Session

from model import (
    drop_tables,
    create_tables,
    models,
    Book,
    Publisher,
    Sale,
    Stock
)


def get_engine() -> Engine:
    """Returns SQLAlchemy engine"""
    env = Env()
    env.read_env()

    db_host = env('DB_HOST')
    db_port = env('DB_PORT')
    db_name = env('DB_NAME')
    db_user = env('DB_USER')
    db_pass = env('DB_PASS')

    url = f"postgresql+psycopg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    return create_engine(url)

def setup(engine: Engine):
    """Sets up tables in the database"""
    drop_tables(engine)
    create_tables(engine)

def import_data(engine: Engine, filename: str):
    """Imports data from a file into the database"""
    with Session(engine) as session:
        with open(filename, encoding='UTF-8') as f:
            for row in json.load(f):
                try:
                    model = models[row.get('model')]
                    inst = model(id=row.get('pk'), **row.get('fields'))
                    session.add(inst)
                except Exception as e:
                    print(e)
                    pass
        session.commit()

def search_sales_by_publisher(session: Session, q: str) -> ScalarResult[Sale]:
    """Searches sales given publisher name or ID

    Args:
        session: SQLAlchemy session.
        q: Publisher name or ID. For publisher name, placeholders "%"
            and "_" can be used.

    """
    stmt = (
        select(Sale)
        .join(Sale.stock)
        .join(Stock.book)
        .join(Stock.shop)
        .join(Book.publisher)
    )
    if q.isnumeric():
        stmt = stmt.where(Publisher.id == int(q))
    else:
        stmt = stmt.where(Publisher.name.ilike(q))
    return session.scalars(stmt)
