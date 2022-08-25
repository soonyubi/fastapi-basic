# 환경별 변수를 넣는 공간
# 운영서버도 있고, 개발서버도 있고, 스테이징 서버도 있고, 로컬서버오 있는데
# 그때마다 다른방법으로 설정파일을 넣는 것을 config.py 에서 수행한다. 

from dataclasses import dataclass, asdict
from os import path, environ

base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))

# @dataclasses라는 데코레이터를 사용한 이유는 나중에 dict객체로 추출하기 위해서 

@dataclass
class Config:
    """
        basic configuration
    """
    BASE_DIR = base_dir

    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True

# 로컬서버
@dataclass
class LocalConfig(Config):
    PROJ_RELOAD : bool = True
    DB_URL : str = "sqlite:///app/userlogin.db"
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]
    
# 운영서버
@dataclass
class ProdConfig(Config):
    PROJ_RELOAD : bool = False
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]

def conf():
    """
    환경 불러오기
    :return:
    """
    config = dict(prod=ProdConfig(), local=LocalConfig())
    return config.get(environ.get("API_ENV", "local"))