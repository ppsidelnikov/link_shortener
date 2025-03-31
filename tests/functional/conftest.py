import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from main import app
from fastapi.testclient import TestClient
from app.db.session import get_db

@pytest.fixture(scope="session")
def test_db():
    # Создаём тестовую базу данных
    engine = create_engine("postgresql://postgres:postgres@localhost:5432/test_url_shortener")
    print("Creating tables...")
    Base.metadata.create_all(engine)  # Создаём все таблицы
    print("Tables created.")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


@pytest.fixture(scope="module")
def client(test_db):
    # Создаём TestClient
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture(scope='session', autouse=True)
def cleanup_db(test_db):
    # Выполняем тесты
    yield
    # Очищаем базу данных после каждого теста
    for table in reversed(Base.metadata.sorted_tables):
        test_db.execute(table.delete())
    test_db.commit()
