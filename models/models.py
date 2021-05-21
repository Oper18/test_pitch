# config: utf-8

import datetime

from sqlalchemy import Column, DateTime, String, ForeignKey, Float, Boolean, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import expression

from .base import Base, BaseModel


class Users(Base, BaseModel):
    __tablename__ = "users"

    id = Column(postgresql.INTEGER, primary_key=True, autoincrement=True)
    username = Column(String(length=64), nullable=False, unique=True)
    salt = Column(String(length=32), nullable=False)
    password = Column(String(length=1024), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    __mapper_args__ = {"eager_defaults": True}


class Subject(Base, BaseModel):
    __tablename__ = "subjects"

    id = Column(postgresql.INTEGER, primary_key=True, autoincrement=True)
    name = Column(String(length=1024), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    __mapper_args__ = {"eager_defaults": True}


class City(Base, BaseModel):
    __tablename__ = "cities"

    id = Column(postgresql.INTEGER, primary_key=True, autoincrement=True)
    name = Column(String(length=1024), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    __mapper_args__ = {"eager_defaults": True}


class Event(Base, BaseModel):
    __tablename__ = "events"

    id = Column(postgresql.INTEGER, primary_key=True, autoincrement=True)
    user_id = Column(postgresql.INTEGER, ForeignKey("cities.id", ondelete="CASCADE"),
                  nullable=False)
    name = Column(String(length=1024), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    city = Column(postgresql.INTEGER, ForeignKey("cities.id", ondelete="CASCADE"),
                  nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    __mapper_args__ = {"eager_defaults": True}


class EventSubject(Base, BaseModel):
    __tablename__ = "events_subjects"

    id = Column(postgresql.INTEGER, primary_key=True, autoincrement=True)
    event = Column(postgresql.INTEGER, ForeignKey("events.id", ondelete="CASCADE"),
                  nullable=False)
    subject = Column(postgresql.INTEGER, ForeignKey("subjects.id", ondelete="CASCADE"),
                  nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class UserFilter(Base, BaseModel):
    __tablename__ = "user_filters"

    id = Column(postgresql.INTEGER, primary_key=True, autoincrement=True)
    user_id = Column(postgresql.INTEGER, ForeignKey("cities.id", ondelete="CASCADE"),
                     nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    city = Column(postgresql.INTEGER, ForeignKey("cities.id", ondelete="CASCADE"),
                  nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    __mapper_args__ = {"eager_defaults": True}


class FilterSubject(Base, BaseModel):
    __tablename__ = "filters_subjects"

    id = Column(postgresql.INTEGER, primary_key=True, autoincrement=True)
    filter = Column(postgresql.INTEGER, ForeignKey("user_filters.id", ondelete="CASCADE"),
                   nullable=False)
    subject = Column(postgresql.INTEGER, ForeignKey("subjects.id", ondelete="CASCADE"),
                     nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
