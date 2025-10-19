import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app # Импортируем наше Fastapi приложение
from app.core.models.base_model import Base # Импортируем Base для создания таблиц
from app.core.db_helper import db_helper # Импортируем наш db_helper для переопределения сессии
from app.core.config import settings # Импортируем настройки для получения URL тестовой БД


# Используем in-memory SQLite для тестов
# Это очень быстро и не требует поднятия отдельного Docker-контейнера
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Или, если нужна настоящая Postgres для более точного тестирования
# TEST_DATABASE_URL = settings.db.url.replace("db", "test_db") # Предполагаем, что имя БД в URL - 'db'
# Создаем асинхронный движок для тестовой БД
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

# Создаем фабрику сессий для тестовой БД
TestSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=test_engine,
)

# Фикстура для создания таблиц и очистки после каждого теста
@pytest.fixture(autouse=True)
async def init_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Переопределяем функцию получения сессии для тестов
async def override_get_test_session():
    async with TestSessionLocal() as session:
        yield session

# Переопределяем зависимость Fastapi на нашу тестовую сессию
app.dependency_overrides[db_helper.get_session] = override_get_test_session


# Фикстура для создания асинхронного тестового клиента
@pytest.fixture(scope="module")
async def ac() -> AsyncClient:
    # Создаем транспорт для нашего Fastapi-приложения
    transport = ASGITransport(app=app)
    # Создаем клиент, передавая транспорт и базовый URL
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac