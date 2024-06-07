from datetime import datetime, date
import typing as t
import uuid

from sqlalchemy.orm import Mapped, DeclarativeBase, attributes, relationship
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.schema import Constraint
import sqlalchemy as sa

from errors import CreateDBException, UpdateDBException, GetDBException, DeleteDBException
from utils.funcs import is_kleymo


__all__ = [
    "Base",
    "UserModel",
    "RefreshTokenModel",
    "WelderModel",
    "WelderCertificationModel",
    "NDTModel"
]


class Base(DeclarativeBase): 

    @classmethod
    async def get(cls, conn: AsyncConnection, ident: uuid.UUID | str):
        try:
            stmt = cls._dump_get_stmt(ident)
            response = await conn.execute(stmt)
            result = response.mappings().one_or_none()

            return result

        except IntegrityError as e:
            raise GetDBException(e.args[0])
        

    @classmethod
    async def get_many(cls, conn: AsyncConnection, expression: sa.ColumnElement):
        try:
            stmt = cls._dump_get_many_stmt(expression)
            
            response = await conn.execute(stmt)

            result = response.mappings().all()

            amount = await cls.count(conn, expression)
            
            return (result, amount)
        except IntegrityError as e:
            raise GetDBException(e.args[0])
        

    @classmethod
    async def create(cls, *data: dict, conn: AsyncConnection):
        try:
            stmt = cls._dump_create_stmt(
                list(data)
            )

            await conn.execute(stmt)
        except IntegrityError as e:
            raise CreateDBException(e.args[0])


    @classmethod
    async def update(cls, conn: AsyncConnection, ident: uuid.UUID | str, data: dict[str, t.Any]):
        try:
            stmt = cls._dump_update_stmt(ident, data)
            await conn.execute(stmt)
        except IntegrityError as e:
            raise UpdateDBException(e.args[0])


    @classmethod
    async def delete(cls, conn: AsyncConnection, ident: uuid.UUID | str):
        try:
            stmt = cls._dump_delete_stmt(ident)
            await conn.execute(stmt)
        except IntegrityError as e:
            raise DeleteDBException(e.args[0])


    @classmethod
    async def count(cls, conn: AsyncConnection, expression: sa.ColumnElement | None = None):
        if isinstance(expression, sa.ColumnElement):
            stmt = sa.select(sa.func.count()).select_from(cls).where(expression)

            return (await conn.execute(stmt)).scalar_one()

        else:
            return (await conn.execute(sa.select(sa.func.count()).select_from(cls))).scalar_one()


    @classmethod
    def _get_column(cls, ident: str | uuid.UUID):
        return sa.inspect(cls).primary_key[0]


    @classmethod
    def _dump_create_stmt(cls, data: list[dict[str, t.Any]]):
        return sa.insert(cls).values(
            data
        )


    @classmethod
    def _dump_get_stmt(cls, ident: str | uuid.UUID):
        return sa.select(cls).where(
            cls._get_column(ident) == ident
        )


    @classmethod
    def _dump_get_many_stmt(cls, expression: sa.ColumnExpressionArgument):
        return sa.select(cls).filter(expression)
    

    @classmethod
    def _dump_update_stmt(cls, ident: str | uuid.UUID, data: dict[str, t.Any]):
        return sa.update(cls).where(
            cls._get_column(ident) == ident
        ).values(
            **data
        )


    @classmethod
    def _dump_delete_stmt(cls, ident: str | uuid.UUID):
        return sa.delete(cls).where(
            cls._get_column(ident) == ident
        )


class UserModel(Base):
    __tablename__ = "user_table"

    ident: Mapped[uuid.UUID] = sa.Column(sa.UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    name: Mapped[str] = sa.Column(sa.String(), nullable=False)
    login: Mapped[str] = sa.Column(sa.String(), unique=True, nullable=False)
    hashed_password: Mapped[str] = sa.Column(sa.String(), nullable=False)
    email: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    sign_date: Mapped[datetime] = sa.Column(sa.DateTime(), nullable=False)
    update_date: Mapped[datetime] = sa.Column(sa.DateTime(), nullable=False)
    login_date: Mapped[datetime] = sa.Column(sa.DateTime(), nullable=False)
    is_superuser: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False)
    

    @classmethod
    def _get_column(cls, ident: str | uuid.UUID) -> attributes.InstrumentedAttribute:
        if isinstance(ident, uuid.UUID):
            return UserModel.ident
        
        try:
            uuid.UUID(ident)
            return UserModel.ident
        except:
            return UserModel.login


class RefreshTokenModel(Base):
    __tablename__ = "refresh_token_table"

    ident: Mapped[uuid.UUID] = sa.Column(sa.UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    user_ident: Mapped[uuid.UUID] = sa.Column(sa.UUID(as_uuid=True), sa.ForeignKey("user_table.ident", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    token: Mapped[str] = sa.Column(sa.String(), nullable=False, unique=True)
    revoked: Mapped[bool] = sa.Column(sa.Boolean(), nullable=False)
    exp_dt: Mapped[datetime] = sa.Column(sa.DateTime(), nullable=False)
    gen_dt: Mapped[datetime] = sa.Column(sa.DateTime(), nullable=False)
    

    @classmethod
    def _get_column(cls, ident: str | uuid.UUID) -> attributes.InstrumentedAttribute:
        if isinstance(ident, uuid.UUID):
            return RefreshTokenModel.ident
        
        try:
            uuid.UUID(ident)
            return RefreshTokenModel.ident
        except:
            return RefreshTokenModel.token


class WelderModel(Base):
    __tablename__ = "welder_table"

    ident: Mapped[uuid.UUID] = sa.Column(sa.UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    kleymo: Mapped[str] = sa.Column(sa.String(4), unique=True)
    name: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    birthday: Mapped[str | None] = sa.Column(sa.Date(), nullable=True)
    sicil: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    passport_number: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    nation: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    status: Mapped[str] = sa.Column(sa.SMALLINT, default=0)
    certifications: Mapped[list["WelderCertificationModel"]] = relationship("WelderCertificationModel", back_populates="welder")
    ndts: Mapped[list["NDTModel"]] = relationship("NDTModel", back_populates="welder")


    @classmethod
    def _get_column(cls, ident: str | uuid.UUID) -> attributes.InstrumentedAttribute:
        if isinstance(ident, str) and not is_kleymo(ident):
            ident = uuid.UUID(ident)

        return WelderModel.ident if isinstance(ident, uuid.UUID) else WelderModel.kleymo


class WelderCertificationModel(Base):
    __tablename__ = "welder_certification_table"

    ident: Mapped[uuid.UUID] = sa.Column(sa.UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    kleymo: Mapped[str] = sa.Column(sa.String(4), sa.ForeignKey("welder_table.kleymo", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    job_title: Mapped[str] = sa.Column(sa.String(), nullable=True)
    certification_number: Mapped[str] = sa.Column(sa.String(), nullable=False)
    certification_date: Mapped[date] = sa.Column(sa.Date(), nullable=False)
    expiration_date: Mapped[date] = sa.Column(sa.Date(), nullable=False)
    expiration_date_fact: Mapped[date] = sa.Column(sa.Date(), nullable=False)
    insert: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    certification_type: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    company: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    gtd: Mapped[list[str] | None] = sa.Column(sa.ARRAY(sa.String), nullable=True)
    method: Mapped[str] = sa.Column(sa.String(), nullable=True)
    details_type: Mapped[list[str] | None] = sa.Column(sa.ARRAY(sa.String), nullable=True)
    joint_type: Mapped[list[str] | None] = sa.Column(sa.ARRAY(sa.String), nullable=True)
    welding_materials_groups: Mapped[list[str] | None] = sa.Column(sa.ARRAY(sa.String), nullable=True)
    welding_materials: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    details_thikness_from: Mapped[float | None] = sa.Column(sa.Float(), nullable=True)
    details_thikness_before: Mapped[float | None] = sa.Column(sa.Float(), nullable=True)
    outer_diameter_from: Mapped[float | None] = sa.Column(sa.Float(), nullable=True)
    outer_diameter_before: Mapped[float | None] = sa.Column(sa.Float(), nullable=True)
    welding_position: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    connection_type: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    rod_diameter_from: Mapped[float | None] = sa.Column(sa.Float(), nullable=True)
    rod_diameter_before: Mapped[float | None] = sa.Column(sa.Float(), nullable=True)
    rod_axis_position: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    weld_type: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    joint_layer: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    sdr: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    automation_level: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    details_diameter_from: Mapped[float | None] = sa.Column(sa.Float(), nullable=True)
    details_diameter_before: Mapped[float | None] = sa.Column(sa.Float(), nullable=True)
    welding_equipment: Mapped[str | None] = sa.Column(sa.String(), nullable=True)

    welder: Mapped[WelderModel] = relationship("WelderModel", back_populates="certifications")

    certification_id = Constraint(sa.UniqueConstraint("certification_number", "insert", "certification_date", "expiration_date_fact"))

    @classmethod
    def _dump_get_many_stmt(cls, expression: sa.ColumnExpressionArgument) -> sa.Select:
        return sa.select(cls).join(WelderModel).filter(expression)
    

class NDTModel(Base):
    __tablename__ = "ndt_table"
    
    ident: Mapped[uuid.UUID] = sa.Column(sa.UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    kleymo: Mapped[str] = sa.Column(sa.String(4), sa.ForeignKey("welder_table.kleymo", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    company: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    subcompany: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    project: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    welding_date: Mapped[date] = sa.Column(sa.Date(), nullable=False)
    ndt_type: Mapped[str | None] = sa.Column(sa.String(), nullable=True)
    total_welded: Mapped[float | None] = sa.Column(sa.Float(), nullable=False, default=0)
    total_ndt: Mapped[float | None] = sa.Column(sa.Float(), nullable=False, default=0)
    accepted: Mapped[float | None] = sa.Column(sa.Float(), nullable=False, default=0)
    rejected: Mapped[float | None] = sa.Column(sa.Float(), nullable=False, default=0)
    
    welder: Mapped[WelderModel] = relationship("WelderModel", back_populates="ndts")

    
    @classmethod
    def _dump_get_many_stmt(cls, expression: sa.ColumnExpressionArgument) -> sa.Select:
        return sa.select(cls).join(WelderModel).filter(expression)
