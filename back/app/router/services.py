from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi.logger import logger
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.common.constant import MAX_API_KEY, MAX_API_WHITELIST
from app.database.conn import db
from app.database.schema import Users, ApiKeys, ApiWhiteLists
from app import models as m
from app.errors import exceptions as ex
import string
import secrets
import json
import requests

from app.models import KakaoMsgBody, MessageOk

router = APIRouter(prefix='/services')


@router.get('')
async def get_all_services(request: Request):
    return dict(your_email=request.state.user.email)

@router.post('kakao/send')
async def send_kakao(request: Request, body: KakaoMsgBody):
    token = "49T43goZ6FJmOhJOmMDxTtoMKmD91QEQj7qnMKyDCinI2AAAAYMTFY5c"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/x-www-form-urlencoded"}
    body = dict(object_type="text", text="Koala Sample for FastAPI", link=dict(web_url="https://dingrr.com", mobile_url="https://dingrr.com"), button_title="지금 확인")
    data = {"template_object": json.dumps(body, ensure_ascii=False)}

    res = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", headers=headers, data=data)
    try:
        res.raise_for_status()
        if res.json()["result_code"] != 0:
            raise Exception("KAKAO SEND FAILED")
    except Exception as e:
        print(res.json())
        logger.warning(e)
        raise ex.KakaoSendFailureEx

    return MessageOk()