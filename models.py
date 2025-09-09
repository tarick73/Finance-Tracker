from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, REAL
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    surname = Column(String(50))
    password = Column(String(50))
    email = Column(String(120), unique=True)

    def __repr__(self):
        return f'<User {self.name!r}>'


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    owner = Column(Integer)


class Transaction(Base):
    __tablename__ = 'transaction'
    id = Column(Integer, primary_key=True)
    description = Column(String(100))
    category = Column(ForeignKey('category.id', ondelete='CASCADE'))
    date = Column(Integer)
    owner = Column(ForeignKey('user.id', ondelete='CASCADE'))
    type = Column(Integer)
    amount = Column(Integer)
