# coding: utf-8

import datetime
import jwt
import dateutil.parser
import uuid

from typing import Optional, List, Any

from fastapi import APIRouter, status, Response, Header

from sqlalchemy.future import select

from response_models import Error40xResponse

from .request_models import Auth, Refresh, Register
from .response_models import AuthResponse, AccountInfo, RegisterResponse

from models.session import get_session
from models.models import Users

from base_obj import password_hash, check_token, check_auth
from settings import ACCESS_TOKEN_LIFETIME, REFRESH_TOKEN_LIFETIME, SERVER_SECRET


router = APIRouter(
    prefix="/v1/auth",
    tags=["auth"]
)


@router.post(
    "",
    responses={
        200: {
            "model": AuthResponse,
        },
        401: {
            "model": Error40xResponse,
            "description": "wrong auth token",
        },
    }
)
async def auth_method(
        auth: Auth,
        response: Response,
        status_code: Optional[Any] = status.HTTP_200_OK,
) -> dict:
    async with get_session() as s:
        user = await s.execute(select(Users).filter(Users.username == auth.username))
        user = user.scalars().first()  #type: Users
        if not user:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return Error40xResponse.parse_obj({"reason": "wrong credentials"})
        if user and auth.password and user.password == password_hash(password=auth.password, salt=user.salt):
            access_token_exp_date = datetime.datetime.now().timestamp() + ACCESS_TOKEN_LIFETIME
            refresh_token_exp_date = datetime.datetime.now().timestamp() + REFRESH_TOKEN_LIFETIME
            access_token = jwt.encode(
                {
                    'user_id': user.id,
                    'username': user.username,
                    'password': user.password,
                    'expiration_time': access_token_exp_date,
                },
                SERVER_SECRET,
                algorithm='HS256'
            )
            refresh_token = jwt.encode(
                {
                    'user_id': user.id,
                    'username': user.username,
                    'password': user.password,
                    'expiration_time': refresh_token_exp_date,
                },
                SERVER_SECRET,
                algorithm='HS256'
            )
            return AuthResponse.parse_obj(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            )

    response.status_code = status.HTTP_401_UNAUTHORIZED
    return Error40xResponse.parse_obj({'reason': 'wrong username or password'})


@router.post(
    "/refresh",
    responses={
        200: {
            "model": AuthResponse,
        },
        401: {
            "model": Error40xResponse,
            "description": "wrong auth token",
        },
    }
)
async def auth_refresh_method(
        refresh: Refresh,
        response: Response,
        status_code: Optional[Any] = status.HTTP_200_OK,
) -> dict:
    code, response, user = await check_token(refresh.refresh_token)
    if code == status.HTTP_200_OK:
        access_token_exp_date = datetime.datetime.now().timestamp() + ACCESS_TOKEN_LIFETIME
        refresh_token_exp_date = datetime.datetime.now().timestamp() + REFRESH_TOKEN_LIFETIME
        access_token = jwt.encode(
            {
                'user_id': user.id,
                'username': user.username,
                'password': user.password,
                'expiration_time': access_token_exp_date,
            },
            SERVER_SECRET,
            algorithm='HS256'
        )
        refresh_token = jwt.encode(
            {
                'user_id': user.id,
                'username': user.username,
                'password': user.password,
                'expiration_time': refresh_token_exp_date,
            },
            SERVER_SECRET,
            algorithm='HS256'
        )
        return AuthResponse.parse_obj({'access_token': access_token, 'refresh_token': refresh_token})

    response.status_code = status.HTTP_401_UNAUTHORIZED
    return Error40xResponse.parse_obj({'reason': 'wrong refresh token'})


@router.get(
    "/account/info",
    responses={
        200: {
            "model": AccountInfo,
            "decription": "full account information",
        },
        401: {
            "model": Error40xResponse,
            "description": "wrong auth token",
        },
    }
)
@check_auth
async def get_user_info(
        response: Response,
        authorization: Optional[str] = Header(None),
        status_code=status.HTTP_200_OK,
        user_info=None,
        etag_request: Optional[str] = None,
) -> dict:
    user_info = user_info.as_dict()
    user_info.pop("salt")
    user_info.pop("password")
    return AccountInfo.parse_obj(user_info)


@router.post(
    "/create",
    responses={
        200: {
            "model": RegisterResponse,
        },
        401: {
            "model": Error40xResponse,
            "description": "wrong auth token",
        },
        406: {
            "model": Error40xResponse,
            "description": "method not accept for this user type",
        },
    }
)
async def register_user(
        reg: Register,
        response: Response,
        authorization: Optional[str] = Header(None),
        status_code: Optional[Any] = status.HTTP_200_OK,
) -> dict:
    salt = uuid.uuid4().hex
    async with get_session() as s:
        user = Users(
            username=reg.username,
            salt=salt,
            password=password_hash(
                password=reg.password,
                salt=salt
            ),
        )
        s.add(user)
        await s.commit()
    return RegisterResponse.parse_obj(
        {"username": reg.username, "password": reg.password}
    )
