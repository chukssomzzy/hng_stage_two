#!/usr/bin/python3
"""Defines Organisation Model"""
from typing import Any, Dict, List, Optional
from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from models.association import users_organisations


class Organisation(Base):
    """Defines the organisation model"""
    _json_name = {
        "id": "orgId"
    }
    __tablename__ = "organisations"
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(255))
    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=users_organisations,
        back_populates="organisations"
    )
    __table_args__ = (
        Index("i_name", "name", "description"),
    )

    def set_name(self, name):
        """Set organisation name"""
        self.name = f"{name}'s Organisation"

    def to_dict(self) -> Dict[str, Any]:
        """return a json serialiable dict"""
        dict_copy = super().to_dict()
        if "users" in dict_copy:
            del dict_copy["users"]

        return dict_copy
