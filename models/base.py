# coding: utf-8

import datetime

from sqlalchemy.ext.declarative import declarative_base
from enum import Enum


Base = declarative_base()


class BaseModel:

    def as_dict(self):
        res = {}
        for c in self.__table__.columns:
            if c.name in ["created_at", "updated_at"]:
                continue
            if isinstance(getattr(self, c.name), datetime.datetime):
                res[c.name] = getattr(self, c.name).isoformat()
            else:
                res[c.name] = getattr(self, c.name)
        return res
