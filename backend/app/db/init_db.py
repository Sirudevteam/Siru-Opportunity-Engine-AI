from app.db.session import Base, engine

# Import models so SQLAlchemy registers metadata before create_all.
from app.models import entities  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

