# coding: utf-8

import jwt
import hashlib
import datetime
import json
import base64
import dateutil.parser

from functools import wraps

from fastapi import status

from sqlalchemy.future import select
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.sqltypes import DateTime

from settings import LOCAL_SALT, SERVER_SECRET
from response_models import Error40xResponse

from models.session import get_session
from models.models import Users


def password_hash(password, salt):
    return hashlib.sha512(password.encode("utf-8") + salt.encode("utf-8") + LOCAL_SALT.encode("utf-8")).hexdigest()


async def check_token(token):
    try:
        token_info = jwt.decode(token, SERVER_SECRET, algorithms=['HS256'])
    except Exception as e:
        # logger.error('check_token, Decode auth token failed: {}'.format(e))
        return status.HTTP_401_UNAUTHORIZED, 'wrong token type', None
    else:
        user_info = None
        async with get_session() as s:
            user_info = await s.execute(select(Users).filter(Users.id == token_info['user_id']))
            user_info = user_info.scalars().first()
        if user_info:
            if user_info.password == token_info['password'] and \
                    token_info['expiration_time'] >= datetime.datetime.now().timestamp():
                return status.HTTP_200_OK, 'user authenticated', user_info
            else:
                return status.HTTP_401_UNAUTHORIZED, 'token expired', None
        else:
            return status.HTTP_401_UNAUTHORIZED, 'no user', None

def check_auth(func):
    @wraps(func)
    async def wrapper(**kwargs):
        header = kwargs.get('authorization')
        if not header:
            kwargs['response'].status_code = status.HTTP_401_UNAUTHORIZED
            return Error40xResponse.parse_obj({'reason': 'no token'})
        try:
            user_type, token = header.split(' ')
            code, response, user_info = await check_token(token=token)
        except Exception as e:
            print(e)
            kwargs['response'].status_code = status.HTTP_401_UNAUTHORIZED
            return Error40xResponse.parse_obj({'reason': 'wrong token type'})
        else:
            if code != status.HTTP_200_OK:
                kwargs['response'].status_code = code
                return Error40xResponse.parse_obj({'reason': response})
            else:
                kwargs['user_info'] = user_info
                return await func(**kwargs)
    return wrapper


def accept_user_type(user_type):
    def decorator(func):
        @wraps(func)
        async def wrapper(**kwargs):
            if kwargs.get('user_info') and kwargs['user_info'].type in user_type:
                return await func(**kwargs)
            else:
                kwargs['response'].status_code = status.HTTP_406_NOT_ACCEPTABLE
                return Error40xResponse.parse_obj({'reason': 'wrong user_type'})
        return wrapper
    return decorator


async def create_update_record(session, db_model, fields, request_model, user, editable=False):
    if request_model.id:
        r = (await session.execute(
            select(db_model)
            .filter(db_model.id == request_model.id)
        ))
        if editable:
            if user and "user_id" in db_model.__dict__ and  r.user_id != user.id:
                return r
            for j in fields:
                if isinstance(db_model.__dict__[j].__getattr__("type"), DateTime) and \
                        request_model.__dict__[j] is not None:
                    r.__setattr__(j, dateutil.parser.parse(request_model.__dict__[j]))
                else:
                    if request_model.__dict__[j] != -1:
                        r.__setattr__(j, request_model.__dict__[j])
                    else:
                        r.__setattr__(j, None)
            await session.flush()

    else:
        db_dict = {}
        for i in db_model.__dict__:
            if i != "id" and \
                    isinstance(db_model.__dict__[i], InstrumentedAttribute) and \
                    i in request_model.__dict__.keys() and \
                    (db_model.__dict__[i].__getattr__("nullable") or request_model.__dict__[i] is not None):
                if isinstance(db_model.__dict__[i].__getattr__("type"), DateTime):
                    db_dict[i] = dateutil.parser.parse(request_model.__dict__[i]) \
                        if request_model.__dict__[i] is not None and request_model.__dict__[i] != -1 else None
                else:
                    db_dict[i] = request_model.__dict__[i] \
                        if request_model.__dict__[i] is not None and request_model.__dict__[i] != -1 else None
        if "user_id" in db_model.__dict__.keys():
            db_dict["user_id"] = user.id
        r = db_model(**db_dict)
        session.add(r)
        await session.flush()

    return r
