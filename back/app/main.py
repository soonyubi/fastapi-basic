from dataclasses import asdict
from fastapi import FastAPI, Depends
from fastapi.security import APIKeyHeader
from typing import Optional
import uvicorn

from app.database.conn import db ,Base
from app.common.config import conf
from app.router import index,auth,users,services
from app.database import schema

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.common.constant import EXCEPT_PATH_LIST, EXCEPT_PATH_REGEX

from app.middleware.token_validator import access_control
from app.middleware.trusted_hosts import TrustedHostMiddleware


API_KEY_HEADER = APIKeyHeader(name='Authorization',auto_error=False)


def create_app():
    c= conf()
    app = FastAPI()
    conf_dict = asdict(c)
    db.init_app(app,**conf_dict)
    # database initialize
    Base.metadata.create_all(bind=db.engine)

    # redis intialize

    # middle ware
    app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch = access_control)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=conf().ALLOW_SITE,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=conf().TRUSTED_HOSTS, except_path=["/health"])    




    # router
    app.include_router(index.router)
    app.include_router(auth.router, tags=['Authentication'], prefix="/api")
    app.include_router(users.router, tags=['Users'], prefix='/api', dependencies=[Depends(API_KEY_HEADER)])
    app.include_router(services.router, tags=['Users'],prefix='/api')
    return app

app = create_app()


if __name__=="__main__":
    uvicorn.run("main:app",host="0.0.0.0",port=8000, reload=True)