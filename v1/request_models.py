# coding: utf-8

from typing import Optional, List
from pydantic import BaseModel


class Auth(BaseModel):
    username: str
    password: str = None
    test_link: str = None


class Refresh(BaseModel):
    refresh_token: str


class Register(BaseModel):
    username: str
    password: str


class CityRequest(BaseModel):
    id: Optional[int]
    name: Optional[str]


class SubjectRequest(BaseModel):
    id: Optional[int]
    name: Optional[str]


class EventRequest(BaseModel):
    id: Optional[int]
    name: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]
    city: Optional[CityRequest]
    subjects: Optional[List[SubjectRequest]]


class FilterRequest(BaseModel):
    id: Optional[int]
    start_time: Optional[str]
    end_time: Optional[str]
    city: Optional[int]
    subjects: Optional[List[int]]
