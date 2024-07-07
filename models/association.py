#!/usr/bin/python3
from sqlalchemy import Column, ForeignKey, Table
from models.base import Base

users_organisations = Table(
    "users_organisations",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "organisation_id",
        ForeignKey("organisations.id", ondelete="CASCADE"),
        primary_key=True
    )
)
