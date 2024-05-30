import pytest
import json
from asyncio import run

from shemas import *
from database import engine
from settings import Settings
from shemas import *
from models import Base


@pytest.fixture(scope="module")
def prepare_db():
    assert Settings.DB_NAME() == "rhi_test"

    async def start_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    run(start_db())


def get_welders() -> list[WelderShema]:
    welders = json.load(open("test/test_data/welders.json", "r", encoding="utf-8"))
    return [WelderShema.model_validate(welder) for welder in welders]


def get_welder_certifications() -> list[WelderCertificationShema]:
    certifications = json.load(open("test/test_data/welder_certifications.json", "r", encoding="utf-8"))
    return [WelderCertificationShema.model_validate(certification) for certification in certifications]


def get_welder_ndts() -> list[NDTShema]:
    ndts = json.load(open("test/test_data/welder_ndts.json", "r", encoding="utf-8"))
    return [NDTShema.model_validate(ndt) for ndt in ndts]


def get_users() -> list[UserShema]:
    users = json.load(open("test/test_data/users.json", "r", encoding="utf-8"))
    return [UserShema.model_validate(user) for user in users]


def get_refresh_tokens() -> list[RefreshTokenShema]:
    tokens = json.load(open("test/test_data/refresh_tokens.json", "r", encoding="utf-8"))
    return [RefreshTokenShema.model_validate(token) for token in tokens]


def get_test_welders() -> list[WelderShema]:
    welders = json.load(open("test/test_data/test_welders.json", "r", encoding="utf-8"))
    return [WelderShema.model_validate(welder) for welder in welders]


def get_test_welder_certifications() -> list[WelderCertificationShema]:
    certifications = json.load(open("test/test_data/test_welder_certifications.json", "r", encoding="utf-8"))
    return [WelderCertificationShema.model_validate(certification) for certification in certifications]


def get_test_welder_ndts() -> list[NDTShema]:
    ndts = json.load(open("test/test_data/test_welder_ndts.json", "r", encoding="utf-8"))
    return [NDTShema.model_validate(ndt) for ndt in ndts]


@pytest.fixture
def welders() -> list[WelderShema]:
    return get_welders()


@pytest.fixture
def welder_certifications() -> list[WelderCertificationShema]:
    return get_welder_certifications()


@pytest.fixture
def ndts() -> list[NDTShema]:
    return get_welder_ndts()


@pytest.fixture
def users() -> list[UserShema]:
    return get_users()


@pytest.fixture
def refresh_tokens() -> list[RefreshTokenShema]:
    return get_refresh_tokens()


@pytest.fixture
def test_welders() -> list[WelderShema]:
    return get_test_welders()


@pytest.fixture
def test_welder_certifications() -> list[WelderCertificationShema]:
    return get_test_welder_certifications()


@pytest.fixture
def test_ndts() -> list[NDTShema]:
    return get_test_welder_ndts()
