from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import CheckConstraint, Engine, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Numeric


class Base(DeclarativeBase):
    """Any model that has unique ID"""

    id: Mapped[int] = mapped_column(primary_key=True)


class Nameable:
    """Any model that has name"""

    name: Mapped[str] = mapped_column(String(100), nullable=False)


class Publisher(Base, Nameable):
    """Publisher model"""

    __tablename__ = "publisher"

    books: Mapped[List['Book']] = relationship(
        back_populates = "publisher",
        cascade = "all, delete-orphan"
    )


class Shop(Base, Nameable):
    """Shop model"""

    __tablename__ = "shop"

    stocks: Mapped[List['Stock']] = relationship(
        back_populates = "shop",
        cascade = "all, delete-orphan"
    )


class Book(Base):
    """Book model"""

    __tablename__ = "book"

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    id_publisher: Mapped[int] = mapped_column(
        ForeignKey("publisher.id"),
        nullable=False
    )

    publisher: Mapped['Publisher'] = relationship(back_populates="books")
    stocks: Mapped[List['Stock']] = relationship(
        back_populates = "book",
        cascade = "all, delete-orphan"
    )


class Stock(Base):
    """Stock model"""

    __tablename__ = "stock"
    __table_args__ = (
        CheckConstraint("count >= 0"),
    )

    id_book: Mapped[int] = mapped_column(ForeignKey("book.id"), nullable=False)
    id_shop: Mapped[int] = mapped_column(ForeignKey("shop.id"), nullable=False)
    count: Mapped[int] = mapped_column(nullable=False, default=0)

    book: Mapped['Book'] = relationship(back_populates="stocks")
    shop: Mapped['Shop'] = relationship(back_populates="stocks")
    sales: Mapped[List['Sale']] = relationship(
        back_populates = "stock",
        cascade = "all, delete-orphan"
    )


class Sale(Base):
    """Book sale model"""

    __tablename__ = "sale"
    __table_args__ = (
        CheckConstraint("price >= 0"),
        CheckConstraint("count > 0"),
    )

    price: Mapped[Decimal] = mapped_column(Numeric[10, 2], nullable=False)
    date_sale: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    id_stock: Mapped[int] = mapped_column(
        ForeignKey("stock.id"),
        nullable=False
    )
    count: Mapped[int] = mapped_column(nullable=False, default=1)

    stock: Mapped['Stock'] = relationship(back_populates="sales")


models = {
    "publisher": Publisher,
    "shop": Shop,
    "book": Book,
    "stock": Stock,
    "sale": Sale
}


def create_tables(engine: Engine):
    """Creates all model tables"""
    Base.metadata.create_all(engine)

def drop_tables(engine: Engine):
    """Drops all model tables"""
    Base.metadata.drop_all(engine)