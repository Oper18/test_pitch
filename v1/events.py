# coding: utf-8

import datetime
import jwt
import dateutil.parser
import uuid

from typing import Optional, List, Any

from fastapi import APIRouter, status, Response, Header, Request, WebSocket

from pydantic import BaseModel

from sqlalchemy.future import select

from response_models import Error40xResponse

from .request_models import EventRequest, FilterRequest
from .response_models import EventResponse, UserFilterResponse

from models.session import get_session
from models.models import Users, Event, City, Subject, EventSubject, UserFilter, FilterSubject

from base_obj import check_auth, create_update_record


router = APIRouter(
    prefix="/v1/events",
    tags=["events"]
)


@router.post(
    "/create",
    responses={
        200: {
            "model": EventResponse,
        },
        401: {
            "model": Error40xResponse,
            "description": "wrong auth token",
        },
    }
)
@check_auth
async def create_event(
        event: EventRequest,
        response: Response,
        request: Request,
        authorization: Optional[str] = Header(None),
        status_code: Optional[Any] = status.HTTP_200_OK,
        user_info: Optional[Any] = None,
) -> dict:
    async with get_session() as s:
        city = None
        if event.city:
            city = await create_update_record(
                session=s,
                db_model=City,
                fields=["name"],
                request_model=event.city,
                user=user_info,
            )
            if not city:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return Error40xResponse.parse_obj({'reason': 'wrong city id'})
        res_subjects = []
        if event.subjects:
            for subject in event.subjects:
                res_subjects.append(
                    await create_update_record(
                        session=s,
                        db_model=Subject,
                        fields=["name"],
                        request_model=subject,
                        user=user_info,
                    )
                )
        event_res = await create_update_record(
            session=s,
            db_model=Event,
            fields=["id", "name", "start_time", "end_time", "city"],
            request_model=type(
                "EventReq",
                (BaseModel,),
                {
                    "id": event.id if event.id else 0,
                    "name": event.name if event.name else -1,
                    "start_time": event.start_time if event.start_time else -1,
                    "end_time": event.end_time if event.end_time else -1,
                    "city": city.id if city else -1,
                }
            )(),
            editable=True,
            user=user_info,
        )
        if res_subjects:
            exist_recs = (await s.execute(
                select(EventSubject.subject)
                .filter(EventSubject.event == event_res.id))
            ).fetchall()
            add_recs = []
            for subject in res_subjects:
                if subject.id not in exist_recs:
                    add_recs.append(
                        EventSubject(
                            event=event_res.id,
                            subject=subject.id
                        )
                    )
            s.add_all(add_recs)
            await s.flush()

        res = event_res.as_dict()
        res["city"] = city.name if city else None
        await s.commit()
        return EventResponse.parse_obj(res)


@router.get(
    "",
    responses={
        200: {
            "model": List[EventResponse],
            "decription": "full account information",
        },
        401: {
            "model": Error40xResponse,
            "description": "wrong auth token",
        },
    }
)
@check_auth
async def get_events(
        response: Response,
        authorization: Optional[str] = Header(None),
        status_code=status.HTTP_200_OK,
        user_info=None,
        city: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        subjects: Optional[str] = None,
        limit: Optional[int] = 20,
        offset: Optional[int] = 0,
) -> List[dict]:
    async with get_session() as s:
        subjects_qs = select(Subject, EventSubject).join(EventSubject, EventSubject.subject == Subject.id)
        if subjects:
            subjects_list = []
            for i in subjects.split(','):
                try:
                    subjects_list.append(int(i))
                except:
                    pass
            subjects_qs = subjects_qs.filter(Subject.id.in_(subjects_list))
        subjects_qs = (await s.execute(subjects_qs)).fetchall()
        if subjects:
            events = select(Event, City, EventSubject).join(City, City.id == Event.city).join(EventSubject, (EventSubject.event == Event.id) & (EventSubject.subject.in_([i.id for i, j in subjects_qs])))
        else:
            events = select(Event, City, EventSubject).join(City, City.id == Event.city).join(EventSubject, EventSubject.event == Event.id)
        if city:
            events.filter(City.id == city)
        if start_time:
            events.filter(Event.start_time == dateutil.parser.parse(start_time))
        if end_time:
            events.filter(Event.end_time == dateutil.parser.parse(end_time))
        events = (await s.execute(events.limit(limit).offset(offset))).fetchall()
        res = []
        for e, c, esub in events:
            e = e.as_dict()
            e["city"] = c.name if c else None
            e["subjects"] = [{"id": subj.id, "name": subj.name} for subj, es in subjects_qs if e["id"] == es.event]
            res.append(e)
        return [EventResponse.parse_obj(e) for e in res]


@router.post(
    "/filters/save",
    responses={
        200: {
            "model": UserFilterResponse,
        },
        401: {
            "model": Error40xResponse,
            "description": "wrong auth token",
        },
    }
)
@check_auth
async def create_event(
        filters: FilterRequest,
        response: Response,
        request: Request,
        authorization: Optional[str] = Header(None),
        status_code: Optional[Any] = status.HTTP_200_OK,
        user_info: Optional[Any] = None,
) -> dict:
    async with get_session() as s:
        filter = await create_update_record(
            session=s,
            db_model=UserFilter,
            fields=["start_time", "end_time", "city"],
            request_model=filters,
            user=user_info,
        )
        filter_subjects = []
        for i in filters.subjects:
            filter_subjects.append(
                FilterSubject(
                    filter=filter.id,
                    subject=i,
                )
            )
        s.add_all(filter_subjects)
        await s.flush()
        subjects = (await s.execute(
            select(Subject)
            .filter(Subject.id.in_(filters.subjects))
        )).scalars().all()
        res = {
            "id": filter.id,
            "start_time": filter.start_time,
            "end_time": filter.end_time,
            "city": filter.city,
            "subjects": [{"id": i.id, "name": i.name} for i in subjects],
        }
        await s.commit()
        return UserFilterResponse.parse_obj(res)


@router.get(
    "/filters",
    responses={
        200: {
            "model": List[UserFilterResponse],
            "decription": "full account information",
        },
        401: {
            "model": Error40xResponse,
            "description": "wrong auth token",
        },
    }
)
@check_auth
async def get_events(
        response: Response,
        authorization: Optional[str] = Header(None),
        status_code=status.HTTP_200_OK,
        user_info=None,
        limit: Optional[int] = 20,
        offset: Optional[int] = 0,
) -> List[dict]:
    async with get_session() as s:
        filters = (await s.execute(
            select(UserFilter)
            .filter(UserFilter.user_id == user_info.id)
        )).scalars().all()
        res = []
        for f in filters:
            subjects = (await s.execute(
                select(Subject, FilterSubject)
                .join(FilterSubject, Subject.id == FilterSubject.subject)
                .filter(FilterSubject.filter == f.id)
            )).scalars().all()
            res.append(
                {
                    "id": f.id,
                    "start_time": f.start_time,
                    "end_time": f.end_time,
                    "city": f.city,
                    "subjects": [{"id": i.id, "name": i.name} for i in subjects],
                }
            )
        return [UserFilterResponse.parse_obj(r) for r in res]
