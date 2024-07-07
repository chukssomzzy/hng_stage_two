#!/usr/bin/python3

"""Defines Organisation Model"""


from os import getenv
from typing import Any, List, Optional, Union

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from models.base import Base
from models.organisations import Organisation
from models.users import User


class DBStorage:
    """Storage interface for database"""
    __classes = {
        "User": User,
        "Organisation": Organisation
    }
    __engine = None

    def __init__(self) -> None:
        """Connects sqlalchemy to storage and creates an engine"""
        db_name = getenv("DB_NAME")
        db_user = getenv("DB_USER")
        db_password = getenv("DB_PASS")
        db_host = getenv("DB_HOST")
        db_api = getenv("DB_API")
        db_dilect = getenv("DB_DIALECT")

        self.__engine = create_engine(
            "{}+{}://{}:{}@{}/{}".
            format(
                db_dilect,
                db_api,
                db_user,
                db_password,
                db_host,
                db_name), pool_pre_ping=True)

    def reload(self) -> None:
        """Reload and allocate a scoped session"""
        if getenv("ENVIRONMENT") == "TEST" and self.__engine:
            Base.metadata.drop_all(self.__engine)
        if self.__engine:
            Base.metadata.create_all(self.__engine)
            session_factory = sessionmaker(
                bind=self.__engine,
            )
            Session = scoped_session(session_factory)
            self.__Session = Session

    @property
    def session(self) -> Session:
        """Return the current session"""
        return self.__Session()

    def delete(self, obj) -> None:
        """Delete a obj from session"""
        self.session.delete(obj)

    def new(self, obj) -> None:
        """Add a new obj to session"""
        self.session.add(obj)

    def save(self) -> None:
        """flush update in session to db"""
        self.session.commit()

    def all(self, cls=None, page=None, limit=None):
        """Return all object in db storage related to a cls or all obj"""
        allObj = {}
        for clss in self.__classes:
            if not cls or cls == clss or cls == self.__classes[clss]:
                for obj in self.session.query(self.__classes[clss]).all():
                    key = obj.__class__.__name__ + "." + str(obj.id)
                    allObj[key] = obj
                if cls and len(allObj):
                    return allObj
        return allObj

    def get(
        self,
        cls: Union[Organisation, User, str],
        id:  str
    ) -> Optional[Union[Organisation, User]]:
        """Return a cls related to an id"""
        u_cls: Any = None
        if cls not in self.__classes and cls not in self.__classes.values():
            return None
        else:
            u_cls = cls
        if cls in self.__classes:
            u_cls = self.__classes[cls]
        org = self.session.query(u_cls).filter_by(id=id).one_or_none()
        return org

    def close(self) -> None:
        """Close the current session and request a new one"""
        if self.session:
            self.__Session.remove()

    def count(self, cls) -> int:
        """Count rows in a specific class or all class"""
        obj_count = 0
        for clss in self.__classes:
            if not cls or cls is self.__classes[clss] or cls == clss:
                obj_count = self.session.query(self.__classes[clss]).count()
                if obj_count and cls:
                    return obj_count
        return int(obj_count)

    def create(
        self,
        cls=None,
        **kwargs
    ) -> Optional[Union[Organisation, User]]:
        """Takes a cls and accepts kwargs to create a new obj"""
        cls_object: Optional[Union[Organisation, User]] = None
        if isinstance(cls, str) and cls in self.__classes:
            u_cls = self.__classes[cls]
            cls_object = u_cls(**kwargs)
        elif isinstance(cls, type) and issubclass(Base, cls):
            cls_object = cls(**kwargs)
        return cls_object

    def filter(self, cls, **kwargs) -> List:
        """Filter storage by list of kwargs"""
        obj_val = []
        if cls in self.__classes:
            cls = self.__classes[cls]
            filter_ses = self.session.query(cls)
            for key, val in kwargs.items():
                key_cls = getattr(cls, key)
                if key_cls:
                    filter_ses = filter_ses.filter(key_cls == val)
            for obj in filter_ses.all():
                obj_val.append(obj)
        return obj_val

    def exists(self, cls, id) -> bool:
        """Check if an obj with a particular ID exists"""
        if cls and cls in self.__classes:
            cls = self.__classes[cls]
            return bool(self.session.query(cls).filter_by(id=id).exists())
        return (False)
