from fastapi import Depends, Header, HTTPException, status

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


ROLE_GROUPS = {
    "read": {"admin", "manager", "sales", "operator", "readonly", "read_only", "system"},
    "operate": {"admin", "manager", "sales", "operator", "system"},
    "manage": {"admin", "manager", "system"},
}


def require_role(group: str):
    def dependency(actor: Actor = Depends(get_actor)) -> Actor:
        normalized = actor.role.lower().replace("-", "_")
        if normalized not in ROLE_GROUPS[group]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{actor.role}' cannot perform this action.",
            )
        return actor

    return dependency

