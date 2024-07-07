#!./venv/bin/python3

from typing import Any
from models import engine
from models.users import User


def create_user(first_name, last_name, email, password) -> Any:
    """create new user"""
    user = engine.filter("User", email=email)
    if user:
        for u in user.values():
            engine.delete(u)
            engine.save()
    new_user = engine.create(
        "User",
        first_name=first_name,
        last_name=last_name,
        email=email,
    )
    if isinstance(new_user, User):
        new_user.set_password(password)
    engine.new(new_user)
    return new_user


def run():
    """test models"""
    user: User = create_user("John", "Doe", "john@gmail.com", "1234")
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john@gmail.com"
    engine.save()


if __name__ == "__main__":
    run()
