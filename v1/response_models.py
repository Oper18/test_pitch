# coding: utf-8

import datetime

from typing import Optional, List

from pydantic import BaseModel


class AuthResponse(BaseModel):
    access_token: Optional[str]
    refresh_token: Optional[str]


class AccountInfo(BaseModel):
    id: int
    type: str
    username: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


class RegisterResponse(BaseModel):
    username: str
    password: str


class SubjectResponse(BaseModel):
    id: int
    name: str


class EventResponse(BaseModel):
    id: int
    name: str
    start_time: Optional[str]
    end_time: Optional[str]
    city: Optional[str]
    subjects: Optional[List[SubjectResponse]]


class UserFilterResponse(BaseModel):
    id: Optional[int]
    start_time: Optional[str]
    end_time: Optional[str]
    city: Optional[int]
    subjects: Optional[List[SubjectResponse]]
