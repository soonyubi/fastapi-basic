from operator import truediv
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    Enum,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import Session, relationship
from sqlalchemy.orm import reconstructor
from app.database.conn import db, Base

class BaseMixin:
    id = Column(Integer, primary_key=True, index=True) 
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    # created_at = Column(DateTime, nullable=True,)
    # updated_at = Column(DateTime, nullable=True,)
    def all_columns(self):
        return [c for c in self.__table__.columns if c.primary_key is False and c.name != "created_at"]

    def __hash__(self):
        return hash(self.id) 

    @classmethod
    def create(cls, session: Session, auto_commit=False, **kwargs):
        """
        테이블 데이터 적재 전용 함수
        :param session:
        :param auto_commit: 자동 커밋 여부
        :param kwargs: 적재 할 데이터
        :return:
        """
        obj = cls()
        for col in obj.all_columns():
            col_name = col.name
            if col_name in kwargs:
                setattr(obj, col_name, kwargs.get(col_name))
        session.add(obj)
        session.flush()
        if auto_commit:
            session.commit()
        return obj

    @classmethod
    def get(cls, session : Session = None, **kwargs) -> object:
        """
        Simply get a Row
        :param session:
        :param kwargs:
        :return:
        """
        sess = next(db.session()) if not session else session
        query = sess.query(cls)
        for key, val in kwargs.items():
            col = getattr(cls, key)
            query = query.filter(col == val)

        if query.count()>1:
            raise Exception("Only one row is supposed to be returned, but got more than one")
        result = query.first()
        if session:
            session.close()
        sess.close()
        return result

    @classmethod
    def filter(cls, session: Session = None, **kwargs):
        """
            get multiple row
            :param session:
            :param kwargs:
            :return :
        """
        condition = []
        for key,val in kwargs.items():
            key = key.split("__")
            
            if len(key)>2:
                raise Exception("No 2 more dunders") 
            col = getattr(cls, key[0]) # id column
            if len(key)==1: condition.append((col==val))
            elif len(key) == 2 and key[1] == 'gt': condition.append((col > val))
            elif len(key) == 2 and key[1] == 'gte': condition.append((col >= val))
            elif len(key) == 2 and key[1] == 'lt': condition.append((col < val))
            elif len(key) == 2 and key[1] == 'lte': condition.append((col <= val))
            elif len(key) == 2 and key[1] == 'in': condition.append((col.in_(val)))
        obj = cls()
        if session:
            obj._session = session
            obj.served = True
        else :
            obj._session = next(db.session())
            obj.served = False
        query = obj._session.query(cls)
        query = query.filter(*condition)
        obj._q = query
        return obj

    @classmethod
    def cls_attr(cls, col_name = None):
        if col_name :
            col = getattr(cls, col_name)
            return col
        else :
            return cls
    
    def order_by(self, *args : str):
        for a in args:
            if a.startswith("-"):
                col_name = a[1:]
                is_asc = False
            else :
                col_name = a
                is_asc = True
            col = self.cls_attr(col_name)
            self._q = self._q.order_by(col.asc()) if is_asc else self._q.order_by(col.des())
        return self

    def update(self, sess: Session = None, auto_commit : bool = False, **kwargs):
        qs = self._q.update(kwargs)
        get_id = self.id
        ret = None

        self._session.flush()
        if qs>0 :
            ret = self._q.first()
        if auto_commit:
            self._session.commit()
        return ret
    
    def first(self):
        result = self._q.first()
        self.close()
        return result
    
    def delete(self, auto_commit : bool = False):
        self._q.delete()
        if auto_commit :
            self._session.commit()
        self.close()

    def all(self):
        print(self.served)
        result = self._q.all()
        self.close()
        return result

    def count(self):
        result = self._q.count()
        self.close()
        return result

    def dict(self,*args : str):
        q_dict = {}
        for c in self.__table__.columns:
            if c.name in args:
                q_dict[c.name] = getattr(self,c.name)
        return q_dict

    def close(self):
        if not self.served:
            #self._session.commit()
            self._session.close()
        else :
            self._session.flush()




class Users(Base, BaseMixin):
    __tablename__ = "users"
    status = Column(Enum("active", "deleted", "blocked"), default="active")
    email = Column(String(length=255), nullable=True)
    pw = Column(String(length=2000), nullable=True)
    name = Column(String(length=255), nullable=True)
    phone_number = Column(String(length=20), nullable=True, unique=True)
    profile_img = Column(String(length=1000), nullable=True)
    sns_type = Column(Enum("FB", "G", "K"), nullable=True)
    marketing_agree = Column(Boolean, nullable=True, default=True)
    keys = relationship("ApiKeys", back_populates="users")

class ApiKeys(Base, BaseMixin):
    __tablename__ = "api_keys"
    access_key = Column(String(length=64), nullable=False, index=True)
    secret_key = Column(String(length=64), nullable=False)
    user_memo = Column(String(length=40), nullable=True)
    status = Column(Enum("active", "stopped", "deleted"), default="active")
    is_whitelisted = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    whitelist = relationship("ApiWhiteLists",backref="api_keys")
    users = relationship("Users",back_populates="keys")

class ApiWhiteLists(Base, BaseMixin):
    __tablename__ = "api_whitelists"
    ip_addr = Column(String(length=64), nullable=False)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False)