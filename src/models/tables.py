from datetime import datetime

from pydantic import EmailStr
from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[EmailStr] = mapped_column(String, nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String(150))
    last_name: Mapped[str] = mapped_column(String(150))
    posts: Mapped[list['Post']] = relationship(back_populates='user', cascade='all, delete-orphan')
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_administrator: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    last_entrance: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class Post(Base):
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(250), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='posts')
    image_path: Mapped[str] = mapped_column(String, nullable=True)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
