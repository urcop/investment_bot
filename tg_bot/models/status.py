from sqlalchemy import Column, Integer, String, select, insert
from sqlalchemy.orm import sessionmaker

from tg_bot.services.db_base import Base


class Status(Base):
    __tablename__ = 'status'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price_month = Column(Integer)
    price_three_month = Column(Integer)

    @classmethod
    async def get_id_by_name(cls, status_name: str, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.id).where(cls.name == status_name)
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def get_name_by_id(cls, status_id: str, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.name).where(cls.id == status_id)
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def get_price_month(cls, id: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.price_month).where(cls.id == id)
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def get_price_three_month(cls, id: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.price_three_month).where(cls.id == id)
            result = await db_session.execute(sql)
            return result.scalar()


class Status2User(Base):
    __tablename__ = 'status2user'
    id = Column(Integer, primary_key=True)
    status_id = Column(Integer)
    user_id = Column(Integer)
    end_time = Column(Integer)

    @classmethod
    async def add_status_to_user(cls, user_id: int, status_id: int, end_time: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = insert(cls).values(user_id=user_id, status_id=status_id, end_time=end_time)
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def get_user(cls, user_id: int, time_now: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.status_id).where(cls.user_id == user_id, cls.end_time > time_now)
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def get_end_time(cls, user_id: int, time_now: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.end_time).where(cls.user_id == user_id, cls.end_time > time_now)
            result = await db_session.execute(sql)
            return result.scalar()
