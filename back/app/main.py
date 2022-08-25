from dataclasses import asdict
from fastapi import FastAPI
from typing import Optional
import uvicorn

from app.database.conn import db ,Base
from app.common.config import conf
from app.router import index,auth
from app.database import schema




def create_app():
    c= conf()
    app = FastAPI()
    conf_dict = asdict(c)
    db.init_app(app,**conf_dict)
    # database initialize
    Base.metadata.create_all(bind=db.engine)

    # redis intialize

    # middle ware

    # router
    app.include_router(index.router)
    app.include_router(auth.router)
    return app

app = create_app()


if __name__=="__main__":
    uvicorn.run("main:app",host="0.0.0.0",port=8000, reload=True)