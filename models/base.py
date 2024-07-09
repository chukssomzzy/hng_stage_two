#!/usr/bin/python3

"""Model Base Class for generalization"""
import copy
from datetime import datetime
from typing import Dict
from uuid import uuid4

from sqlalchemy import Index, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Defines Async Base Class For the Model"""
    _class_atr = {"id": uuid4, "updated_at": datetime.fromisoformat,
                  "created_at":  datetime.fromisoformat}
    _json_name = {}
    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=uuid4
    )
    # created_at: Mapped[datetime] = mapped_column(nullable=False,
    #                                              default=datetime.utcnow)
    # updated_at: Mapped[datetime] = mapped_column(nullable=False,
    #                                              default=datetime.utcnow)
    # __table_args__ = (
    #     Index("i_created_at", "created_at"),
    #     Index("i_updated_at", "updated_at"),
    #     Index("i_id_created_updated", "id", "created_at", "updated_at",
    #           unique=True),
    # )

    def __init__(self, *args, **kwargs) -> None:
        """Initializes the base class from kwargs"""
        if kwargs:
            for k, v in self._json_name.items():
                if v in kwargs:
                    kwargs[k] = kwargs.pop(v)
            if "id" not in kwargs:
                self.id = self.__gen_id()
            for k, v in kwargs.items():
                if k not in Base._class_atr:
                    setattr(self, k, v)
                else:
                    assert isinstance(v, str), "Argument to __init__ of a \
model class must be a string"
                    setattr(self, k, Base._class_atr[k](v))
        else:
            self.id = self.__gen_id()
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()

    def __gen_id(self) -> str:
        """Generate id for a class"""
        return str(uuid4())

    def __str__(self) -> str:
        """Get the string representation of an object"""
        return f"[{self.__class__.__name__}.{self.id!s}]({self.__dict__!s})"

    def update(self, *args, **kwargs) -> None:
        """Update a model object properties"""
        for k, v in kwargs.items():
            if k not in self._class_atr:
                setattr(self, k, v)
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict:
        """Convert object to a json serializable form"""
        dict_copy = copy.deepcopy(self.__dict__)

        if "created_at" in dict_copy:
            dict_copy["created_at"] = dict_copy["created_at"].isoformat()
        if "updated_at" in dict_copy:
            dict_copy["updated_at"] = dict_copy["updated_at"].isoformat()
        if "_sa_instance_state" in dict_copy:
            dict_copy.pop("_sa_instance_state", None)

        for k, v in self._json_name.items():
            if k in dict_copy:
                dict_copy[v] = dict_copy.pop(k)
        return dict_copy

    def save(self) -> None:
        """Save object to the database"""
        from models import engine
        engine.new(self)
