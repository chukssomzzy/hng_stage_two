#!/usr/bin/python3

"""A User model"""
from typing import Dict, Optional, List

import bcrypt
from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


from models.base import Base
from models.association import users_organisations


class User(Base):
    """Defines the user model"""
    _json_name = {
        "first_name": "firstName",
        "last_name": "lastName",
        "id": "userId"
    }
    __tablename__ = "users"
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    _password_hash: Mapped[str] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(255))
    organisations: Mapped[List["Organisation"]] = relationship(
        secondary=users_organisations,
        back_populates="users"
    )
    __table_args__ = (
        Index("i_email_first_last", "email", "first_name", "last_name",
              unique=True),
    )

    def __init__(self, *args, **kwargs):
        """Initializes user object"""
        if kwargs and "password" in kwargs:
            kwargs.pop("password")

        super().__init__(*args, **kwargs)

    def check_password(self, password: str) -> bool:
        """Check if the users password is correct"""
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self._password_hash.encode("utf-8")
        )

    def __str__(self):
        """Overload the str method"""
        _password_hash = self.__dict__.get("_password_hash")
        if _password_hash:
            del self.__dict__["_password_hash"]
        str_rep = super().__str__()
        self.__dict__["_password_hash"] = _password_hash
        return str_rep

    @property
    def password(self):
        """Get the value of password"""
        raise NotImplementedError("Password is not readable on user object")

    def set_password(self, password: str) -> None:
        """Set the password value on an object"""
        self._password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def to_dict(self) -> Dict:
        """Create a serializable user object"""
        dict_copy = super().to_dict()
        if "_password_hash" in dict_copy:
            dict_copy.pop("_password_hash", None)
        if "organisations" in dict_copy:
            del dict_copy["organisations"]

        return dict_copy
