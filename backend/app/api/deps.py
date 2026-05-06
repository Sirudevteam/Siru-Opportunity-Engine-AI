from fastapi import Header

from app.schemas import Actor


def get_actor(
    x_siru_user_id: str | None = Header(default=None),
    x_siru_user_name: str | None = Header(default=None),
    x_siru_role: str | None = Header(default=None),
) -> Actor:
    return Actor(
        id=x_siru_user_id or "system",
        name=x_siru_user_name or "system",
        role=x_siru_role or "system",
    )

