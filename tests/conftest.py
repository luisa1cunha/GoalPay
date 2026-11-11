import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models
from app.database import Base


@pytest.fixture
def s():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as sessao:
        yield sessao