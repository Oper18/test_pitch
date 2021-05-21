# coding: utf-8

import os

from contextlib import asynccontextmanager

from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from settings import BASEDIR

class _RoutingSession(AsyncSession):
    """This class """

    engine_pool = {}

    def __init__(self, **kwargs):
        bind = self.setup_bind(kwargs)
        super().__init__(bind=bind)

    def setup_bind(self, kwargs):
        return create_async_engine(
            'sqlite+aiosqlite:///{}'.format(os.path.join(BASEDIR, 'db.sqlite3')),
            echo=True)


_Session = sessionmaker(class_=_RoutingSession)

@asynccontextmanager
async def get_session():
    session = None
    try:
        session = _Session()
        yield session
    finally:
        if session is not None:
            await session.close()
