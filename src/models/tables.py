from datetime import datetime

from pydantic import EmailStr
from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey, Date, or_, and_
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
    profile: Mapped['Profile'] = relationship(back_populates='user', cascade='all, delete-orphan')
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_administrator: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    last_entrance: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    followers: Mapped[list['Friend']] = relationship(back_populates='follower_user',
                                                     foreign_keys='Friend.follower_user_id')
    following: Mapped[list['Friend']] = relationship(back_populates='following_user',
                                                     foreign_keys='Friend.following_user_id')


class Friend(Base):
    __tablename__ = 'friend'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    follower_user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    follower_user: Mapped['User'] = relationship(back_populates='followers', foreign_keys=[follower_user_id])
    following_user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    following_user: Mapped['User'] = relationship(back_populates='following', foreign_keys=[following_user_id])
    friends: Mapped[bool] = mapped_column(Boolean, default=False)


class Profile(Base):
    __tablename__ = 'profile'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='profile')
    date_of_birth: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    photography: Mapped[str] = mapped_column(String, nullable=True)
    city_of_birth: Mapped[str] = mapped_column(String(150), nullable=True)
    city_of_residence: Mapped[str] = mapped_column(String(150), nullable=True)
    family_status: Mapped[str] = mapped_column(String(150), nullable=True)
    additional_information: Mapped[str] = mapped_column(String, nullable=True)


class Post(Base):
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(250), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='posts')
    image_path: Mapped[str] = mapped_column(String, nullable=True)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())


class Chat(Base):
    __tablename__ = 'chat'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_chat_1_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    user_chat_2_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    messages: Mapped[list['Messages']] = relationship('Messages', back_populates="chat")


class Messages(Base):
    __tablename__ = 'messages'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    recipient_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    chat_id: Mapped[int] = mapped_column(Integer, ForeignKey('chat.id'))
    chat: Mapped['Chat'] = relationship('Chat', back_populates="messages")
    message: Mapped[str] = mapped_column(String(150), nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
