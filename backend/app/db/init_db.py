from app.core.config import get_settings
from app.db.session import Base, engine

# Import models so SQLAlchemy registers metadata before create_all.
from app.models import entities  # noqa: F401


def init_db() -> None:
    if not get_settings().auto_create_tables:
        return
    Base.metadata.create_all(bind=engine)

