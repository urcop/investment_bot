from sqlalchemy import Column, Integer, String, select, insert, func, BigInteger, Boolean, delete, update, and_
from sqlalchemy.orm import sessionmaker

from tg_bot.models.users import User
from tg_bot.services.db_base import Base


class Worker(Base):
    __tablename__ = 'workers'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    password = Column(String, default='1')
    active = Column(Boolean, default=False)

    @classmethod
    async def _get_last_worker_id(cls, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(func.max(cls.id))
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def add_worker(cls, user_id: int, password: str, session_maker: sessionmaker):
        async with session_maker() as db_session:
            worker_id = await cls._get_last_worker_id(session_maker=session_maker)
            sql = insert(cls).values(id=worker_id + 1 if worker_id else 1, user_id=user_id, password=password)
            result = await db_session.execute(sql)
            await db_session.commit()
            await User.set_role(user_id=user_id, role='worker', session_maker=session_maker)
            return result

    @classmethod
    async def delete_worker(cls, user_id: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = delete(cls).where(cls.user_id == user_id)
            result = await db_session.execute(sql)
            await db_session.commit()
            await User.set_role(user_id=user_id, role='user', session_maker=session_maker)
            return result

    @classmethod
    async def auth_worker(cls, user_id: int, password: str, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls).where(and_(user_id == cls.user_id, password == cls.password))
            result = await db_session.execute(sql)
            return True if result.first() else False

    @classmethod
    async def set_active(cls, user_id: int, active: bool, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = update(cls).where(user_id == cls.user_id).values({'active': active})
            result = await db_session.execute(sql)
            await db_session.commit()
            return result
