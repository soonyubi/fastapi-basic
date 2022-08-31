import base64
import hmac
import time
import typing
import re

import jwt
import sqlalchemy.exc

from jwt.exceptions import ExpiredSignatureError, DecodeError
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.common.constant import EXCEPT_PATH_LIST, EXCEPT_PATH_REGEX
from app.database.conn import db
from app.database.schema import Users
from app.errors import exceptions as ex

from app.common import config, constant
from app.errors.exceptions import APIException
from app.models import UserToken

from app.utils.date_utils import D
from app.utils.logger import api_logger
from app.utils.query_utils import to_dict

async def access_control(request: Request, call_next):
    request.state.req_time = D.datetime()
    request.state.start = time.time()
    request.state.inspect = None
    request.state.user = None
    ip = request.headers["x-forwarded-for"] if "x-forwarded-for" in request.headers.keys() else request.client.host
    request.state.ip = ip.split('.')[0] if ',' in ip else ip
    headers = request.headers
    cookies = request.cookies
    url = request.url.path
    if await url_pattern_check(url, EXCEPT_PATH_REGEX) or url in EXCEPT_PATH_LIST:
        response = await call_next(request)
        if url !="/": # root path 
            await api_logger(request=request, response= response)
        return response

    try : 
        if url.startswith("/api"): # api 요청일 경우 헤더로 토큰 검사
            if "authorization" in headers.keys():
                token_info = await token_decode(access_token = headers.get("authorization"))

                request.state.user = UserToken(**token_info)
            # 토큰 없음
            else :
                if "authorization" not in headers.keys():
                    raise ex.NotAuthorized()
        else : # 템플릿 렌더링일 경우 쿠키에서 토큰 검사     
            cookies["Authorization"] = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MTQsImVtYWlsIjoia29hbGFAZGluZ3JyLmNvbSIsIm5hbWUiOm51bGwsInBob25lX251bWJlciI6bnVsbCwicHJvZmlsZV9pbWciOm51bGwsInNuc190eXBlIjpudWxsfQ.4vgrFvxgH8odoXMvV70BBqyqXOFa2NDQtzYkGywhV48"

            if 'authorization' not in cookies.keys():
                raise ex.NotAuthorized()
            token_info = token_decode(access_token=cookies.get('authoriazation'))
            request.state.user = UserToken(**token_info)

        response = await call_next(request)
        await api_logger(request=request, response= response)
    except Exception as e :
        error = await exception_handler(e)
        error_dict = dict(status_code = error.status_code, content=error.detail, code = error.code)
        response = JSONResponse(status_code=error.status_code, content= error_dict)
    return response


async def url_pattern_check(path, pattern):
    result = re.match(pattern, path)
    if result:
        return True
    return False


async def token_decode(access_token):
    """
    :param access_token:
    :return:
    """
    try:
        access_token = access_token.replace("Bearer ", "")
        payload = jwt.decode(access_token, key=constant.JWT_SECRET, algorithms=[constant.JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise ex.TokenExpiredEx()
    except DecodeError:
        raise ex.TokenDecodeEx()
    return payload


async def exception_handler(error: Exception):
    print(error)
    if not isinstance(error, APIException):
        error = APIException(ex=error, detail=str(error))
    return error